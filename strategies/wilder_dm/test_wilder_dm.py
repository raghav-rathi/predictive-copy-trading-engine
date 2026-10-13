"""Wilder DMI tests. Network-free."""

import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strategies import base as B
from strategies.wilder_dm import indicators, risk, signals


def _frame(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 10.0)}
    )


def _rally(n=120, seed=5):
    """Chop then a steady rally: ADX > 25 and rising through the mid-rally."""
    rng = np.random.default_rng(seed)
    c = np.zeros(n)
    c[:40] = 100 + rng.normal(0, 0.8, 40).cumsum() * 0.4
    c[40:] = c[39] + np.arange(1, n - 39) * 1.0
    o = np.empty(n)
    o[0] = c[0]
    o[1:] = c[:-1]
    return _frame(o, np.maximum(o, c) + 0.4, np.minimum(o, c) - 0.4, c)


class TestWilderDm(unittest.TestCase):
    def test_sar_hand_computed_uptrend(self):
        c = np.array([100.0, 101, 102, 103, 104])
        h = c + 1.0
        l = c - 1.0
        sar, trend = indicators.parabolic_sar(h, l, c)
        # hand-derived with the classic "prior two lows" clamp:
        # i=1: 99+0.02*3=99.06 -> min(l0=99) = 99.0
        # i=2: 99+0.02*3=99.06 -> min(l1,l0)=99 -> 99.0; h2=103>102: ep=103 af=0.04
        # i=3: 99+0.04*4=99.16 -> min(l2,l1)=100 -> 99.16; ep=104 af=0.06
        # i=4: 99.16+0.06*4.84=99.4504 -> min(l3,l2)=101 -> 99.4504
        expected = [99.0, 99.0, 99.0, 99.16, 99.4504]
        for got, want in zip(sar, expected):
            self.assertAlmostEqual(got, want, places=4)
        self.assertTrue((trend == 1).all())

    def test_sar_flip_on_crash(self):
        c = np.array([100.0, 101, 102, 103, 104, 96.0])
        h = np.array([101.0, 102, 103, 104, 105, 104.5])
        l = np.array([99.0, 100, 101, 102, 103, 95.0])
        sar, trend = indicators.parabolic_sar(h, l, c)
        self.assertEqual(trend[5], -1)
        self.assertAlmostEqual(sar[5], 105.0, places=6)  # prior extreme point

    def test_sar_never_violates_prior_lows_in_uptrend(self):
        df = indicators.add_indicators(_rally())
        up = df["sar_trend"] == 1
        # SAR must stay at/below the lower of the prior two lows
        ok = df.loc[up, "sar"] <= df["l"].rolling(2).min().loc[up] + 1e-9
        self.assertTrue(ok.all())

    def test_di_cross_with_gate_fires_entry(self):
        df = indicators.add_indicators(_rally())
        # bar 50: ADX > 25 and rising in this series; force a +DI cross there
        self.assertGreater(df["adx"].iloc[50], 25.0)
        self.assertGreater(df["adx"].iloc[50], df["adx_prev"].iloc[50])
        df.loc[df.index[49], "plus_di"] = 10.0
        df.loc[df.index[49], "minus_di"] = 20.0
        df.loc[df.index[50], "plus_di"] = 25.0
        df.loc[df.index[50], "minus_di"] = 15.0
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[50])

    def test_di_cross_without_gate_does_not_fire(self):
        # directionless sine: ADX stays < 25 everywhere it is valid
        j = np.arange(200)
        c = 100 + 0.3 * np.sin(j / 1.0)
        o = np.empty(200)
        o[0] = c[0]
        o[1:] = c[:-1]
        df = indicators.add_indicators(
            _frame(o, np.maximum(o, c) + 0.1, np.minimum(o, c) - 0.1, c)
        )
        self.assertLess(float(df["adx"].max()), 25.0)
        # force a +DI cross at bar 60 (valid, sub-gate ADX)
        self.assertFalse(pd.isna(df["adx"].iloc[60]))
        df.loc[df.index[59], "plus_di"] = 10.0
        df.loc[df.index[59], "minus_di"] = 20.0
        df.loc[df.index[60], "plus_di"] = 25.0
        df.loc[df.index[60], "minus_di"] = 15.0
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].iloc[60])

    def test_range_rule_and_adx_dead_are_exits(self):
        df = signals.add_signals(indicators.add_indicators(_rally()))
        rr = (df["adx"] < df["plus_di"]) & (df["adx"] < df["minus_di"])
        dead = df["adx"] < 20.0
        self.assertTrue(df.loc[rr, "long_exit"].all())
        self.assertTrue(df.loc[dead, "long_exit"].all())
        self.assertTrue(df.loc[rr, "short_exit"].all())

    def test_sar_flip_is_exit(self):
        df = indicators.add_indicators(_rally())
        crashed = df.copy()
        crashed.loc[crashed.index[100]:, ["o", "h", "l", "c"]] = 50.0
        out = signals.add_signals(indicators.add_indicators(crashed))
        flips = np.where(
            (out["sar_trend"] == -1).to_numpy()
            & (out["sar_trend"].shift(1) == 1).to_numpy()
        )[0]
        self.assertGreater(len(flips), 0)
        self.assertTrue(out["long_exit"].iloc[flips[0]])

    def test_no_lookahead(self):
        df = _rally()
        full = signals.add_signals(indicators.add_indicators(df))
        cut = signals.add_signals(indicators.add_indicators(df.iloc[:80]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "sar", "sar_trend"):
            a = full[col].iloc[:80].to_numpy()
            b = cut[col].to_numpy()
            if np.issubdtype(a.dtype, np.floating):
                self.assertTrue(np.allclose(a, b, equal_nan=True), col)
            else:
                self.assertTrue((a == b).all(), col)

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_rally()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_sanity(self):
        r = risk.RISK
        self.assertGreater(r.stop_atr_mult, 0)
        self.assertEqual(r.max_hold_bars, 120)
        self.assertTrue(0 < r.risk_frac < 1)
        self.assertGreaterEqual(r.max_leverage, 1.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertGreaterEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
