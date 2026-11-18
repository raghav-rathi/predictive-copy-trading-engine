"""Stochastic RSI cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stochastic_rsi import indicators, risk, signals
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


def _cross_rows(k_prev, d_prev, k_now, d_now):
    return pd.DataFrame([
        dict(stochrsi_k=k_prev, stochrsi_d=d_prev),
        dict(stochrsi_k=k_now, stochrsi_d=d_now),
    ])


class TestStochasticRsi(unittest.TestCase):
    def test_registered(self):
        self.assertIn("stochastic_rsi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_stochrsi_flat_is_50(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertTrue((df["stochrsi"].dropna() == 50.0).all())
        self.assertTrue((df["stochrsi_k"].dropna() == 50.0).all())
        self.assertTrue((df["stochrsi_d"].dropna() == 50.0).all())

    def test_stochrsi_bounded(self):
        df = indicators.add_indicators(_random_walk_frame())
        for col in ("stochrsi", "stochrsi_k", "stochrsi_d"):
            s = df[col].dropna()
            self.assertTrue((s >= 0).all())
            self.assertTrue((s <= 100).all())

    def test_d_is_sma3_of_k(self):
        df = indicators.add_indicators(_random_walk_frame())
        expect = df["stochrsi_k"].rolling(3, min_periods=3).mean()
        pd.testing.assert_series_equal(df["stochrsi_d"], expect,
                                       check_names=False)

    def test_k_is_sma3_of_stochrsi(self):
        df = indicators.add_indicators(_random_walk_frame())
        expect = df["stochrsi"].rolling(3, min_periods=3).mean()
        pd.testing.assert_series_equal(df["stochrsi_k"], expect,
                                       check_names=False)

    def test_stochrsi_high_on_steady_rise(self):
        closes = [100.0 + i for i in range(200)]
        df = indicators.add_indicators(_frame(closes))
        # While RSI is still climbing (before it saturates at 100 and
        # the 14-bar range collapses to the 50.0 guard), %K pegs high.
        self.assertGreater(df["stochrsi_k"].max(), 80)

    def test_stochrsi_low_on_steady_fall(self):
        rng = np.random.default_rng(3)
        c = 100 * np.exp(np.cumsum(rng.normal(-0.005, 0.01, 500)))
        df = indicators.add_indicators(_frame(c))
        self.assertLess(df["stochrsi_k"].min(), 20)

    def test_long_entry_cross_from_oversold(self):
        df = signals.add_signals(_cross_rows(15.0, 16.0, 17.0, 16.5))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_no_long_entry_prior_k_not_oversold(self):
        df = signals.add_signals(_cross_rows(25.0, 24.0, 26.0, 25.0))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_no_long_entry_without_cross(self):
        # %K already above %D on the prior bar: no cross.
        df = signals.add_signals(_cross_rows(18.0, 16.0, 19.0, 16.5))
        self.assertFalse(df["long_entry"].iloc[1])

    def test_short_entry_cross_from_overbought(self):
        df = signals.add_signals(_cross_rows(85.0, 84.0, 83.0, 84.5))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_no_short_entry_prior_k_not_overbought(self):
        df = signals.add_signals(_cross_rows(75.0, 76.0, 74.0, 75.0))
        self.assertFalse(df["short_entry"].iloc[1])

    def test_long_exit_on_cross_down(self):
        df = signals.add_signals(_cross_rows(30.0, 29.0, 28.0, 29.5))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

    def test_long_exit_on_k_cross_above_80(self):
        df = signals.add_signals(_cross_rows(79.0, 70.0, 81.0, 71.0))
        self.assertTrue(df["long_exit"].iloc[1])

    def test_no_long_exit_on_touch_above_80(self):
        # %K already above 80 on the prior bar: no cross, no exit.
        df = signals.add_signals(_cross_rows(85.0, 70.0, 86.0, 71.0))
        self.assertFalse(df["long_exit"].iloc[1])

    def test_short_exit_on_k_cross_below_20(self):
        df = signals.add_signals(_cross_rows(21.0, 30.0, 19.0, 29.0))
        self.assertTrue(df["short_exit"].iloc[1])

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
        for col in ("stochrsi", "stochrsi_k", "stochrsi_d",
                    "long_entry", "long_exit"):
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
