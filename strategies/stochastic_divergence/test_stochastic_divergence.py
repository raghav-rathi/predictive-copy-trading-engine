"""Stochastic Divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stochastic_divergence import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes * 1.001
    l = np.array(lows, dtype=float) if lows is not None else closes * 0.999
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c * 1.001, "l": c * 0.999, "c": c,
        "v": np.full(n, 100.0),
    })


def _long_frame():
    # Regular bullish divergence: first swing low ~90 (close near the low,
    # %K pinned near 0), recovery, then a LOWER low (85) whose close
    # recovers to 93, so %K at the second pivot is higher.
    seg1 = [100 - 0.5 * i for i in range(20)]
    rec = [91 + i for i in range(10)]
    seg2 = [100 - 1.0 * i for i in range(8)]
    closes = seg1 + rec + seg2 + [94, 96, 98, 100, 102, 104, 106, 108, 110, 112]
    lows = [x * 0.999 for x in closes]
    highs = [x * 1.001 for x in closes]
    lows[37] = 85.0
    highs[37] = 94.0
    return _frame(closes, highs, lows)


def _short_frame():
    # Regular bearish divergence: first swing high ~110 (close near the
    # high, %K pinned near 100), dip, then a HIGHER high (115) whose close
    # only reaches 112, so %K at the second pivot is lower.
    seg1 = [100 + 0.5 * i for i in range(20)]
    rec = [109 - i for i in range(10)]
    seg2 = [100 + 1.0 * i for i in range(12)]
    closes = seg1 + rec + seg2 + [111, 109, 107, 105, 103, 101, 99, 97, 95, 93]
    highs = [x * 1.001 for x in closes]
    lows = [x * 0.999 for x in closes]
    highs[41] = 115.0
    lows[41] = 110.0
    closes[41] = 112.0
    return _frame(closes, highs, lows)


class TestStochasticDivergence(unittest.TestCase):
    def test_registered(self):
        self.assertIn("stochastic_divergence", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
            self.assertTrue(np.isfinite(tail[col].dropna()).all())

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_regular_bullish_divergence(self):
        df = _run(_long_frame())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_on_regular_bearish_divergence(self):
        df = _run(_short_frame())
        self.assertTrue(df["short_entry"].any())

    def test_no_lookahead_flat_data(self):
        # Flat closes: %K is constant 50, no pivot pair can diverge, so no
        # entry can occur.
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_before_pivot_confirmation(self):
        # The long entry must land on the confirmation bar (pivot + 2),
        # never on or before the pivot bar itself.
        df = _run(_long_frame())
        idx = df.index[df["long_entry"]].tolist()
        self.assertTrue(idx)
        # Second swing low is at index 37; confirmation is index 39.
        self.assertEqual(idx[0], 39)


if __name__ == "__main__":
    unittest.main()
