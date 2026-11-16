"""Schwager volatility-ratio tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.schwager_volatility_ratio import indicators, risk, signals


def _vr_frame():
    """60 flat bars (TR=1) with crafted wide bars.

    Bar 30: wide bearish (TR=3, close in lower quarter, ret5 < 0).
    Bar 40: wide bullish (TR=3, close in upper quarter, ret5 > 0).
    Bar 50: narrow bearish (TR=1.5 -- below the VR>2 threshold).
    Bar 55: wide bar closing mid-range (no fade signal).
    """
    n = 60
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    c = np.full(n, 100.0)
    o = c.copy()
    h = np.full(n, 100.5)
    l = np.full(n, 99.5)
    v = np.full(n, 100.0)
    h[30], l[30], c[30] = 101.5, 98.5, 98.7
    h[40], l[40], c[40] = 101.5, 98.5, 101.3
    h[50], l[50], c[50] = 100.75, 99.25, 99.3
    h[55], l[55], c[55] = 101.5, 98.5, 100.0
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


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


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("vr", "bar_pos", "ret5", "atr"):
            self.assertIn(col, ind.columns)

    def test_vr_analytic_on_flat_then_wide(self):
        ind = indicators.add_indicators(_vr_frame())
        # 29 bars of TR=1, so EMA(prior TR) = 1.0; bar 30 TR=3 -> VR=3
        self.assertAlmostEqual(ind["vr"].iloc[30], 3.0, places=6)

    def test_vr_excludes_current_bar(self):
        # a lone wide bar must read VR>2 on its own bar (its TR is not
        # in its own EMA denominator), then decay on later bars
        ind = indicators.add_indicators(_vr_frame())
        self.assertGreater(ind["vr"].iloc[30], 2.0)
        self.assertLess(ind["vr"].iloc[31], ind["vr"].iloc[30])

    def test_bar_pos_analytic(self):
        ind = indicators.add_indicators(_vr_frame())
        self.assertAlmostEqual(ind["bar_pos"].iloc[30], 0.2 / 3.0, places=6)
        self.assertAlmostEqual(ind["bar_pos"].iloc[40], 2.8 / 3.0, places=6)
        self.assertAlmostEqual(ind["bar_pos"].iloc[55], 0.5, places=6)

    def test_ret5_analytic(self):
        ind = indicators.add_indicators(_vr_frame())
        self.assertAlmostEqual(ind["ret5"].iloc[30], -0.013, places=6)
        self.assertAlmostEqual(ind["ret5"].iloc[40], 0.013, places=6)

    def test_vr_flat_is_one(self):
        df = _vr_frame()
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["vr"].iloc[20:30], 1.0))

    def test_warmup_nans(self):
        ind = indicators.add_indicators(_frame())
        self.assertTrue(ind["vr"].iloc[:14].isna().all())
        self.assertFalse(ind["vr"].iloc[15:].isna().any())

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_bearish_wide_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_vr_frame()))
        self.assertTrue(sig["long_entry"].iloc[30])
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_short_entry_on_bullish_wide_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_vr_frame()))
        self.assertTrue(sig["short_entry"].iloc[40])
        self.assertEqual(sig["short_entry"].sum(), 1)

    def test_no_entry_below_vr_threshold(self):
        sig = signals.add_signals(indicators.add_indicators(_vr_frame()))
        self.assertFalse(sig["long_entry"].iloc[50])
        self.assertFalse(sig["short_entry"].iloc[50])

    def test_no_entry_on_mid_range_wide_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_vr_frame()))
        self.assertFalse(sig["long_entry"].iloc[55])
        self.assertFalse(sig["short_entry"].iloc[55])

    def test_no_entry_when_ret5_disagrees(self):
        # bearish-position wide bar but 5-bar return positive: no fade
        df = _vr_frame()
        df.loc[30, "c"] = 98.7
        # lift the closes 5 bars back so ret5 flips positive
        df.loc[25, "c"] = 97.0
        df.loc[25, "h"] = 97.5
        df.loc[25, "l"] = 96.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(sig["long_entry"].iloc[30])

    def test_exits_are_opposite_wide_bars(self):
        sig = signals.add_signals(indicators.add_indicators(_vr_frame()))
        pd.testing.assert_series_equal(
            sig["long_exit"], sig["short_entry"], check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], sig["long_entry"], check_names=False)

    def test_one_entry_per_wide_bar(self):
        # consecutive wide bars each emit exactly one signal
        df = _vr_frame()
        df.loc[31, "h"] = 101.5
        df.loc[31, "l"] = 98.5
        df.loc[31, "c"] = 98.8
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].iloc[30])
        self.assertTrue(sig["long_entry"].iloc[31])
        self.assertEqual(sig["long_entry"].sum(), 2)

    def test_no_lookahead(self):
        df = _vr_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 30
        trunc = signals.add_signals(
            indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 10)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertEqual(risk.WARMUP, 30)

    def test_registration(self):
        import strategies.schwager_volatility_ratio as mod
        from strategies.registry import REGISTRY

        self.assertIn("schwager_volatility_ratio", REGISTRY)
        self.assertIs(REGISTRY["schwager_volatility_ratio"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "schwager_volatility_ratio")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
