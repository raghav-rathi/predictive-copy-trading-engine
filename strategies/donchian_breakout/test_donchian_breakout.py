"""Donchian Channel Breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian_breakout import indicators, risk, signals
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


def _breakout_frame():
    """30 flat bars at 100 (h 101 / l 99), 10 bars at 105, 10 at 95."""
    closes = [100.0] * 30 + [105.0] * 10 + [95.0] * 10
    return _frame(closes, highs=[c + 1 for c in closes],
                  lows=[c - 1 for c in closes])


class TestDonchianBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("donchian_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_channel_math_hand_computed(self):
        # Rising closes 100..139, highs = closes, lows = closes - 1.
        closes = list(range(100, 140))
        df = indicators.add_indicators(
            _frame(closes, highs=closes, lows=[c - 1 for c in closes]))
        # At bar 20 the prior-20 highs are bars 0..19 = 100..119.
        self.assertAlmostEqual(df["dc_upper"].iloc[20], 119.0)
        # At bar 39 the prior-20 highs are bars 19..38 = 119..138.
        self.assertAlmostEqual(df["dc_upper"].iloc[39], 138.0)
        # Prior-20 lows at bar 20 are bars 0..19 = 99..118.
        self.assertAlmostEqual(df["dc_lower"].iloc[20], 99.0)
        # Prior-10 lows at bar 20 are bars 10..19 = 109..118.
        self.assertAlmostEqual(df["exit_low"].iloc[20], 109.0)
        # Prior-10 highs at bar 20 are bars 10..19 = 110..119.
        self.assertAlmostEqual(df["exit_high"].iloc[20], 119.0)
        self.assertAlmostEqual(df["dc_mid"].iloc[20], (119.0 + 99.0) / 2)

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["dc_upper"].iloc[:20].isna().all())
        self.assertTrue(df["dc_lower"].iloc[:20].isna().all())
        self.assertFalse(np.isnan(df["dc_upper"].iloc[20]))
        self.assertFalse(np.isnan(df["exit_low"].iloc[10]))
        self.assertTrue(df["exit_low"].iloc[:10].isna().all())

    def test_long_entry_on_breakout(self):
        df = _run(_breakout_frame())
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["long_exit"].iloc[30])

    def test_short_entry_on_breakdown(self):
        df = _run(_breakout_frame())
        self.assertTrue(df["short_entry"].iloc[40])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_turtle_10bar_exit(self):
        # Close below the prior-10-bar low but still above the
        # 20-bar low: the Turtle exit fires on its own.
        df = pd.DataFrame({
            "c": [100.0, 94.0, 89.0],
            "dc_upper": [110.0, 110.0, 110.0],
            "dc_lower": [90.0, 90.0, 90.0],
            "exit_low": [95.0, 95.0, 95.0],
            "exit_high": [105.0, 105.0, 105.0],
        })
        out = signals.add_signals(df)
        self.assertFalse(out["long_exit"].iloc[0])
        self.assertTrue(out["long_exit"].iloc[1])  # Turtle 10-bar exit
        self.assertTrue(out["long_exit"].iloc[2])  # opposite extreme
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].iloc[1])

    def test_short_exit_mirror(self):
        df = pd.DataFrame({
            "c": [100.0, 106.0, 111.0],
            "dc_upper": [110.0, 110.0, 110.0],
            "dc_lower": [90.0, 90.0, 90.0],
            "exit_low": [95.0, 95.0, 95.0],
            "exit_high": [105.0, 105.0, 105.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["short_exit"].iloc[1])  # Turtle 10-bar exit
        self.assertTrue(out["short_exit"].iloc[2])  # opposite extreme

    def test_no_entry_on_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_entry_fires_once_while_above_channel(self):
        # The 105 leg stays above the channel; the transition fires
        # exactly once (bar 30), not on every bar of the leg.
        df = _run(_breakout_frame())
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["long_entry"].iloc[31:40].any())

    def test_atr_on_flat_frame(self):
        # h - l = 2 on a flat frame, so Wilder ATR(14) is 2.0.
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["atr"].iloc[100], 2.0, places=6)

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
        self.assertEqual(risk.WARMUP, 40)

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
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("dc_upper", "dc_lower", "exit_low", "exit_high",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["dc_upper"].isna().all())


if __name__ == "__main__":
    unittest.main()
