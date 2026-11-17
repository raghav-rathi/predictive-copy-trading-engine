"""Trendline Breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.trendline_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _pivot_frame():
    """40 flat bars (h=100, l=90, c=100) with two swing highs
    (h=120 at bar 10, h=110 at bar 25) and two swing lows
    (l=80 at bar 12, l=85 at bar 28)."""
    n = 40
    highs = [100.0] * n
    highs[10] = 120.0
    highs[25] = 110.0
    lows = [90.0] * n
    lows[12] = 80.0
    lows[28] = 85.0
    return _frame([100.0] * n, highs=highs, lows=lows)


class TestTrendlineBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("trendline_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_pivot_confirmation_lag(self):
        # Pivot at bar 10 is NOT visible at bar 10; it is confirmed
        # (and only then visible) at bar 15.
        df = indicators.add_indicators(_pivot_frame())
        self.assertFalse(df["swing_high"].iloc[10])
        self.assertFalse(df["swing_high"].iloc[14])
        self.assertTrue(df["swing_high"].iloc[15])
        self.assertTrue(df["swing_high"].iloc[30])  # pivot at 25
        self.assertFalse(df["swing_low"].iloc[12])
        self.assertTrue(df["swing_low"].iloc[17])   # pivot at 12
        self.assertTrue(df["swing_low"].iloc[33])   # pivot at 28

    def test_downtrend_line_exact(self):
        # Line through (10, 120) and (25, 110): slope -2/3.
        # At bar 30: 110 - (2/3)*5 = 106.6667; at 35: 103.3333.
        df = indicators.add_indicators(_pivot_frame())
        self.assertTrue(np.isnan(df["downtrend_line"].iloc[29]))
        self.assertAlmostEqual(df["downtrend_line"].iloc[30], 110 - 10.0 / 3.0)
        self.assertAlmostEqual(df["downtrend_line"].iloc[35], 110 - 20.0 / 3.0)

    def test_uptrend_line_exact(self):
        # Line through (12, 80) and (28, 85): slope 5/16 = 0.3125.
        # At bar 33: 85 + 0.3125*5 = 86.5625; at 38: 88.125.
        df = indicators.add_indicators(_pivot_frame())
        self.assertTrue(np.isnan(df["uptrend_line"].iloc[32]))
        self.assertAlmostEqual(df["uptrend_line"].iloc[33], 86.5625)
        self.assertAlmostEqual(df["uptrend_line"].iloc[38], 88.125)

    def test_no_line_before_two_pivots(self):
        # Only one swing high confirmed before bar 30: no downtrend
        # line yet; only one swing low confirmed before bar 33:
        # no uptrend line yet.
        df = indicators.add_indicators(_pivot_frame())
        self.assertTrue(df["downtrend_line"].iloc[:30].isna().all())
        self.assertTrue(df["uptrend_line"].iloc[:33].isna().all())

    def test_equal_peaks_are_not_pivots(self):
        # Two adjacent equal highs: neither is strictly greater
        # than the 5 bars on each side, so neither is a pivot.
        n = 40
        highs = [100.0] * n
        highs[10] = 120.0
        highs[11] = 120.0
        df = indicators.add_indicators(
            _frame([100.0] * n, highs=highs, lows=[90.0] * n))
        self.assertFalse(df["swing_high"].any())
        self.assertTrue(df["downtrend_line"].isna().all())

    def test_signal_logic_crafted_rows(self):
        # Close crosses above the downtrend line -> long entry +
        # short exit; crosses below the uptrend line -> short
        # entry + long exit.
        rows = [dict(c=100.0, downtrend_line=105.0, uptrend_line=95.0),
                dict(c=110.0, downtrend_line=105.0, uptrend_line=95.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        rows = [dict(c=100.0, downtrend_line=105.0, uptrend_line=95.0),
                dict(c=90.0, downtrend_line=105.0, uptrend_line=95.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

    def test_no_entry_without_cross(self):
        # Close stays below the downtrend line: no cross, no entry,
        # even though a line exists.
        rows = [dict(c=100.0, downtrend_line=105.0, uptrend_line=95.0),
                dict(c=102.0, downtrend_line=105.0, uptrend_line=95.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # A line appearing (NaN -> value) with the close already
        # above it is not a cross either.
        rows = [dict(c=110.0, downtrend_line=np.nan, uptrend_line=np.nan),
                dict(c=110.0, downtrend_line=105.0, uptrend_line=95.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertFalse(df["long_entry"].iloc[1])

    def test_entry_fires_on_line_break(self):
        # Pivot frame: downtrend line at bar 30 is ~106.67 and
        # falling; close 100 at bar 30 then 108 at bar 31 crosses
        # above it (line at 31 is 106.0).
        n = 40
        highs = [100.0] * n
        highs[10] = 120.0
        highs[25] = 110.0
        lows = [90.0] * n
        lows[12] = 80.0
        lows[28] = 85.0
        closes = [100.0] * 31 + [108.0] + [100.0] * 8
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["long_entry"].iloc[30])
        self.assertTrue(df["long_entry"].iloc[31])
        self.assertTrue(df["short_exit"].iloc[31])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 120)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("swing_high", "swing_low", "downtrend_line",
                    "uptrend_line", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["downtrend_line"].isna().all())
        self.assertTrue(df["uptrend_line"].isna().all())


if __name__ == "__main__":
    unittest.main()
