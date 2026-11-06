"""Megaphone Pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.megaphone_pattern import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.3
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.3
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "t": t, "o": np.concatenate([[closes[0]], closes[:-1]]),
        "h": h, "l": l, "c": closes, "v": v,
    })


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


def _zigzag(pivot_prices):
    """Piecewise-linear closes through pivot prices spaced 10 bars apart."""
    closes = []
    for k in range(len(pivot_prices) - 1):
        seg = np.linspace(pivot_prices[k], pivot_prices[k + 1], 10, endpoint=False)
        closes.extend(seg.tolist())
    closes.append(float(pivot_prices[-1]))
    return closes


class TestMegaphonePattern(unittest.TestCase):
    def test_registered(self):
        self.assertIn("megaphone_pattern", registry.REGISTRY)

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

    def test_long_entry_after_third_lower_low(self):
        # H 102, L 98, H 104, L 96, H 106, L 94, then rally above 106.
        closes = _zigzag([100, 102, 98, 104, 96, 106, 94, 108])
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_after_third_higher_high(self):
        # L 98, H 102, L 96, H 104, L 94, H 106, then sell-off below 94.
        closes = _zigzag([100, 98, 102, 96, 104, 94, 106, 92])
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].any())

    def test_no_lookahead_flat_data(self):
        # Flat closes: no pivots, no pattern, no entries.
        closes = [100.0] * 150
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_incomplete_pattern_no_entry(self):
        # Only one higher high / one lower low: pattern incomplete.
        closes = _zigzag([100, 102, 98, 104, 108])
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
