"""RSI(2) mean-reversion tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi2 import indicators, risk, signals


def _frame(n=600, seed=21):
    rng = np.random.default_rng(seed)
    # uptrend with sharp pullbacks: ideal RSI(2) long setup
    drift = np.full(n, 0.002)
    drift[100:110] = -0.03
    drift[300:310] = -0.03
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.004)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestRSI2(unittest.TestCase):
    def test_pullback_generates_long_entries(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        n = int(df["long_entry"].sum())
        self.assertGreater(n, 0, "no long entries on pullback series")
        # entries only in uptrend
        entered = df[df["long_entry"]]
        self.assertTrue((entered["c"] > entered["sma200"]).all())

    def test_entries_need_rsi_extreme(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        entered = df[df["long_entry"]]
        self.assertTrue((entered["rsi2"] < 10.0).all())

    def test_exit_after_snapback(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        # after a long entry, an exit should fire within a few bars
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        i = idx[0]
        window = df.iloc[i + 1:i + 25]
        self.assertTrue(bool(window["long_exit"].any()))

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.target_atr_mult, 2.0)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertGreaterEqual(risk.WARMUP, 200)


if __name__ == "__main__":
    unittest.main()
