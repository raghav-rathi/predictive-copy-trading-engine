"""Hurst exponent regime switch tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.hurst_exponent_regime import indicators, risk, signals
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


def _ar_returns(rho, seed=1, n=5000):
    rng = np.random.default_rng(seed)
    e = rng.normal(0, 0.01, n)
    r = np.zeros(n)
    for i in range(1, n):
        r[i] = rho * r[i - 1] + e[i]
    return r


def _signal_frame(mode, ema20, ema50, rsi, closes):
    n = len(mode)
    return pd.DataFrame({
        "mode": np.array(mode, dtype=int),
        "ema20": np.array(ema20, dtype=float),
        "ema50": np.array(ema50, dtype=float),
        "rsi14": np.array(rsi, dtype=float),
        "c": np.array(closes, dtype=float),
    })


class TestHurstExponentRegime(unittest.TestCase):
    def test_registered(self):
        self.assertIn("hurst_exponent_regime", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_hurst_estimator_persistent_vs_antipersistent(self):
        r_p = _ar_returns(0.8)
        r_a = _ar_returns(-0.8)
        for sl in (slice(0, 200), slice(1000, 1200), slice(3000, 3200)):
            self.assertGreater(indicators._hurst_rs(r_p[sl]), 0.55)
            self.assertLess(indicators._hurst_rs(r_a[sl]), 0.45)
        # Alternating returns are strongly mean-reverting.
        r_alt = np.tile([0.01, -0.01], 100)
        self.assertLess(indicators._hurst_rs(r_alt), 0.45)
        # Constant returns: no dispersion, estimator falls back to 0.5.
        self.assertEqual(indicators._hurst_rs(np.full(200, 0.001)), 0.5)
        self.assertEqual(indicators._hurst_rs(np.zeros(200)), 0.5)

    def test_hurst_needs_full_window(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue((df["hurst"].iloc[:199] == 0.5).all())
        self.assertTrue(df["hurst"].iloc[199:].between(0.0, 1.0).all())

    def test_mode_values_and_hysteresis(self):
        # Two consecutive trend bars are not enough to switch.
        h = np.array([0.5] * 10 + [0.7] * 2 + [0.5] * 5)
        m = indicators._regime_mode(h)
        self.assertTrue((m == 0).all())
        # Three consecutive trend bars switch; three consecutive
        # neutral bars switch back to 0.
        h = np.array([0.5] * 5 + [0.7] * 3 + [0.5] * 10)
        m = indicators._regime_mode(h)
        self.assertEqual(m[7], 1)
        self.assertEqual(m[9], 1)
        self.assertEqual(m[10], 0)
        # Trend -> reversion needs 3 consecutive reversion bars.
        h = np.array([0.7] * 5 + [0.3] * 2 + [0.7] * 5 + [0.3] * 3)
        m = indicators._regime_mode(h)
        self.assertEqual(m[6], 1)   # only 2 reversion bars: still trend
        self.assertEqual(m[14], -1)  # 3rd consecutive reversion bar
        # A single neutral bar breaks a pending streak.
        h = np.array([0.7] * 5 + [0.3] * 2 + [0.5] + [0.3] * 2)
        m = indicators._regime_mode(h)
        # Mode is 0 for the first two bars (switch needs 3), then 1
        # throughout: the neutral bar restarts the reversion streak.
        self.assertTrue((m[:2] == 0).all())
        self.assertTrue((m[2:] == 1).all())

    def test_trend_long_entry_on_ema_cross_up(self):
        df = signals.add_signals(_signal_frame(
            mode=[1] * 5,
            ema20=[10, 10, 10, 11, 12], ema50=[11, 11, 11, 11, 11],
            rsi=[60, 60, 60, 60, 60], closes=[100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].iloc[:4].any())
        self.assertTrue(df["long_entry"].iloc[4])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_no_trend_entry_when_mode_is_reversion(self):
        # Identical EMA cross-up, but the mode is reversion: no entry.
        df = signals.add_signals(_signal_frame(
            mode=[-1] * 5,
            ema20=[10, 10, 10, 11, 12], ema50=[11, 11, 11, 11, 11],
            rsi=[60, 60, 60, 60, 60], closes=[100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_when_mode_is_neutral(self):
        df = signals.add_signals(_signal_frame(
            mode=[0] * 5,
            ema20=[10, 10, 10, 11, 12], ema50=[11, 11, 11, 11, 11],
            rsi=[40, 35, 32, 29, 28], closes=[100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_reversion_long_entry_on_rsi_cross_below_30(self):
        df = signals.add_signals(_signal_frame(
            mode=[-1] * 5,
            ema20=[12, 12, 12, 12, 12], ema50=[11, 11, 11, 11, 11],
            rsi=[40, 35, 32, 29, 28], closes=[100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].iloc[:3].any())
        self.assertTrue(df["long_entry"].iloc[3])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_no_reversion_entry_when_mode_is_trend(self):
        # Identical RSI cross below 30, but the mode is trend: no entry.
        df = signals.add_signals(_signal_frame(
            mode=[1] * 5,
            ema20=[12, 12, 12, 12, 12], ema50=[11, 11, 11, 11, 11],
            rsi=[40, 35, 32, 29, 28], closes=[100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].any())

    def test_reversion_short_entry_on_rsi_cross_above_70(self):
        df = signals.add_signals(_signal_frame(
            mode=[-1] * 5,
            ema20=[10, 10, 10, 10, 10], ema50=[11, 11, 11, 11, 11],
            rsi=[60, 65, 68, 71, 72], closes=[100, 100, 100, 100, 100]))
        self.assertTrue(df["short_entry"].iloc[3])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_trend_long_exit_on_close_below_ema50(self):
        df = signals.add_signals(_signal_frame(
            mode=[1] * 5,
            ema20=[12, 12, 12, 12, 12], ema50=[11, 11, 11, 11, 11],
            rsi=[60, 60, 60, 60, 60], closes=[100, 100, 100, 100, 10]))
        self.assertTrue(df["long_exit"].iloc[4])
        self.assertFalse(df["long_exit"].iloc[:4].any())

    def test_reversion_long_exit_on_rsi_cross_above_50(self):
        df = signals.add_signals(_signal_frame(
            mode=[-1] * 5,
            ema20=[10, 10, 10, 10, 10], ema50=[11, 11, 11, 11, 11],
            rsi=[45, 48, 49, 52, 55], closes=[100, 100, 100, 100, 100]))
        self.assertFalse(df["long_exit"].iloc[:3].any())
        self.assertTrue(df["long_exit"].iloc[3])

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
        self.assertEqual(risk.WARMUP, 250)

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
        self.assertTrue((df["mode"] == 0).all())
        self.assertTrue((df["hurst"] == 0.5).all())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("hurst", "mode", "long_entry",
                    "short_entry", "long_exit", "short_exit"):
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
