"""EMA cross + session VWAP momentum tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.ema_vwap_momentum import indicators, risk, signals


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


def _day_boundary_frame():
    """6 hourly bars from 2023-12-31 22:00 UTC: bars 0-1 are Dec 31,
    bars 2-5 are Jan 1. Volumes vary so the VWAP is not trivial."""
    t0 = 1704060000000  # 2023-12-31 22:00 UTC
    closes = [100, 101, 102, 103, 104, 105]
    return _frame(closes, highs=[c + 1 for c in closes],
                  lows=[c - 1 for c in closes],
                  vols=[10, 20, 30, 40, 50, 60], t0=t0)


def _flat_then_rise_frame():
    closes = [100] * 30 + [100 + 2 * i for i in range(1, 51)]
    return _frame(closes)


def _flat_then_fall_frame():
    closes = [100] * 30 + [100 - 2 * i for i in range(1, 51)]
    return _frame(closes)


class TestEmaVwapMomentum(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ema_vwap_momentum", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_vwap_equals_tp_on_first_bar_of_day(self):
        df = indicators.add_indicators(_day_boundary_frame())
        # Bar 2 is 2024-01-01 00:00 UTC: VWAP resets to that bar's
        # typical price (102), ignoring the Dec 31 bars.
        self.assertAlmostEqual(df["vwap_day"].iloc[2], 102.0)

    def test_vwap_cumulative_within_day(self):
        df = indicators.add_indicators(_day_boundary_frame())
        # Dec 31: (100*10 + 101*20) / 30.
        self.assertAlmostEqual(df["vwap_day"].iloc[1], 100.6667, places=4)
        # Jan 1: (102*30 + 103*40) / 70.
        self.assertAlmostEqual(df["vwap_day"].iloc[3], 102.5714, places=4)
        # Jan 1, 3 bars in: (102*30 + 103*40 + 104*50) / 120.
        self.assertAlmostEqual(df["vwap_day"].iloc[4], 103.1667, places=4)

    def test_vwap_never_nan(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(df["vwap_day"].isna().any())

    def test_ema_fast_above_slow_on_uptrend(self):
        df = indicators.add_indicators(_flat_then_rise_frame())
        self.assertGreater(df["ema_fast"].iloc[-1], df["ema_slow"].iloc[-1])

    def test_ema_fast_below_slow_on_downtrend(self):
        df = indicators.add_indicators(_flat_then_fall_frame())
        self.assertLess(df["ema_fast"].iloc[-1], df["ema_slow"].iloc[-1])

    def test_ema_warmup_nans(self):
        df = indicators.add_indicators(_flat_then_rise_frame())
        self.assertTrue(np.isnan(df["ema_fast"].iloc[7]))
        self.assertFalse(np.isnan(df["ema_fast"].iloc[8]))
        self.assertTrue(np.isnan(df["ema_slow"].iloc[19]))
        self.assertFalse(np.isnan(df["ema_slow"].iloc[20]))

    def test_long_entry_on_cross_above_vwap(self):
        df = _run(_flat_then_rise_frame())
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_cross_below_vwap(self):
        df = _run(_flat_then_fall_frame())
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertTrue(df["short_entry"].iloc[30])
        self.assertFalse(df["long_entry"].any())

    def test_no_long_entry_when_cross_above_but_below_vwap(self):
        # EMA(9) crosses above EMA(21) on row 1, but the close is
        # below the session VWAP -> no long entry.
        rows = pd.DataFrame([
            dict(ema_fast=99.0, ema_slow=100.0, c=98.0, vwap_day=99.0),
            dict(ema_fast=101.0, ema_slow=100.0, c=98.5, vwap_day=99.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_short_entry_when_cross_below_but_above_vwap(self):
        rows = pd.DataFrame([
            dict(ema_fast=101.0, ema_slow=100.0, c=102.0, vwap_day=101.0),
            dict(ema_fast=99.0, ema_slow=100.0, c=101.5, vwap_day=101.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exit_long_on_vwap_cross_down(self):
        rows = pd.DataFrame([
            dict(ema_fast=101.0, ema_slow=100.0, c=102.0, vwap_day=101.0),
            dict(ema_fast=102.0, ema_slow=100.5, c=100.5, vwap_day=101.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[1])

    def test_exit_long_on_ema_cross_down(self):
        rows = pd.DataFrame([
            dict(ema_fast=101.0, ema_slow=100.0, c=102.0, vwap_day=101.0),
            dict(ema_fast=99.0, ema_slow=100.0, c=102.0, vwap_day=101.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])

    def test_exit_short_on_vwap_cross_up(self):
        rows = pd.DataFrame([
            dict(ema_fast=99.0, ema_slow=100.0, c=98.0, vwap_day=99.0),
            dict(ema_fast=98.0, ema_slow=99.5, c=99.5, vwap_day=99.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["short_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[1])

    def test_no_entry_before_ema_warmup(self):
        # EMA(21) is NaN before bar 20, so no cross can fire earlier.
        df = _run(_random_walk_frame())
        self.assertFalse(df["long_entry"].iloc[:20].any())
        self.assertFalse(df["short_entry"].iloc[:20].any())

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
        for col in ("ema_fast", "ema_slow", "vwap_day",
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
