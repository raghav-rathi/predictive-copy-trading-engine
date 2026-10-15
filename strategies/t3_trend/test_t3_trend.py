"""Tillson T3 tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.t3_trend import indicators, risk, signals


def _frame(n, c):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestT3(unittest.TestCase):
    def test_coefficients_sum_to_one(self):
        a = indicators.VFACTOR
        c1 = -(a**3)
        c2 = 3 * a**2 + 3 * a**3
        c3 = -6 * a**2 - 3 * a - 3 * a**3
        c4 = 1 + 3 * a + a**3 + 3 * a**2
        self.assertAlmostEqual(c1 + c2 + c3 + c4, 1.0, places=12)

    def test_constant_series_returns_constant(self):
        n = 120
        df = indicators.add_indicators(_frame(n, np.full(n, 100.0)))
        self.assertAlmostEqual(df["t3_fast"].iloc[-1], 100.0, places=6)
        self.assertAlmostEqual(df["t3_slow"].iloc[-1], 100.0, places=6)

    def test_t3_matches_manual_chain(self):
        n = 80
        rng = np.random.default_rng(0)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        df = indicators.add_indicators(_frame(n, c))
        s = df["c"]
        e1 = B.ema(s, 5)
        e2 = B.ema(e1, 5)
        e3 = B.ema(e2, 5)
        e4 = B.ema(e3, 5)
        e5 = B.ema(e4, 5)
        e6 = B.ema(e5, 5)
        a = indicators.VFACTOR
        c1, c2 = -(a**3), 3 * a**2 + 3 * a**3
        c3, c4 = -6 * a**2 - 3 * a - 3 * a**3, 1 + 3 * a + a**3 + 3 * a**2
        exp = c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3
        pd.testing.assert_series_equal(df["t3_fast"], exp, check_names=False)

    def test_cross_fires_both_directions(self):
        n = 240
        i = np.arange(n)
        c = 100.0 + 10.0 * np.sin(i / 15.0)
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        self.assertTrue(sig["long_entry"].any())
        self.assertTrue(sig["short_entry"].any())

    def test_no_nan_after_warmup(self):
        n = 200
        c = 100.0 + np.cumsum(np.random.default_rng(3).normal(0, 0.3, n))
        df = indicators.add_indicators(_frame(n, c))
        self.assertFalse(df[["t3_fast", "t3_slow"]].iloc[90:].isna().any().any())
        sig = signals.add_signals(df)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 90)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)


if __name__ == "__main__":
    unittest.main()
