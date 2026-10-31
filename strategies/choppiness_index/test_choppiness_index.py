"""Choppiness Index tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.choppiness_index import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes, "l": closes,
                         "c": closes, "v": np.full(n, 100.0)})


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


class TestChoppinessIndex(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("chop", "donchian_high", "donchian_low", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_chop_hand_computed_steady_trend(self):
        # +1 per bar, h = l = c: TR = 1 on every bar after the first,
        # 14-bar TR sum = 14, window range = 13, so
        # CHOP = 100 * log10(14/13) / log10(14) ~= 2.81.
        closes = [100.0 + i for i in range(40)]
        df = indicators.add_indicators(_frame(closes))
        expected = 100 * math.log10(14 / 13) / math.log10(14)
        self.assertAlmostEqual(df["chop"].iloc[20], expected, places=2)

    def test_chop_nan_on_flat_prices(self):
        df = indicators.add_indicators(_frame([100.0] * 40))
        self.assertTrue(df["chop"].iloc[20:].isna().all())

    def test_donchian_prior_bar_only(self):
        # Prior band on bar i must exclude bar i itself: after a flat
        # stretch at 100, the first 101 bar still sees a prior high of 100.
        closes = [100.0] * 30 + [101.0, 101.0, 101.0]
        df = indicators.add_indicators(_frame(closes))
        self.assertEqual(df["donchian_high"].iloc[30], 100.0)
        self.assertEqual(df["donchian_low"].iloc[30], 100.0)

    def test_long_entry_on_breakout_after_flat(self):
        closes = [100.0] * 30 + [101.0, 101.0, 101.0]
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_breakdown_after_flat(self):
        closes = [100.0] * 30 + [99.0, 99.0, 99.0]
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].iloc[30])
        self.assertFalse(df["long_entry"].any())

    def test_long_exit_on_opposite_band_cross(self):
        closes = [100.0] * 30 + [101.0, 101.0, 99.0]
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertTrue(df["long_exit"].iloc[32])

    def test_no_entry_when_choppy(self):
        # Alternating 100/110 gives CHOP = 100 (TR sum 140, range 10);
        # a breakout to 120 still has CHOP far above 38.2, so no entry.
        closes = [100.0 if i % 2 == 0 else 110.0 for i in range(40)] + [120.0]
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].iloc[40])
        self.assertFalse(df["long_entry"].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_last_bar_change_keeps_earlier_signals(self):
        closes = [100.0] * 30 + [101.0, 101.0, 99.0, 102.0, 98.0]
        df1 = _run(_frame(closes))
        closes2 = list(closes)
        closes2[-1] = closes2[-1] * 1.5
        df2 = _run(_frame(closes2))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("choppiness_index", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["choppiness_index"].slug,
                         "choppiness_index")
        self.assertEqual(risk.WARMUP, 30)

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

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
