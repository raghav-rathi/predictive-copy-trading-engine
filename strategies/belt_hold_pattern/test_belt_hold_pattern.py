"""Belt Hold Pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.belt_hold_pattern import indicators, risk, signals
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


class TestBeltHoldPattern(unittest.TestCase):
    def test_registered(self):
        self.assertIn("belt_hold_pattern", registry.REGISTRY)

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

    def test_long_entry_bullish_belt_hold(self):
        # Steady downtrend, then a tall white candle opening on its low.
        closes = list(np.linspace(100, 90, 40))
        highs = [c + 0.2 for c in closes]
        lows = [c - 0.2 for c in closes]
        opens = [closes[0]] + closes[:-1]
        closes.append(95.5)
        opens.append(90.2)
        highs.append(96.0)
        lows.append(90.0)
        df = _run(_frame(closes, highs, lows, opens=opens))
        self.assertTrue(df["long_entry"].iloc[-1])

    def test_short_entry_bearish_belt_hold(self):
        # Steady uptrend, then a long black candle opening on its high.
        closes = list(np.linspace(100, 110, 40))
        highs = [c + 0.2 for c in closes]
        lows = [c - 0.2 for c in closes]
        opens = [closes[0]] + closes[:-1]
        closes.append(104.5)
        opens.append(109.8)
        highs.append(110.0)
        lows.append(104.0)
        df = _run(_frame(closes, highs, lows, opens=opens))
        self.assertTrue(df["short_entry"].iloc[-1])

    def test_no_lookahead_flat_data(self):
        # Flat closes: no trend, no qualifying candle, no entries.
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_zero_range_bar_never_qualifies(self):
        # A doji / zero-range bar in a downtrend must not fire.
        closes = list(np.linspace(100, 90, 40)) + [90.0]
        highs = [c + 0.2 for c in closes[:-1]] + [90.0]
        lows = [c - 0.2 for c in closes[:-1]] + [90.0]
        opens = [closes[0]] + closes[:-1]
        opens[-1] = 90.0
        df = _run(_frame(closes, highs, lows, opens=opens))
        self.assertFalse(df["long_entry"].iloc[-1])


if __name__ == "__main__":
    unittest.main()
