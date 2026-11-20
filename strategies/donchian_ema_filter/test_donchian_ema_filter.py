"""Donchian EMA filter tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies import registry
from strategies.backtest import run_backtest
from strategies.donchian_ema_filter import indicators, risk, signals


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


def _breakout_long_frame():
    """60 bars flat at 100, then a close at 102 (above the prior
    20-bar high of 100.5 and above EMA(50) ~100). Long entry at bar 60."""
    return _frame([100.0] * 60 + [102.0, 102.0, 101.0])


def _breakout_short_frame():
    """Mirror: 60 bars flat at 100, then a close at 98, 10 bars at 99,
    then a close at 101 (above the prior 10-bar high of 99.5).
    Short entry at bar 60, short exit at bar 71."""
    return _frame([100.0] * 60 + [98.0] + [99.0] * 10 + [101.0])


class TestDonchianEmaFilter(unittest.TestCase):
    def test_registered(self):
        self.assertIn("donchian_ema_filter", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_donchian_levels_use_previous_bars_only(self):
        # Flat at 100 (h=100.5, l=99.5): from bar 20 the prior-20-bar
        # levels are 100.5 / 99.5, and they are NaN before bar 20.
        df = indicators.add_indicators(_frame([100.0] * 30))
        self.assertTrue(df["donchian_upper"].iloc[:20].isna().all())
        self.assertTrue(df["donchian_lower"].iloc[:20].isna().all())
        self.assertAlmostEqual(df["donchian_upper"].iloc[20], 100.5)
        self.assertAlmostEqual(df["donchian_lower"].iloc[20], 99.5)
        self.assertAlmostEqual(df["donchian_upper"].iloc[29], 100.5)

    def test_donchian_level_excludes_current_bar(self):
        # A spike bar's own high must not raise the level on its own bar.
        closes = [100.0] * 25 + [110.0]
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["donchian_upper"].iloc[25], 100.5)

    def test_ema_50_flat_series(self):
        df = indicators.add_indicators(_frame([100.0] * 60))
        self.assertTrue(df["ema_50"].iloc[:49].isna().all())
        self.assertAlmostEqual(df["ema_50"].iloc[59], 100.0)

    def test_ema_50_matches_base_ema(self):
        df = indicators.add_indicators(_random_walk_frame(n=200))
        expected = B.ema(df["c"], 50)
        pd.testing.assert_series_equal(df["ema_50"], expected, check_names=False)

    def test_long_entry_on_breakout_above_ema(self):
        df = _run(_breakout_long_frame())
        self.assertAlmostEqual(df["donchian_upper"].iloc[60], 100.5)
        self.assertGreater(df["c"].iloc[60], df["ema_50"].iloc[60])
        self.assertTrue(df["long_entry"].iloc[60])
        self.assertFalse(df["long_entry"].iloc[:60].any())
        self.assertFalse(df["short_entry"].iloc[60])

    def test_short_entry_on_breakdown_below_ema(self):
        df = _run(_breakout_short_frame())
        self.assertTrue(df["short_entry"].iloc[60])
        self.assertFalse(df["short_entry"].iloc[:60].any())
        self.assertFalse(df["long_entry"].iloc[60])

    def test_ema_filter_blocks_breakout(self):
        # Decline 120 -> 100, flat at 100, then a jump to 102: above
        # the prior 20-bar high (100.5) but still below EMA(50)
        # (~103.8), so no long entry.
        closes = np.concatenate([np.linspace(120, 100, 50),
                                 [100.0] * 20, [102.0]])
        df = _run(_frame(closes))
        self.assertGreater(df["c"].iloc[70], df["donchian_upper"].iloc[70])
        self.assertLess(df["c"].iloc[70], df["ema_50"].iloc[70])
        self.assertFalse(df["long_entry"].iloc[70])
        self.assertFalse(df["long_entry"].any())

    def test_ema_filter_direct(self):
        rows = pd.DataFrame({
            "c": [102.0, 102.0],
            "donchian_upper": [100.5, 100.5],
            "donchian_lower": [99.5, 99.5],
            "ema_50": [103.0, 100.0],
            "exit_low_10": [99.0, 99.0],
            "exit_high_10": [103.0, 103.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])  # below EMA: blocked
        self.assertTrue(df["long_entry"].iloc[1])   # above EMA: fires

    def test_long_exit_below_prior_10bar_low(self):
        # Breakout at 60, 10 bars at 101, then a close at 99 (below
        # the prior 10-bar low of 100.5): long exit at bar 71.
        closes = [100.0] * 60 + [102.0] + [101.0] * 10 + [99.0]
        df = _run(_frame(closes))
        self.assertAlmostEqual(df["exit_low_10"].iloc[71], 100.5)
        self.assertTrue(df["long_exit"].iloc[71])
        self.assertFalse(df["long_exit"].iloc[:71].any())

    def test_short_exit_above_prior_10bar_high(self):
        df = _run(_breakout_short_frame())
        self.assertAlmostEqual(df["exit_high_10"].iloc[71], 99.5)
        self.assertTrue(df["short_exit"].iloc[71])

    def test_no_entry_on_close_exactly_at_level(self):
        # Close exactly at the prior 20-bar high is not a breakout.
        df = _run(_frame([100.0] * 60 + [100.5]))
        self.assertFalse(df["long_entry"].iloc[60])
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_on_flat_frame(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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
        for col in ("donchian_upper", "donchian_lower", "ema_50",
                    "exit_low_10", "exit_high_10", "long_entry",
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
