"""Grid Trading tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.grid_trading import indicators, risk, signals
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


class TestGridTrading(unittest.TestCase):
    def test_registered(self):
        self.assertIn("grid_trading", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_grid_exact_small_window(self):
        # n=5 window: bars 0..4 have highs 110..114, lows 90..94.
        # On bar 4: grid_high=114, grid_low=90, range=24, step=2.4,
        # mid=102, close 95 -> pos=(95-90)/24=0.20833.
        highs = [110.0, 111.0, 112.0, 113.0, 114.0]
        lows = [90.0, 91.0, 92.0, 93.0, 94.0]
        closes = [100.0, 101.0, 102.0, 103.0, 95.0]
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows),
                                       n=5, levels=10)
        self.assertAlmostEqual(df["grid_high"].iloc[4], 114.0)
        self.assertAlmostEqual(df["grid_low"].iloc[4], 90.0)
        self.assertAlmostEqual(df["grid_range"].iloc[4], 24.0)
        self.assertAlmostEqual(df["grid_step"].iloc[4], 2.4)
        self.assertAlmostEqual(df["grid_mid"].iloc[4], 102.0)
        self.assertAlmostEqual(df["grid_pos"].iloc[4], 5.0 / 24.0)
        self.assertTrue(np.isnan(df["grid_high"].iloc[3]))

    def test_grid_pos_bounds(self):
        # Close at the range low -> pos 0; at the range high -> pos 1.
        df = indicators.add_indicators(_frame(
            [90.0] * 250, highs=[110.0] * 250, lows=[90.0] * 250))
        self.assertAlmostEqual(df["grid_pos"].iloc[-1], 0.0)
        df = indicators.add_indicators(_frame(
            [110.0] * 250, highs=[110.0] * 250, lows=[90.0] * 250))
        self.assertAlmostEqual(df["grid_pos"].iloc[-1], 1.0)
        # Midpoint close -> pos 0.5.
        df = indicators.add_indicators(_frame(
            [100.0] * 250, highs=[110.0] * 250, lows=[90.0] * 250))
        self.assertAlmostEqual(df["grid_pos"].iloc[-1], 0.5)

    def test_grid_hand_computed_random(self):
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 300)))
        highs = closes + rng.uniform(0.1, 1.0, 300)
        lows = closes - rng.uniform(0.1, 1.0, 300)
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        gh = pd.Series(highs).rolling(200, min_periods=200).max()
        gl = pd.Series(lows).rolling(200, min_periods=200).min()
        pos_manual = (pd.Series(closes) - gl) / (gh - gl)
        pd.testing.assert_series_equal(
            df["grid_pos"].reset_index(drop=True),
            pos_manual.reset_index(drop=True), check_names=False, atol=1e-12)
        self.assertTrue(((df["grid_pos"].dropna() >= 0.0)
                         & (df["grid_pos"].dropna() <= 1.0)).all())

    def test_signal_logic_crafted_rows(self):
        # Bottom 20%: long entry, no short entry.
        rows = [dict(c=91.0, grid_pos=0.10, grid_mid=100.0),
                dict(c=92.0, grid_pos=0.15, grid_mid=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Top 20%: short entry.
        rows = [dict(c=109.0, grid_pos=0.90, grid_mid=100.0),
                dict(c=108.0, grid_pos=0.85, grid_mid=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        # Exactly 0.20 / 0.80 counts as in the zone (inclusive bounds).
        rows = [dict(c=94.0, grid_pos=0.20, grid_mid=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[0])
        rows = [dict(c=106.0, grid_pos=0.80, grid_mid=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[0])
        # Midpoint: long exit and short exit both fire (each side's
        # exit is evaluated against its own open position).
        rows = [dict(c=100.0, grid_pos=0.50, grid_mid=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        # NaN pos (zero range / warmup): no entry. Exits are based on
        # close vs midpoint, so with c == mid both exits still fire.
        rows = [dict(c=100.0, grid_pos=np.nan, grid_mid=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])

    def test_long_entry_fires_in_bottom_zone(self):
        # 250 bars pinned at the range low: grid_pos = 0, long fires.
        df = _run(_frame([90.0] * 300, highs=[110.0] * 300,
                         lows=[90.0] * 300))
        self.assertTrue(df["long_entry"].iloc[250])
        self.assertFalse(df["short_entry"].iloc[250])

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

    def test_no_lookahead_flat_midpoint(self):
        # Flat close at the range midpoint: pos 0.5, no entries.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("grid_pos", "grid_mid", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): grid_pos NaN, no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        self.assertTrue(df["grid_pos"].iloc[-1] != df["grid_pos"].iloc[-1])
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
