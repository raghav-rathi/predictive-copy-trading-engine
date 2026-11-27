"""Tests for strategies/timeframes.py. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import timeframes

T0 = 1700006400000  # 2023-11-15 00:00 UTC (hour-aligned)


def _df(n=48, close=None):
    c = np.arange(100.0, 100.0 + n) if close is None else np.asarray(close, float)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 10.0)}
    )


class TestResample4h(unittest.TestCase):
    def test_blocks_are_utc_aligned_and_aggregate(self):
        df = _df(48)
        bars4 = timeframes.resample_4h(df)
        self.assertEqual(len(bars4), 12)
        # first block: 00:00-04:00 UTC, o = first open, c = 4th close, v = 40
        self.assertEqual(int(bars4.iloc[0]["t"]), T0)
        self.assertAlmostEqual(bars4.iloc[0]["o"], 100.0)
        self.assertAlmostEqual(bars4.iloc[0]["c"], 103.0)
        self.assertAlmostEqual(bars4.iloc[0]["v"], 40.0)
        self.assertAlmostEqual(bars4.iloc[0]["h"], 103.5)
        self.assertAlmostEqual(bars4.iloc[0]["l"], 99.5)

    def test_partial_last_block_kept(self):
        bars4 = timeframes.resample_4h(_df(10))
        self.assertEqual(len(bars4), 3)  # 4 + 4 + 2 bars
        self.assertAlmostEqual(bars4.iloc[2]["c"], 109.0)
        self.assertAlmostEqual(bars4.iloc[2]["v"], 20.0)


class TestMacd4hAligned(unittest.TestCase):
    def test_first_4h_block_is_nan_then_completed_bar_used(self):
        df = _df(200)
        out = timeframes.macd_4h_aligned(df)
        # bars 0-3 sit inside the first (uncompleted) 4h block -> NaN
        self.assertTrue(out["macd_hist_4h"].iloc[:4].isna().all())
        # MACD(12,26,9) needs 34 completed 4h bars (ewm counts non-NaN
        # observations, so the signal line is defined one bar earlier
        # than the naive 26+9): first defined value lands on the 1h bar
        # opening when the 34th 4h bar closes (bar 136)
        self.assertTrue(out["macd_hist_4h"].iloc[:136].isna().all())
        self.assertFalse(pd.isna(out["macd_hist_4h"].iloc[136]))
        # bars 136-139 all see the same completed 4h bar
        self.assertTrue((out["macd_hist_4h"].iloc[136:140] == out["macd_hist_4h"].iloc[136]).all())
        # bar 140 sees the next completed 4h bar (different value)
        self.assertNotEqual(out["macd_hist_4h"].iloc[140], out["macd_hist_4h"].iloc[136])

    def test_no_lookahead_later_bars_do_not_change_earlier_values(self):
        df = _df(200)
        early = timeframes.macd_4h_aligned(df.iloc[:100])["macd_hist_4h"].to_numpy()
        full = timeframes.macd_4h_aligned(df)["macd_hist_4h"].to_numpy()[:100]
        np.testing.assert_array_equal(
            np.nan_to_num(early, nan=-999.0), np.nan_to_num(full, nan=-999.0)
        )

    def test_columns_present(self):
        out = timeframes.macd_4h_aligned(_df(200))
        for col in ("macd_4h", "macd_signal_4h", "macd_hist_4h"):
            self.assertIn(col, out.columns)


if __name__ == "__main__":
    unittest.main()
