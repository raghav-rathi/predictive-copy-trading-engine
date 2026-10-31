"""Woodie pivots tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.woodie_pivots import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

MIDNIGHT_MS = int(pd.Timestamp("2023-11-15", tz="UTC").value // 1_000_000)


def _frame(closes, h_mult=1.001, l_mult=0.999, start_ms=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t0 = MIDNIGHT_MS if start_ms is None else start_ms
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes * h_mult,
                         "l": closes * l_mult, "c": closes,
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


def _two_day_frame(day2_closes):
    # Day 1: 24 bars, h=110, l=90, closes rising 96..100 (last = 100).
    # With h_mult/l_mult overridden per-bar below, set h/l directly.
    day1_c = np.linspace(96.0, 100.0, 24)
    closes = np.concatenate([day1_c, np.array(day2_closes, dtype=float)])
    n = len(closes)
    t = (MIDNIGHT_MS + np.arange(n) * 3_600_000).astype("int64")
    h = np.where(np.arange(n) < 24, 110.0, closes * 1.001)
    l = np.where(np.arange(n) < 24, 90.0, closes * 0.999)
    return pd.DataFrame({"t": t, "o": closes, "h": h, "l": l, "c": closes,
                         "v": np.full(n, 100.0)})


class TestWoodiePivots(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("pp", "r1", "s1", "r2", "s2", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_first_day_no_levels_no_signals(self):
        df = _run(_two_day_frame([105.0] * 24))
        self.assertTrue(df["pp"].iloc[:24].isna().all())
        self.assertFalse(df["long_entry"].iloc[:24].any())
        self.assertFalse(df["short_entry"].iloc[:24].any())

    def test_hand_computed_prior_day_levels(self):
        # Day 1: H=110, L=90, C=100 -> PP=100, R1=110, S1=90, R2=120, S2=80.
        df = _run(_two_day_frame([105.0] * 24))
        row = df.iloc[24]
        self.assertAlmostEqual(row["pp"], 100.0, places=9)
        self.assertAlmostEqual(row["r1"], 110.0, places=9)
        self.assertAlmostEqual(row["s1"], 90.0, places=9)
        self.assertAlmostEqual(row["r2"], 120.0, places=9)
        self.assertAlmostEqual(row["s2"], 80.0, places=9)
        # Levels constant across day 2.
        self.assertTrue(np.allclose(df["pp"].iloc[24:48], 100.0))

    def test_long_on_r1_cross(self):
        df = _run(_two_day_frame([105.0, 108.0, 112.0] + [112.0] * 21))
        self.assertTrue(df["long_entry"].iloc[24:48].any())
        self.assertEqual(int(df["long_entry"].iloc[24:48].idxmax()), 26)

    def test_short_on_s1_cross(self):
        df = _run(_two_day_frame([95.0, 92.0, 88.0] + [88.0] * 21))
        self.assertTrue(df["short_entry"].iloc[24:48].any())
        self.assertEqual(int(df["short_entry"].iloc[24:48].idxmax()), 26)

    def test_long_exit_on_pp_cross_down(self):
        df = _run(_two_day_frame(
            [105.0, 112.0, 111.0, 108.0, 102.0, 99.0] + [99.0] * 18))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())
        # Exit must come after the entry.
        self.assertGreater(int(df["long_exit"].idxmax()),
                           int(df["long_entry"].idxmax()))

    def test_no_lookahead(self):
        df1 = _run(_random_walk_frame())
        frame = _random_walk_frame()
        frame.loc[frame.index[-1], "c"] = frame["c"].iloc[-1] * 1.5
        df2 = _run(frame)
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
        self.assertIn("woodie_pivots", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["woodie_pivots"].slug, "woodie_pivots")
        self.assertEqual(risk.WARMUP, 50)

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
