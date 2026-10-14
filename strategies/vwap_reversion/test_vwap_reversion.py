"""VWAP reversion tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vwap_reversion import indicators, risk, signals


def _frame(n=300, seed=17):
    rng = np.random.default_rng(seed)
    # two days: first a dump below VWAP (long setup), then a rip (short setup)
    t0 = 1_700_000_000_000
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    c = np.empty(n)
    c[:150] = 100 - np.linspace(0, 3, 150) + rng.normal(0, 0.05, 150)
    c[150:] = 97 + np.linspace(0, 6, 150) + rng.normal(0, 0.05, 150)
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestVWAP(unittest.TestCase):
    def test_vwap_resets_daily(self):
        df = indicators.add_indicators(_frame())
        # VWAP at the first bar of day 2 should be near that bar's price
        day2 = df[df["t"] >= 1_700_000_000_000 + 24 * 3_600_000].iloc[0]
        self.assertLess(abs(day2["vwap"] - day2["c"]) / day2["c"], 0.02)

    def test_stretch_generates_entries(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        total = int(df["long_entry"].sum() + df["short_entry"].sum())
        self.assertGreater(total, 0)

    def test_entries_need_z_extreme(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        longs = df[df["long_entry"]]
        shorts = df[df["short_entry"]]
        if len(longs):
            self.assertTrue((longs["vwap_z"] < -1.5).all())
        if len(shorts):
            self.assertTrue((shorts["vwap_z"] > 1.5).all())

    def test_exits_at_vwap(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        # long exits only when back at/above VWAP
        exits = df[df["long_exit"] & df["vwap_z"].notna()]
        self.assertTrue((exits["vwap_z"] >= 0).all())

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertIsNone(risk.RISK.target_atr_mult)


if __name__ == "__main__":
    unittest.main()
