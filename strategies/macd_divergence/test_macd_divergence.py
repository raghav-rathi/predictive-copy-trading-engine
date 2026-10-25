"""MACD histogram divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_divergence import indicators, risk, signals
from strategies import registry


def _frame_from_close_path(pivots, leg_bars=10, tail_bars=10):
    closes = []
    for a, b in zip(pivots[:-1], pivots[1:]):
        seg = np.linspace(a, b, leg_bars + 1)
        closes.extend(seg[:-1].tolist())
    closes.append(pivots[-1])
    tail_end = pivots[-1] + (2.0 if pivots[-1] < pivots[-2] else -2.0)
    closes.extend(np.linspace(pivots[-1], tail_end, tail_bars + 1)[1:].tolist())
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _frame_from_segments(segments, start, prefix_bars=0):
    """segments = [(end, bars), ...]; joints are shared, no jumps.

    Each segment contributes `bars` bars ending just before `end`;
    the next segment starts exactly at `end`. `prefix_bars` flat bars
    at `start` are prepended first, so early pivots sit past the
    MACD warmup (EMA26 needs 26 bars before the histogram is finite).
    """
    closes = [float(start)] * prefix_bars
    cur = start
    for end, bars in segments:
        seg = np.linspace(cur, end, bars + 1)
        closes.extend(seg[:-1].tolist())
        cur = end
    closes.append(cur)
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _run(df):
    df = indicators.add_indicators(df)
    return signals.add_signals(df)


def _random_walk_frame(n=300, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    n2 = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n2))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n2))
    t = (1_700_000_000_000 + np.arange(n2) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n2)})


class TestMacdDivergence(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_frame_from_close_path([100, 90, 97, 89, 99]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_bullish_divergence_long(self):
        # steep 6-bar drop (histogram very negative at the first low),
        # rebound, then a long shallow 20-bar drop to a lower low: the
        # histogram has settled near zero by the second low, so it
        # prints a HIGHER low while price prints a LOWER low.
        df = _run(_frame_from_segments([(85, 6), (95, 10), (83, 20), (95, 10)], start=100, prefix_bars=30))
        self.assertTrue((df["macd_div_dir"] == 1).any())
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_bearish_divergence_short(self):
        df = _run(_frame_from_segments([(115, 6), (105, 10), (117, 20), (105, 10)], start=100, prefix_bars=30))
        self.assertTrue((df["macd_div_dir"] == -1).any())
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_no_divergence_on_equal_legs(self):
        # two identical declines to the same low: the second low is not
        # lower, so no divergence (now with finite histogram values,
        # unlike the early-pivot NaN case)
        df = _run(_frame_from_segments([(90, 10), (100, 10), (90, 10), (100, 10)], start=100, prefix_bars=30))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        df = _run(_frame_from_close_path([100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        self.assertIn("macd_divergence", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
