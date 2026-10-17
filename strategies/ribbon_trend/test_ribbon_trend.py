"""Ribbon-trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ribbon_trend import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.2):
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
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestRibbonTrend(unittest.TestCase):
    def test_stacked_in_sustained_trend(self):
        c = 100 + 1.2 * np.arange(300)
        df = indicators.add_indicators(_frame(c, spread=0.01))
        tail = df.iloc[-30:]
        self.assertTrue(bool(tail["ribbon_bull"].all()))
        self.assertGreater(float(tail["ribbon_fan"].iloc[-1]), 0.004)

    def test_flat_market_blocks_entries_via_fan(self):
        # the 0.4% fan gate is the chop filter: micro-aligned EMAs in flat
        # chop carry no fan spread, so entries must stay rare
        rng = np.random.default_rng(121)
        df = _run(_frame(100 + rng.normal(0, 0.1, 400), spread=0.05))
        entries = int(df["long_entry"].sum() + df["short_entry"].sum())
        self.assertLess(entries / len(df), 0.05)

    def test_flip_triggers_entry(self):
        # downtrend then strong uptrend: bear -> bull flip with fan
        dn = 200 - 1.0 * np.arange(120)
        up = 80 + 1.2 * np.arange(180)
        df = _run(_frame(np.concatenate([dn, up]), spread=0.05))
        self.assertTrue(bool(df["long_entry"].any()))

    def test_exhaustion_exits(self):
        # alignment lost must set long_exit
        dn = 200 - 1.0 * np.arange(120)
        up = 80 + 1.2 * np.arange(180)
        flat = up[-1] + np.zeros(120)
        df = _run(_frame(np.concatenate([dn, up, flat]), spread=0.05))
        longs = df["long_entry"]
        if bool(longs.any()):
            first = int(np.where(longs)[0][0])
            self.assertTrue(bool(df["long_exit"].iloc[first + 1 :].any()))

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(122)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 300))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        trunc = _run(_frame(c[:200]))
        np.testing.assert_allclose(
            df["ribbon_fan"].iloc[199], trunc["ribbon_fan"].iloc[199], rtol=1e-12
        )


if __name__ == "__main__":
    unittest.main()
