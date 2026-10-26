"""Tests for roc_momentum. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.roc_momentum import indicators, risk, signals
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


class TestRocMomentum(unittest.TestCase):
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
        self.assertIn("roc_momentum", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["roc_momentum"].slug, "roc_momentum")
        self.assertEqual(risk.WARMUP, 20)

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

    def test_cross_up_fires_on_reversal(self):
        df = _run(_frame_from_close(np.concatenate([np.linspace(100, 80, 40), np.linspace(80, 115, 40)])))
        self.assertTrue(df["long_entry"].any())

    def test_cross_down_fires_on_reversal(self):
        df = _run(_frame_from_close(np.concatenate([np.linspace(80, 115, 40), np.linspace(115, 80, 40)])))
        self.assertTrue(df["short_entry"].any())

    def test_no_short_on_monotonic_rise(self):
        df = _run(_frame_from_close(np.linspace(100, 150, 120)))
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
