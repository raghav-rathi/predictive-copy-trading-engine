"""NR7 Breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.nr7_breakout import indicators, risk, signals
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


class TestNr7Breakout(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("atr",):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_registered_in_registry(self):
        self.assertIn("nr7_breakout", registry.REGISTRY)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        self.assertTrue(np.isfinite(res.equity).all())

    def test_nr7_bar_detected(self):
        # Ranges: 10, 9, 8, 7, 6, 5, 4 -> bar 6 (range 4) is the
        # narrowest of the last 7, so it is the NR7 bar.
        highs = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]
        lows = [90.0, 91.0, 92.0, 93.0, 94.0, 95.0, 96.0]
        closes = [95.0, 95.5, 96.0, 96.5, 97.0, 97.5, 98.0]
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertAlmostEqual(df["nr7_high"].iloc[6], 100.0)
        self.assertAlmostEqual(df["nr7_low"].iloc[6], 96.0)

    def test_no_nr7_when_not_narrowest(self):
        # Ranges increase: no bar is narrower than all six before it.
        highs = [100.0] * 10
        lows = [99.0, 98.0, 97.0, 96.0, 95.0, 94.0, 93.0, 92.0, 91.0, 90.0]
        df = _run(_frame([95.0] * 10, highs=highs, lows=lows))
        self.assertTrue(df["nr7_high"].isna().all())


if __name__ == "__main__":
    unittest.main()
