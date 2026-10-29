"""MACD Bollinger tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_bollinger import indicators, risk, signals
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


def _indicator_frame(macd, lower, upper, mid=None, sig=None):
    """Hand-built indicator frame so signal crosses are exact."""
    n = len(macd)
    mid = np.zeros(n) if mid is None else np.asarray(mid, dtype=float)
    sig = np.zeros(n) if sig is None else np.asarray(sig, dtype=float)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": np.zeros(n), "h": np.zeros(n), "l": np.zeros(n),
        "c": np.zeros(n), "v": np.zeros(n),
        "macd": np.asarray(macd, dtype=float),
        "macd_signal": sig,
        "macd_hist": np.asarray(macd, dtype=float) - sig,
        "macd_bb_mid": mid,
        "macd_bb_upper": np.asarray(upper, dtype=float),
        "macd_bb_lower": np.asarray(lower, dtype=float),
        "macd_bb_width": np.asarray(upper, dtype=float) - np.asarray(lower, dtype=float),
        "atr": np.ones(n),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestMacdBollinger(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("macd", "macd_signal", "macd_hist", "macd_bb_mid",
                    "macd_bb_upper", "macd_bb_lower", "macd_bb_width", "atr"):
            self.assertIn(col, df.columns, col)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_entry_on_lower_band_release(self):
        # MACD below its lower band (-2), then crosses back up through
        # it while still below zero.
        df = signals.add_signals(_indicator_frame(
            macd=[-3.0, -3.0, -1.0, -0.5], lower=[-2.0] * 4, upper=[2.0] * 4))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_upper_band_release(self):
        df = signals.add_signals(_indicator_frame(
            macd=[3.0, 3.0, 1.0, 0.5], lower=[-2.0] * 4, upper=[2.0] * 4))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_when_macd_on_wrong_side_of_zero(self):
        # Cross up through the lower band but MACD already positive:
        # not an oversold release, no long.
        df = signals.add_signals(_indicator_frame(
            macd=[-3.0, -3.0, 1.0], lower=[-2.0] * 3, upper=[2.0] * 3))
        self.assertFalse(df["long_entry"].any())

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
        self.assertIn("macd_bollinger", registry.REGISTRY)
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
