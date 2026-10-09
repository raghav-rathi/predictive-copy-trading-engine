"""Keltner+ADX tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.keltner_adx import indicators, risk, signals


def _frame(n=600, seed=23):
    rng = np.random.default_rng(seed)
    # strong trends so ADX is high and channel breaks happen
    drift = np.concatenate([np.full(300, 0.005), np.full(300, -0.005)])
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.006)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestKeltnerADX(unittest.TestCase):
    def test_breakouts_generate_entries(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        total = int(df["long_entry"].sum() + df["short_entry"].sum())
        self.assertGreater(total, 0)

    def test_entries_need_adx_regime(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        entered = df[df["long_entry"] | df["short_entry"]]
        self.assertTrue((entered["adx"] > 25.0).all())

    def test_longs_break_upper(self):
        df = indicators.add_indicators(_frame())
        df = signals.add_signals(df)
        longs = df[df["long_entry"]]
        # entry bar close broke above the band (cross semantics)
        for i in longs.index[:5]:
            self.assertGreater(df["c"].iloc[i], df["kc_upper"].iloc[i])

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)


if __name__ == "__main__":
    unittest.main()
