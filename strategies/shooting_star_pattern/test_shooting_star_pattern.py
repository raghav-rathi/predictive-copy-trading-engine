"""Shooting Star Pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.shooting_star_pattern import indicators, risk, signals
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


class TestShootingStarPattern(unittest.TestCase):
    def test_registered(self):
        self.assertIn("shooting_star_pattern", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in ("ema20", "ret5", "body", "candle_range", "upper_shadow", "lower_shadow"):
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

    def test_short_entry_on_shooting_star(self):
        # Steady 1%/bar uptrend, then a textbook shooting star as the last bar.
        closes = list(100 * (1.01 ** i) for i in range(60))
        opens = list(closes)
        highs = [c * 1.001 for c in closes]
        lows = [c * 0.999 for c in closes]
        last_c = closes[-1]
        opens[-1] = last_c - 1.0
        closes[-1] = last_c
        highs[-1] = last_c + 9.0
        lows[-1] = last_c - 2.0
        df = _run(_frame(closes, highs=highs, lows=lows, opens=opens))
        self.assertTrue(df["shooting_star"].iloc[-1])
        self.assertTrue(df["short_entry"].iloc[-1])

    def test_long_entry_on_inverted_hammer(self):
        # Steady 1%/bar downtrend, then a textbook inverted hammer.
        closes = list(200 * (0.99 ** i) for i in range(60))
        opens = list(closes)
        highs = [c * 1.001 for c in closes]
        lows = [c * 0.999 for c in closes]
        last_c = closes[-1]
        opens[-1] = last_c - 1.0
        closes[-1] = last_c
        highs[-1] = last_c + 0.5
        lows[-1] = last_c - 11.0
        df = _run(_frame(closes, highs=highs, lows=lows, opens=opens))
        self.assertTrue(df["inverted_hammer"].iloc[-1])
        self.assertTrue(df["long_entry"].iloc[-1])

    def test_no_lookahead_flat_data(self):
        # Flat closes: no trend context, so no entries at all.
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_pattern_without_trend_no_entry(self):
        # A shooting star shape on flat closes must not trigger a short:
        # the uptrend context (ret5 > 1%) is absent.
        closes = [100.0] * 60
        opens = list(closes)
        highs = [c * 1.001 for c in closes]
        lows = [c * 0.999 for c in closes]
        opens[-1] = 99.0
        closes[-1] = 100.0
        highs[-1] = 109.0
        lows[-1] = 98.0
        df = _run(_frame(closes, highs=highs, lows=lows, opens=opens))
        self.assertTrue(df["shooting_star"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])


if __name__ == "__main__":
    unittest.main()
