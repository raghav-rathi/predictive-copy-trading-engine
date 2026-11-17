"""Heikin Ashi + MACD momentum filter tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.heikin_ashi_macd import indicators, risk, signals
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


def _signal_frame(rows):
    return pd.DataFrame(rows)


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


class TestHeikinAshiMacd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("heikin_ashi_macd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_ha_close_exact(self):
        # Single bar o=100, h=110, l=90, c=100 -> HA close (100+110+90+100)/4 = 100.
        df = indicators.add_indicators(_frame([100.0], highs=[110.0], lows=[90.0]))
        self.assertAlmostEqual(df["ha_c"].iloc[0], 100.0)

    def test_ha_open_seed(self):
        # First bar seeds HA-open = (o + c) / 2 = (100 + 100) / 2 = 100.
        df = indicators.add_indicators(_frame([100.0], highs=[110.0], lows=[90.0]))
        self.assertAlmostEqual(df["ha_o"].iloc[0], 100.0)
        # Seed differs when o != c: o=90, c=110 -> seed (90+110)/2 = 100,
        # HA close = (90+120+80+110)/4 = 100.
        df = indicators.add_indicators(_frame(
            [110.0], highs=[120.0], lows=[80.0], opens=[90.0]))
        self.assertAlmostEqual(df["ha_o"].iloc[0], 100.0)
        self.assertAlmostEqual(df["ha_c"].iloc[0], 100.0)

    def test_ha_recursion_exact(self):
        # Bar 0: o=100,h=110,l=90,c=100 -> ha_c=100, ha_o=100.
        # Bar 1: o=100,h=120,l=95,c=115 -> ha_c=107.5, ha_o=(100+100)/2=100,
        #        ha_h=120, ha_l=95.
        # Bar 2: o=115,h=118,l=110,c=112 -> ha_c=113.75,
        #        ha_o=(100+107.5)/2=103.75, ha_h=118, ha_l=103.75.
        df = indicators.add_indicators(_frame(
            [100.0, 115.0, 112.0],
            highs=[110.0, 120.0, 118.0],
            lows=[90.0, 95.0, 110.0],
            opens=[100.0, 100.0, 115.0]))
        self.assertAlmostEqual(df["ha_c"].iloc[1], 107.5)
        self.assertAlmostEqual(df["ha_o"].iloc[1], 100.0)
        self.assertAlmostEqual(df["ha_h"].iloc[1], 120.0)
        self.assertAlmostEqual(df["ha_l"].iloc[1], 95.0)
        self.assertAlmostEqual(df["ha_c"].iloc[2], 113.75)
        self.assertAlmostEqual(df["ha_o"].iloc[2], 103.75)
        self.assertAlmostEqual(df["ha_h"].iloc[2], 118.0)
        self.assertAlmostEqual(df["ha_l"].iloc[2], 103.75)

    def test_ha_high_low_use_ha_values(self):
        # Bar where the raw high/low are inside the HA open/close:
        # o=100,h=101,l=99,c=100 -> ha_c=100, ha_o=100, so ha_h=101, ha_l=99.
        # Second bar: o=100,h=100.5,l=99.5,c=100 -> ha_c=100, ha_o=100,
        # ha_h must be max(100.5, 100, 100) = 100.5.
        df = indicators.add_indicators(_frame(
            [100.0, 100.0], highs=[101.0, 100.5], lows=[99.0, 99.5]))
        self.assertAlmostEqual(df["ha_h"].iloc[0], 101.0)
        self.assertAlmostEqual(df["ha_l"].iloc[0], 99.0)

    def test_macd_columns_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(np.isfinite(df["macd_hist"].iloc[60:]).all())
        self.assertTrue(np.isfinite(df["macd"].iloc[60:]).all())
        self.assertTrue(np.isfinite(df["macd_signal"].iloc[60:]).all())

    def test_signal_logic_crafted_rows(self):
        # Hist crosses up (prev -1 -> 1) + bullish HA -> long entry + short exit.
        rows = [dict(macd_hist=-1.0, ha_o=100.0, ha_c=99.0),
                dict(macd_hist=1.0, ha_o=100.0, ha_c=101.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Hist crosses down (prev 1 -> -1) + bearish HA -> short entry + long exit.
        rows = [dict(macd_hist=1.0, ha_o=100.0, ha_c=101.0),
                dict(macd_hist=-1.0, ha_o=100.0, ha_c=99.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

    def test_long_entry_needs_bullish_ha(self):
        # Hist crosses up but the HA candle is bearish: no long entry.
        # (The short exit still fires on the opposite zero-cross.)
        rows = [dict(macd_hist=-1.0, ha_o=100.0, ha_c=101.0),
                dict(macd_hist=1.0, ha_o=100.0, ha_c=99.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])

    def test_short_entry_needs_bearish_ha(self):
        # Hist crosses down but the HA candle is bullish: no short entry.
        rows = [dict(macd_hist=1.0, ha_o=100.0, ha_c=99.0),
                dict(macd_hist=-1.0, ha_o=100.0, ha_c=101.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])

    def test_no_cross_no_entry(self):
        # Hist stays positive: no zero-cross, no entries, no exits.
        rows = [dict(macd_hist=1.0, ha_o=100.0, ha_c=101.0),
                dict(macd_hist=2.0, ha_o=100.0, ha_c=101.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_entries_fire_on_random_walk(self):
        df = _run(_random_walk_frame())
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertGreater(int(df["short_entry"].sum()), 0)

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
        # Flat closes: MACD hist is 0, no zero-cross, no entries.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("ha_c", "macd_hist", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertEqual(len(df), 10)


if __name__ == "__main__":
    unittest.main()
