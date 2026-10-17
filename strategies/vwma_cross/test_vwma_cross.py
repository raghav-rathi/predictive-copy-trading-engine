"""VWMA-cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vwma_cross import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, v=None, spread=0.2):
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
            "v": np.full(n, 100.0) if v is None else np.asarray(v, dtype=float),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestVwmaCross(unittest.TestCase):
    def test_vwma_matches_manual(self):
        rng = np.random.default_rng(111)
        n = 200
        c = 100 + np.cumsum(rng.normal(0, 0.6, n))
        v = rng.uniform(50, 150, n)
        df = indicators.add_indicators(_frame(c, v))
        tp = (df["h"] + df["l"] + df["c"]) / 3
        exp = (tp * df["v"]).rolling(20, min_periods=20).sum() / df["v"].rolling(20, min_periods=20).sum()
        np.testing.assert_allclose(df["vwma_fast"].to_numpy()[25:], exp.to_numpy()[25:], rtol=1e-9)

    def test_heavy_volume_pulls_fast_line(self):
        # one huge-volume up bar must lift the fast VWMA above a flat slow one
        c = np.full(120, 100.0)
        v = np.full(120, 100.0)
        c = np.append(c, [110.0] * 3)
        v = np.append(v, [10000.0] * 3)
        df = indicators.add_indicators(_frame(c, v, spread=0.1))
        self.assertGreater(float(df["vwma_fast"].iloc[-1]), float(df["vwma_slow"].iloc[-1]))

    def test_cross_up_triggers_long(self):
        rng = np.random.default_rng(112)
        c = np.concatenate([100 + rng.normal(0, 0.4, 100).cumsum(),
                            105 + 0.5 * np.arange(120)])
        # volume surges with the rally: conviction at the cross
        v = np.concatenate([np.full(100, 100.0), np.full(120, 200.0)])
        df = _run(_frame(c, v))
        self.assertTrue(bool(df["long_entry"].any()))

    def test_low_volume_blocks_entry(self):
        # cross occurs but volume is flat below its average -> no entry
        rng = np.random.default_rng(113)
        c = np.concatenate([100 + rng.normal(0, 0.4, 100).cumsum(),
                            105 + 0.5 * np.arange(120)])
        v = np.full(220, 100.0)
        v[100:220] = 50.0  # volume drops as price rises: filter blocks
        df = indicators.add_indicators(_frame(c, v))
        df = signals.add_signals(df)
        cross = ((df["vwma_fast"] > df["vwma_slow"]) &
                 (df["vwma_fast"].shift(1) <= df["vwma_slow"].shift(1))).fillna(False)
        if bool(cross.any()):
            self.assertFalse(bool((df["long_entry"] & ~df["vol_ok"]).any()))

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(114)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 300))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        trunc = _run(_frame(c[:200]))
        np.testing.assert_allclose(
            df["vwma_fast"].iloc[199], trunc["vwma_fast"].iloc[199], rtol=1e-12
        )


if __name__ == "__main__":
    unittest.main()
