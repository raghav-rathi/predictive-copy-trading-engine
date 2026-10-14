"""Chaikin Money Flow tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cmf_trend import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(h, l, c, v=None):
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": np.asarray(c, dtype=float),
            "h": np.asarray(h, dtype=float),
            "l": np.asarray(l, dtype=float),
            "c": np.asarray(c, dtype=float),
            "v": np.asarray(v, dtype=float),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestCmfTrend(unittest.TestCase):
    def test_formula_independent(self):
        rng = np.random.default_rng(51)
        n = 150
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
        h = c * (1 + rng.uniform(0, 0.005, n))
        l = c * (1 - rng.uniform(0, 0.005, n))
        v = rng.uniform(50, 150, n)
        df = indicators.add_indicators(_frame(h, l, c, v))
        clv = ((c - l) - (h - c)) / (h - l)
        mfv = clv * v
        expect = (
            pd.Series(mfv).rolling(21, min_periods=21).sum()
            / pd.Series(v).rolling(21, min_periods=21).sum()
        )
        pd.testing.assert_series_equal(df["cmf"], expect, check_names=False)

    def test_bounds(self):
        rng = np.random.default_rng(52)
        n = 300
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, n)))
        h = c * (1 + rng.uniform(0, 0.01, n))
        l = c * (1 - rng.uniform(0, 0.01, n))
        df = indicators.add_indicators(_frame(h, l, c)).dropna(subset=["cmf"])
        self.assertTrue(((df["cmf"] >= -1.0) & (df["cmf"] <= 1.0)).all())

    def test_all_high_closes_positive(self):
        n = 60
        c = 100.0 + np.arange(n)
        h = c + 0.5
        l = c - 2.0  # closes pinned near highs -> accumulation
        df = indicators.add_indicators(_frame(h, l, c))
        self.assertTrue((df["cmf"].dropna() > 0).all())

    def test_flat_bar_no_nan(self):
        n = 60
        c = np.full(n, 100.0)
        df = indicators.add_indicators(_frame(c + 0.5, c - 0.5, c))
        self.assertFalse(df["cmf"].iloc[30:].isna().any())

    def test_regime_filter_blocks_countertrend(self):
        # Steady downtrend: longs must never fire (price < 200-SMA).
        n = 400
        c = 500.0 - 0.5 * np.arange(n)
        h = c + 0.3
        l = c - 0.3
        df = _run(_frame(h, l, c))
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(55)
        n = 400
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
        h = c * (1 + rng.uniform(0, 0.005, n))
        l = c * (1 - rng.uniform(0, 0.005, n))
        df = _run(_frame(h, l, c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(57)
        n = 300
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
        h = c * (1 + 0.003)
        l = c * (1 - 0.003)
        full = indicators.add_indicators(_frame(h, l, c))
        cut = indicators.add_indicators(_frame(h[:200], l[:200], c[:200]))
        pd.testing.assert_series_equal(
            full["cmf"].iloc[:200], cut["cmf"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 220)


if __name__ == "__main__":
    unittest.main()
