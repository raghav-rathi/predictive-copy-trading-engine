"""Hull Moving Average cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.hull_ma_cross import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes * 1.001,
                         "l": closes * 0.999, "c": closes,
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestHullMaCross(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("hma_fast", "hma_slow", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_wma_hand_computed(self):
        # WMA([1,2,3,4], 4) with weights 1,2,3,4 = (1+4+9+16)/10 = 3.0.
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(indicators.wma(s, 4).iloc[-1], 3.0, places=9)
        # WMA([10,20], 2) = (10 + 40)/3 = 50/3.
        s2 = pd.Series([10.0, 20.0])
        self.assertAlmostEqual(indicators.wma(s2, 2).iloc[-1], 50.0 / 3.0, places=9)

    def test_hma_constant_series(self):
        # On a constant series every WMA equals the constant, so HMA does too.
        df = _run(_frame([100.0] * 200))
        self.assertTrue(np.allclose(df["hma_fast"].iloc[risk.WARMUP:], 100.0))
        self.assertTrue(np.allclose(df["hma_slow"].iloc[risk.WARMUP:], 100.0))

    def test_hma_faster_than_slow_on_trend(self):
        # Steady uptrend: the fast HMA must sit above the slow HMA.
        df = _run(_frame([100.0 + 0.1 * i for i in range(300)]))
        self.assertGreater(df["hma_fast"].iloc[-1], df["hma_slow"].iloc[-1])

    def test_long_on_bullish_cross(self):
        # Long downtrend then sharp recovery: fast HMA crosses above slow.
        closes = [200.0 - 0.2 * i for i in range(200)] + \
                 [160.0 + 0.8 * i for i in range(80)]
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())

    def test_short_on_bearish_cross(self):
        closes = [100.0 + 0.2 * i for i in range(200)] + \
                 [140.0 - 0.8 * i for i in range(80)]
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].any())

    def test_no_lookahead(self):
        # Changing the last bar's close must not change earlier signals.
        df1 = _run(_random_walk_frame())
        frame = _random_walk_frame()
        frame.loc[frame.index[-1], "c"] = frame["c"].iloc[-1] * 1.5
        df2 = _run(frame)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_warmup_gating(self):
        # Before the slow HMA exists (WMA(64) at bar 63 + WMA(8)
        # pass = bar 70) there can be no cross signal. Bars 71-79
        # may carry signals but the harness gates entries at WARMUP.
        df = _run(_random_walk_frame())
        self.assertFalse(df["long_entry"].iloc[:71].any())
        self.assertFalse(df["short_entry"].iloc[:71].any())

    def test_registration_and_warmup(self):
        self.assertIn("hull_ma_cross", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["hull_ma_cross"].slug, "hull_ma_cross")
        self.assertEqual(risk.WARMUP, 80)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
