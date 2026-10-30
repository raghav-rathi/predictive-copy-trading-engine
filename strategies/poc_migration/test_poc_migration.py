"""POC migration tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.poc_migration import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, vols=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    if vols is None:
        vols = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes + 0.05,
                         "l": closes - 0.05, "c": closes, "v": vols})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestPocMigration(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("poc", "poc_change_10", "poc_dir", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_poc_rises_long(self):
        # 50 quiet bars at 100, then 20 heavy bars at 110: the POC
        # jumps to the top bin on the first heavy bar, close > POC.
        closes = [100.0] * 50 + [110.0] * 20
        vols = np.array([10.0] * 50 + [1000.0] * 20)
        df = _run(_frame(closes, vols))
        self.assertGreater(df["poc"].iloc[50], df["poc"].iloc[49])
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_poc_falls_short(self):
        closes = [110.0] * 50 + [100.0] * 20
        vols = np.array([10.0] * 50 + [1000.0] * 20)
        df = _run(_frame(closes, vols))
        self.assertLess(df["poc"].iloc[50], df["poc"].iloc[49])
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_flat_poc_no_signal(self):
        # Constant price: POC never moves, close equals POC, so
        # neither entry condition (strictly above/below) can fire.
        df = _run(_frame([100.0] * 120))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_poc_flip_exits(self):
        # Long on the rise to 110, then heavy volume back at 100
        # flips POC down and must exit the long.
        closes = [100.0] * 50 + [110.0] * 20 + [100.0] * 30
        vols = np.array([10.0] * 50 + [1000.0] * 20 + [1000.0] * 30)
        df = _run(_frame(closes, vols))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("poc_migration", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["poc_migration"].slug,
                         "poc_migration")
        self.assertEqual(risk.WARMUP, 65)

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
