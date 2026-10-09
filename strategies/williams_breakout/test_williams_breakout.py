"""Williams breakout tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.williams_breakout import indicators, risk, signals


def _frame(n=400, seed=31):
    rng = np.random.default_rng(seed)
    # flat, then a volatility expansion with a breakout
    c = np.empty(n)
    c[:200] = 100 + rng.normal(0, 0.1, 200)
    c[200:] = 100 + np.cumsum(rng.normal(0.01, 0.8, 200))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n))
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestWilliams(unittest.TestCase):
    def test_breakout_generates_entries(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        total = int(df["long_entry"].sum() + df["short_entry"].sum())
        self.assertGreater(total, 0)

    def test_entries_need_expansion(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        entered = df[df["long_entry"] | df["short_entry"]]
        self.assertTrue(entered["range_expanded"].fillna(False).all())

    def test_long_breaks_prior_high(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        longs = df[df["long_entry"]]
        for i in longs.index[:5]:
            self.assertGreater(df["c"].iloc[i], df["hi_24"].iloc[i])

    def test_no_signal_exits(self):
        # exits come only from the risk layer for this strategy
        df = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertEqual(int(df["long_exit"].sum() + df["short_exit"].sum()), 0)

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.target_atr_mult, 2.0)
        self.assertEqual(risk.RISK.max_hold_bars, 48)


if __name__ == "__main__":
    unittest.main()
