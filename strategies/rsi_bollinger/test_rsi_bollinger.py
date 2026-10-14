"""Bollinger-on-RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_bollinger import indicators, risk, signals
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


class TestRsiBollinger(unittest.TestCase):
    def test_bands_formula_independent(self):
        rng = np.random.default_rng(41)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        df = indicators.add_indicators(_frame(c))
        rsi = B.rsi(pd.Series(c), 14)
        mid = rsi.rolling(20, min_periods=20).mean()
        sd = rsi.rolling(20, min_periods=20).std()
        pd.testing.assert_series_equal(df["rsi_bb_mid"], mid, check_names=False)
        pd.testing.assert_series_equal(
            df["rsi_bb_upper"], mid + 2.0 * sd, check_names=False
        )
        pd.testing.assert_series_equal(
            df["rsi_bb_lower"], mid - 2.0 * sd, check_names=False
        )

    def test_bands_ordering(self):
        rng = np.random.default_rng(3)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.015, 200)))
        df = indicators.add_indicators(_frame(c)).dropna()
        self.assertTrue((df["rsi_bb_upper"] >= df["rsi_bb_mid"]).all())
        self.assertTrue((df["rsi_bb_mid"] >= df["rsi_bb_lower"]).all())

    def test_exhaustion_bounce_gives_long(self):
        # Sharp selloff (RSI pinned low) then bounce: lower-band tag + re-entry.
        rng = np.random.default_rng(19)
        n1, n2 = 80, 160
        c1 = 200.0 - 1.2 * np.arange(n1) + rng.normal(0, 0.4, n1).cumsum() * 0.05
        c2 = c1[-1] + 0.5 * np.arange(n2) + rng.normal(0, 0.4, n2).cumsum() * 0.05
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_long_entry_requires_prior_stretch(self):
        # Every long entry bar must have had RSI at/below the lower band
        # on the prior bar (the cross definition).
        rng = np.random.default_rng(23)
        c = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 600)))
        df = _run(_frame(c))
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx:
            self.assertLessEqual(df["rsi"].iloc[i - 1], df["rsi_bb_lower"].iloc[i - 1])
            self.assertGreater(df["rsi"].iloc[i], df["rsi_bb_lower"].iloc[i])

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(7)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 250)))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(29)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))
        full = indicators.add_indicators(_frame(c))
        cut = indicators.add_indicators(_frame(c[:200]))
        pd.testing.assert_series_equal(
            full["rsi_bb_upper"].iloc[:200], cut["rsi_bb_upper"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.WARMUP, 50)


if __name__ == "__main__":
    unittest.main()
