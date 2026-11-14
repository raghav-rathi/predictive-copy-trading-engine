"""Fibonacci cluster tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fibonacci_cluster import indicators, risk, signals
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


def _swing_frame(n=700, seed=21, cycles=6):
    """Slow sine swings: clean 5-bar fractal pivots in both directions."""
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
        self.df = _swing_frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("atr", "fib_sup", "fib_sup_n", "fib_res", "fib_res_n",
                    "fib_n_clusters", "fib_n_pivots", "fib_n_swings"):
            self.assertIn(col, self.ind.columns)

    def test_pivots_detected_and_alternate(self):
        # sine swings of +-25% produce many >= 2% swings
        self.assertGreater(int(self.ind["fib_n_pivots"].iloc[-1]), 10)
        self.assertGreater(int(self.ind["fib_n_swings"].iloc[-1]), 10)

    def test_clusters_form(self):
        # clusters exist on a large share of bars once swings form
        after = self.ind.iloc[120:]
        self.assertGreater((after["fib_n_clusters"] > 0).mean(), 0.5)

    def test_cluster_members_from_different_swings(self):
        # every reported cluster has >= 2 members (by construction)
        sup_n = self.ind.loc[self.ind["fib_sup"].notna(), "fib_sup_n"]
        res_n = self.ind.loc[self.ind["fib_res"].notna(), "fib_res_n"]
        self.assertTrue((sup_n >= 2).all())
        self.assertTrue((res_n >= 2).all())

    def test_support_below_close_resistance_above(self):
        m = self.ind["fib_sup"].notna()
        self.assertTrue((self.ind.loc[m, "fib_sup"] < self.ind.loc[m, "c"]).all())
        m = self.ind["fib_res"].notna()
        self.assertTrue((self.ind.loc[m, "fib_res"] > self.ind.loc[m, "c"]).all())

    def test_pivot_confirmation_lag(self):
        # a pivot centred on bar i only appears in the zigzag at bar i+2:
        # a V-trough at bar 29 (low pivot) and a spike peak at bar 30
        # (high pivot) must not be counted before bars 31 / 32.
        n = 60
        c = np.concatenate([
            np.linspace(100.0, 90.0, 30),   # steady decline to the trough
            [110.0],                        # single-bar spike peak
            np.full(29, 100.0),
        ])
        o = np.concatenate([[100.0], c[:-1]])
        h = np.maximum(o, c)
        l = np.minimum(o, c)
        v = np.full(n, 100.0)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})
        ind = indicators.add_indicators(df)
        # nothing confirmed before bar 31 (trough centre 29 + 2 bars)
        self.assertEqual(int(ind["fib_n_pivots"].iloc[30]), 0)
        self.assertGreaterEqual(int(ind["fib_n_pivots"].iloc[31]), 1)
        # the spike peak (centre 30) joins at bar 32
        self.assertGreaterEqual(int(ind["fib_n_pivots"].iloc[32]), 2)

    def test_levels_are_retracements_of_last_swings(self):
        # cluster_levels groups levels within width only when >= 2 swings agree
        lv = [(100.0, 0), (100.3, 1), (105.0, 0)]
        cl = indicators.cluster_levels(lv, width=0.5)
        self.assertEqual(len(cl), 1)
        self.assertAlmostEqual(cl[0][0], 100.15, places=9)
        self.assertEqual(cl[0][1], 2)
        # a lone level from one swing is not a cluster
        cl = indicators.cluster_levels([(100.0, 0), (105.0, 1)], width=0.5)
        self.assertEqual(len(cl), 0)

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

    def test_entries_fire_both_sides_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)
        self.assertGreater(sig["long_exit"].sum(), 0)
        self.assertGreater(sig["short_exit"].sum(), 0)

    def test_long_entry_is_a_bounce(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        longs = sig["long_entry"]
        self.assertTrue((ind.loc[longs, "l"] <= ind.loc[longs, "fib_sup"]
                         + 0.25 * ind.loc[longs, "atr"]).all())
        self.assertTrue((ind.loc[longs, "c"] > ind.loc[longs, "fib_sup"]).all())
        shorts = sig["short_entry"]
        self.assertTrue((ind.loc[shorts, "h"] >= ind.loc[shorts, "fib_res"]
                         - 0.25 * ind.loc[shorts, "atr"]).all())
        self.assertTrue((ind.loc[shorts, "c"] < ind.loc[shorts, "fib_res"]).all())

    def test_no_entries_without_clusters(self):
        # flat prices: no pivots, no swings, no clusters, no signals
        n = 300
        c = np.full(n, 100.0)
        o, h, l = c.copy(), c.copy(), c.copy()
        v = np.full(n, 100.0)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(int(sig[col].sum()), 0)

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.WARMUP, 120)

    def test_registration(self):
        import strategies.fibonacci_cluster as mod
        from strategies.registry import REGISTRY

        self.assertIn("fibonacci_cluster", REGISTRY)
        self.assertIs(REGISTRY["fibonacci_cluster"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "fibonacci_cluster")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
