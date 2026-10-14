"""Chandelier Exit tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chandelier_exit import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _trending(n=300, seed=7, direction=1):
    rng = np.random.default_rng(seed)
    c = 100 + direction * 0.30 * np.arange(n) + rng.normal(0, 0.10, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.25
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.25
    return _ohlcv(o, h, l, c)


def _chop(n=300, seed=7):
    """Flat range with constant highs/lows: close can never print above the
    prior 22-bar high, so breakout entries must stay silent."""
    rng = np.random.default_rng(seed)
    c = 100 + 0.05 * np.sin(np.arange(n) / 8) + rng.normal(0, 0.02, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.full(n, 100.50)
    l = np.full(n, 99.50)
    return _ohlcv(o, h, l, c)


class TestChandelierExit(unittest.TestCase):
    def test_chandelier_line_formula(self):
        n = 60
        c = np.full(n, 100.0)
        o = np.full(n, 100.0)
        h = np.full(n, 100.0)
        l = np.full(n, 100.0)
        h[5] = 110.0  # highest high within window
        df = indicators.add_indicators(_ohlcv(o, h, l, c))
        i = 30
        hh = h[i - 22 : i].max()  # prior 22 bars, excluding bar i
        tr = np.maximum(h - l, np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1)))
        tr[0] = h[0] - l[0]
        # pandas ewm adjust=False: y0 = x0, then y_j = k*x_j + (1-k)*y_{j-1}
        k = 1.0 / 22
        atr = tr[0]
        for j in range(1, i + 1):
            atr = k * tr[j] + (1 - k) * atr
        self.assertAlmostEqual(df["hh22"].iloc[i], hh, places=9)
        self.assertAlmostEqual(df["chand_long"].iloc[i], hh - 3.0 * atr, places=8)
        ll = l[i - 22 : i].min()
        self.assertAlmostEqual(df["chand_short"].iloc[i], ll + 3.0 * atr, places=8)

    def test_breakout_entry_fires_on_new_highs(self):
        df = signals.add_signals(indicators.add_indicators(_trending(direction=1)))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)
        idx = df.index[df["long_entry"]]
        for i in idx:
            self.assertLessEqual(df["c"].iloc[i - 1], df["hh22"].iloc[i - 1])
            self.assertGreater(df["c"].iloc[i], df["hh22"].iloc[i])

    def test_no_entry_on_flat_chop(self):
        df = signals.add_signals(indicators.add_indicators(_chop()))
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_exit_fires_below_chandelier(self):
        n = 160
        c = np.empty(n)
        c[:100] = 100 + 0.4 * np.arange(100)
        c[100:] = c[99] - 1.5 * np.arange(1, n - 100 + 1)  # dump below the line
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.2
        l = np.minimum(o, c) - 0.2
        df = signals.add_signals(indicators.add_indicators(_ohlcv(o, h, l, c)))
        idx = df.index[df["long_exit"]]
        self.assertGreater(len(idx), 0)
        i = idx[0]
        self.assertLess(df["c"].iloc[i], df["chand_long"].iloc[i])

    def test_no_lookahead_truncation(self):
        full = _trending()
        ind_full = indicators.add_indicators(full)
        for i in (100, 250):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("hh22", "ll22", "atr22", "chand_long", "chand_short"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_trending(direction=-1)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
