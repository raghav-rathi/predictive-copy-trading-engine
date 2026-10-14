"""SMI Ergodic tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.smi_ergodic import indicators, risk, signals

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


def _ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False, min_periods=n).mean().to_numpy()


class TestSmiErgodic(unittest.TestCase):
    def test_formula_independent(self):
        rng = np.random.default_rng(9)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 400)))
        df = indicators.add_indicators(_frame(c))
        d = np.full_like(c, np.nan)
        d[1:] = np.diff(c)
        num = _ema(_ema(d, 20), 5)
        den = _ema(_ema(np.abs(d), 20), 5)
        expect = 100 * num / den
        got = df["smi"].to_numpy()
        mask = ~np.isnan(expect)
        self.assertTrue(mask.sum() > 300)
        np.testing.assert_allclose(got[mask], expect[mask], rtol=1e-9)

    def test_bounded(self):
        rng = np.random.default_rng(4)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, 500)))
        df = indicators.add_indicators(_frame(c))
        valid = df["smi"].dropna()
        self.assertTrue(((valid >= -100) & (valid <= 100)).all())

    def test_long_on_sustained_rally(self):
        rng = np.random.default_rng(6)
        n1, n2 = 150, 250
        c1 = 100.0 + rng.normal(0, 0.5, n1).cumsum() * 0.1
        c2 = c1[-1] + 0.4 * np.arange(n2) + rng.normal(0, 0.5, n2).cumsum() * 0.1
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_regime_filter_blocks_countertrend_cross(self):
        # Build a frame where SMI is deeply negative: no long entries allowed.
        c = 200.0 - 0.5 * np.arange(400)
        df = _run(_frame(c))
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_signal_columns_boolean_no_nan(self):
        c = 100.0 + np.sin(np.arange(300) / 6.0) * 4.0
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(21)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))
        full = indicators.add_indicators(_frame(c))
        cut = indicators.add_indicators(_frame(c[:200]))
        pd.testing.assert_series_equal(
            full["smi"].iloc[:200], cut["smi"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
