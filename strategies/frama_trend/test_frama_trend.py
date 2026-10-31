"""FRAMA trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.frama_trend import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": h, "l": l, "c": closes,
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


def _flat_then_rise_then_fall():
    flat = [100.0] * 30
    rise = [100.0 + i for i in range(1, 21)]   # 101..120
    fall = [120.0 - i for i in range(1, 21)]   # 119..100
    return flat + rise + fall


class TestFramaTrend(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("frama_price", "frama_n1", "frama_n2", "frama_n3",
                    "frama_dim", "frama_alpha", "frama", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_hand_computed_linear_trend(self):
        # h = 100+i, l = 99+i, i = 0..15: N1 = N2 = N3 = 1, so D = 1,
        # alpha = 1, FRAMA(15) = price(15) = (115 + 114) / 2 = 114.5.
        highs = [100.0 + i for i in range(16)]
        lows = [99.0 + i for i in range(16)]
        closes = [(h + l) / 2 for h, l in zip(highs, lows)]
        df = indicators.add_indicators(_frame(closes, highs, lows))
        self.assertAlmostEqual(df["frama_n1"].iloc[15], 1.0)
        self.assertAlmostEqual(df["frama_n2"].iloc[15], 1.0)
        self.assertAlmostEqual(df["frama_n3"].iloc[15], 1.0)
        self.assertAlmostEqual(df["frama_dim"].iloc[15], 1.0)
        self.assertAlmostEqual(df["frama_alpha"].iloc[15], 1.0)
        self.assertAlmostEqual(df["frama"].iloc[15], 114.5)

    def test_flat_series_stays_at_price(self):
        df = indicators.add_indicators(_frame([100.0] * 100))
        self.assertTrue((df["frama"].iloc[40:] == 100.0).all())
        # h/l spread is 1.0, so N1 = N2 = 0.125, N3 = 0.0625, D = 2 and
        # alpha = exp(-4.6) ~= 0.01005 (above the 0.01 clamp floor).
        self.assertTrue(
            ((df["frama_alpha"].iloc[40:] >= 0.01)
             & (df["frama_alpha"].iloc[40:] <= 0.011)).all())

    def test_alpha_and_dim_bounds(self):
        df = indicators.add_indicators(_random_walk_frame())
        a = df["frama_alpha"].iloc[risk.WARMUP:]
        d = df["frama_dim"].iloc[risk.WARMUP:]
        self.assertTrue(((a >= 0.01) & (a <= 1.0)).all())
        self.assertTrue(((d >= 1.0) & (d <= 2.0)).all())

    def test_long_on_rise_short_on_fall(self):
        df = _run(_frame(_flat_then_rise_then_fall()))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["short_entry"].any())
        self.assertLess(df.index[df["long_entry"]][0],
                        df.index[df["short_entry"]][0])

    def test_no_lookahead_last_close(self):
        closes = _flat_then_rise_then_fall()
        df1 = _run(_frame(closes))
        closes2 = list(closes)
        closes2[-1] = closes2[-1] * 1.5
        df2 = _run(_frame(closes2))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("frama_trend", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["frama_trend"].slug, "frama_trend")
        self.assertEqual(registry.REGISTRY["frama_trend"].warmup_bars, risk.WARMUP)
        self.assertEqual(risk.WARMUP, 40)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)

    def test_warmup_gating_in_backtest(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        if len(res.trades):
            self.assertTrue(
                (res.trades["entry_t"] >= int(df["t"].iloc[risk.WARMUP])).all())

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
