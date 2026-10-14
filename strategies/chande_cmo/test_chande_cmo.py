"""Chande Momentum Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chande_cmo import indicators, risk, signals

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


class TestChandeCmo(unittest.TestCase):
    def test_formula_independent(self):
        rng = np.random.default_rng(61)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        df = indicators.add_indicators(_frame(c))
        d = np.full_like(c, np.nan)
        d[1:] = np.diff(c)
        up = np.where(d > 0, d, 0.0)
        dn = np.where(d < 0, -d, 0.0)
        up[np.isnan(d)] = np.nan  # match pandas diff(): bar 0 is NaN, not 0
        dn[np.isnan(d)] = np.nan
        su = pd.Series(up).rolling(14, min_periods=14).sum()
        sd = pd.Series(dn).rolling(14, min_periods=14).sum()
        expect = (100.0 * (su - sd) / (su + sd)).fillna(0.0)
        pd.testing.assert_series_equal(df["cmo"], expect, check_names=False)

    def test_bounds(self):
        rng = np.random.default_rng(62)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, 300)))
        df = indicators.add_indicators(_frame(c)).dropna()
        self.assertTrue(((df["cmo"] >= -100) & (df["cmo"] <= 100)).all())

    def test_all_up_days_is_100(self):
        c = 100.0 + np.arange(40)
        df = indicators.add_indicators(_frame(c))
        self.assertAlmostEqual(df["cmo"].iloc[-1], 100.0, places=9)

    def test_oversold_recovery_gives_long(self):
        rng = np.random.default_rng(63)
        n1, n2 = 60, 160
        c1 = 200.0 - 1.5 * np.arange(n1) + rng.normal(0, 0.3, n1).cumsum() * 0.05
        c2 = c1[-1] + 0.8 * np.arange(n2) + rng.normal(0, 0.3, n2).cumsum() * 0.05
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_long_entry_crosses_minus50(self):
        rng = np.random.default_rng(64)
        c = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.02, 600)))
        df = _run(_frame(c))
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx:
            self.assertLessEqual(df["cmo"].iloc[i - 1], -50.0)
            self.assertGreater(df["cmo"].iloc[i], -50.0)

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(65)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 250)))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(66)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))
        full = indicators.add_indicators(_frame(c))
        cut = indicators.add_indicators(_frame(c[:200]))
        pd.testing.assert_series_equal(
            full["cmo"].iloc[:200], cut["cmo"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
