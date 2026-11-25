"""MESA Sine Wave tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mesa_sine_wave import indicators, risk, signals


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


def _sine_df(n=600, period=40, amp=10.0, seed=3):
    rng = np.random.default_rng(seed)
    x = np.arange(n)
    c = 100.0 + amp * np.sin(2 * np.pi * x / period) + rng.normal(0, 0.3, n)
    return _df_from_c(c)


class TestMesaSineWave(unittest.TestCase):
    def test_sine_and_lead_bounded_and_in_phase(self):
        df = indicators.add_indicators(_sine_df())
        valid = df.iloc[130:]
        self.assertFalse(valid["mesa_sine"].isna().any())
        self.assertFalse(valid["mesa_lead_sine"].isna().any())
        self.assertTrue(bool(((valid["mesa_sine"] >= -1.0) & (valid["mesa_sine"] <= 1.0)).all()))
        self.assertTrue(bool(((valid["mesa_lead_sine"] >= -1.0) & (valid["mesa_lead_sine"] <= 1.0)).all()))

    def test_lead_is_phase_plus_45_degrees(self):
        df = indicators.add_indicators(_sine_df())
        valid = df.iloc[130:]
        expect = np.sin(valid["mesa_phase"] + np.pi / 4.0)
        self.assertTrue(bool(np.allclose(valid["mesa_lead_sine"], expect, atol=1e-9)))

    def test_period_clamped_6_to_50(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        valid = df["mesa_period"].iloc[130:]
        self.assertTrue(bool(((valid >= 6.0) & (valid <= 50.0)).all()))

    def test_period_recovers_known_cycle(self):
        df = indicators.add_indicators(_sine_df(n=800, period=40))
        med = float(np.median(df["mesa_period"].iloc[200:]))
        self.assertTrue(20.0 <= med <= 50.0, med)

    def test_sine_wave_tracks_known_cycle(self):
        # sine should correlate positively with the underlying cycle
        df = indicators.add_indicators(_sine_df(n=800, period=40, amp=10.0))
        valid = df.iloc[200:]
        cyc = np.sin(2 * np.pi * np.arange(200, 800) / 40.0)
        corr = float(np.corrcoef(valid["mesa_sine"], cyc)[0, 1])
        self.assertTrue(corr > 0.3, corr)

    def test_cycle_fires_both_directions(self):
        sig = signals.add_signals(indicators.add_indicators(_sine_df(n=800, period=40)))
        self.assertTrue(bool(sig["long_entry"].iloc[130:].any()))
        self.assertTrue(bool(sig["short_entry"].iloc[130:].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("mesa_sine", "mesa_lead_sine", "mesa_phase", "mesa_period", "mesa_i2", "mesa_q2"):
            self.assertFalse(sig[col].iloc[130:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_exits_are_opposite_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_smooth_param_changes_output(self):
        d1 = indicators.add_indicators(_sine_df(), smooth=0.1)
        d2 = indicators.add_indicators(_sine_df(), smooth=0.4)
        self.assertFalse(bool(np.allclose(d1["mesa_sine"].iloc[200:], d2["mesa_sine"].iloc[200:])))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("mesa_sine", "mesa_lead_sine", "mesa_phase", "mesa_period", "mesa_i2", "mesa_q2"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.mesa_sine_wave as mod

        self.assertEqual(mod.SPEC.slug, "mesa_sine_wave")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
