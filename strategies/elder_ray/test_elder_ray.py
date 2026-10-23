"""Elder Ray tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elder_ray import indicators, risk, signals
from strategies import base as B

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(h, l, c):
    n = len(c)
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": np.asarray(c, dtype=float),
            "h": np.asarray(h, dtype=float),
            "l": np.asarray(l, dtype=float),
            "c": np.asarray(c, dtype=float),
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestElderRay(unittest.TestCase):
    def test_formula_independent(self):
        rng = np.random.default_rng(71)
        n = 120
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
        h = c * 1.003
        l = c * 0.997
        df = indicators.add_indicators(_frame(h, l, c))
        ema = B.ema(pd.Series(c), 13)
        pd.testing.assert_series_equal(df["bull_power"], h - ema, check_names=False)
        pd.testing.assert_series_equal(df["bear_power"], l - ema, check_names=False)

    def test_long_setup_logic(self):
        # Construct: rising EMA, bear power negative and turning up.
        n = 80
        c = 100.0 + 0.3 * np.arange(n)  # steady rise -> EMA rising
        h = c + 0.5
        # lows dip further then recover: bear power negative, turns up late
        dip = np.concatenate([np.linspace(0, -2.0, 40), np.linspace(-2.0, -0.2, 40)])
        l = c + dip
        df = _run(_frame(h, l, c))
        longs = df.index[df["long_entry"]]
        self.assertGreater(len(longs), 0)
        for i in longs:
            self.assertLess(df["bear_power"].iloc[i], 0)
            self.assertGreater(
                df["elder_ema"].iloc[i], df["elder_ema"].iloc[i - 1]
            )

    def test_flat_market_no_entries(self):
        n = 100
        c = np.full(n, 100.0)
        df = _run(_frame(c + 0.1, c - 0.1, c))
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(73)
        n = 250
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
        df = _run(_frame(c * 1.004, c * 0.996, c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(75)
        n = 200
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
        full = indicators.add_indicators(_frame(c * 1.004, c * 0.996, c))
        cut = indicators.add_indicators(_frame(c[:120] * 1.004, c[:120] * 0.996, c[:120]))
        pd.testing.assert_series_equal(
            full["bull_power"].iloc[:120], cut["bull_power"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
