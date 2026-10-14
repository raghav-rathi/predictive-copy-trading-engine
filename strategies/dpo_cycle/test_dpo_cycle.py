"""Detrended Price Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dpo_cycle import indicators, risk, signals
from strategies import base as B

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.2):
    c = np.asarray(c, dtype=float)
    n = len(c)
    prev = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": prev,
            "h": np.maximum(c, prev) + spread,
            "l": np.minimum(c, prev) - spread,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestDpoCycle(unittest.TestCase):
    def test_formula_independent(self):
        rng = np.random.default_rng(81)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        df = indicators.add_indicators(_frame(c))
        expect = pd.Series(c) - pd.Series(c).rolling(21, min_periods=21).mean().shift(11)
        pd.testing.assert_series_equal(df["dpo"], expect, check_names=False)

    def test_sine_wave_phase(self):
        # Pure sine: DPO should be positive near cycle peaks, negative near troughs.
        n = 200
        c = 100.0 + 10.0 * np.sin(2 * np.pi * np.arange(n) / 40.0)
        df = indicators.add_indicators(_frame(c)).dropna()
        # At the sine peak (bar 10, 50, ...) DPO > 0; at troughs DPO < 0.
        self.assertGreater(df["dpo"].iloc[10], 0)
        self.assertLess(df["dpo"].iloc[30], 0)

    def test_cycle_crosses_give_entries(self):
        n = 300
        c = 100.0 + 8.0 * np.sin(2 * np.pi * np.arange(n) / 36.0)
        df = _run(_frame(c))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertGreater(int(df["short_entry"].sum()), 0)

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(83)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 250)))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(85)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))
        full = indicators.add_indicators(_frame(c))
        cut = indicators.add_indicators(_frame(c[:200]))
        pd.testing.assert_series_equal(
            full["dpo"].iloc[:200], cut["dpo"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
