"""MA envelope breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.envelope_trend import indicators, risk, signals
from strategies import registry


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _run(c):
    df = _frame_from_close(c)
    df = indicators.add_indicators(df)
    return signals.add_signals(df)


class TestEnvelopeTrend(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(np.linspace(100, 130, 200))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_upper_envelope_breakout_fires(self):
        flat = np.full(40, 100.0)
        jump = np.linspace(100, 108, 10)
        hold = np.full(30, 108.0)
        df = _run(np.concatenate([flat, jump, hold]))
        self.assertTrue(df["long_entry"].any())
        i = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreater(df["c"].iloc[i], df["env_upper"].iloc[i])

    def test_lower_envelope_breakout_fires(self):
        flat = np.full(40, 100.0)
        drop = np.linspace(100, 92, 10)
        hold = np.full(30, 92.0)
        df = _run(np.concatenate([flat, drop, hold]))
        self.assertTrue(df["short_entry"].any())

    def test_small_move_inside_envelope_no_entry(self):
        flat = np.full(40, 100.0)
        drift = np.linspace(100, 103, 20)
        df = _run(np.concatenate([flat, drift]))
        self.assertFalse(df["long_entry"].any())

    def test_midline_exit_after_breakout(self):
        flat = np.full(40, 100.0)
        jump = np.linspace(100, 108, 10)
        hold = np.full(20, 108.0)
        fall = np.linspace(108, 100, 15)
        df = _run(np.concatenate([flat, jump, hold, fall]))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())

    def test_flat_data_no_entries(self):
        df = _run(np.full(120, 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        path = np.concatenate([np.full(40, 100.0), np.linspace(100, 108, 10), np.full(50, 108.0)])
        full = _run(path)
        trunc = _run(path[:80])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:80].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        self.assertIn("envelope_trend", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
