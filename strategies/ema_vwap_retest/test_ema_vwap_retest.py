"""EMA/VWAP retest tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ema_vwap_retest import indicators, risk, signals


def _frame(n=500, seed=37):
    rng = np.random.default_rng(seed)
    # rally through PDH, then pullback to 8 EMA: textbook retest setup
    c = np.empty(n)
    c[:250] = 100 + np.linspace(0, 8, 250) + rng.normal(0, 0.15, 250)
    c[250:300] = c[249] - np.linspace(0, 1.5, 50) + rng.normal(0, 0.1, 50)
    c[300:] = c[299] + np.linspace(0, 4, 200) + rng.normal(0, 0.15, 200)
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 200.0)})


class TestEmaVwapRetest(unittest.TestCase):
    def test_setup_generates_long_entries(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_entries_need_trend_stack(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        longs = df[df["long_entry"]]
        self.assertTrue(((longs["c"] > longs["ema8"]) & (longs["ema8"] > longs["ema20"])).all())
        self.assertTrue((longs["c"] > longs["vwap"]).all())

    def test_entries_need_breakout_memory(self):
        df = indicators.add_indicators(_frame())
        df = signals.add_signals(df)
        longs = df[df["long_entry"]]
        # a PDH break happened within the last 12 bars before each entry
        for i in longs.index[:5]:
            window = df.iloc[max(0, i - 12):i + 1]
            broke = ((window["c"] > window["pdh"]) &
                     (window["c"].shift(1) <= window["pdh"].shift(1))).any()
            self.assertTrue(broke)

    def test_exits_on_ema8_break(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        exits = df[df["long_exit"] & df["ema8"].notna()]
        self.assertTrue((exits["c"] < exits["ema8"]).all())

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.max_hold_bars, 48)


if __name__ == "__main__":
    unittest.main()
