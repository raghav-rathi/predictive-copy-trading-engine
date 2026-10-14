"""Ichimoku tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ichimoku import indicators, risk, signals


def _frame(n=900, seed=13):
    rng = np.random.default_rng(seed)
    # oscillating drift -> repeated Tenkan/Kijun crosses above/below cloud
    t = np.arange(n)
    drift = 0.006 * np.sin(2 * np.pi * t / 150)
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.006)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestIchimoku(unittest.TestCase):
    def _crafted(self):
        # rows: 0 warmup(NaN) | 1 long setup | 2 nothing | 3 short setup
        n = 4
        df = pd.DataFrame({
            "tenkan":   [np.nan, 102.0, 101.0, 98.0],
            "kijun":    [np.nan, 101.0, 101.5, 99.0],
            "tenkan_p": [np.nan, 100.5, 102.0, 99.5],   # previous-bar tenkan
            "kijun_p":  [np.nan, 101.0, 101.0, 98.5],   # previous-bar kijun
            "senkou_a": [np.nan, 100.0, 100.0, 101.0],
            "senkou_b": [np.nan, 99.5, 100.5, 100.5],
            "c":        [100.0, 103.0, 100.0, 97.0],
            "h":        [101.0, 103.5, 100.5, 97.5],
            "l":        [99.0, 102.5, 99.5, 96.5],
            "h26":      [99.0, 99.0, 99.0, 99.0],       # h.shift(26)
            "l26":      [98.0, 98.0, 98.0, 102.0],       # l.shift(26)
        })
        return df

    def _signals_on_crafted(self, df):
        # replicate add_signals logic against crafted columns
        out = df.copy()
        valid = out["senkou_a"].notna() & out["tenkan"].notna() & out["h26"].notna()
        above = out["c"] > out[["senkou_a", "senkou_b"]].max(axis=1)
        below = out["c"] < out[["senkou_a", "senkou_b"]].min(axis=1)
        tk_up = (out["tenkan"] > out["kijun"]) & (out["tenkan_p"] <= out["kijun_p"])
        tk_dn = (out["tenkan"] < out["kijun"]) & (out["tenkan_p"] >= out["kijun_p"])
        out["long_entry"] = above & tk_up & (out["c"] > out["h26"]) & valid
        out["short_entry"] = below & tk_dn & (out["c"] < out["l26"]) & valid
        return out

    def test_entries_fire(self):
        df = self._signals_on_crafted(self._crafted())
        self.assertTrue(df.loc[1, "long_entry"])
        self.assertTrue(df.loc[3, "short_entry"])
        self.assertFalse(df.loc[0, "long_entry"] or df.loc[0, "short_entry"])
        self.assertFalse(df.loc[2, "long_entry"] or df.loc[2, "short_entry"])

    def test_longs_above_cloud(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        longs = df[df["long_entry"]]
        self.assertTrue((longs["c"] > longs["cloud_top"]).all())

    def test_shorts_below_cloud(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        shorts = df[df["short_entry"]]
        self.assertTrue((shorts["c"] < shorts["cloud_bot"]).all())

    def test_no_entries_during_warmup(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        early = df.iloc[:80]
        self.assertEqual(int(early["long_entry"].sum() + early["short_entry"].sum()), 0)

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertTrue(risk.RISK.allow_shorts)


if __name__ == "__main__":
    unittest.main()
