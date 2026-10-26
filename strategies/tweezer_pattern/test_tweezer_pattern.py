"""Tests for tweezer_pattern. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tweezer_pattern import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame_from_close(c, seed=7, vol=100.0):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = np.full(n, vol) + rng.uniform(0, 10, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _ohlc(o, h, l, c, v=None):
    o = np.asarray(o, dtype=float); h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float); c = np.asarray(c, dtype=float)
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.asarray(v, dtype=float)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestTweezerPattern(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_frame_from_close(np.concatenate([np.linspace(100, 80, 60), np.linspace(80, 120, 60)])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_flat_data_no_entries(self):
        df = _run(_frame_from_close(np.full(120, 100.0)))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        series = np.concatenate([np.linspace(100, 80, 60), np.linspace(80, 120, 60)])
        full = _run(_frame_from_close(series))
        trunc = _run(_frame_from_close(series[:100]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        self.assertIn("tweezer_pattern", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["tweezer_pattern"].slug, "tweezer_pattern")
        self.assertEqual(risk.WARMUP, 10)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)

    def test_backtest_smoke_on_synthetic(self):
        df = _run(_frame_from_close(np.concatenate([np.linspace(100, 80, 100), np.linspace(80, 130, 100)])))
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h", warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("net_pnl_usd", m)
        self.assertIn("trades", m)

    def test_tweezer_top_fires_short(self):
        o = np.array([100.0, 108.0]); h = np.array([110.0, 110.05]); l = np.array([95.0, 96.0]); c = np.array([108.0, 105.0])
        o = np.concatenate([np.full(30, 100.0), o]); h = np.concatenate([np.full(30, 100.0), h])
        l = np.concatenate([np.full(30, 100.0), l]); c = np.concatenate([np.full(30, 100.0), c])
        df = _run(_ohlc(o, h, l, c))
        self.assertTrue(df["short_entry"].iloc[-1])

    def test_tweezer_bottom_fires_long(self):
        o = np.array([108.0, 100.0]); h = np.array([112.0, 112.0]); l = np.array([95.0, 95.05]); c = np.array([100.0, 103.0])
        o = np.concatenate([np.full(30, 108.0), o]); h = np.concatenate([np.full(30, 112.0), h])
        l = np.concatenate([np.full(30, 112.0), l]); c = np.concatenate([np.full(30, 108.0), c])
        df = _run(_ohlc(o, h, l, c))
        self.assertTrue(df["long_entry"].iloc[-1])


if __name__ == "__main__":
    unittest.main()
