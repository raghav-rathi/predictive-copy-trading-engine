"""Supertrend + EMA(200) filter tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.supertrend_ema_filter import indicators, risk, signals
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


def _flat_frame(n=400, close=100.0):
    return _frame([close] * n)


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


def _uptrend_frame(n=600, drift=0.001):
    """Steady uptrend: Supertrend flips up early and stays up; close
    stays above EMA(200) once the EMA is defined."""
    closes = 100.0 * (1.0 + drift) ** np.arange(n)
    return _frame(closes)


class TestSupertrendEmaFilter(unittest.TestCase):
    def test_registered(self):
        self.assertIn("supertrend_ema_filter", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_supertrend_matches_shared_primitive(self):
        # The Supertrend columns must be exactly the shared
        # strategies.base.supertrend(10, 3.0) output.
        df_raw = _random_walk_frame()
        df = indicators.add_indicators(df_raw)
        st = B.supertrend(df_raw["h"], df_raw["l"], df_raw["c"], 10, 3.0)
        pd.testing.assert_series_equal(df["st_line"], st["supertrend"],
                                       check_names=False)
        pd.testing.assert_series_equal(df["st_dir"], st["supertrend_dir"],
                                       check_names=False)

    def test_indicator_ema200_hand_computed(self):
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 400)))
        df = indicators.add_indicators(_frame(closes))
        alpha = 2.0 / (indicators.EMA_N + 1)
        ema_manual = closes[0]
        for x in closes[1:]:
            ema_manual = alpha * x + (1.0 - alpha) * ema_manual
        self.assertAlmostEqual(df["ema_200"].iloc[399], ema_manual, places=8)
        # EMA(200) is NaN before 200 bars: defined from index 199.
        self.assertTrue(np.isnan(df["ema_200"].iloc[198]))
        self.assertFalse(np.isnan(df["ema_200"].iloc[199]))

    def test_flip_up_above_ema_enters_long(self):
        rows = pd.DataFrame([
            dict(st_dir=-1.0, st_dir_prev=-1.0, c=100.0, ema_200=90.0),
            dict(st_dir=1.0, st_dir_prev=-1.0, c=105.0, ema_200=90.0),
            dict(st_dir=1.0, st_dir_prev=1.0, c=106.0, ema_200=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertEqual(list(df["long_entry"]), [False, True, False])
        self.assertFalse(df["short_entry"].any())
        # The flip-up bar is also a short exit.
        self.assertTrue(df["short_exit"].iloc[1])

    def test_flip_up_below_ema_blocked(self):
        # Supertrend flips up but close is below EMA(200): no long.
        rows = pd.DataFrame([
            dict(st_dir=-1.0, st_dir_prev=-1.0, c=80.0, ema_200=90.0),
            dict(st_dir=1.0, st_dir_prev=-1.0, c=85.0, ema_200=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_flip_down_below_ema_enters_short(self):
        rows = pd.DataFrame([
            dict(st_dir=1.0, st_dir_prev=1.0, c=100.0, ema_200=110.0),
            dict(st_dir=-1.0, st_dir_prev=1.0, c=95.0, ema_200=110.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].any())
        self.assertTrue(df["long_exit"].iloc[1])

    def test_flip_down_above_ema_blocked(self):
        rows = pd.DataFrame([
            dict(st_dir=1.0, st_dir_prev=1.0, c=120.0, ema_200=110.0),
            dict(st_dir=-1.0, st_dir_prev=1.0, c=115.0, ema_200=110.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["short_entry"].any())

    def test_exit_not_gated_by_ema(self):
        # Long exit fires on the flip down even when close is still
        # above EMA(200) (filter gates entries only).
        rows = pd.DataFrame([
            dict(st_dir=1.0, st_dir_prev=1.0, c=120.0, ema_200=110.0),
            dict(st_dir=-1.0, st_dir_prev=1.0, c=115.0, ema_200=110.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])

    def test_full_pipeline_uptrend(self):
        df = _run(_uptrend_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue((tail["st_dir"] == 1).all())
        self.assertTrue((tail["c"] > tail["ema_200"]).all())
        # Exactly one long entry: the flip bar (before warmup it may
        # have fired, but at most one flip exists in a clean uptrend).
        self.assertLessEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].any())

    def test_no_signal_flat(self):
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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 400))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("st_line", "st_dir", "ema_200",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:400].reset_index(drop=True),
                df2[col].iloc[:400].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
