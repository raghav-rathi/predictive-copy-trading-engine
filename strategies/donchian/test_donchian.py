"""Donchian breakout tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian import indicators, risk, signals


def _trend(n=400, drift=0.004, seed=3):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.006, n)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestDonchian(unittest.TestCase):
    def test_uptrend_generates_long_entries(self):
        df = signals.add_signals(indicators.add_indicators(_trend(drift=0.004)))
        self.assertGreater(int(df["long_entry"].sum()), 3)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_downtrend_generates_short_entries(self):
        df = signals.add_signals(indicators.add_indicators(_trend(drift=-0.004)))
        self.assertGreater(int(df["short_entry"].sum()), 3)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_no_lookahead(self):
        df = signals.add_signals(indicators.add_indicators(_trend()))
        idx = df.index[df["long_entry"]]
        for i in idx[:5]:
            prior_high = df["h"].iloc[max(0, i - 20):i].max()
            self.assertGreater(df["c"].iloc[i], prior_high)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_trend()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertGreater(risk.WARMUP, 20)


if __name__ == "__main__":
    unittest.main()
