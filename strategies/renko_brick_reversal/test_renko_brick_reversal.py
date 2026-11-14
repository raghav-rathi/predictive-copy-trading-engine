"""Renko brick reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.renko_brick_reversal import indicators, risk, signals
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


def _stair_frame():
    """Deterministic closes: 5 down steps, then up steps, then down steps.

    Each step is exactly one brick (brick=2.0 passed directly to
    renko_bricks), so brick counts are exact.
    """
    closes = [100.0]
    for _ in range(5):   # 5 down bricks: 100 -> 90
        closes.append(closes[-1] - 2.0)
    for _ in range(4):   # 4 up bricks: 90 -> 98
        closes.append(closes[-1] + 2.0)
    for _ in range(5):   # 5 down bricks: 98 -> 88
        closes.append(closes[-1] - 2.0)
    n = len(closes)
    c = np.array(closes)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("brick_size", "renko_dir", "renko_run", "renko_prev_run",
                    "renko_top", "renko_bottom", "renko_bricks", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_brick_size_is_mean_atr_first_200(self):
        a = B.atr(self.df["h"], self.df["l"], self.df["c"], 14)
        expect = float(a.iloc[13:200].mean())
        self.assertAlmostEqual(float(self.ind["brick_size"].iloc[0]), expect, places=9)
        self.assertTrue((self.ind["brick_size"] == expect).all())

    def test_brick_size_positive(self):
        self.assertGreater(float(self.ind["brick_size"].iloc[0]), 0)

    def test_stair_bricks_exact(self):
        # direct unit check of the brick builder with a fixed brick size
        rb = indicators.renko_bricks(_stair_frame()["c"], 2.0)
        # closes: 100, 98, 96, 94, 92, 90, 92, 94, 96, 98, 96, 94, 92, 90, 88
        # The first up step (90 -> 92) does NOT clear the last brick top
        # (92) + brick (2), so bricks are: 5 down, 3 up, 4 down = 12 total.
        self.assertEqual(int(rb["renko_bricks"].iloc[-1]), 12)
        self.assertEqual(int(rb["renko_dir"].iloc[5]), -1)   # after 5 down
        self.assertEqual(int(rb["renko_run"].iloc[5]), 5)
        self.assertEqual(int(rb["renko_dir"].iloc[9]), 1)    # after 3 up
        self.assertEqual(int(rb["renko_run"].iloc[9]), 3)
        self.assertEqual(int(rb["renko_prev_run"].iloc[9]), 5)  # run before was 5 down
        self.assertEqual(int(rb["renko_dir"].iloc[-1]), -1)
        self.assertEqual(int(rb["renko_run"].iloc[-1]), 4)
        self.assertEqual(int(rb["renko_prev_run"].iloc[-1]), 3)

    def test_multi_brick_bar(self):
        # one bar jumping 3 brick sizes prints 3 bricks at once
        c = pd.Series([100.0, 100.0, 106.0, 106.0])
        rb = indicators.renko_bricks(c, 2.0)
        self.assertEqual(int(rb["renko_bricks"].iloc[2]), 3)
        self.assertEqual(int(rb["renko_run"].iloc[2]), 3)

    def test_no_nan_after_warmup(self):
        self.assertFalse(self.ind["renko_dir"].iloc[220:].isna().any())
        self.assertFalse(self.ind["atr"].iloc[220:].isna().any())

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

    def test_stair_reversals_fire_once_each(self):
        df = _stair_frame()
        rb = indicators.renko_bricks(df["c"], 2.0)
        df = pd.concat([df, rb], axis=1)
        df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
        sig = signals.add_signals(df)
        # bullish 2-brick reversal completes on the 2nd up brick (bar 8):
        # 5 down bricks, then up bricks print at bars 7, 8, 9
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(bool(sig["long_entry"].iloc[8]))
        # bearish 2-brick reversal completes on the 2nd down brick (bar 12)
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertTrue(bool(sig["short_entry"].iloc[12]))
        # exits are the opposite reversals
        self.assertTrue(bool(sig["long_exit"].iloc[12]))
        self.assertTrue(bool(sig["short_exit"].iloc[8]))

    def test_no_reversal_without_three_brick_run(self):
        # 2 down bricks only, then 2 up bricks: prev run is 2, not >= 3
        closes = [100.0, 98.0, 96.0, 98.0, 100.0, 102.0]
        c = pd.Series(closes)
        rb = indicators.renko_bricks(c, 2.0)
        df = pd.DataFrame({"c": c})
        df = pd.concat([df, rb], axis=1)
        df["atr"] = pd.Series([1.0] * len(c))
        sig = signals.add_signals(df)
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_entries_fire_on_random_walk(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _frame()
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
        self.assertEqual(risk.WARMUP, 220)

    def test_registration(self):
        import strategies.renko_brick_reversal as mod
        from strategies.registry import REGISTRY

        self.assertIn("renko_brick_reversal", REGISTRY)
        self.assertIs(REGISTRY["renko_brick_reversal"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "renko_brick_reversal")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
