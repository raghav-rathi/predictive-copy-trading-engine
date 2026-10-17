"""HalfTrend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.half_trend import indicators, risk, signals

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


class TestHalfTrend(unittest.TestCase):
    def test_line_below_price_in_uptrend(self):
        # strong steady uptrend: trend must be +1 and the line below close
        rng = np.random.default_rng(31)
        c = 100 + 0.5 * np.arange(400) + rng.normal(0, 0.3, 400).cumsum() * 0.05
        df = _run(_frame(c))
        tail = df.iloc[-50:]
        self.assertTrue(bool((tail["halftrend_dir"] == 1.0).all()))
        self.assertTrue(bool((tail["halftrend"] < tail["c"]).all()))

    def test_line_above_price_in_downtrend(self):
        rng = np.random.default_rng(32)
        c = 200 - 0.5 * np.arange(400) + rng.normal(0, 0.3, 400).cumsum() * 0.05
        df = _run(_frame(c))
        tail = df.iloc[-50:]
        self.assertTrue(bool((tail["halftrend_dir"] == -1.0).all()))
        self.assertTrue(bool((tail["halftrend"] > tail["c"]).all()))

    def test_flip_marks_entry(self):
        # V-shape: downtrend then uptrend forces at least one flip up
        rng = np.random.default_rng(33)
        c1 = 200 - 0.6 * np.arange(200)
        c2 = 80 + 0.6 * np.arange(200)
        c = np.concatenate([c1, c2]) + rng.normal(0, 0.2, 400).cumsum() * 0.05
        df = _run(_frame(c))
        self.assertTrue(bool(df["long_entry"].any()))

    def test_entries_are_mutually_exclusive_with_position(self):
        # no bar can be both a long and a short entry
        rng = np.random.default_rng(34)
        df = _run(_frame(100 + np.cumsum(rng.normal(0, 1.0, 500))))
        self.assertFalse(bool((df["long_entry"] & df["short_entry"]).any()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)

    def test_no_lookahead_on_line(self):
        # the line value at bar i must not depend on data after i
        rng = np.random.default_rng(35)
        c = 100 + np.cumsum(rng.normal(0, 1.0, 400))
        full = indicators.add_indicators(_frame(c))
        trunc = indicators.add_indicators(_frame(c[:250]))
        np.testing.assert_allclose(
            full["halftrend"].iloc[249], trunc["halftrend"].iloc[249], rtol=1e-9
        )


if __name__ == "__main__":
    unittest.main()
