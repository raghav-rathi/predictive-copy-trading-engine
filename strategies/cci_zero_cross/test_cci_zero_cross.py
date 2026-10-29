"""CCI zero-cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cci_zero_cross import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


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


def _indicator_frame(cci, c, trend_sma):
    n = len(cci)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": np.zeros(n), "h": np.zeros(n), "l": np.zeros(n),
        "c": np.asarray(c, dtype=float), "v": np.zeros(n),
        "cci": np.asarray(cci, dtype=float),
        "trend_sma": np.asarray(trend_sma, dtype=float),
        "atr": np.ones(n),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestCciZeroCross(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("cci", "trend_sma", "atr"):
            self.assertIn(col, df.columns, col)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_entry_on_zero_cross_in_uptrend(self):
        df = signals.add_signals(_indicator_frame(
            cci=[-5.0, 5.0], c=[105.0, 106.0], trend_sma=[100.0, 100.0]))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_zero_cross_in_downtrend(self):
        df = signals.add_signals(_indicator_frame(
            cci=[5.0, -5.0], c=[95.0, 94.0], trend_sma=[100.0, 100.0]))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].any())

    def test_cross_against_trend_ignored(self):
        # CCI crosses above zero but price is BELOW its SMA(50):
        # counter-trend cross, no long.
        df = signals.add_signals(_indicator_frame(
            cci=[-5.0, 5.0], c=[95.0, 96.0], trend_sma=[100.0, 100.0]))
        self.assertFalse(df["long_entry"].any())
        # Mirror: cross below zero while price is above trend.
        df = signals.add_signals(_indicator_frame(
            cci=[5.0, -5.0], c=[105.0, 104.0], trend_sma=[100.0, 100.0]))
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        df = _run(_random_walk_frame(n=300, seed=11))
        flat = pd.DataFrame({"t": df["t"], "o": 100.0, "h": 100.0,
                             "l": 100.0, "c": 100.0, "v": 100.0})
        out = _run(flat)
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].any())

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
        self.assertIn("cci_zero_cross", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 60)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)
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
