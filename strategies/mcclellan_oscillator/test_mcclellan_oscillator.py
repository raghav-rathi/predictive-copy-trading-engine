"""McClellan Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mcclellan_oscillator import indicators, risk, signals
from strategies import base as B


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _count_frame(n_up, n_down, n_flat=0):
    """Frame with an exact up/down/flat mix in the first window."""
    n = n_up + n_down + n_flat
    o = np.full(n, 100.0)
    c = np.array([101.0] * n_up + [99.0] * n_down + [100.0] * n_flat)
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _osc_frame(osc_values):
    """Indicator frame with a hand-built oscillator path (summation = cumsum)."""
    n = len(osc_values)
    osc = pd.Series(osc_values, dtype=float)
    summ = osc.fillna(0.0).cumsum()
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 100.0,
        "rana": 0.0, "mc_osc": osc, "mc_summation": summ, "atr": 1.0,
    })


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("rana", "mc_osc", "mc_summation", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_rana_all_up_is_1000(self):
        ind = indicators.add_indicators(_count_frame(24, 0))
        self.assertAlmostEqual(ind["rana"].iloc[23], 1000.0)

    def test_rana_all_down_is_minus_1000(self):
        ind = indicators.add_indicators(_count_frame(0, 24))
        self.assertAlmostEqual(ind["rana"].iloc[23], -1000.0)

    def test_rana_mixed_analytic(self):
        # 18 up, 6 down over the window: 1000*(18-6)/24 = 500.
        ind = indicators.add_indicators(_count_frame(18, 6))
        self.assertAlmostEqual(ind["rana"].iloc[23], 500.0)

    def test_rana_ties_neutral(self):
        # 12 up, 6 down, 6 flat: 1000*(12-6)/18 = 333.33 (flats excluded).
        ind = indicators.add_indicators(_count_frame(12, 6, 6))
        self.assertAlmostEqual(ind["rana"].iloc[23], 1000.0 * 6 / 18, places=6)

    def test_rana_bounded(self):
        self.assertTrue(((self.ind["rana"].dropna() >= -1000.0)
                         & (self.ind["rana"].dropna() <= 1000.0)).all())

    def test_osc_is_ema_difference(self):
        expect = B.ema(self.ind["rana"], 19) - B.ema(self.ind["rana"], 39)
        pd.testing.assert_series_equal(self.ind["mc_osc"], expect, check_names=False)

    def test_summation_is_cumsum_of_osc(self):
        expect = self.ind["mc_osc"].fillna(0.0).cumsum()
        pd.testing.assert_series_equal(
            self.ind["mc_summation"], expect, check_names=False)

    def test_warmup_nans(self):
        self.assertTrue(self.ind["rana"].iloc[:23].isna().all())
        self.assertFalse(self.ind["rana"].iloc[23:].isna().any())
        # EMA39 needs 39 non-NaN RANA values; RANA starts at index 23,
        # so the oscillator's first valid bar is index 23 + 38 = 61.
        self.assertTrue(self.ind["mc_osc"].iloc[:61].isna().all())
        self.assertFalse(self.ind["mc_osc"].iloc[61:].isna().any())

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_cross_after_deep_excursion(self):
        # Oscillator deep below -50, then crosses above 0; summation rises.
        osc = [-80.0, -70.0, -60.0, -55.0, -30.0, -5.0, 4.0, 10.0, 12.0]
        sig = signals.add_signals(_osc_frame(osc))
        self.assertTrue(sig["long_entry"].iloc[6])
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_no_long_without_excursion(self):
        # Cross above 0 from just -5: no -50 excursion, no entry.
        osc = [-5.0, -4.0, -3.0, -2.0, -1.0, 2.0, 5.0, 8.0]
        sig = signals.add_signals(_osc_frame(osc))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_short_entry_on_cross_after_high_excursion(self):
        osc = [80.0, 70.0, 60.0, 55.0, 30.0, 5.0, -4.0, -10.0, -12.0]
        sig = signals.add_signals(_osc_frame(osc))
        self.assertTrue(sig["short_entry"].iloc[6])
        self.assertEqual(sig["short_entry"].sum(), 1)

    def test_no_short_without_excursion(self):
        osc = [5.0, 4.0, 3.0, 2.0, 1.0, -2.0, -5.0, -8.0]
        sig = signals.add_signals(_osc_frame(osc))
        self.assertEqual(sig["short_entry"].sum(), 0)

    def test_long_exit_on_cross_back(self):
        osc = [-80.0, -60.0, -30.0, -5.0, 4.0, 10.0, 8.0, -2.0, -6.0]
        sig = signals.add_signals(_osc_frame(osc))
        # Cross back below 0 at index 7 (summation also falls there).
        self.assertTrue(sig["long_exit"].iloc[7])

    def test_short_exit_on_cross_back(self):
        osc = [80.0, 60.0, 30.0, 5.0, -4.0, -10.0, -8.0, 2.0, 6.0]
        sig = signals.add_signals(_osc_frame(osc))
        self.assertTrue(sig["short_exit"].iloc[7])

    def test_entries_fire_on_random_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertGreater(sig["long_entry"].sum() + sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.target_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.mcclellan_oscillator as mod
        from strategies.registry import REGISTRY

        self.assertIn("mcclellan_oscillator", REGISTRY)
        self.assertIs(REGISTRY["mcclellan_oscillator"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "mcclellan_oscillator")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
