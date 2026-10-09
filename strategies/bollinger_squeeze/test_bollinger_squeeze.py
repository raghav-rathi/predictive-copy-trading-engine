"""Bollinger squeeze tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_squeeze import indicators, risk, signals


def _frame(n=800, seed=5):
    rng = np.random.default_rng(seed)
    i = np.arange(n)
    # squeeze zone: fast oscillation around a flat level -> BB inside Keltner
    # then a +4% gap (volatility jump) -> squeeze releases
    base = np.where(
        i < 400,
        100 + 0.3 * np.sin(2 * np.pi * i / 4) + rng.normal(0, 0.02, n),
        100.0,
    )
    c = base.copy()
    c[400:] = 104.0 + rng.normal(0, 0.05, n - 400).cumsum() * 0.1
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestSqueeze(unittest.TestCase):
    def test_squeeze_detected_in_quiet_regime(self):
        df = indicators.add_indicators(_frame())
        squeeze_zone = df.iloc[100:350]
        self.assertGreater(squeeze_zone["squeeze"].mean(), 0.3)

    def _crafted(self):
        # hand-built indicator frame: row1 = long release, row3 = short release
        return pd.DataFrame({
            "squeeze":      [True, False, True, False, False],
            "squeeze_prev": [True, True, True, True, False],
            "c":            [100.0, 101.0, 101.0, 99.0, 99.5],
            "kc_mid":       [100.0, 100.0, 100.5, 100.0, 100.0],
            "mom":          [0.0, 1.0, 0.0, -1.0, 0.0],
        })

    def test_release_generates_entries(self):
        df = indicators.add_indicators(_frame())
        rel = (df["squeeze_prev"].fillna(False) & ~df["squeeze"].fillna(True)).sum()
        self.assertGreater(int(rel), 0, "no squeeze release in synthetic frame")

    def test_long_release_logic(self):
        df = signals.add_signals(self._crafted())
        self.assertTrue(df.loc[1, "long_entry"])
        self.assertFalse(df.loc[1, "short_entry"])

    def test_short_release_logic(self):
        df = signals.add_signals(self._crafted())
        self.assertTrue(df.loc[3, "short_entry"])
        self.assertFalse(df.loc[3, "long_entry"])

    def test_no_release_no_entry(self):
        df = signals.add_signals(self._crafted())
        self.assertFalse(df.loc[0, "long_entry"] or df.loc[0, "short_entry"])
        self.assertFalse(df.loc[4, "long_entry"] or df.loc[4, "short_entry"])

    def test_entries_only_on_release(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        entered = df[df["long_entry"] | df["short_entry"]]
        self.assertTrue(entered["squeeze_prev"].fillna(False).all())

    def test_momentum_agrees_with_side(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        longs = df[df["long_entry"]]
        shorts = df[df["short_entry"]]
        if len(longs):
            self.assertTrue((longs["mom"] > 0).all())
        if len(shorts):
            self.assertTrue((shorts["mom"] < 0).all())

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertEqual(risk.RISK.max_hold_bars, 72)


if __name__ == "__main__":
    unittest.main()
