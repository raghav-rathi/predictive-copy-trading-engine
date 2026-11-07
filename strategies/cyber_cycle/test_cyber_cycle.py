"""Cyber Cycle tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cyber_cycle import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
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
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _sine_frame(n=400, period=40, amp=5.0):
    i = np.arange(n)
    c = 100 + amp * np.sin(2 * np.pi * i / period)
    return _frame(c)


class TestCyberCycle(unittest.TestCase):
    def test_registered(self):
        self.assertIn("cyber_cycle", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_smooth_values(self):
        # smooth[3] = (103 + 2*102 + 2*101 + 100)/6 = 101.5
        # smooth[4] = (104 + 2*103 + 2*102 + 101)/6 = 102.5
        df = indicators.add_indicators(_frame([100, 101, 102, 103, 104, 105, 106]))
        self.assertAlmostEqual(df["cc_smooth"].iloc[3], 101.5)
        self.assertAlmostEqual(df["cc_smooth"].iloc[4], 102.5)

    def test_cycle_zero_on_linear_ramp(self):
        # A perfect ramp has zero second difference, so the cycle
        # filter output stays at zero.
        closes = [100.0 + i for i in range(200)]
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(np.abs(df["cc_cycle"].iloc[10:]).max() < 1e-9)

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["cc_smooth"]).all())
        self.assertTrue(np.isfinite(tail["cc_cycle"]).all())
        self.assertTrue(np.isfinite(tail["cc_signal"]).all())

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

    def test_entries_on_sine_wave(self):
        df = _run(_sine_frame())
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["short_entry"].any())

    def test_exits_mirror_reverse_cross(self):
        df = _run(_sine_frame())
        # Every long exit is a short entry and vice versa by construction.
        self.assertTrue((df["long_exit"] == df["short_entry"]).all())
        self.assertTrue((df["short_exit"] == df["long_entry"]).all())

    def test_no_lookahead_flat(self):
        closes = [100.0] * 200
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue((df["cc_cycle"] == 0).all())

    def test_no_entry_on_pure_ramp(self):
        closes = [100.0 + i for i in range(200)]
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
