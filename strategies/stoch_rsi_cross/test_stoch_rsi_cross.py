"""Stochastic RSI Crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stoch_rsi_cross import indicators, risk, signals
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


class TestStochRsiCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("stoch_rsi_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_flat_frame_scores_50(self):
        # Flat closes: RSI is 0 everywhere (no gains), so the RSI
        # window has zero range -> %K = 50, %D = 50.
        df = indicators.add_indicators(_frame([100.0] * 200))
        self.assertAlmostEqual(df["rsi14"].iloc[100], 0.0, places=6)
        self.assertAlmostEqual(df["stoch_k"].iloc[100], 50.0, places=6)
        self.assertAlmostEqual(df["stoch_d"].iloc[100], 50.0, places=6)

    def test_stoch_k_matches_formula(self):
        # Independent recomputation of %K from the RSI column.
        df0 = _random_walk_frame()
        df = indicators.add_indicators(df0)
        rsi = df["rsi14"]
        lo = rsi.rolling(14, min_periods=14).min()
        hi = rsi.rolling(14, min_periods=14).max()
        expected = 100.0 * (rsi - lo) / (hi - lo)
        expected = expected.where((hi - lo) > 0, 50.0)
        for i in (50, 200, 1000):
            self.assertAlmostEqual(df["stoch_k"].iloc[i],
                                   expected.iloc[i], places=8)

    def test_d_is_sma3_of_k(self):
        df = indicators.add_indicators(_random_walk_frame())
        expected = df["stoch_k"].rolling(3, min_periods=3).mean()
        for i in (50, 200, 1000):
            self.assertAlmostEqual(df["stoch_d"].iloc[i],
                                   expected.iloc[i], places=8)

    def test_k_range(self):
        df = indicators.add_indicators(_random_walk_frame())
        k = df["stoch_k"].dropna()
        self.assertTrue(((k >= 0) & (k <= 100)).all())

    def test_warmup_nans(self):
        # B.rsi fills its pre-window values (0.0), so RSI is defined
        # from bar 0 and %K is first defined once its 14-bar RSI
        # window is full (bar 13); %D needs 3 %K values (bar 15).
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["stoch_k"].iloc[:13].isna().all())
        self.assertFalse(np.isnan(df["stoch_k"].iloc[13]))
        self.assertTrue(df["stoch_d"].iloc[:15].isna().all())
        self.assertFalse(np.isnan(df["stoch_d"].iloc[15]))

    def test_long_entry_cross_up_below_20(self):
        df = pd.DataFrame({
            "stoch_k": [10.0, 11.0, 15.0, 25.0],
            "stoch_d": [12.0, 12.0, 12.0, 12.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[2])   # 15 > 12, was below, k < 20
        self.assertFalse(out["long_entry"].iloc[3])  # k=25 not < 20
        self.assertFalse(out["short_entry"].any())

    def test_short_entry_cross_down_above_80(self):
        df = pd.DataFrame({
            "stoch_k": [90.0, 89.0, 85.0, 75.0],
            "stoch_d": [88.0, 88.0, 88.0, 88.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["short_entry"].iloc[2])  # 85 < 88, was above, k > 80
        self.assertFalse(out["short_entry"].iloc[3])  # k=75 not > 80

    def test_no_entry_when_cross_outside_zone(self):
        df = pd.DataFrame({
            "stoch_k": [40.0, 45.0, 55.0, 60.0],
            "stoch_d": [50.0, 50.0, 50.0, 50.0],
        })
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].any())
        self.assertTrue(out["short_exit"].iloc[2])  # cross up exits a short

    def test_exit_is_opposite_cross(self):
        df = pd.DataFrame({
            "stoch_k": [10.0, 20.0, 11.0, 5.0],
            "stoch_d": [12.0, 12.0, 12.0, 12.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_exit"].iloc[2])   # k crosses down thru d
        self.assertTrue(out["short_exit"].iloc[1])  # k crosses up thru d
        self.assertFalse(out["long_entry"].iloc[1])  # k=20 not < 20

    def test_random_walk_produces_entries(self):
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
        for col in ("stoch_k", "stoch_d", "rsi14",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["stoch_k"].isna().all())


if __name__ == "__main__":
    unittest.main()
