"""Fibonacci time zones tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fibonacci_time_zones import indicators, risk, signals
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


def _fib_frame(dip_close=110.5, reclaim_close=115.5, end_bar=80):
    """Bullish Fib time-zone setup.

    Bars 0-59: steady rise 90 -> 119.5 (swing high centre 59,
        confirmed bar 61). Bars 60-66: dip to a swing low at
        centre 66 (low 105.5, confirmed bar 68) — the anchor.
    Zone counts after anchor 66: 74 (+8), 79 (+13), 87, 100.
    Zone window 73-75: bar 73 dips (close 110.5 < EMA(20) ~112.5),
    bar 74 reclaims (close 115.5 > EMA(20) ~112.8, previous close
    below its EMA(20), close > EMA(50) ~110.1) -> long entry at
    bar 74. Bars 75-80 drift up; no second trigger.
    """
    closes, highs, lows = [], [], []
    for i in range(60):
        c = 90.0 + 0.5 * i
        closes.append(c)
        highs.append(c + 0.5)
        lows.append(c - 0.5)
    for c in [118.0, 116.0, 114.0, 112.0, 110.0, 108.0, 106.5]:
        closes.append(c)
        highs.append(c + 0.5)
        lows.append(c - 0.5)
    lows[66] = 105.5
    highs[66] = 107.5
    for c in [108.0, 110.0, 112.0, 113.0, 114.0, 115.0]:
        closes.append(c)
        highs.append(c + 0.5)
        lows.append(c - 0.5)
    closes.append(dip_close)
    highs.append(dip_close + 0.5)
    lows.append(dip_close - 1.0)
    closes.append(reclaim_close)
    highs.append(reclaim_close + 0.5)
    lows.append(reclaim_close - 1.0)
    closes.append(117.0)
    highs.append(117.5)
    lows.append(116.5)
    for c in [118.0, 119.0, 120.0, 121.0, 122.0]:
        closes.append(c)
        highs.append(c + 0.5)
        lows.append(c - 0.5)
    return _frame(closes[:end_bar + 1], highs=highs[:end_bar + 1],
                  lows=lows[:end_bar + 1])


def _mirror_frame(df):
    """Reflect prices about 100: bullish setup becomes bearish."""
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


class TestFibonacciTimeZones(unittest.TestCase):
    def test_registered(self):
        self.assertIn("fibonacci_time_zones", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_anchor_reanchors_on_new_swing(self):
        df = indicators.add_indicators(_fib_frame())
        # Swing high at centre 59 anchors first (confirmed bar 61).
        self.assertEqual(df["anchor_kind"].iloc[64], -1)
        self.assertAlmostEqual(df["anchor_bar"].iloc[64], 59.0)
        # Swing low at centre 66 re-anchors (confirmed bar 68).
        self.assertEqual(df["anchor_kind"].iloc[68], 1)
        self.assertAlmostEqual(df["anchor_bar"].iloc[68], 66.0)
        self.assertAlmostEqual(df["anchor_low"].iloc[68], 105.5)

    def test_zone_windows(self):
        df = indicators.add_indicators(_fib_frame())
        # Anchor 66: +8 zone window is bars 73-75; +13 is 78-80.
        self.assertFalse(df["in_zone"].iloc[72])
        self.assertTrue(df["in_zone"].iloc[73])
        self.assertTrue(df["in_zone"].iloc[74])
        self.assertTrue(df["in_zone"].iloc[75])
        self.assertFalse(df["in_zone"].iloc[76])
        self.assertFalse(df["in_zone"].iloc[77])
        self.assertTrue(df["in_zone"].iloc[79])

    def test_long_trigger_on_reclaim_inside_zone(self):
        df = _run(_fib_frame())
        self.assertFalse(df["long_entry"].iloc[:74].any())
        self.assertTrue(df["long_entry"].iloc[74])
        self.assertFalse(df["short_entry"].iloc[74])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_bear_short_trigger_on_mirrored_frame(self):
        df = _run(_mirror_frame(_fib_frame()))
        self.assertFalse(df["short_entry"].iloc[:74].any())
        self.assertTrue(df["short_entry"].iloc[74])
        self.assertFalse(df["long_entry"].iloc[74])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_no_entry_without_pullback_cross_in_zone(self):
        # Bar 73 stays above EMA(20) (close 115.5) and bar 74 too,
        # so no cross back above EMA(20) lands inside the window.
        df = _run(_fib_frame(dip_close=115.5, reclaim_close=116.5))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_when_reclaim_lands_outside_zone(self):
        # Dip on bars 73-74, still below EMA(20) on bar 75, reclaim
        # only on bar 76 — outside the 73-75 window, so no trade.
        df0 = _fib_frame()
        closes = list(df0["c"])
        highs = list(df0["h"])
        lows = list(df0["l"])
        closes[73] = 110.5
        closes[74] = 111.0
        closes[75] = 111.5
        closes[76] = 116.0
        for i in (73, 74, 75, 76):
            highs[i] = closes[i] + 0.5
            lows[i] = closes[i] - 0.5
        df = _run(_frame(closes[:77], highs=highs[:77], lows=lows[:77]))
        self.assertFalse(df["long_entry"].any())

    def test_exit_long_below_anchor_low(self):
        rows = pd.DataFrame([dict(
            c=105.0, long_trigger=False, short_trigger=False,
            anchor_low=106.0, anchor_high=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=110.0, long_trigger=False, short_trigger=True,
            anchor_low=106.0, anchor_high=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(
            c=121.0, long_trigger=False, short_trigger=False,
            anchor_low=106.0, anchor_high=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

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
        for col in ("ema20", "anchor_bar", "anchor_kind", "in_zone",
                    "fib_state", "long_entry", "short_entry", "long_exit"):
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
