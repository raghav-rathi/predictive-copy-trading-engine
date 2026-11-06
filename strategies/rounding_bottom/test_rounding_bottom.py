"""Rounding Bottom tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rounding_bottom import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, vols=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "t": t, "o": np.concatenate([[closes[0]], closes[:-1]]),
        "h": closes + 0.5, "l": closes - 0.5, "c": closes, "v": v,
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


def _saucer_closes():
    # 130 bars: gentle descent, then a 60-bar U (bars 40-99) with rims
    # ~110 / ~112, trough 90 near bar 69, then a breakout.
    closes = list(np.linspace(112, 108, 40))
    closes += list(np.linspace(108, 110, 15))          # bars 40-54 left rim
    closes += list(np.linspace(110, 100, 5))           # bars 55-59
    closes += list(np.linspace(100, 90, 10))           # bars 60-69 to trough
    closes += list(np.linspace(90, 98, 10))            # bars 70-79 up
    closes += list(np.linspace(98, 106, 5))            # bars 80-84
    closes += list(np.linspace(106, 112, 15))          # bars 85-99 right rim
    return closes


def _inverted_saucer_closes():
    closes = list(np.linspace(88, 92, 40))
    closes += list(np.linspace(92, 90, 15))            # bars 40-54 left rim low
    closes += list(np.linspace(90, 100, 5))            # bars 55-59
    closes += list(np.linspace(100, 110, 10))          # bars 60-69 to peak
    closes += list(np.linspace(110, 102, 10))          # bars 70-79 down
    closes += list(np.linspace(102, 94, 5))            # bars 80-84
    closes += list(np.linspace(94, 88, 15))            # bars 85-99 right rim low
    return closes


class TestRoundingBottom(unittest.TestCase):
    def test_registered(self):
        self.assertIn("rounding_bottom", registry.REGISTRY)

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

    def test_long_entry_on_neckline_breakout(self):
        closes = _saucer_closes()
        vols = [100.0] * len(closes)
        closes = closes + [113.0, 114.0]
        vols = vols + [300.0, 300.0]
        df = _run(_frame(closes, vols))
        self.assertTrue(df["rb_pattern"].any())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_on_rounding_top_breakdown(self):
        closes = _inverted_saucer_closes()
        vols = [100.0] * len(closes)
        closes = closes + [87.0, 86.0]
        vols = vols + [300.0, 300.0]
        df = _run(_frame(closes, vols))
        self.assertTrue(df["rt_pattern"].any())
        self.assertTrue(df["short_entry"].any())

    def test_no_lookahead_flat_data(self):
        # Flat closes: no saucer, no neckline, no entries.
        closes = [100.0] * 150
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["rb_pattern"].any())
        self.assertFalse(df["rt_pattern"].any())


if __name__ == "__main__":
    unittest.main()
