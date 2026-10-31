"""HalfTrend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.halftrend import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": h, "l": l, "c": closes,
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


def _rise_drop_rise():
    rise = [100.0 + i for i in range(40)]          # 100..139
    drop = [130.0, 125.0, 120.0, 115.0, 110.0]
    rec = [130.0 + 5.0 * i for i in range(10)]     # 130..175
    return rise + drop + rec


class TestHalfTrend(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("highPrice", "lowPrice", "highma", "lowma", "atr100",
                    "ht_trend", "ht", "atrHigh", "atrLow", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_hand_computed_extremes_and_mas(self):
        df = indicators.add_indicators(
            _frame([9.5, 11.5, 13.5], highs=[10, 12, 14], lows=[9, 11, 13]))
        self.assertAlmostEqual(df["highPrice"].iloc[1], 12.0)
        self.assertAlmostEqual(df["lowPrice"].iloc[1], 9.0)
        self.assertAlmostEqual(df["highma"].iloc[1], 11.0)
        self.assertAlmostEqual(df["lowma"].iloc[1], 10.0)
        self.assertTrue(np.isnan(df["highPrice"].iloc[0]))

    def test_trend_values_binary(self):
        df = _run(_random_walk_frame())
        self.assertTrue(df["ht_trend"].isin([0, 1]).all())

    def test_short_on_drop_then_long_on_recovery(self):
        df = _run(_frame(_rise_drop_rise()))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue(df["long_entry"].any())
        first_short = df.index[df["short_entry"]][0]
        first_long = df.index[df["long_entry"]][0]
        self.assertLess(first_short, first_long)

    def test_flip_bar_exits_and_reenters(self):
        df = _run(_frame(_rise_drop_rise()))
        # Every short entry after the first flip exits a long, and every
        # long entry after the first flip exits a short, on the same bar.
        se = df.index[df["short_entry"]]
        le = df.index[df["long_entry"]]
        for bar in se[1:]:
            self.assertTrue(df["long_exit"].iloc[bar])
        for bar in le[1:]:
            self.assertTrue(df["short_exit"].iloc[bar])

    def test_no_lookahead_last_close(self):
        closes = _rise_drop_rise()
        df1 = _run(_frame(closes))
        closes2 = list(closes)
        closes2[-1] = closes2[-1] * 1.5
        df2 = _run(_frame(closes2))
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

    def test_registration_and_warmup(self):
        self.assertIn("halftrend", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["halftrend"].slug, "halftrend")
        self.assertEqual(registry.REGISTRY["halftrend"].warmup_bars, risk.WARMUP)
        self.assertEqual(risk.WARMUP, 110)

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

    def test_warmup_gating_in_backtest(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        if len(res.trades):
            self.assertTrue(
                (res.trades["entry_t"] >= int(df["t"].iloc[risk.WARMUP])).all())

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
