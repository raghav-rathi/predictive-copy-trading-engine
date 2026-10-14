"""Qstick tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.qstick import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(o, c):
    o = np.asarray(o, dtype=float)
    c = np.asarray(c, dtype=float)
    n = len(c)
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": o,
            "h": np.maximum(o, c) + 0.1,
            "l": np.minimum(o, c) - 0.1,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestQstick(unittest.TestCase):
    def test_formula_independent(self):
        rng = np.random.default_rng(31)
        n = 120
        o = 100 + rng.normal(0, 1, n).cumsum()
        c = o + rng.normal(0, 1, n)
        df = indicators.add_indicators(_frame(o, c))
        body = pd.Series(c - o)
        expect = body.rolling(8, min_periods=8).mean()
        pd.testing.assert_series_equal(df["qstick"], expect, check_names=False)
        expect_trig = expect.rolling(8, min_periods=8).mean()
        pd.testing.assert_series_equal(
            df["qstick_trigger"], expect_trig, check_names=False
        )

    def test_all_up_bodies_positive(self):
        n = 40
        o = np.arange(n, dtype=float)
        c = o + 1.0  # every bar closes up
        df = indicators.add_indicators(_frame(o, c))
        self.assertTrue((df["qstick"].dropna() > 0).all())

    def test_long_cross_after_downtrend(self):
        # Downtrend (negative bodies) then uptrend: must cross above zero.
        n1, n2 = 60, 120
        o1 = 200.0 - np.arange(n1, dtype=float)
        c1 = o1 - 1.0
        o2 = np.full(n2, o1[-1])
        c2 = o2 + 1.0 + 0.05 * np.arange(n2)
        df = _run(_frame(np.concatenate([o1, o2]), np.concatenate([c1, c2])))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(8)
        n = 150
        o = 100 + rng.normal(0, 1, n).cumsum()
        c = o + rng.normal(0, 1, n)
        df = _run(_frame(o, c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(12)
        n = 200
        o = 100 + rng.normal(0, 1, n).cumsum()
        c = o + rng.normal(0, 1, n)
        full = indicators.add_indicators(_frame(o, c))
        cut = indicators.add_indicators(_frame(o[:120], c[:120]))
        pd.testing.assert_series_equal(
            full["qstick"].iloc[:120], cut["qstick"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
