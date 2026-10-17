"""Liquidity-sweep tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.liquidity_sweep import indicators, risk, signals

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


class TestLiquiditySweep(unittest.TestCase):
    def _flat(self, n, px=100.0, jitter=0.05):
        rng = np.random.default_rng(61)
        c = px + rng.normal(0, jitter, n).cumsum() * 0.1
        return _frame(c, c + 0.1, c - 0.1, c)

    def test_constructed_sweep_up_detected(self):
        df = self._flat(60)
        # force a sweep bar: spike the high 3 ATR above the pool high,
        # close back inside
        df.loc[59, "h"] = df["h"].max() + 1.5
        df.loc[59, "c"] = df.loc[59, "o"]
        out = _run(df)
        self.assertTrue(bool(out["sweep_up"].iloc[59]))
        self.assertTrue(bool(out["short_entry"].iloc[59]))

    def test_constructed_sweep_dn_detected(self):
        df = self._flat(60)
        df.loc[59, "l"] = df["l"].min() - 1.5
        df.loc[59, "c"] = df.loc[59, "o"]
        out = _run(df)
        self.assertTrue(bool(out["sweep_dn"].iloc[59]))
        self.assertTrue(bool(out["long_entry"].iloc[59]))

    def test_close_beyond_level_is_not_a_sweep(self):
        # genuine breakout: close holds above the pool high -> no sweep
        df = self._flat(60)
        df.loc[59, "h"] = df["h"].max() + 1.5
        df.loc[59, "c"] = df.loc[59, "h"]  # closes beyond the level
        out = _run(df)
        self.assertFalse(bool(out["sweep_up"].iloc[59]))
        self.assertFalse(bool(out["short_entry"].iloc[59]))

    def test_tiny_poke_is_not_a_sweep(self):
        # 0.01 poke beyond the level: fails the MIN_WICK_ATR gate
        df = self._flat(60)
        df.loc[59, "h"] = df["h"].max() + 0.001
        df.loc[59, "c"] = df.loc[59, "o"]
        out = _run(df)
        self.assertFalse(bool(out["sweep_up"].iloc[59]))

    def test_breakout_close_exits_faded_position(self):
        df = self._flat(80)
        df.loc[79, "c"] = df["c"].max() + 2.0  # closing break of pool high
        out = _run(df)
        self.assertTrue(bool(out["long_exit"].iloc[79]))

    def test_signal_columns_boolean(self):
        rng = np.random.default_rng(62)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 300))
        df = _run(_frame(c, c + 0.4, c - 0.4, c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)


if __name__ == "__main__":
    unittest.main()
