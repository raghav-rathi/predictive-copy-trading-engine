"""EMA crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ema_cross import indicators, risk, signals
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


class TestEmaCross(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(np.linspace(100, 130, 200))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_cross_up_fires_on_reversal(self):
        down = np.linspace(100, 80, 40)
        up = np.linspace(80, 115, 40)
        df = _run(np.concatenate([down, up]))
        self.assertTrue(df["long_entry"].any())
        i = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreater(df["ema_fast"].iloc[i], df["ema_slow"].iloc[i])

    def test_cross_down_fires_on_reversal(self):
        up = np.linspace(80, 115, 40)
        down = np.linspace(115, 80, 40)
        df = _run(np.concatenate([up, down]))
        self.assertTrue(df["short_entry"].any())

    def test_no_short_on_monotonic_rise(self):
        df = _run(np.linspace(100, 150, 120))
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        df = _run(np.full(120, 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exit_is_opposite_cross(self):
        down = np.linspace(100, 80, 40)
        up = np.linspace(80, 115, 40)
        down2 = np.linspace(115, 85, 40)
        df = _run(np.concatenate([down, up, down2]))
        self.assertTrue(df["long_exit"].any())

    def test_no_lookahead_truncation(self):
        full = _run(np.concatenate([np.linspace(100, 80, 60), np.linspace(80, 120, 60)]))
        trunc = _run(np.concatenate([np.linspace(100, 80, 60), np.linspace(80, 120, 60)])[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        self.assertIn("ema_cross", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["ema_cross"].slug, "ema_cross")
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
