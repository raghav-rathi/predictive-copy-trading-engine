"""MACD Histogram Divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_histogram_divergence import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest
from strategies import base as B


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


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


def _v_shape_frame():
    """60 flat bars, then a V dip: lows 99.5, 99, 98.5, 98, 98.5,
    99, 99.5 with closes tracking the lows + 0.5."""
    closes = [100.0] * 60
    dip = [99.5, 99.0, 98.5, 98.0, 98.5, 99.0, 99.5]
    closes += dip
    closes += [100.0] * 20
    lows = [c - 0.5 for c in closes]
    # Make the dip lows exact: low at the trough bar is 97.5.
    return _frame(closes, lows=lows)


class TestMacdHistogramDivergence(unittest.TestCase):
    def test_registered(self):
        self.assertIn("macd_histogram_divergence", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_macd_flat_zero(self):
        df = indicators.add_indicators(_frame([100.0] * 200))
        self.assertAlmostEqual(df["macd_hist"].iloc[100], 0.0, places=9)
        self.assertAlmostEqual(df["macd_line"].iloc[100], 0.0, places=9)

    def test_macd_matches_base(self):
        df0 = _random_walk_frame()
        df = indicators.add_indicators(df0)
        m = B.macd(df0["c"], 12, 26, 9)
        for i in (50, 200, 1000):
            self.assertAlmostEqual(df["macd_line"].iloc[i], m["macd"].iloc[i], places=8)
            self.assertAlmostEqual(df["macd_hist"].iloc[i], m["macd_hist"].iloc[i], places=8)

    def test_pivot_low_confirmed_two_bars_later(self):
        df = indicators.add_indicators(_v_shape_frame())
        # Trough low is at bar 63 (closes[63] = 98.0); confirmation
        # is bar 65.
        self.assertFalse(df["pivot_low_conf"].iloc[:65].any())
        self.assertTrue(df["pivot_low_conf"].iloc[65])
        self.assertAlmostEqual(df["pivot_low_price"].iloc[65], 97.5, places=6)

    def test_pivot_high_confirmed_two_bars_later(self):
        # Mirror: an inverted V (peak) in the highs.
        closes = [100.0] * 60 + [100.5, 101.0, 101.5, 102.0, 101.5, 101.0, 100.5] + [100.0] * 20
        highs = [c + 0.5 for c in closes]
        df = indicators.add_indicators(_frame(closes, highs=highs))
        self.assertTrue(df["pivot_high_conf"].iloc[65])
        self.assertAlmostEqual(df["pivot_high_price"].iloc[65], 102.5, places=6)

    def test_no_pivot_on_flat(self):
        df = indicators.add_indicators(_frame([100.0] * 200))
        self.assertFalse(df["pivot_low_conf"].any())
        self.assertFalse(df["pivot_high_conf"].any())
        self.assertFalse(df["bull_div"].any())
        self.assertFalse(df["bear_div"].any())

    def test_bull_div_entry_and_exit_wiring(self):
        df = pd.DataFrame({
            "macd_hist": [0.5, 0.6, 0.7, 0.8],
            "bull_div": [False, True, False, False],
            "bear_div": [False, False, False, True],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["short_exit"].iloc[1])   # bull div exits shorts
        self.assertTrue(out["short_entry"].iloc[3])
        self.assertTrue(out["long_exit"].iloc[3])    # bear div exits longs

    def test_long_exit_on_hist_cross_below_zero(self):
        df = pd.DataFrame({
            "macd_hist": [1.0, 0.5, -0.5, -1.0],
            "bull_div": [False] * 4,
            "bear_div": [False] * 4,
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_exit"].iloc[2])
        self.assertFalse(out["long_exit"].iloc[3])
        self.assertFalse(out["long_entry"].any())

    def test_short_exit_on_hist_cross_above_zero(self):
        df = pd.DataFrame({
            "macd_hist": [-1.0, -0.5, 0.5, 1.0],
            "bull_div": [False] * 4,
            "bear_div": [False] * 4,
        })
        out = signals.add_signals(df)
        self.assertTrue(out["short_exit"].iloc[2])
        self.assertFalse(out["short_exit"].iloc[3])
        self.assertFalse(out["short_entry"].any())

    def test_entries_equal_divergences(self):
        df = _run(_random_walk_frame())
        pd.testing.assert_series_equal(
            df["long_entry"].reset_index(drop=True),
            df["bull_div"].reset_index(drop=True), check_names=False)
        pd.testing.assert_series_equal(
            df["short_entry"].reset_index(drop=True),
            df["bear_div"].reset_index(drop=True), check_names=False)

    def test_random_walk_produces_divergences(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertGreater(int(df["bull_div"].sum()), 0)
        self.assertGreater(int(df["bear_div"].sum()), 0)

    def test_double_bottom_divergence(self):
        # Dip 1: fast 5-bar fall to 95, recover. Then 30 flat bars
        # (MACD decays toward 0), then dip 2: a slower 20-bar fall
        # to a LOWER low of 92, recover. The slower second fall
        # leaves the histogram higher at its low, the second pivot
        # is 55 bars after the first (inside the 60-bar lookback),
        # and the recovery turns the histogram up on the
        # confirmation bar -> bullish divergence.
        closes = [100.0] * 60
        closes += list(np.linspace(99, 95, 5))
        closes += list(np.linspace(96, 100, 5))
        closes += [100.0] * 30
        closes += list(np.linspace(99.5, 92, 20))
        closes += list(np.linspace(93, 100, 8))
        closes += [100.0] * 20
        df = indicators.add_indicators(_frame(closes))
        self.assertEqual(int(df["bull_div"].sum()), 1)
        i = int(np.where(df["bull_div"].to_numpy())[0][0])
        self.assertAlmostEqual(df["pivot_low_price"].iloc[i], 91.5, places=6)
        self.assertLess(df["pivot_low_hist"].iloc[i], 0.0)
        self.assertGreater(df["pivot_low_hist"].iloc[i], -0.52)

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
        self.assertEqual(risk.WARMUP, 80)

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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("macd_hist", "pivot_low_conf", "bull_div",
                    "bear_div", "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["macd_hist"].isna().all())


if __name__ == "__main__":
    unittest.main()
