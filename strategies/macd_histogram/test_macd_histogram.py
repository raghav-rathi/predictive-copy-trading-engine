"""MACD histogram tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_histogram import indicators, risk, signals
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


def _ema_manual(x, n):
    """Plain EMA recursion: alpha = 2/(n+1), seeded at x[0]."""
    alpha = 2.0 / (n + 1)
    out = np.empty(len(x))
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = alpha * x[i] + (1.0 - alpha) * out[i - 1]
    return out


class TestMacdHistogram(unittest.TestCase):
    def test_registered(self):
        self.assertIn("macd_histogram", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_macd_values_hand_computed(self):
        # Manual EMA(12) - EMA(26), then EMA(9) of that line, on a
        # smooth rising series; compare at bar 100.
        rng = np.random.default_rng(11)
        closes = 100 + np.cumsum(rng.normal(0.05, 0.5, 200))
        df = indicators.add_indicators(_frame(closes))
        ema12 = _ema_manual(closes, 12)
        ema26 = _ema_manual(closes, 26)
        line = ema12 - ema26
        # Signal is EMA(9) of the line, seeded at the first valid
        # line value (bar 25, when EMA(26) first exists).
        sig = np.full(200, np.nan)
        alpha9 = 2.0 / 10
        sig[25] = line[25]
        for i in range(26, 200):
            sig[i] = alpha9 * line[i] + (1.0 - alpha9) * sig[i - 1]
        self.assertAlmostEqual(df["macd"].iloc[100], line[100], places=8)
        self.assertAlmostEqual(df["macd_signal"].iloc[100], sig[100], places=8)
        self.assertAlmostEqual(df["macd_hist"].iloc[100],
                               line[100] - sig[100], places=8)
        # Histogram is NaN until the signal EMA has 9 valid values.
        self.assertTrue(np.isnan(df["macd_hist"].iloc[32]))
        self.assertTrue(np.isfinite(df["macd_hist"].iloc[33]))

    def test_hist_is_macd_minus_signal(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[100:]
        pd.testing.assert_series_equal(
            tail["macd_hist"], tail["macd"] - tail["macd_signal"],
            check_names=False)

    def test_histogram_cross_up_fires_long(self):
        # Flat at 100, then a steady rise to 130, then a steady fall
        # back to 100: the histogram must cross above zero on the rise
        # and below zero on the fall.
        closes = ([100.0] * 60
                  + list(np.linspace(100.0, 130.0, 30))
                  + list(np.linspace(130.0, 100.0, 30)))
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["short_entry"].any())
        # Every long entry is a genuine zero cross of the histogram.
        hist = df["macd_hist"]
        for i in np.where(df["long_entry"])[0]:
            self.assertGreater(hist.iloc[i], 0.0)
            self.assertLessEqual(hist.iloc[i - 1], 0.0)
        for i in np.where(df["short_entry"])[0]:
            self.assertLess(hist.iloc[i], 0.0)
            self.assertGreaterEqual(hist.iloc[i - 1], 0.0)
        # No entry before the histogram exists (bar 34).
        self.assertFalse(df["long_entry"].iloc[:34].any())
        self.assertFalse(df["short_entry"].iloc[:34].any())

    def test_flat_data_no_signals(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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
        self.assertEqual(risk.WARMUP, 40)

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
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("macd", "macd_signal", "macd_hist",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): MACD is still defined, but a
        # flat series produces a zero histogram and no crosses.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
