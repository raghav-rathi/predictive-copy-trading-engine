"""Raschke 3-bar triangle tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.three_bar_triangle import indicators, risk, signals
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


def _triangle_frame(break_vol=200.0, break_close=111.0):
    """25 flat bars (vol 100, h 110, l 90, c 100), contraction bar 25
    (h 108 < 110, l 92 > 90 -> triangle 108/92), breakout bar 26
    with close 111 and volume 200 (> 1.25x vol_ma20 ~100)."""
    closes = [100.0] * 25 + [100.0, break_close]
    highs = [110.0] * 25 + [108.0, 112.0]
    lows = [90.0] * 25 + [92.0, 105.0]
    vols = [100.0] * 25 + [100.0, break_vol]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


class TestThreeBarTriangle(unittest.TestCase):
    def test_registered(self):
        self.assertIn("three_bar_triangle", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_contraction_definition(self):
        df = indicators.add_indicators(_triangle_frame())
        self.assertFalse(df["contraction"].iloc[:25].any())
        self.assertTrue(df["contraction"].iloc[25])
        self.assertFalse(df["contraction"].iloc[26])

    def test_triangle_levels(self):
        df = indicators.add_indicators(_triangle_frame())
        self.assertAlmostEqual(df["tri_high"].iloc[25], 110.0)
        self.assertAlmostEqual(df["tri_low"].iloc[25], 90.0)
        # Levels persist into the breakout bar.
        self.assertAlmostEqual(df["tri_high"].iloc[26], 110.0)
        self.assertAlmostEqual(df["tri_low"].iloc[26], 90.0)

    def test_triangle_expiry_after_five_bars(self):
        closes = [100.0] * 32
        # Bars 26..31 print highs of 112, so none of them is a
        # contraction (112 is not below the prior two bars' high).
        highs = [110.0] * 25 + [108.0] + [112.0] * 6
        lows = [90.0] * 25 + [92.0] + [95.0] * 6
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        # Valid on bars 25..30 (contraction + 5), NaN from bar 31.
        self.assertFalse(np.isnan(df["tri_high"].iloc[30]))
        self.assertTrue(np.isnan(df["tri_high"].iloc[31]))
        self.assertTrue(np.isnan(df["tri_low"].iloc[31]))

    def test_long_entry_on_volume_breakout(self):
        df = _run(_triangle_frame())
        self.assertFalse(df["long_entry"].iloc[:26].any())
        self.assertTrue(df["long_entry"].iloc[26])
        self.assertFalse(df["short_entry"].iloc[26])

    def test_no_entry_without_volume_expansion(self):
        df = _run(_triangle_frame(break_vol=110.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_breakout(self):
        # Close stays inside the triangle despite high volume.
        df = _run(_triangle_frame(break_vol=200.0, break_close=105.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_after_window_expires(self):
        # Breakout 6 bars after the contraction: triangle expired.
        # Bars 26..30 print highs of 112, so no fresh contraction
        # restarts the window.
        closes = [100.0] * 25 + [100.0] + [100.0] * 5 + [111.0]
        highs = [110.0] * 25 + [108.0] + [112.0] * 5 + [112.0]
        lows = [90.0] * 25 + [92.0] + [95.0] * 5 + [105.0]
        vols = [100.0] * 31 + [200.0]
        df = _run(_frame(closes, highs=highs, lows=lows, vols=vols))
        self.assertFalse(df["long_entry"].any())

    def test_short_entry_mirror(self):
        closes = [100.0] * 25 + [100.0, 89.0]
        highs = [110.0] * 25 + [108.0, 95.0]
        lows = [90.0] * 25 + [92.0, 88.0]
        vols = [100.0] * 25 + [100.0, 200.0]
        df = _run(_frame(closes, highs=highs, lows=lows, vols=vols))
        self.assertTrue(df["short_entry"].iloc[26])
        self.assertFalse(df["long_entry"].iloc[26])

    def test_new_contraction_restarts_triangle(self):
        # Second contraction at bar 28 replaces the first triangle.
        closes = [100.0] * 25 + [100.0, 100.0, 100.0, 100.0]
        highs = [110.0] * 25 + [108.0, 105.0, 104.0, 103.0]
        lows = [90.0] * 25 + [92.0, 95.0, 96.0, 97.0]
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["contraction"].iloc[28])
        # Triangle from bars 26..28: high 105, low 95.
        self.assertAlmostEqual(df["tri_high"].iloc[28], 105.0)
        self.assertAlmostEqual(df["tri_low"].iloc[28], 95.0)

    def test_vol_ma20(self):
        df = indicators.add_indicators(_flat_frame(n=30, vol=100.0))
        self.assertAlmostEqual(df["vol_ma20"].iloc[19], 100.0)
        self.assertTrue(np.isnan(df["vol_ma20"].iloc[18]))

    def test_exit_long_on_failed_breakout(self):
        rows = pd.DataFrame([dict(
            c=89.0, tri_high=110.0, tri_low=90.0, v=200.0, vol_ma20=100.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])

    def test_exit_short_on_breakout(self):
        rows = pd.DataFrame([dict(
            c=111.0, tri_high=110.0, tri_low=90.0, v=200.0, vol_ma20=100.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])

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
        for col in ("contraction", "tri_high", "vol_ma20", "long_entry",
                    "short_entry", "long_exit"):
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
