"""Linear regression slope tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.linear_regression_slope import indicators, risk, signals


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=130, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(slope, r2, closes=None):
    n = len(slope)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "c": c,
        "linreg_slope": np.array(slope, dtype=float),
        "linreg_r2": np.array(r2, dtype=float),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestLinearRegressionSlope(unittest.TestCase):
    def test_registered(self):
        self.assertIn("linear_regression_slope", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: slope 0, R^2 0 (no variance to explain), fitted
        # value equals the price.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[indicators.PERIOD:]
        self.assertTrue(np.allclose(tail["linreg_slope"], 0.0))
        self.assertTrue(np.allclose(tail["linreg_r2"], 0.0))
        self.assertTrue(np.allclose(tail["linreg_value"], 100.0))
        self.assertTrue(df.iloc[: indicators.PERIOD - 1]["linreg_slope"].isna().all())

    def test_indicator_values_perfect_line(self):
        # Exact line close = 100 + 0.5*i: slope 0.5, R^2 1, fitted
        # value at bar i equals the close.
        closes = 100 + 0.5 * np.arange(200)
        df = indicators.add_indicators(_frame(closes))
        for i in (50, 100, 199):
            self.assertAlmostEqual(df["linreg_slope"].iloc[i], 0.5, places=9)
            self.assertAlmostEqual(df["linreg_r2"].iloc[i], 1.0, places=9)
            self.assertAlmostEqual(df["linreg_value"].iloc[i], closes[i], places=9)
            self.assertAlmostEqual(
                df["linreg_slope_norm"].iloc[i], 0.5 / closes[i], places=12)

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        valid = df["linreg_r2"].dropna()
        self.assertGreater(len(valid), 50)
        self.assertTrue(((valid >= 0) & (valid <= 1)).all())
        self.assertTrue(np.isfinite(df["linreg_slope"].dropna()).all())
        # R^2 must equal the squared Pearson correlation of close
        # against bar index over the same window (independent check).
        c = df["c"].to_numpy()
        x = np.arange(20, dtype=float)
        for i in (100, 250, 399):
            w = c[i - 19: i + 1]
            r = np.corrcoef(x, w)[0, 1]
            self.assertAlmostEqual(df["linreg_r2"].iloc[i], r * r, places=9)

    def test_indicator_values_downtrend(self):
        # Steady -1%/bar fall: slope negative, R^2 near 1.
        closes = 100 * (0.99 ** np.arange(200))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[150:]
        self.assertTrue((tail["linreg_slope"] < 0).all())
        self.assertTrue((tail["linreg_r2"] > 0.9).all())

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.WARMUP, 50)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_slope_turn(self):
        # Slope turns positive at index 1 with R^2 0.6 >= 0.5.
        df = signals.add_signals(_signal_frame(
            [-0.1, 0.05, 0.1, 0.1], [0.6, 0.6, 0.6, 0.6]))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_short_entry_on_slope_turn(self):
        df = signals.add_signals(_signal_frame(
            [0.1, -0.05, -0.1, -0.1], [0.6, 0.6, 0.6, 0.6]))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_no_entry_without_strong_r2(self):
        # Slope turns positive but R^2 is 0.4 < 0.5: no entry.
        df = signals.add_signals(_signal_frame(
            [-0.1, 0.05, 0.1], [0.4, 0.4, 0.4]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_turn(self):
        # Slope already positive (no turn): no entry.
        df = signals.add_signals(_signal_frame(
            [0.05, 0.1, 0.15], [0.6, 0.6, 0.6]))
        self.assertFalse(df["long_entry"].any())

    def test_exit_on_slope_flip(self):
        # Long exit when the slope turns negative.
        df = signals.add_signals(_signal_frame(
            [0.1, 0.1, -0.05], [0.6, 0.6, 0.6]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        # Short exit when the slope turns positive.
        df = signals.add_signals(_signal_frame(
            [-0.1, -0.1, 0.05], [0.6, 0.6, 0.6]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_exit_on_r2_collapse(self):
        # R^2 falls to 0.2 < 0.3: both sides exit even with slope
        # still pointing the "right" way.
        df = signals.add_signals(_signal_frame(
            [0.1, 0.1, 0.1], [0.6, 0.6, 0.2]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertTrue(df["short_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_determinism(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 100))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [500.0] * 50))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue((df1[col].iloc[:100] == df2[col].iloc[:100]).all())

    def test_edge_short_frame(self):
        # Fewer bars than the 20-bar window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["linreg_slope"].isna().all())


if __name__ == "__main__":
    unittest.main()
