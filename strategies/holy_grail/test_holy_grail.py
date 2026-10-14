"""Holy Grail tests. Network-free."""

import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strategies.holy_grail import indicators, risk, signals


def _frame(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 10.0)}
    )


def _trend_with_pullback(seed=3, n=110):
    """Chop, then a steady climb (ADX rises through 30), a pullback, resume.
    Deterministic via seed; produces at least one Holy Grail long."""
    rng = np.random.default_rng(seed)
    c = np.zeros(n)
    c[:40] = 100 + rng.normal(0, 1.0, 40).cumsum() * 0.3
    c[40:60] = c[39] + np.arange(1, 21) * 0.35
    c[60] = c[59] - 2.0
    c[61:] = c[60] + np.arange(1, n - 60) * 0.6
    o = np.empty(n)
    o[0] = c[0]
    o[1:] = c[:-1]
    return _frame(o, np.maximum(o, c) + 0.3, np.minimum(o, c) - 0.3, c)


def _sine_flat(n=200):
    """Directionless oscillation: ADX stays low, no Holy Grail setup possible."""
    j = np.arange(n)
    c = 100 + 0.3 * np.sin(j / 1.0)
    o = np.empty(n)
    o[0] = c[0]
    o[1:] = c[:-1]
    return _frame(o, np.maximum(o, c) + 0.1, np.minimum(o, c) - 0.1, c)


class TestHolyGrail(unittest.TestCase):
    def test_long_entry_fires(self):
        df = signals.add_signals(indicators.add_indicators(_trend_with_pullback()))
        self.assertGreaterEqual(int(df["long_entry"].sum()), 1)

    def test_short_mirror_fires(self):
        base = _trend_with_pullback()
        cc = (200.0 - base["c"]).to_numpy()
        oo = np.empty(len(cc))
        oo[0] = cc[0]
        oo[1:] = cc[:-1]
        m = _frame(oo, np.maximum(oo, cc) + 0.3, np.minimum(oo, cc) - 0.3, cc)
        m["t"] = base["t"].to_numpy()
        df = signals.add_signals(indicators.add_indicators(m))
        self.assertGreaterEqual(int(df["short_entry"].sum()), 1)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_no_entries_without_adx_gate(self):
        df = signals.add_signals(indicators.add_indicators(_sine_flat()))
        self.assertLess(float(df["adx"].max()), 30.0)
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_one_signal_per_adx_turnup(self):
        df = indicators.add_indicators(_trend_with_pullback())
        df = signals.add_signals(df)
        up_ok = (
            (df["adx"] > 30.0)
            & (df["adx"] > df["adx_prev"])
            & (df["plus_di"] > df["minus_di"])
        ).to_numpy()
        entries = np.where(df["long_entry"].to_numpy())[0]
        self.assertGreaterEqual(len(entries), 1)
        for prev, cur in zip(entries[:-1], entries[1:]):
            turnup = np.where(up_ok[prev + 1 : cur + 1]
                              & ~np.roll(up_ok, 1)[prev + 1 : cur + 1])[0]
            self.assertGreater(len(turnup), 0,
                               f"no fresh ADX turn-up between entries {prev} and {cur}")

    def test_swing_stop_exit(self):
        df = indicators.add_indicators(_trend_with_pullback())
        df = signals.add_signals(df)
        entries = np.where(df["long_entry"].to_numpy())[0]
        self.assertGreater(len(entries), 0)
        e = entries[0]
        # crash the market after entry: close below any possible swing low
        crashed = df.copy()
        crashed.loc[crashed.index[e + 2]:, ["o", "h", "l", "c"]] = 1.0
        out = signals.add_signals(indicators.add_indicators(crashed))
        exits = np.where(out["long_exit"].to_numpy())[0]
        self.assertTrue(np.any(exits > e), "no long_exit after price crashed")

    def test_breakout_bar_takes_out_touch_high(self):
        df = indicators.add_indicators(_trend_with_pullback())
        df = signals.add_signals(df)
        entries = np.where(df["long_entry"].to_numpy())[0]
        self.assertGreater(len(entries), 0)
        # every entry bar's high exceeds the previous bar's high (a buy-stop
        # take-out prints a fresh high vs the immediately prior bar in this
        # deterministic series; guards against entries firing on flat bars)
        for e in entries:
            self.assertGreater(df["h"].iloc[e], df["h"].iloc[e - 1])

    def test_no_lookahead(self):
        df = _trend_with_pullback()
        full = signals.add_signals(indicators.add_indicators(df))
        cut = signals.add_signals(indicators.add_indicators(df.iloc[:70]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue((full[col].iloc[:70].to_numpy() == cut[col].to_numpy()).all(), col)

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_trend_with_pullback()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_sanity(self):
        r = risk.RISK
        self.assertGreater(r.stop_atr_mult, 0)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertTrue(0 < r.risk_frac < 1)
        self.assertGreaterEqual(r.max_leverage, 1.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertGreaterEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
