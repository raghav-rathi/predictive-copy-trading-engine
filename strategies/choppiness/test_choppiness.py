"""Choppiness tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.choppiness import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.2):
    c = np.asarray(c, dtype=float)
    n = len(c)
    prev = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": prev,
            "h": np.maximum(c, prev) + spread,
            "l": np.minimum(c, prev) - spread,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestChoppiness(unittest.TestCase):
    def test_chop_bounds(self):
        rng = np.random.default_rng(101)
        df = indicators.add_indicators(_frame(100 + np.cumsum(rng.normal(0, 1.0, 300))))
        ch = df["chop"].dropna()
        self.assertTrue(bool(((ch >= 0) & (ch <= 100)).all()))

    def test_straight_trend_is_not_choppy(self):
        c = 100 + 1.0 * np.arange(200)
        df = indicators.add_indicators(_frame(c, spread=0.01))
        self.assertTrue(bool((df["chop"].dropna() < 38.2).all()))

    def test_space_filling_chop_scores_high(self):
        # maximally space-filling chop (alternating bars fill the window
        # range every bar) must score at the top of the index
        alt = 100 + np.cumsum(np.tile([1.5, -1.5], 150))
        df = indicators.add_indicators(_frame(alt, spread=0.05))
        ch = df["chop"].dropna().iloc[-50:]
        self.assertTrue(bool((ch > 61.8).all()))
        self.assertTrue(bool(df["choppy"].iloc[-50:].all()))

    def test_breakout_only_when_trending(self):
        # a breakout bar during chop must NOT enter
        t = np.arange(200)
        c = 100 + 2.0 * np.sin(t / 2.0)
        df = _run(_frame(c, spread=0.05))
        choppy_bars = df["choppy"].fillna(False)
        self.assertFalse(bool((df["long_entry"] & choppy_bars).any()))
        self.assertFalse(bool((df["short_entry"] & choppy_bars).any()))

    def test_trend_breakout_enters(self):
        rng = np.random.default_rng(102)
        c = np.concatenate([100 + 0.2 * np.sin(np.arange(100) / 2.0),
                            100 + 1.5 * np.arange(100)]) + rng.normal(0, 0.1, 200)
        df = _run(_frame(c, spread=0.05))
        self.assertTrue(bool(df["long_entry"].any()))

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(103)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 300))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        trunc = _run(_frame(c[:200]))
        np.testing.assert_allclose(
            df["chop"].iloc[199], trunc["chop"].iloc[199], rtol=1e-12
        )


if __name__ == "__main__":
    unittest.main()
