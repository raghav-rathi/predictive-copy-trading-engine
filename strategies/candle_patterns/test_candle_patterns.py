"""Candlestick pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.candle_patterns import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(o, h, l, c, v=None):
    n = len(c)
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": np.asarray(o, dtype=float),
            "h": np.asarray(h, dtype=float),
            "l": np.asarray(l, dtype=float),
            "c": np.asarray(c, dtype=float),
            "v": np.full(n, 100.0) if v is None else np.asarray(v, dtype=float),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _quiet(n, px=100.0, seed=81):
    rng = np.random.default_rng(seed)
    c = px + rng.normal(0, 0.3, n).cumsum() * 0.2
    return c, c + 0.3, c - 0.3, c


class TestCandlePatterns(unittest.TestCase):
    def test_bullish_engulfing(self):
        c, h, l, cc = _quiet(40)
        o = list(c[:38]) + [101.0, 99.5]
        h = list(h[:38]) + [101.5, 102.5]
        l = list(l[:38]) + [99.0, 99.0]
        c = list(c[:38]) + [100.0, 102.0]  # bearish bar, then engulfing bull
        df = _run(_frame(o, h, l, c))
        self.assertTrue(bool(df["bull_engulf"].iloc[39]))
        self.assertTrue(bool(df["long_entry"].iloc[39]))

    def test_bearish_engulfing(self):
        c, h, l, cc = _quiet(40)
        o = list(c[:38]) + [99.0, 100.5]
        h = list(h[:38]) + [101.0, 101.0]
        l = list(l[:38]) + [98.5, 97.5]
        c = list(c[:38]) + [100.0, 98.0]
        df = _run(_frame(o, h, l, c))
        self.assertTrue(bool(df["bear_engulf"].iloc[39]))
        self.assertTrue(bool(df["short_entry"].iloc[39]))

    def test_bullish_pin_bar(self):
        c, h, l, cc = _quiet(40)
        # long lower wick, small body in the top third
        o = list(c[:39]) + [100.0]
        h = list(h[:39]) + [100.6]
        l = list(l[:39]) + [97.0]
        c = list(c[:39]) + [100.4]
        df = _run(_frame(o, h, l, c))
        self.assertTrue(bool(df["bull_pin"].iloc[39]))
        self.assertTrue(bool(df["long_entry"].iloc[39]))

    def test_doji_is_not_a_pin(self):
        # long wicks but body centered: not a pin bar
        c, h, l, cc = _quiet(40)
        o = list(c[:39]) + [100.0]
        h = list(h[:39]) + [102.0]
        l = list(l[:39]) + [98.0]
        c = list(c[:39]) + [100.0]
        df = _run(_frame(o, h, l, c))
        self.assertFalse(bool(df["bull_pin"].iloc[39]))
        self.assertFalse(bool(df["bear_pin"].iloc[39]))

    def test_opposite_pattern_exits(self):
        c, h, l, cc = _quiet(40)
        o = list(c[:38]) + [101.0, 99.5]
        h = list(h[:38]) + [101.5, 102.5]
        l = list(l[:38]) + [99.0, 99.0]
        c = list(c[:38]) + [100.0, 102.0]
        df = _run(_frame(o, h, l, c))
        # exit columns are wired exactly to the opposite pattern flags
        self.assertTrue(bool((df["long_exit"] == (df["bear_engulf"] | df["bear_pin"])).all()))
        self.assertTrue(bool((df["short_exit"] == (df["bull_engulf"] | df["bull_pin"])).all()))

    def test_signal_columns_boolean(self):
        rng = np.random.default_rng(82)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 300))
        df = _run(_frame(c, c + 0.4, c - 0.4, c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)


if __name__ == "__main__":
    unittest.main()
