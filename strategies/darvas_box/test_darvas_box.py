"""Darvas Box tests. Network-free, synthetic only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.darvas_box import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _darvas_frame(breakout_vol=100.0):
    """Hand-built box: flat 100s, a 110 spike at bar 60, 3 failing bars,
    breakout bar 64 (close 111 > top 110), soft close 98 at bar 65."""
    n = 90
    o = np.full(n, 99.5)
    h = np.full(n, 100.0)
    l = np.full(n, 99.0)
    c = np.full(n, 99.5)
    v = np.full(n, 100.0)
    # bar 60: the box high
    o[60], h[60], l[60], c[60] = 105.0, 110.0, 104.0, 108.0
    # bars 61-63: fail to make a new high (box confirms at 63)
    l[61], l[62], l[63] = 103.0, 102.0, 99.0
    # bar 64: breakout attempt (high exceeds the top by construction)
    o[64], h[64], l[64], c[64], v[64] = 99.5, 112.0, 99.0, 111.0, breakout_vol
    # bar 65: closes below the box floor -> exit
    o[65], h[65], l[65], c[65] = 98.0, 100.0, 97.5, 98.0
    return _ohlcv(o, h, l, c, v)


def _downtrend(n=400, seed=3):
    rng = np.random.default_rng(seed)
    c = 100 - 0.15 * np.arange(n) + rng.normal(0, 0.15, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.2
    return _ohlcv(o, h, l, c)


class TestDarvasBox(unittest.TestCase):
    def test_top_confirmed_only_after_three_non_exceeding(self):
        ind = indicators.add_indicators(_darvas_frame())
        # bar 63: window [0,60] max = 110, highs 61-63 all < 110
        self.assertAlmostEqual(ind["box_top"].iloc[63], 110.0)
        self.assertTrue(ind["box_confirmed"].iloc[63])
        # bar 62: window not yet full -> no top, not confirmed
        self.assertTrue(pd.isna(ind["box_top"].iloc[62]))
        self.assertFalse(ind["box_confirmed"].iloc[62])
        # bar 64 (the breakout bar): its own high 112 exceeds the top 110,
        # so the on-bar confirmation is False -- entry uses the PRIOR bar
        self.assertFalse(ind["box_confirmed"].iloc[64])

    def test_bottom_min_low_since_top_bar(self):
        ind = indicators.add_indicators(_darvas_frame())
        self.assertEqual(ind["box_top_bar"].iloc[63], 60)
        # min low over [60, 62] = min(104, 103, 102)
        self.assertAlmostEqual(ind["box_bottom"].iloc[63], 102.0)

    def test_entry_rejects_low_volume_breakout(self):
        df = signals.add_signals(indicators.add_indicators(_darvas_frame(breakout_vol=100.0)))
        # price mechanics are right but v=100 < 1.25 * vol_sma20 -> no entry
        self.assertFalse(df["vol_ok"].iloc[64])
        self.assertFalse(df["long_entry"].iloc[64])
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_entry_fires_on_volume_confirmed_breakout(self):
        df = signals.add_signals(indicators.add_indicators(_darvas_frame(breakout_vol=200.0)))
        self.assertTrue(df["vol_ok"].iloc[64])
        self.assertTrue(df["long_entry"].iloc[64])
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_exit_fires_below_floor(self):
        df = signals.add_signals(indicators.add_indicators(_darvas_frame()))
        # box floor at 65 = min low over [60, 64] = 99; close 98 < 99
        self.assertTrue(df["long_exit"].iloc[65])
        self.assertFalse(df["long_exit"].iloc[64])

    def test_no_shorts_ever(self):
        for frame in (_darvas_frame(200.0), _downtrend()):
            df = signals.add_signals(indicators.add_indicators(frame))
            self.assertFalse(df["short_entry"].any())
            self.assertFalse(df["short_exit"].any())

    def test_no_lookahead_truncation(self):
        full = _darvas_frame(200.0)
        ind_full = indicators.add_indicators(full)
        for i in (80, 85):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("box_top", "box_bottom", "box_confirmed", "vol_sma20", "vol_ok"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or a == b, (col, i, a, b)
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_darvas_frame(200.0)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertAlmostEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 100)


if __name__ == "__main__":
    unittest.main()
