"""Ergodic oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ergodic_indicator import indicators, risk, signals
from strategies import base as B
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


def _manual_ema(values, n):
    """pandas ewm(span=n, adjust=False, min_periods=n), reimplemented
    by hand: NaN inputs are skipped without resetting the recursion,
    output is NaN until n non-NaN inputs have been seen."""
    alpha = 2.0 / (n + 1)
    out = [float("nan")] * len(values)
    prev = None
    count = 0
    for i, x in enumerate(values):
        if x is None or (isinstance(x, float) and np.isnan(x)):
            continue
        count += 1
        prev = x if prev is None else alpha * x + (1.0 - alpha) * prev
        if count >= n:
            out[i] = prev
    return out


class TestErgodicIndicator(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ergodic_indicator", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_ergodic_converges_to_100_on_steady_rise(self):
        # Constant +1 momentum: PC -> 1, APC -> 1, ergodic -> 100.
        closes = 100.0 + np.arange(600, dtype=float)
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["ergodic"].iloc[-1], 100.0, delta=0.5)

    def test_ergodic_converges_to_minus_100_on_steady_fall(self):
        # Constant -1 momentum: ergodic -> -100.
        closes = 700.0 - np.arange(600, dtype=float)
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["ergodic"].iloc[-1], -100.0, delta=0.5)

    def test_ergodic_hand_computed(self):
        # Full double-EMA pipeline recomputed by hand on a random walk.
        rng = np.random.default_rng(5)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 300)))
        df = indicators.add_indicators(_frame(closes))
        m = np.diff(closes, prepend=np.nan)
        pc = _manual_ema(_manual_ema(m, 25), 13)
        apc = _manual_ema(_manual_ema(np.abs(m), 25), 13)
        for i in (100, 200, 299):
            expected = 100.0 * pc[i] / apc[i]
            self.assertAlmostEqual(df["ergodic"].iloc[i], expected, places=6)

    def test_signal_line_is_ema7(self):
        # The signal line is EMA(7) of the ergodic line.
        df = indicators.add_indicators(_random_walk_frame(n=400))
        pd.testing.assert_series_equal(
            df["ergodic_signal"], B.ema(df["ergodic"], 7),
            check_names=False)

    def test_bounded(self):
        # |ergodic| <= 100 everywhere it is finite (denominator >=
        # |numerator| by construction).
        df = indicators.add_indicators(_random_walk_frame(n=1500))
        vals = df["ergodic"].dropna()
        self.assertTrue(((vals >= -100.0) & (vals <= 100.0)).all())

    def test_crosses_fire_on_swinging_market(self):
        # A slow sine-wave price produces repeated ergodic/signal
        # crosses in both directions.
        i = np.arange(1500, dtype=float)
        closes = 100.0 + 10.0 * np.sin(2.0 * np.pi * i / 200.0)
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[100:].any())
        self.assertTrue(df["short_entry"].iloc[100:].any())

    def test_signal_logic_crafted_rows(self):
        rows = [
            dict(ergodic=-5.0, ergodic_signal=0.0),
            dict(ergodic=5.0, ergodic_signal=0.0),
            dict(ergodic=-5.0, ergodic_signal=0.0),
        ]
        df = signals.add_signals(pd.DataFrame(rows))
        # Row 1: cross above -> long entry + short exit.
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Row 2: cross below -> short entry + long exit.
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[2])
        # NaN lines (warmup): no entry, no exit.
        df = signals.add_signals(pd.DataFrame(
            [dict(ergodic=np.nan, ergodic_signal=np.nan)]))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_no_signal_on_flat(self):
        # Flat price -> momentum 0 -> ergodic 0, signal 0: no crosses.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["ergodic"], 0.0, atol=1e-12))

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
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("ergodic", "ergodic_signal", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): same flat behaviour.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
