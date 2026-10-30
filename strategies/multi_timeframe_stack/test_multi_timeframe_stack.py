"""Multi-timeframe stack tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.multi_timeframe_stack import indicators, risk, signals
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


def _uptrend_with_dip_recovery():
    # 240 bars gently rising (4h trend up), a sharp 14-bar dip that
    # drags EMA(9) below EMA(21), then a sharp 16-bar recovery that
    # crosses back up while the 4h trend is still up.
    base = [100.0 + 0.05 * i for i in range(240)]
    dip = [base[-1] - 0.6 * (i + 1) for i in range(14)]
    rec = [dip[-1] + 0.8 * (i + 1) for i in range(16)]
    return base + dip + rec


def _downtrend_with_rally_pullback():
    base = [120.0 - 0.05 * i for i in range(240)]
    rally = [base[-1] + 0.6 * (i + 1) for i in range(14)]
    fall = [rally[-1] - 0.8 * (i + 1) for i in range(16)]
    return base + rally + fall


class TestMultiTimeframeStack(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("ema9", "ema21", "htf_ema20", "htf_ema50",
                    "htf_trend", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_htf_trend_up_on_uptrend(self):
        df = _run(_frame(_uptrend_with_dip_recovery()))
        self.assertEqual(df["htf_trend"].iloc[230], 1)

    def test_long_on_1h_cross_in_4h_uptrend(self):
        df = _run(_frame(_uptrend_with_dip_recovery()))
        self.assertTrue(df["long_entry"].any())
        # Every long entry must sit on a 4h uptrend bar.
        self.assertTrue((df.loc[df["long_entry"], "htf_trend"] == 1).all())

    def test_short_on_1h_cross_in_4h_downtrend(self):
        df = _run(_frame(_downtrend_with_rally_pullback()))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue((df.loc[df["short_entry"], "htf_trend"] == -1).all())

    def test_no_trade_against_htf_trend(self):
        # Steady uptrend with no 1h cross-down that survives: a
        # cross-down while the 4h trend is up must never short.
        df = _run(_frame([100.0 + 0.05 * i for i in range(300)]))
        self.assertFalse(df["short_entry"].any())

    def test_incomplete_4h_bar_not_used(self):
        # Changing the final bar's close must not move any 4h value:
        # the final bar's group is either incomplete or has no
        # 1h bar after it to observe.
        df1 = _run(_frame(_uptrend_with_dip_recovery()))
        closes = _uptrend_with_dip_recovery()
        closes[-1] = closes[-1] * 1.5
        df2 = _run(_frame(closes))
        pd.testing.assert_series_equal(
            df1["htf_ema20"].reset_index(drop=True),
            df2["htf_ema20"].reset_index(drop=True), check_names=False)
        pd.testing.assert_series_equal(
            df1["htf_trend"].reset_index(drop=True),
            df2["htf_trend"].reset_index(drop=True), check_names=False)

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("multi_timeframe_stack", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["multi_timeframe_stack"].slug,
                         "multi_timeframe_stack")
        self.assertEqual(risk.WARMUP, 230)

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
