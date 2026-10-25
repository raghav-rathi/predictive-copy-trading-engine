"""Swing support / resistance bounce tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.swing_sr_bounce import indicators, risk, signals
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


class TestSwingSrBounce(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_frame_from_close_path([110, 100, 108, 100.4, 108, 100.2, 108]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_support_bounce_long(self):
        # two lows at 100 / 100.4 cluster into support ~100.2; the third
        # touch bounces. tail_bars=0: the helper's reversal tail would
        # itself print opposite-side bounces after the test window.
        df = _run(_frame_from_close_path([110, 100, 108, 100.4, 108, 100.2, 108], tail_bars=0))
        self.assertTrue(df["long_entry"].any())
        i = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreaterEqual(i, 50)
        self.assertFalse(df["short_entry"].any())

    def test_resistance_bounce_short(self):
        df = _run(_frame_from_close_path([90, 100, 92, 99.6, 92, 99.8, 92], tail_bars=0))
        self.assertTrue(df["short_entry"].any())
        i = int(np.argmax(df["short_entry"].to_numpy()))
        self.assertGreaterEqual(i, 50)
        self.assertFalse(df["long_entry"].any())

    def test_single_touch_no_level_no_entry(self):
        # one swing low never becomes a level (needs 2+ touches)
        df = _run(_frame_from_close_path([110, 100, 108, 102, 108]))
        self.assertFalse(df["long_entry"].any())

    def test_flat_data_no_entries(self):
        # tail_bars=0: the helper's reversal tail is not flat
        df = _run(_frame_from_close_path([100, 100, 100, 100, 100, 100, 100], tail_bars=0))
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
        self.assertIn("swing_sr_bounce", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 100)


if __name__ == "__main__":
    unittest.main()
