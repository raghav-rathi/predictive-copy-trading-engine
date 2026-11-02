"""VHF Trend Regime tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vhf import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes * 1.001
    l = np.array(lows, dtype=float) if lows is not None else closes * 0.999
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": closes, "h": h, "l": l, "c": closes, "v": v})


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


class TestVhf(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ['vhf', 'sma28', 'atr']:
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_registered_in_registry(self):
        self.assertIn("vhf", registry.REGISTRY)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        self.assertTrue(np.isfinite(res.equity).all())

    def test_linear_trend_vhf_high(self):
        closes = [100 + 0.5 * i for i in range(200)]
        df = _run(_frame(closes))
        self.assertGreater(df["vhf"].iloc[-1], 0.8)

    def test_choppy_series_vhf_low(self):
        closes = [100.0 if i % 2 == 0 else 101.0 for i in range(200)]
        df = _run(_frame(closes))
        self.assertLess(df["vhf"].iloc[-1], 0.5)


if __name__ == "__main__":
    unittest.main()
