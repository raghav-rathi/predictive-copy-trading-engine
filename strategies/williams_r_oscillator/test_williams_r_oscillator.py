"""Williams %R oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.williams_r_oscillator import indicators, risk, signals
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


class TestWilliamsROscillator(unittest.TestCase):
    def test_registered(self):
        self.assertIn("williams_r_oscillator", registry.REGISTRY)

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

    def test_williams_r_range_and_midpoint(self):
        # Flat price in a fixed 90-110 range: %R must sit at -50, inside [-100, 0].
        n = 80
        df = indicators.add_indicators(
            _frame([100.0] * n, highs=[110.0] * n, lows=[90.0] * n))
        tail = df["williams_r"].iloc[14:]
        self.assertTrue(((tail >= -100) & (tail <= 0)).all())
        self.assertTrue(np.allclose(tail, -50.0))

    def test_long_entry_on_oversold_exit(self):
        # Hand-set %R path: -85 -> -75 crosses back above -80 with close > SMA50.
        df = pd.DataFrame({
            "c": [90.0, 90.0, 90.0, 95.0, 101.0, 102.0, 103.0, 99.0, 99.0, 90.0],
            "williams_r": [-95.0, -95.0, -95.0, -85.0, -75.0, -10.0, -5.0, -30.0, -85.0, -95.0],
            "sma50": [100.0] * 10,
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[4])
        self.assertFalse(out["long_entry"].iloc[:4].any())
        # Long exit when %R crosses above -20 (index 5: -75 -> -10).
        self.assertTrue(out["long_exit"].iloc[5])
        # Short entry when %R crosses below -20 with close < SMA50 (index 7).
        self.assertTrue(out["short_entry"].iloc[7])
        # Short exit when %R crosses below -80 (index 8: -30 -> -85).
        self.assertTrue(out["short_exit"].iloc[8])


if __name__ == "__main__":
    unittest.main()
