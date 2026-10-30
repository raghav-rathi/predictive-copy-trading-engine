"""Liquidity sweep tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.liquidity_sweep import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(rows):
    """rows: (o, h, l, c) tuples."""
    n = len(rows)
    arr = np.array(rows, dtype=float)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": arr[:, 0], "h": arr[:, 1],
                         "l": arr[:, 2], "c": arr[:, 3],
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _prefix(n=25):
    # Flat range: prior-20-bar low 98, high 102.
    return [(100, 102, 98, 100)] * n


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


class TestLiquiditySweep(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("sweep_low_level", "sweep_high_level", "atr"):
            self.assertIn(col, df.columns)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["sweep_low_level"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["sweep_high_level"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["sweep_dir"].isna().any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_sweep_same_bar_reclaim(self):
        # Low wicks to 96 below the 98 level, closes at 99 back inside.
        df = _run(_frame(_prefix() + [(100, 100, 96, 99)]))
        self.assertEqual(df["sweep_dir"].iloc[-1], 1)
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].any())

    def test_short_sweep_same_bar_reclaim(self):
        df = _run(_frame(_prefix() + [(100, 104, 100, 101)]))
        self.assertEqual(df["sweep_dir"].iloc[-1], -1)
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].any())

    def test_long_sweep_next_bar_reclaim(self):
        # Sweep bar closes below the level (97 <= 98, no reclaim);
        # the next bar closes back above it (99 > 98) -> fires then.
        df = _run(_frame(_prefix() + [(100, 100, 96, 97), (97, 100, 98, 99)]))
        self.assertEqual(df["sweep_dir"].iloc[-2], 0)
        self.assertEqual(df["sweep_dir"].iloc[-1], 1)
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_breakdown_without_reclaim_is_not_a_sweep(self):
        # Wicks below, closes below, and stays below: a breakdown.
        df = _run(_frame(_prefix() + [(100, 100, 96, 97), (97, 98, 96, 96)]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_opposite_sweep_exits(self):
        df = _run(_frame(_prefix() + [(100, 100, 96, 99),
                                      (99, 104, 99, 101)]))
        # Second bar: high wicks above the prior-20 high? The
        # prior-20 high after the sweep bar is still 102, so
        # 104 > 102 and close 101 < 102 -> opposite sweep exits.
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        import strategies.liquidity_sweep  # noqa: F401
        self.assertIn("liquidity_sweep", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["liquidity_sweep"].slug,
                         "liquidity_sweep")

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
        self.assertEqual(risk.WARMUP, 25)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
