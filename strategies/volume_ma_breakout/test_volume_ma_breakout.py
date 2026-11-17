"""Volume MA Breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.volume_ma_breakout import indicators, risk, signals
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


def _long_breakout_frame():
    """20 quiet bars (vol 100, high 110, low 90, close 100), then a
    breakout bar: new high 120, vol 160 (1.6x mean), close 115."""
    closes = [100.0] * 20 + [115.0]
    highs = [110.0] * 20 + [120.0]
    lows = [90.0] * 20 + [91.0]
    vols = [100.0] * 20 + [160.0]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


def _short_breakout_frame():
    """Mirror: 20 quiet bars, then a breakdown bar: new low 80,
    vol 160 (1.6x mean), close 85."""
    closes = [100.0] * 20 + [85.0]
    highs = [110.0] * 20 + [109.0]
    lows = [90.0] * 20 + [80.0]
    vols = [100.0] * 20 + [160.0]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


class TestVolumeMaBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("volume_ma_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_long_breakout_exact(self):
        df = indicators.add_indicators(_long_breakout_frame())
        last = df.iloc[-1]
        self.assertAlmostEqual(last["vol_mean_20"], 100.0)
        self.assertAlmostEqual(last["vol_ratio"], 1.6)
        self.assertEqual(last["high_20"], 120.0)
        self.assertTrue(last["long_breakout"])
        self.assertFalse(last["short_breakout"])
        self.assertFalse(df["long_breakout"].iloc[:-1].any())
        self.assertFalse(df["short_breakout"].iloc[:-1].any())

    def test_short_breakout_exact(self):
        df = indicators.add_indicators(_short_breakout_frame())
        last = df.iloc[-1]
        self.assertAlmostEqual(last["vol_ratio"], 1.6)
        self.assertEqual(last["low_20"], 80.0)
        self.assertTrue(last["short_breakout"])
        self.assertFalse(last["long_breakout"])

    def test_entries_fire_on_breakout_frames(self):
        df = _run(_long_breakout_frame())
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])
        df = _run(_short_breakout_frame())
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_breakout_without_volume(self):
        # New high but volume only 1.2x mean: no breakout.
        df = indicators.add_indicators(_frame(
            [100.0] * 20 + [115.0], highs=[110.0] * 20 + [120.0],
            lows=[90.0] * 20 + [91.0], vols=[100.0] * 20 + [120.0]))
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 1.2)
        self.assertFalse(df["long_breakout"].iloc[-1])

    def test_volume_threshold_strict(self):
        # Exactly 1.5x mean volume is NOT a breakout (strict >).
        df = indicators.add_indicators(_frame(
            [100.0] * 20 + [115.0], highs=[110.0] * 20 + [120.0],
            lows=[90.0] * 21, vols=[100.0] * 20 + [150.0]))
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 1.5)
        self.assertFalse(df["long_breakout"].iloc[-1])

    def test_no_breakout_without_new_extreme(self):
        # Volume spike but high 105, below the 20-bar high of 110,
        # and low 91, above the 20-bar low of 90: no breakout either way.
        df = indicators.add_indicators(_frame(
            [100.0] * 20 + [104.0], highs=[110.0] * 20 + [105.0],
            lows=[90.0] * 20 + [91.0], vols=[100.0] * 20 + [300.0]))
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 3.0)
        self.assertFalse(df["long_breakout"].iloc[-1])
        self.assertFalse(df["short_breakout"].iloc[-1])

    def test_vol_mean_excludes_current_bar(self):
        # A huge current-bar spike must not dilute its own mean:
        # mean of previous 20 bars is 100 even with vol 1000 now.
        df = indicators.add_indicators(_frame(
            [100.0] * 20 + [115.0], highs=[110.0] * 20 + [120.0],
            lows=[90.0] * 21, vols=[100.0] * 20 + [1000.0]))
        self.assertAlmostEqual(df["vol_mean_20"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 10.0)

    def test_long_exit_exact(self):
        # 10 bars with low 90, then a bar closing at 89 -> long exit.
        df = _run(_frame([100.0] * 10 + [89.0],
                         highs=[101.0] * 11, lows=[90.0] * 10 + [88.0]))
        self.assertAlmostEqual(df["low_10_prev"].iloc[-1], 90.0)
        self.assertTrue(df["long_exit"].iloc[-1])
        self.assertFalse(df["short_exit"].iloc[-1])

    def test_short_exit_exact(self):
        # 10 bars with high 110, then a bar closing at 111 -> short exit.
        df = _run(_frame([100.0] * 10 + [111.0],
                         highs=[110.0] * 10 + [112.0], lows=[99.0] * 11))
        self.assertAlmostEqual(df["high_10_prev"].iloc[-1], 110.0)
        self.assertTrue(df["short_exit"].iloc[-1])
        self.assertFalse(df["long_exit"].iloc[-1])

    def test_exit_uses_prior_bars_only(self):
        # Current bar's own low (85) is below the prior 10-bar low
        # (90), but the close (95) is above it: no long exit.
        df = _run(_frame([100.0] * 10 + [95.0],
                         highs=[101.0] * 11, lows=[90.0] * 10 + [85.0]))
        self.assertAlmostEqual(df["low_10_prev"].iloc[-1], 90.0)
        self.assertFalse(df["long_exit"].iloc[-1])
        # Close exactly at the prior 10-bar low: no exit (strict <).
        df = _run(_frame([100.0] * 10 + [90.0],
                         highs=[101.0] * 11, lows=[90.0] * 11))
        self.assertFalse(df["long_exit"].iloc[-1])

    def test_no_exit_without_10_prior_bars(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_signal_logic_crafted_rows(self):
        rows = [dict(long_breakout=True, short_breakout=False,
                     c=100.0, low_10_prev=90.0, high_10_prev=110.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])
        rows = [dict(long_breakout=False, short_breakout=True,
                     c=100.0, low_10_prev=90.0, high_10_prev=110.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_entry"].iloc[0])
        rows = [dict(long_breakout=False, short_breakout=False,
                     c=89.0, low_10_prev=90.0, high_10_prev=110.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

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
        for col in ("long_breakout", "short_breakout", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): no new extreme, no breakout.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100, vols=[1000.0] * 100))
        self.assertFalse(df["long_breakout"].any())
        self.assertFalse(df["short_breakout"].any())


if __name__ == "__main__":
    unittest.main()
