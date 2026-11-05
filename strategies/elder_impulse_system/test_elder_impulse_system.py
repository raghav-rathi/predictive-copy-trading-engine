"""Elder Impulse System tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elder_impulse_system import indicators, risk, signals
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


def _trend_frame():
    """Flat, then a down run, then a strong up run (impulse flips red -> green)."""
    flat = [100.0] * 60
    down = list(100 * (0.99 ** i) for i in range(1, 21))
    up = list(down[-1] * (1.015 ** i) for i in range(1, 41))
    return _frame(flat + down + up)


class TestElderImpulseSystem(unittest.TestCase):
    def test_registered(self):
        self.assertIn("elder_impulse_system", registry.REGISTRY)

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

    def test_green_bar_on_sustained_uptrend(self):
        # A long clean uptrend must produce green impulse bars.
        closes = [100.0] * 40 + list(100 * (1.01 ** i) for i in range(60))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[40:]  # from the trend start (hist peaks early, then fades)
        self.assertTrue(tail["impulse_green"].any())

    def test_long_entry_after_red_run(self):
        df = _run(_trend_frame())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_after_green_run(self):
        # Mirror: up run then down run must fire a short entry.
        flat = [100.0] * 60
        up = list(100 * (1.01 ** i) for i in range(1, 21))
        down = list(up[-1] * (0.985 ** i) for i in range(1, 41))
        df = _run(_frame(flat + up + down))
        self.assertTrue(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
