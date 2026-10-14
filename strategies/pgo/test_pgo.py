"""Pretty Good Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pgo import indicators, risk, signals
from strategies import base as B

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.5):
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


class TestPgo(unittest.TestCase):
    def test_formula_independent(self):
        rng = np.random.default_rng(91)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        df = _frame(c)
        got = indicators.add_indicators(df)
        cc = pd.Series(c)
        dist = cc - cc.rolling(14, min_periods=14).mean()
        vol = B.atr(df["h"], df["l"], df["c"], 14)
        expect = dist / vol
        pd.testing.assert_series_equal(got["pgo"], expect, check_names=False)

    def test_thrust_up_gives_positive_pgo(self):
        # Steady climb: close sits above its mean -> PGO positive.
        c = 100.0 + 0.5 * np.arange(60)
        df = indicators.add_indicators(_frame(c))
        self.assertGreater(df["pgo"].iloc[-1], 1.0)

    def test_breakout_entry_on_thrust(self):
        # Flat then a sharp thrust: PGO must cross +1.
        rng = np.random.default_rng(93)
        n1, n2 = 80, 60
        c1 = 100.0 + rng.normal(0, 0.1, n1).cumsum() * 0.1
        c2 = c1[-1] + 3.0 * np.arange(n2)
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_long_entry_crosses_plus_one(self):
        rng = np.random.default_rng(95)
        c = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 600)))
        df = _run(_frame(c))
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx:
            self.assertLessEqual(df["pgo"].iloc[i - 1], 1.0)
            self.assertGreater(df["pgo"].iloc[i], 1.0)

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(97)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 250)))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(99)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))
        full = indicators.add_indicators(_frame(c))
        cut = indicators.add_indicators(_frame(c[:200]))
        pd.testing.assert_series_equal(
            full["pgo"].iloc[:200], cut["pgo"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
