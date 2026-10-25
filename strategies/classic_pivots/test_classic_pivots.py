"""Classic pivot breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.classic_pivots import indicators, risk, signals
from strategies import registry


def _frame(rows):
    """rows = list of (o, h, l, c)."""
    n = len(rows)
    arr = np.asarray(rows, dtype=float)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": arr[:, 0], "h": arr[:, 1], "l": arr[:, 2],
                         "c": arr[:, 3], "v": np.full(n, 100.0)})


def _run(rows):
    df = _frame(rows)
    df = indicators.add_indicators(df)
    return signals.add_signals(df)


def _flat_row(px):
    return (px, px + 0.1, px - 0.1, px)


class TestClassicPivots(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run([_flat_row(100.0)] * 60)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_pivot_math(self):
        # bar0: H=110, L=90, C=100 -> bar1 levels PP=100, R1=110, S1=90
        df = _run([(100, 110, 90, 100), (100, 101, 99, 100), (100, 101, 99, 100)])
        self.assertAlmostEqual(df["piv_pp"].iloc[1], 100.0)
        self.assertAlmostEqual(df["piv_r1"].iloc[1], 110.0)
        self.assertAlmostEqual(df["piv_s1"].iloc[1], 90.0)

    def test_r1_breakout_fires(self):
        rows = [
            (100, 110, 90, 100),   # sets bar1 levels: PP=100, R1=110
            (100, 106, 104, 105),  # close 105 < R1 110
            (105, 113, 111, 112),  # bar2 levels from bar1: R1=106; close 112 > 106
        ]
        df = _run(rows)
        self.assertTrue(df["long_entry"].iloc[2])

    def test_s1_breakdown_fires(self):
        rows = [
            (100, 110, 90, 100),   # sets bar1 levels: S1=90
            (100, 96, 94, 95),     # close 95 > S1 90
            (95, 93, 91, 88),      # bar2 levels from bar1: S1=94; close 88 < 94
        ]
        df = _run(rows)
        self.assertTrue(df["short_entry"].iloc[2])

    def test_pp_exit_after_breakout(self):
        rows = [
            (100, 110, 90, 100),
            (100, 106, 104, 105),
            (105, 113, 111, 112),  # long_entry here
            (112, 112, 108, 104),  # bar3 levels from bar2: PP=112; close 104 < 112
        ]
        df = _run(rows)
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[3])

    def test_flat_data_no_entries(self):
        df = _run([_flat_row(100.0)] * 60)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_registration(self):
        self.assertIn("classic_pivots", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 20)


if __name__ == "__main__":
    unittest.main()
