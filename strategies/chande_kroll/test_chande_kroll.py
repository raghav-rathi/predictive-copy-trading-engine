"""Chande & Kroll stop tests. Network-free.

Note on seeds: Chande-Kroll entries are pullback/reversal-catch signals —
in a steady synthetic trend they fire only when noise pulls price through a
stop line and back, so the (drift, vol, seed) combos below were picked to
exhibit the behavior deterministically. The direction purity (zero
opposite-direction entries) is structural: the SMA21 bias gate blocks the
wrong side in a steady trend.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chande_kroll import indicators, risk, signals


def _trend(n=1400, drift=0.0012, seed=3, vol=0.006, start=100.0):
    rng = np.random.default_rng(seed)
    c = start * np.exp(np.cumsum(rng.normal(drift, vol, n)))
    o = np.concatenate([[start], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


def _reversal(up=600, down=600, drift=0.004, vol=0.008, seed=5):
    c1 = _trend(up, drift, seed=seed, vol=vol)["c"].to_numpy()
    c2 = _trend(down, -drift, seed=seed + 100, vol=vol, start=float(c1[-1]))["c"].to_numpy()
    c = np.concatenate([c1, c2])
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(up + down) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(up + down, 100.0)})


class TestChandeKroll(unittest.TestCase):
    def test_uptrend_generates_long_entries(self):
        df = signals.add_signals(
            indicators.add_indicators(_trend(drift=0.004, vol=0.008, seed=17))
        )
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_downtrend_generates_short_entries(self):
        df = signals.add_signals(
            indicators.add_indicators(_trend(drift=-0.004, vol=0.006, seed=44))
        )
        self.assertGreater(int(df["short_entry"].sum()), 0)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_reversal_series_fires_entries_and_exits(self):
        df = signals.add_signals(indicators.add_indicators(_reversal()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertGreater(int(df["short_entry"].sum()), 0)
        self.assertGreater(int(df["long_exit"].sum()), 0)
        self.assertGreater(int(df["short_exit"].sum()), 0)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_trend()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_no_lookahead(self):
        raw = _trend(drift=0.004, vol=0.008, seed=17)
        df = signals.add_signals(indicators.add_indicators(raw))
        idx = df.index[df["long_entry"]]
        self.assertGreaterEqual(len(idx), 3)
        for i in idx[:3]:
            trunc = raw.iloc[: i + 1]
            res = signals.add_signals(indicators.add_indicators(trunc))
            self.assertTrue(res["long_entry"].iloc[-1])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 6.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.WARMUP, 80)
        self.assertGreater(risk.WARMUP, 10 + 9 + 21)  # covers p+q+sma21 lookbacks

    def test_stop_lines_shifted_one_bar(self):
        df = indicators.add_indicators(_trend())
        # p=10 then q=9 rolling windows -> first valid raw at bar 17,
        # shifted by 1 -> first valid stop-line value at bar 18
        self.assertTrue(df["long_stop"].iloc[:18].isna().all())
        self.assertTrue(df["short_stop"].iloc[:18].isna().all())
        self.assertFalse(df["long_stop"].iloc[18:30].isna().all())
        self.assertFalse(df["short_stop"].iloc[18:30].isna().all())


if __name__ == "__main__":
    unittest.main()
