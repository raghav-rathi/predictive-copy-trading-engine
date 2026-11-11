"""MACD + session VWAP tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_vwap_combo import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

# 2023-11-15 00:00:00 UTC — a UTC-midnight t base, so the first 24
# hourly bars form exactly one session.
MIDNIGHT_MS = 1_700_006_400_000


def _frame(closes, highs=None, lows=None, vols=None, opens=None,
           t0=1_700_000_000_000):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=300, close=100.0):
    return _frame([close] * n)


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


def _ema_manual(values, n):
    """Plain EMA recursion, alpha = 2/(n+1), seeded at values[0]."""
    alpha = 2.0 / (n + 1)
    out = [values[0]]
    for x in values[1:]:
        out.append(alpha * x + (1.0 - alpha) * out[-1])
    return np.array(out)


class TestMacdVwapCombo(unittest.TestCase):
    def test_registered(self):
        self.assertIn("macd_vwap_combo", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_macd_hand_computed(self):
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        df = indicators.add_indicators(_frame(closes))
        ema12 = _ema_manual(closes, 12)
        ema26 = _ema_manual(closes, 26)
        macd_line = ema12 - ema26
        # The signal EMA runs over the MACD line, which is NaN before
        # bar 26 (EMA(26) min_periods); pandas ewm skips those NaNs
        # and seeds at the first defined MACD value (bar 25).
        sig_line = _ema_manual(macd_line[25:], 9)
        # pandas ewm(min_periods=n) is NaN until the window fills;
        # from bar 26 on both EMAs are defined, and the signal EMA
        # (min_periods=9 over the MACD line, itself NaN before bar 26)
        # is defined from bar 33 on.
        i = 100
        self.assertAlmostEqual(df["macd"].iloc[i], macd_line[i], places=8)
        self.assertAlmostEqual(df["macd_signal"].iloc[i], sig_line[i - 25],
                               places=8)
        self.assertAlmostEqual(df["macd_hist"].iloc[i],
                               macd_line[i] - sig_line[i - 25], places=8)
        self.assertTrue(np.isnan(df["macd"].iloc[24]))
        self.assertFalse(np.isnan(df["macd"].iloc[25]))
        self.assertTrue(np.isnan(df["macd_signal"].iloc[32]))
        self.assertFalse(np.isnan(df["macd_signal"].iloc[33]))

    def test_indicator_vwap_hand_computed(self):
        # One session, three bars: tp 100/102/101, vols 10/10/30.
        # vwap: 100, (1000+1020)/20 = 101, 5050/50 = 101.
        closes = [100.0, 102.0, 101.0]
        highs = [100.0, 103.0, 102.0]
        lows = [100.0, 101.0, 100.0]
        vols = [10.0, 10.0, 30.0]
        df = indicators.add_indicators(_frame(
            closes, highs=highs, lows=lows, vols=vols, t0=MIDNIGHT_MS))
        self.assertAlmostEqual(df["vwap_day"].iloc[0], 100.0, places=10)
        self.assertAlmostEqual(df["vwap_day"].iloc[1], 101.0, places=10)
        self.assertAlmostEqual(df["vwap_day"].iloc[2], 101.0, places=10)

    def test_indicator_vwap_resets_at_midnight(self):
        # 24 bars in one session (indices 0-23) then two bars of the
        # next day (indices 24-25): the day-2 VWAP is just that day's
        # typical prices, with no day-1 leakage.
        closes = [100.0] * 24 + [120.0, 120.0]
        highs = [c + 0.5 for c in closes]
        lows = [c - 0.5 for c in closes]
        df = indicators.add_indicators(_frame(
            closes, highs=highs, lows=lows, t0=MIDNIGHT_MS))
        self.assertAlmostEqual(df["vwap_day"].iloc[23], 100.0, places=10)
        self.assertAlmostEqual(df["vwap_day"].iloc[24], 120.0, places=10)
        # And the day-1 VWAP never leaks into day 2.
        self.assertAlmostEqual(df["vwap_day"].iloc[25], 120.0, places=10)

    def test_long_entry_cross_above_vwap(self):
        rows = pd.DataFrame({
            "macd": [0.0, 2.0, 3.0],
            "macd_signal": [1.0, 1.0, 1.0],
            "c": [105.0, 105.0, 105.0],
            "vwap_day": [100.0, 100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertEqual(list(df["long_entry"]), [False, True, False])
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["short_exit"].iloc[1])

    def test_long_entry_blocked_below_vwap(self):
        rows = pd.DataFrame({
            "macd": [0.0, 2.0, 3.0],
            "macd_signal": [1.0, 1.0, 1.0],
            "c": [95.0, 95.0, 95.0],
            "vwap_day": [100.0, 100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_cross_below_vwap(self):
        rows = pd.DataFrame({
            "macd": [3.0, 1.0, 0.0],
            "macd_signal": [2.0, 2.0, 2.0],
            "c": [95.0, 95.0, 95.0],
            "vwap_day": [100.0, 100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertEqual(list(df["short_entry"]), [False, True, False])
        self.assertFalse(df["long_entry"].any())
        self.assertTrue(df["long_exit"].iloc[1])

    def test_short_entry_blocked_above_vwap(self):
        rows = pd.DataFrame({
            "macd": [3.0, 1.0, 0.0],
            "macd_signal": [2.0, 2.0, 2.0],
            "c": [105.0, 105.0, 105.0],
            "vwap_day": [100.0, 100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["short_entry"].any())

    def test_exit_not_gated_by_vwap(self):
        # A bearish MACD cross exits a long even while close is still
        # above VWAP (filter gates entries only).
        rows = pd.DataFrame({
            "macd": [3.0, 1.0],
            "macd_signal": [2.0, 2.0],
            "c": [105.0, 105.0],
            "vwap_day": [100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])

    def test_no_signal_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("macd", "macd_signal", "vwap_day",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:300].reset_index(drop=True),
                df2[col].iloc[:300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
