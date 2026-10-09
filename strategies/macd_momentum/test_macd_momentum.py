"""MACD momentum tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_momentum import indicators, risk, signals


def _frame(n=700, seed=9):
    rng = np.random.default_rng(seed)
    # momentum waves: drift oscillates so histogram crosses zero repeatedly
    t = np.arange(n)
    drift = 0.004 * np.sin(2 * np.pi * t / 120)
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.006)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    ts = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": ts, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestMACD(unittest.TestCase):
    def test_crosses_generate_entries(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        total = int(df["long_entry"].sum() + df["short_entry"].sum())
        self.assertGreater(total, 2)

    def test_longs_only_above_ema200(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        longs = df[df["long_entry"]]
        if len(longs):
            self.assertTrue((longs["c"] > longs["ema200"]).all())

    def test_shorts_only_below_ema200(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        shorts = df[df["short_entry"]]
        if len(shorts):
            self.assertTrue((shorts["c"] <= shorts["ema200"]).all())

    def test_exits_follow_opposite_cross(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        # long exits happen exactly on histogram cross-down bars
        exits = df.index[df["long_exit"]]
        for i in exits[:10]:
            self.assertLess(df["macd_hist"].iloc[i], 0)
            self.assertGreaterEqual(df["macd_hist_prev"].iloc[i], 0)

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)


if __name__ == "__main__":
    unittest.main()
