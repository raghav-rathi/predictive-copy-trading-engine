"""Ehlers dominant-cycle tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_dominant_cycle import indicators, risk, signals


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


def _reference_bp(c):
    """Independent step-by-step recomputation of hp + bp."""
    hp_period = 2.0 * 20.0 / (1.0 - 0.7 / 2.0)
    a_hp = (1.0 - np.sin(2.0 * np.pi / hp_period)) / np.cos(2.0 * np.pi / hp_period)
    hp = np.zeros(len(c))
    for i in range(1, len(c)):
        hp[i] = 0.5 * (1.0 + a_hp) * (c[i] - c[i - 1]) + a_hp * hp[i - 1]
    beta = np.cos(2.0 * np.pi / 20.0)
    gamma = 1.0 / np.cos(4.0 * np.pi * 0.7 / 20.0)
    alpha = gamma - np.sqrt(gamma * gamma - 1.0)
    bp = np.zeros(len(c))
    for i in range(2, len(c)):
        bp[i] = (
            0.5 * (1.0 - alpha) * (hp[i] - hp[i - 2])
            + beta * (1.0 + alpha) * bp[i - 1]
            - alpha * bp[i - 2]
        )
    return hp, bp


class TestEhlersDominantCycle(unittest.TestCase):
    def test_bp_matches_direct_computation(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        hp, bp = _reference_bp(df["c"].to_numpy())
        self.assertTrue(bool(np.allclose(df["hp"].to_numpy(), hp, atol=1e-9)))
        self.assertTrue(bool(np.allclose(df["bp"].to_numpy(), bp, atol=1e-9)))

    def test_resonator_coeffs(self):
        beta, alpha = indicators._resonator_coeffs(20.0, 0.7)
        self.assertAlmostEqual(beta, np.cos(2.0 * np.pi / 20.0), places=12)
        gamma = 1.0 / np.cos(4.0 * np.pi * 0.7 / 20.0)
        self.assertAlmostEqual(alpha, gamma - np.sqrt(gamma * gamma - 1.0), places=12)
        self.assertTrue(0.0 < alpha < 1.0)

    def test_hp_detrender_kills_constant_and_trend(self):
        # flat series -> hp decays to ~0
        ind = indicators.add_indicators(_df_from_c(np.full(300, 100.0)))
        self.assertTrue(bool(np.abs(ind["hp"].iloc[50:]).max() < 1e-9))
        # linear trend -> hp settles at the analytic steady state
        # HP = 0.5*(1+a)/(1-a) * slope (a one-pole high-pass passes a
        # ramp as a constant offset, it removes the DC level, not the
        # slope); check it converges to that value, not to zero.
        slope = 0.05
        ind = indicators.add_indicators(_df_from_c(100.0 + slope * np.arange(600)))
        a_hp = (1.0 - np.sin(2.0 * np.pi / indicators.HP_PERIOD)) / np.cos(
            2.0 * np.pi / indicators.HP_PERIOD
        )
        steady = 0.5 * (1.0 + a_hp) / (1.0 - a_hp) * slope
        self.assertAlmostEqual(float(ind["hp"].iloc[300:].mean()), steady, places=3)

    def test_dominant_cycle_measures_sine_period_20(self):
        ind = indicators.add_indicators(_sine_df(period=20, n=600))
        # after spin-up the measured cycle should sit near the true 20
        med = float(np.median(ind["dom_cycle"].iloc[300:]))
        self.assertGreaterEqual(med, 16.0)
        self.assertLessEqual(med, 24.0)

    def test_dominant_cycle_measures_sine_period_40(self):
        ind = indicators.add_indicators(_sine_df(period=40, n=800))
        med = float(np.median(ind["dom_cycle"].iloc[400:]))
        self.assertGreaterEqual(med, 32.0)
        self.assertLessEqual(med, 48.0)

    def test_dominant_cycle_clamped(self):
        ind = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((ind["dom_cycle"] >= 6.0) & (ind["dom_cycle"] <= 50.0)).all()))
        self.assertFalse(ind["dom_cycle"].isna().any())

    def test_dominant_cycle_defaults_to_centre_period(self):
        # flat series: no zero crossings at all -> 20 throughout
        ind = indicators.add_indicators(_df_from_c(np.full(300, 100.0)))
        self.assertTrue(bool((ind["dom_cycle"] == 20.0).all()))

    def test_long_fires_on_bp_cross_up(self):
        sig = signals.add_signals(indicators.add_indicators(_sine_df(period=20, n=600)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        # every up-cross is both a long entry and a short exit
        self.assertTrue(bool((sig["long_entry"] == sig["short_exit"]).all()))
        self.assertTrue(bool((sig["short_entry"] == sig["long_exit"]).all()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_signals_match_crosses_directly(self):
        ind = indicators.add_indicators(_rand_df(800, seed=5))
        sig = signals.add_signals(ind)
        bp = ind["bp"]
        expect_up = ((bp > 0) & (bp.shift(1) <= 0)).fillna(False)
        expect_down = ((bp < 0) & (bp.shift(1) >= 0)).fillna(False)
        self.assertTrue(bool((sig["long_entry"] == expect_up).all()))
        self.assertTrue(bool((sig["short_entry"] == expect_down).all()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("hp", "bp", "dom_cycle", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("hp", "bp", "dom_cycle", "atr14"):
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

    def test_registration_imports_cleanly(self):
        import strategies.ehlers_dominant_cycle as mod

        self.assertEqual(mod.SPEC.slug, "ehlers_dominant_cycle")
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
