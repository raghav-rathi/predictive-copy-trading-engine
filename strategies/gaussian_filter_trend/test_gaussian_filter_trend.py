"""Gaussian filter trend tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.gaussian_filter_trend import indicators, risk, signals
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
    """Slow sine swings: fast/slow Gaussian filters cross repeatedly."""
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
        for col in ("gf_p10", "gf_p30", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_alpha_values(self):
        # alpha = (1 - sin(2*pi/P)) / cos(2*pi/P); both in (0, 1).
        self.assertAlmostEqual(indicators.alpha(10), 0.5095, places=3)
        self.assertAlmostEqual(indicators.alpha(30), 0.8096, places=3)
        self.assertTrue(0 < indicators.alpha(10) < 1)
        self.assertTrue(0 < indicators.alpha(30) < 1)
        # Longer period -> larger alpha -> smoother (more weight on history).
        self.assertGreater(indicators.alpha(30), indicators.alpha(10))

    def test_constant_series_passes_through(self):
        # Coefficient bracket sums to exactly 1, so a constant input is
        # preserved by every pole count.
        s = pd.Series(np.full(200, 42.0))
        for poles in (1, 2, 3, 4):
            got = indicators.gaussian_filter(s, 10, poles)
            self.assertTrue(np.allclose(got, 42.0, atol=1e-9), poles)

    def test_four_pole_recursion_matches_formula(self):
        # Independent re-implementation of the brief's recursion.
        s = self.df["c"]
        a = indicators.alpha(10)
        b = 1.0 - a
        g = s.to_numpy(dtype=float)
        f = np.empty(len(g))
        f[:4] = g[:4]
        for i in range(4, len(g)):
            f[i] = (a**4 * g[i] + 4 * b * f[i - 1] - 6 * b**2 * f[i - 2]
                    + 4 * b**3 * f[i - 3] - b**4 * f[i - 4])
        got = indicators.gaussian_filter(s, 10, 4).to_numpy()
        self.assertTrue(np.allclose(got, f, atol=1e-9))

    def test_filter_smoother_than_price(self):
        # CORRECTION: with Ehlers' alpha the period-10 filter is the
        # SLOWER baseline (smaller bar-to-bar moves) and period-30 the
        # faster tracker. Both are smoother than raw price.
        c = self.df["c"]
        self.assertLess(self.ind["gf_p10"].diff().abs().mean(),
                        c.diff().abs().mean())
        self.assertLess(self.ind["gf_p30"].diff().abs().mean(),
                        c.diff().abs().mean())
        self.assertLess(self.ind["gf_p10"].diff().abs().mean(),
                        self.ind["gf_p30"].diff().abs().mean())

    def test_filter_lags_price_on_trend(self):
        # On a steady uptrend both filters sit below price; the
        # period-10 (slow) line lags further below than period-30.
        n = 300
        c = pd.Series(100 + 0.1 * np.arange(n))
        slow = indicators.gaussian_filter(c, 10, 4)
        fast = indicators.gaussian_filter(c, 30, 4)
        self.assertTrue((fast.iloc[50:] < c.iloc[50:]).all())
        self.assertTrue((slow.iloc[50:] < fast.iloc[50:]).all())
        # Measured steady-state lags: ~0.385 (P=10) vs ~0.094 (P=30).
        self.assertAlmostEqual(float((c - slow).iloc[200]), 0.385, places=2)
        self.assertAlmostEqual(float((c - fast).iloc[200]), 0.094, places=2)

    def test_p30_crosses_p10_at_swing_extremes(self):
        # The corrected crossover buys bottoms and sells tops: on a
        # sine wave, P=30 crosses above P=10 near troughs and below
        # it near peaks.
        n = 720
        x = np.linspace(0, 3 * 2 * np.pi, n)
        c = pd.Series(100 + 25 * np.sin(x))
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": c, "h": c + 0.1, "l": c - 0.1, "c": c, "v": 100.0,
        })
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        ups = np.where(sig["long_entry"])[0]
        dns = np.where(sig["short_entry"])[0]
        self.assertGreater(len(ups), 0)
        self.assertGreater(len(dns), 0)
        # Long entries land near troughs (price < 85), shorts near peaks (> 115).
        self.assertTrue(all(c.iloc[i] < 85 for i in ups if i > 50))
        self.assertTrue(all(c.iloc[i] > 115 for i in dns if i > 50))

    def test_no_nans_after_warmup(self):
        self.assertFalse(self.ind["gf_p10"].iloc[100:].isna().any())
        self.assertFalse(self.ind["gf_p30"].iloc[100:].isna().any())

    def test_invalid_poles_rejected(self):
        with self.assertRaises(ValueError):
            indicators.gaussian_filter(self.df["c"], 10, 5)

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

    def test_entries_are_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        fast, slow = ind["gf_p30"], ind["gf_p10"]
        pd.testing.assert_series_equal(
            sig["long_entry"], B.crossed_above(fast, slow).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_entry"], B.crossed_below(fast, slow).fillna(False).astype(bool),
            check_names=False)

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        fast, slow = ind["gf_p30"], ind["gf_p10"]
        pd.testing.assert_series_equal(
            sig["long_exit"], B.crossed_below(fast, slow).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], B.crossed_above(fast, slow).fillna(False).astype(bool),
            check_names=False)

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
        self.assertEqual(risk.WARMUP, 100)

    def test_registration(self):
        import strategies.gaussian_filter_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("gaussian_filter_trend", REGISTRY)
        self.assertIs(REGISTRY["gaussian_filter_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "gaussian_filter_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
