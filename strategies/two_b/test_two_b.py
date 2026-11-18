"""Sperandeo 2B reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.two_b import indicators, risk, signals
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


def _top_frame():
    """20 quiet bars, new 20-bar high 115 at bar 20, 5 pullback bars,
    retest bar 26 closes 116 above 115 (retest low 100), failure
    bar 27 closes 99 below 100 -> short trigger at 27."""
    closes = [100.0] * 20 + [112.0] + [100.0] * 5 + [116.0, 99.0]
    highs = [110.0] * 20 + [115.0] + [110.0] * 5 + [117.0, 110.0]
    lows = [90.0] * 20 + [108.0] + [95.0] * 5 + [100.0, 95.0]
    return _frame(closes, highs=highs, lows=lows)


def _bottom_frame():
    """Mirror of _top_frame: new 20-bar low 85 at bar 20, 5 pullback
    bars, retest bar 26 closes 84 below 85 (retest high 100),
    failure bar 27 closes 101 above 100 -> long trigger at 27."""
    closes = [100.0] * 20 + [88.0] + [100.0] * 5 + [84.0, 101.0]
    highs = [110.0] * 20 + [92.0] + [105.0] * 5 + [100.0, 105.0]
    lows = [90.0] * 20 + [85.0] + [90.0] * 5 + [83.0, 90.0]
    return _frame(closes, highs=highs, lows=lows)


class TestTwoB(unittest.TestCase):
    def test_registered(self):
        self.assertIn("two_b", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_new_high_20_previous_bars_only(self):
        df = indicators.add_indicators(_top_frame())
        self.assertTrue(df["new_high_20"].iloc[20])
        # The retest bar's high (117) is a new high too, but the
        # retest check runs first; the pattern still arms/fails.
        self.assertFalse(df["new_high_20"].iloc[21])
        self.assertAlmostEqual(df["last_top_extreme"].iloc[26], 115.0)

    def test_new_low_20_previous_bars_only(self):
        df = indicators.add_indicators(_bottom_frame())
        self.assertTrue(df["new_low_20"].iloc[20])
        self.assertFalse(df["new_low_20"].iloc[21])
        self.assertAlmostEqual(df["last_bottom_extreme"].iloc[26], 85.0)

    def test_top_armed_and_retest_level(self):
        df = indicators.add_indicators(_top_frame())
        # Pullback done at bar 25 (5 bars after the extreme).
        self.assertFalse(df["armed_top"].iloc[24])
        self.assertTrue(df["armed_top"].iloc[25])
        self.assertTrue(df["armed_top"].iloc[26])
        self.assertAlmostEqual(df["retest_level"].iloc[26], 100.0)
        self.assertTrue(df["await_top"].iloc[26])

    def test_top_short_trigger_on_failure_close(self):
        df = _run(_top_frame())
        self.assertFalse(df["short_entry"].iloc[:27].any())
        self.assertTrue(df["short_entry"].iloc[27])
        self.assertFalse(df["long_entry"].iloc[27])
        # Trigger fires on one bar only.
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_bottom_long_trigger_on_failure_close(self):
        df = _run(_bottom_frame())
        self.assertFalse(df["long_entry"].iloc[:27].any())
        self.assertTrue(df["long_entry"].iloc[27])
        self.assertFalse(df["short_entry"].iloc[27])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertAlmostEqual(df["retest_level"].iloc[26], 100.0)

    def test_no_entry_without_retest(self):
        # New high + pullback, but the retest bar never closes above
        # the extreme -> no trigger.
        closes = [100.0] * 20 + [112.0] + [100.0] * 10
        highs = [110.0] * 20 + [115.0] + [110.0] * 10
        lows = [90.0] * 20 + [108.0] + [95.0] * 10
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_without_failure(self):
        # Retest happens but price never closes below the retest low.
        closes = [100.0] * 20 + [112.0] + [100.0] * 5 + [116.0] + [110.0] * 5
        highs = [110.0] * 20 + [115.0] + [110.0] * 5 + [117.0] + [112.0] * 5
        lows = [90.0] * 20 + [108.0] + [95.0] * 5 + [100.0] + [105.0] * 5
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_when_pullback_too_short(self):
        # Bar 23 closes above the extreme only 3 bars after it: that
        # bar is itself a fresh 20-bar high, so it re-arms instead
        # of counting as a retest; no failure follows.
        closes = [100.0] * 20 + [112.0, 100.0, 100.0, 116.0] + [110.0] * 5
        highs = [110.0] * 20 + [115.0, 110.0, 110.0, 117.0] + [112.0] * 5
        lows = [90.0] * 20 + [108.0, 95.0, 95.0, 100.0] + [105.0] * 5
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].any())

    def test_fresh_extreme_rearms(self):
        # A higher high during the pullback re-arms on the new extreme.
        closes = [100.0] * 20 + [112.0, 118.0] + [100.0] * 5 + [119.0]
        highs = [110.0] * 20 + [115.0, 120.0] + [110.0] * 5 + [119.0]
        lows = [90.0] * 20 + [108.0, 110.0] + [95.0] * 5 + [100.0]
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertAlmostEqual(df["last_top_extreme"].iloc[-1], 120.0)

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=99.0, long_trigger=False, short_trigger=True,
            last_bottom_extreme=85.0, last_top_extreme=115.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_invalidation(self):
        # Close below the arming low extreme invalidates a long.
        rows = pd.DataFrame([dict(
            c=84.0, long_trigger=False, short_trigger=False,
            last_bottom_extreme=85.0, last_top_extreme=115.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(
            c=116.0, long_trigger=False, short_trigger=False,
            last_bottom_extreme=85.0, last_top_extreme=115.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

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
        self.assertEqual(risk.WARMUP, 60)

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
        for col in ("new_high_20", "retest_level", "long_entry",
                    "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
