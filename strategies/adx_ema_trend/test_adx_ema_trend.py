"""ADX EMA Trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adx_ema_trend import indicators, risk, signals
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


def _rising_frame(n=300):
    # Flat first (both EMAs seed at the same level), then a steady
    # linear rise: EMA20 crosses above EMA50, +DI dominates, ADX rises.
    closes = [100.0] * 60 + [100.0 + 0.5 * i for i in range(n - 60)]
    return _frame(closes)


def _falling_frame(n=300):
    closes = [250.0] * 60 + [250.0 - 0.5 * i for i in range(n - 60)]
    return _frame(closes)


def _trend_reversal_frame():
    # Flat, rise, dip, rise again: the dip produces a cross down while
    # ADX is strong (short entry), and the second rise produces a
    # cross up while ADX is still strong (long entry). A from-flat
    # single rise does NOT fire: ADX is still NaN at the first cross.
    closes = ([100.0] * 60 + [100.0 + 0.5 * i for i in range(120)]
              + [160.0 - 0.5 * i for i in range(40)]
              + [140.0 + 0.5 * i for i in range(120)])
    return _frame(closes)


class TestAdxEmaTrend(unittest.TestCase):
    def test_registered(self):
        self.assertIn("adx_ema_trend", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_ema_flat_equals_close(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["ema20"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["ema50"].iloc[-1], 100.0)

    def test_ema20_faster_than_ema50_on_rise(self):
        df = indicators.add_indicators(_rising_frame())
        self.assertGreater(df["ema20"].iloc[-1], df["ema50"].iloc[-1])
        self.assertGreater(df["ema20"].iloc[-1], 100.0)

    def test_adx_strong_on_sustained_trend(self):
        df = indicators.add_indicators(_rising_frame())
        last = df.iloc[-1]
        self.assertGreater(last["adx"], 25)
        self.assertGreater(last["plus_di"], last["minus_di"])
        df = indicators.add_indicators(_falling_frame())
        last = df.iloc[-1]
        self.assertGreater(last["adx"], 25)
        self.assertGreater(last["minus_di"], last["plus_di"])

    def test_long_entry_fires_on_rising_series(self):
        df = _run(_trend_reversal_frame())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_fires_on_falling_series(self):
        df = _run(_trend_reversal_frame())
        self.assertTrue(df["short_entry"].any())

    def test_signal_logic_crafted_rows(self):
        # Cross up + ADX 30 + +DI > -DI -> long entry only.
        rows = pd.DataFrame([
            dict(ema20=99.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
            dict(ema20=101.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Cross down + ADX 30 + -DI > +DI -> short entry only.
        rows = pd.DataFrame([
            dict(ema20=101.0, ema50=100.0, adx=30.0, plus_di=10.0, minus_di=20.0),
            dict(ema20=99.0, ema50=100.0, adx=30.0, plus_di=10.0, minus_di=20.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_adx_threshold_strict(self):
        # ADX exactly 25 is NOT strong (strict >).
        rows = pd.DataFrame([
            dict(ema20=99.0, ema50=100.0, adx=25.0, plus_di=20.0, minus_di=10.0),
            dict(ema20=101.0, ema50=100.0, adx=25.0, plus_di=20.0, minus_di=10.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])

    def test_di_direction_required(self):
        # Cross up but -DI dominates -> no long entry.
        rows = pd.DataFrame([
            dict(ema20=99.0, ema50=100.0, adx=30.0, plus_di=10.0, minus_di=20.0),
            dict(ema20=101.0, ema50=100.0, adx=30.0, plus_di=10.0, minus_di=20.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_no_entry_without_cross(self):
        # EMA20 already above EMA50, no cross on bar 1 -> no entry.
        rows = pd.DataFrame([
            dict(ema20=101.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
            dict(ema20=102.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])

    def test_exit_on_cross_below(self):
        rows = pd.DataFrame([
            dict(ema20=101.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
            dict(ema20=99.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

    def test_exit_on_adx_weak(self):
        # No cross, but ADX drops below 20 -> both exits fire (trend dead).
        rows = pd.DataFrame([
            dict(ema20=101.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
            dict(ema20=102.0, ema50=100.0, adx=15.0, plus_di=20.0, minus_di=10.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])

    def test_exit_adx_boundary(self):
        # ADX exactly 20 is NOT weak (strict <).
        rows = pd.DataFrame([
            dict(ema20=101.0, ema50=100.0, adx=30.0, plus_di=20.0, minus_di=10.0),
            dict(ema20=102.0, ema50=100.0, adx=20.0, plus_di=20.0, minus_di=10.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_exit"].iloc[1])

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
        for col in ("ema20", "ema50", "long_entry", "long_exit"):
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
