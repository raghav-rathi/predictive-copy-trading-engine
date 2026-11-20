"""Heikin Ashi + EMA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.heikin_ashi_ema import indicators, risk, signals
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


def _trend_frame():
    """80 bars rising 100 -> 130, then 80 bars falling 130 -> 95."""
    return _frame(list(np.linspace(100, 130, 80))
                  + list(np.linspace(130, 95, 80)))


class TestHeikinAshiEma(unittest.TestCase):
    def test_registered(self):
        self.assertIn("heikin_ashi_ema", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_ha_close_math(self):
        df = indicators.add_indicators(_trend_frame())
        df0 = _trend_frame()
        expected = (df0["o"] + df0["h"] + df0["l"] + df0["c"]) / 4
        pd.testing.assert_series_equal(df["ha_close"], expected,
                                       check_names=False)

    def test_ha_open_seed_and_recursion(self):
        df0 = _trend_frame()
        df = indicators.add_indicators(df0)
        self.assertAlmostEqual(df["ha_open"].iloc[0],
                               (df0["o"].iloc[0] + df0["c"].iloc[0]) / 2)
        for i in (1, 2, 3, 50, 100):
            expected = (df["ha_open"].iloc[i - 1]
                        + df["ha_close"].iloc[i - 1]) / 2
            self.assertAlmostEqual(df["ha_open"].iloc[i], expected)

    def test_ha_open_never_uses_future(self):
        # HA open on bar i depends only on HA values through bar i-1.
        df = indicators.add_indicators(_trend_frame())
        # On a steady rise HA open trails HA close (open < close).
        self.assertTrue((df["ha_close"].iloc[50:79]
                         > df["ha_open"].iloc[50:79]).all())

    def test_ema_ordering_on_uptrend(self):
        df = indicators.add_indicators(_trend_frame())
        self.assertTrue((df["ema_fast"].iloc[60:79]
                         > df["ema_mid"].iloc[60:79]).all())
        self.assertTrue((df["ema_mid"].iloc[60:79]
                         > df["ema_slow"].iloc[60:79]).all())

    def test_long_entries_start_when_slow_ema_valid(self):
        df = _run(_trend_frame())
        self.assertFalse(df["long_entry"].iloc[:49].any())
        self.assertTrue(df["long_entry"].iloc[49])
        self.assertEqual(int(df["long_entry"].sum()), 32)

    def test_short_entries_on_falling_leg(self):
        df = _run(_trend_frame())
        self.assertFalse(df["short_entry"].iloc[:95].any())
        self.assertTrue(df["short_entry"].iloc[95])
        self.assertEqual(int(df["short_entry"].sum()), 65)

    def test_no_long_when_close_below_ema50(self):
        # Falling leg: closes below EMA(50) after the turn, so no
        # long entries appear there despite bullish HA candles early
        # in the leg.
        df = _run(_trend_frame())
        self.assertFalse(df["long_entry"].iloc[100:].any())

    def test_exit_on_ha_flip(self):
        df = pd.DataFrame({
            "ha_close": [101.0, 99.0],
            "ha_open": [100.0, 100.0],
            "ema_fast": [101.0, 101.0],
            "ema_mid": [100.0, 100.0],
            "c": [101.0, 99.0],
            "ema_slow": [99.0, 99.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[0])
        self.assertTrue(out["long_exit"].iloc[1])  # HA flipped bearish

    def test_exit_on_ema_cross_against(self):
        # HA still bullish, but EMA(9) drops below EMA(21): long exits.
        df = pd.DataFrame({
            "ha_close": [101.0, 102.0],
            "ha_open": [100.0, 100.0],
            "ema_fast": [101.0, 99.0],
            "ema_mid": [100.0, 100.0],
            "c": [101.0, 102.0],
            "ema_slow": [99.0, 99.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_exit"].iloc[1])
        self.assertFalse(out["short_entry"].iloc[1])

    def test_short_exit_on_ha_flip(self):
        df = pd.DataFrame({
            "ha_close": [99.0, 101.0],
            "ha_open": [100.0, 100.0],
            "ema_fast": [99.0, 99.0],
            "ema_mid": [100.0, 100.0],
            "c": [99.0, 101.0],
            "ema_slow": [101.0, 101.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["short_entry"].iloc[0])
        self.assertTrue(out["short_exit"].iloc[1])  # HA flipped bullish

    def test_flat_frame_no_entries(self):
        df = _run(_flat_frame())
        # HA close == HA open on a flat frame (doji), so no entries.
        self.assertTrue((df["ha_close"] == df["ha_open"]).iloc[10:].all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["ema_fast"].iloc[:8].isna().all())
        self.assertTrue(df["ema_mid"].iloc[:20].isna().all())
        self.assertTrue(df["ema_slow"].iloc[:49].isna().all())
        self.assertFalse(np.isnan(df["ema_slow"].iloc[49]))
        self.assertFalse(df["ha_open"].isna().any())

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
        for col in ("ha_open", "ha_close", "ema_fast", "ema_slow",
                    "long_entry", "short_entry", "long_exit"):
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
