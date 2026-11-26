"""Ehlers universal oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_universal_osc import indicators, risk, signals


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _sine_df(period=20, n=600, amp=5.0):
    t = np.arange(n)
    c = 100.0 + amp * np.sin(2.0 * np.pi * t / period)
    return _df_from_c(c)


def _reference_bp(med):
    """Independent step-by-step recomputation of the resonator."""
    beta = np.cos(2.0 * np.pi / 20.0)
    gamma = 1.0 / np.cos(4.0 * np.pi * 0.3 / 20.0)
    alpha = gamma - np.sqrt(gamma * gamma - 1.0)
    bp = np.zeros(len(med))
    for i in range(2, len(med)):
        bp[i] = (
            0.5 * (1.0 - alpha) * (med[i] - med[i - 2])
            + beta * (1.0 + alpha) * bp[i - 1]
            - alpha * bp[i - 2]
        )
    return bp


class TestEhlersUniversalOsc(unittest.TestCase):
    def test_bp_matches_direct_computation(self):
        df = _rand_df(800, seed=5)
        ind = indicators.add_indicators(df)
        med = ((df["h"] + df["l"]) / 2).to_numpy()
        expect = _reference_bp(med)
        self.assertTrue(bool(np.allclose(ind["bp"].to_numpy(), expect, atol=1e-9)))

    def test_resonator_coeffs(self):
        beta, alpha = indicators._resonator_coeffs(20.0, 0.3)
        self.assertAlmostEqual(beta, np.cos(2.0 * np.pi / 20.0), places=12)
        gamma = 1.0 / np.cos(4.0 * np.pi * 0.3 / 20.0)
        self.assertAlmostEqual(alpha, gamma - np.sqrt(gamma * gamma - 1.0), places=12)
        self.assertTrue(0.0 < alpha < 1.0)

    def test_agc_normalizes_sine_to_unit_rms(self):
        # a steady sine through the resonator is sinusoidal, so
        # dividing by its rolling RMS should give ~unit RMS
        ind = indicators.add_indicators(_sine_df(period=20, n=600))
        tail = ind["bp_norm"].iloc[300:]
        rms = float(np.sqrt((tail ** 2).mean()))
        self.assertGreaterEqual(rms, 0.8)
        self.assertLessEqual(rms, 1.2)

    def test_agc_zero_guard_on_flat_series(self):
        # flat series -> BP is 0 -> RMS is 0 -> bp_norm is 0, not NaN
        ind = indicators.add_indicators(_df_from_c(np.full(300, 100.0)))
        self.assertTrue(bool((ind["bp"] == 0.0).all()))
        self.assertTrue(bool((ind["bp_norm"] == 0.0).all()))
        self.assertFalse(ind["bp_norm"].isna().any())

    def test_trigger_is_scaled_delayed_bp_norm(self):
        ind = indicators.add_indicators(_rand_df(800, seed=5))
        expect = ind["bp_norm"].shift(1) * 0.9
        ok = np.allclose(ind["trigger"].iloc[1:].to_numpy(),
                         expect.iloc[1:].to_numpy(), atol=1e-12)
        self.assertTrue(bool(ok))
        self.assertTrue(pd.isna(ind["trigger"].iloc[0]))

    def test_signals_match_crosses_directly(self):
        ind = indicators.add_indicators(_rand_df(800, seed=5))
        sig = signals.add_signals(ind)
        bp_norm, trig = ind["bp_norm"], ind["trigger"]
        expect_up = ((bp_norm > trig) & (bp_norm.shift(1) <= trig.shift(1))).fillna(False)
        expect_down = ((bp_norm < trig) & (bp_norm.shift(1) >= trig.shift(1))).fillna(False)
        self.assertTrue(bool((sig["long_entry"] == expect_up).all()))
        self.assertTrue(bool((sig["short_entry"] == expect_down).all()))
        self.assertTrue(bool((sig["long_entry"] == sig["short_exit"]).all()))
        self.assertTrue(bool((sig["short_entry"] == sig["long_exit"]).all()))

    def test_long_and_short_fire_on_sine(self):
        sig = signals.add_signals(indicators.add_indicators(_sine_df(period=20, n=600)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("bp", "bp_norm", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        # trigger is NaN only at bar 0 (shift of the first value)
        self.assertFalse(sig["trigger"].iloc[1:].isna().any())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("bp", "bp_norm", "trigger", "atr14"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_bandwidth_param_changes_bp(self):
        df1 = indicators.add_indicators(_rand_df(), bandwidth=0.3)
        df2 = indicators.add_indicators(_rand_df(), bandwidth=0.7)
        self.assertFalse(bool(np.allclose(df1["bp"].iloc[60:], df2["bp"].iloc[60:])))

    def test_trigger_scale_param_changes_trigger(self):
        df1 = indicators.add_indicators(_rand_df(), trigger_scale=0.9)
        df2 = indicators.add_indicators(_rand_df(), trigger_scale=0.5)
        self.assertFalse(bool(np.allclose(
            df1["trigger"].iloc[60:].fillna(0), df2["trigger"].iloc[60:].fillna(0))))

    def test_registration_imports_cleanly(self):
        import strategies.ehlers_universal_osc as mod

        self.assertEqual(mod.SPEC.slug, "ehlers_universal_osc")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
