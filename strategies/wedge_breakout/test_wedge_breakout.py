"""Wedge breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wedge_breakout import indicators, risk, signals
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


class TestWedgeBreakout(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_frame_from_close_path([100, 110, 105, 112, 109, 104]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_rising_wedge_short(self):
        # H1=110, L1=105, H2=112, L2=109: highs rise slower than lows
        # (converging upward). The dip to 111 after L2 confirms the
        # pivot, then the break below the lower line fires the short.
        df = _run(_frame_from_close_path([100, 110, 105, 112, 109, 111, 104]))
        self.assertTrue(df["short_entry"].any())
        i = int(np.argmax(df["short_entry"].to_numpy()))
        self.assertGreaterEqual(i, 45)  # second low confirms at bar 45
        self.assertFalse(df["long_entry"].any())

    def test_falling_wedge_long(self):
        # L1=120, H1=125, L2=118, H2=122: highs fall faster than lows
        # (converging downward). The dip to 120 after H2 confirms the
        # pivot, then the break above the upper line fires the long.
        df = _run(_frame_from_close_path([130, 120, 125, 118, 122, 120, 128]))
        self.assertTrue(df["long_entry"].any())
        i = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreaterEqual(i, 45)
        self.assertFalse(df["short_entry"].any())

    def test_parallel_lines_no_wedge(self):
        # tail_bars=0: the helper's reversal tail would itself form a
        # converging wedge after the parallel window; cut it off.
        df = _run(_frame_from_close_path([100, 110, 105, 115, 110, 120], tail_bars=0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        df = _run(_frame_from_close_path([100, 100, 100, 100, 100, 100]))
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
        self.assertIn("wedge_breakout", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 100)


if __name__ == "__main__":
    unittest.main()
