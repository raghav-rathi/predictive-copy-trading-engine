"""Coppock Curve tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.coppock_curve import indicators, risk, signals

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


class TestCoppockCurve(unittest.TestCase):
    def test_formula_independent(self):
        # Independent recomputation: WMA(10) of ROC14+ROC11.
        c = 100.0 + 0.3 * np.arange(120)
        df = indicators.add_indicators(_frame(c))
        cc = np.asarray(c, dtype=float)
        roc14 = np.full_like(cc, np.nan)
        roc11 = np.full_like(cc, np.nan)
        roc14[14:] = 100 * (cc[14:] - cc[:-14]) / cc[:-14]
        roc11[11:] = 100 * (cc[11:] - cc[:-11]) / cc[:-11]
        mom = roc14 + roc11
        w = np.arange(1, 11, dtype=float)
        expect = np.full_like(cc, np.nan)
        for i in range(9, len(cc)):
            win = mom[i - 9 : i + 1]
            if not np.isnan(win).any():
                expect[i] = float((win * w).sum() / w.sum())
        got = df["coppock"].to_numpy()
        mask = ~np.isnan(expect)
        self.assertTrue(mask.sum() > 50)
        np.testing.assert_allclose(got[mask], expect[mask], rtol=1e-9)

    def test_warmup_nans_then_valid(self):
        c = 100.0 + 0.1 * np.arange(100)
        df = indicators.add_indicators(_frame(c))
        self.assertTrue(df["coppock"].iloc[:23].isna().all())
        self.assertTrue(np.isfinite(df["coppock"].iloc[-1]))

    def test_long_cross_on_recovery(self):
        # Deep selloff then steady recovery: curve must cross above zero.
        rng = np.random.default_rng(3)
        n1, n2 = 120, 300
        c1 = 200.0 - 0.8 * np.arange(n1) + rng.normal(0, 0.3, n1).cumsum() * 0.05
        c2 = c1[-1] + 0.7 * np.arange(n2) + rng.normal(0, 0.3, n2).cumsum() * 0.05
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_signal_columns_boolean_no_nan(self):
        c = 100.0 + np.sin(np.arange(200) / 8.0) * 5.0
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")
            self.assertFalse(df[col].isna().any())

    def test_no_lookahead(self):
        # Truncating the frame must not change earlier indicator values.
        rng = np.random.default_rng(11)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))
        full = indicators.add_indicators(_frame(c))
        cut = indicators.add_indicators(_frame(c[:200]))
        pd.testing.assert_series_equal(
            full["coppock"].iloc[:200], cut["coppock"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
