"""Sine-weighted MA trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sine_weighted_ma_trend import indicators, risk, signals
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


def _swing_frame(n=700, seed=21, cycles=3):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, cycles * 2 * np.pi, n)
    c = 100 + 25 * np.sin(x) + rng.normal(0, 0.4, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("swma_fast", "swma_slow", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_weights_half_sine_symmetric(self):
        w = indicators.swma_weights(20)
        self.assertEqual(len(w), 20)
        self.assertTrue(np.allclose(w, w[::-1]))
        self.assertTrue((w > 0).all())
        self.assertAlmostEqual(w[9], w.max(), places=12)
        # analytic: sin(pi*(i+1)/21)
        expect = np.sin(np.pi * (np.arange(20) + 1) / 21.0)
        self.assertTrue(np.allclose(w, expect))

    def test_swma_is_weighted_average(self):
        c = self.df["c"]
        w = indicators.swma_weights(20)
        expect = c.rolling(20, min_periods=20).apply(
            lambda x: float(np.dot(w, x)) / w.sum(), raw=True)
        got = self.ind["swma_fast"]
        pd.testing.assert_series_equal(got, expect, check_names=False)

    def test_swma_of_constant_is_constant(self):
        df = _frame()
        df["c"] = 50.0
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["swma_fast"].dropna(), 50.0))
        self.assertTrue(np.allclose(ind["swma_slow"].dropna(), 50.0))

    def test_warmup_nans(self):
        self.assertTrue(self.ind["swma_fast"].iloc[:19].isna().all())
        self.assertFalse(self.ind["swma_fast"].iloc[19:].isna().any())
        self.assertTrue(self.ind["swma_slow"].iloc[:39].isna().all())
        self.assertFalse(self.ind["swma_slow"].iloc[40:].isna().any())

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

    def test_entries_are_fast_slow_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        pd.testing.assert_series_equal(
            sig["long_entry"],
            B.crossed_above(ind["swma_fast"], ind["swma_slow"]).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_entry"],
            B.crossed_below(ind["swma_fast"], ind["swma_slow"]).fillna(False).astype(bool),
            check_names=False)

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        pd.testing.assert_series_equal(
            sig["long_exit"], sig["short_entry"], check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], sig["long_entry"], check_names=False)

    def test_crosses_fire_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.sine_weighted_ma_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("sine_weighted_ma_trend", REGISTRY)
        self.assertIs(REGISTRY["sine_weighted_ma_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "sine_weighted_ma_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
