"""Linear regression channel tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.linear_regression_channel import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes * 1.001,
                         "l": closes * 0.999, "c": closes,
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestLinearRegressionChannel(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("lr_mid", "lr_upper", "lr_lower", "lr_slope",
                    "lr_std", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_linear_series_exact_fit(self):
        # Perfect line: slope 1, mid = current close, zero residual std,
        # so upper == lower == mid.
        df = _run(_frame([100.0 + i for i in range(200)]))
        row = df.iloc[99]
        self.assertAlmostEqual(row["lr_slope"], 1.0, places=9)
        self.assertAlmostEqual(row["lr_mid"], 199.0, places=9)
        self.assertAlmostEqual(row["lr_std"], 0.0, places=9)
        self.assertAlmostEqual(row["lr_upper"], row["lr_lower"], places=9)

    def test_constant_series(self):
        df = _run(_frame([100.0] * 200))
        self.assertAlmostEqual(df["lr_slope"].iloc[99], 0.0, places=9)
        self.assertAlmostEqual(df["lr_mid"].iloc[99], 100.0, places=9)
        self.assertAlmostEqual(df["lr_std"].iloc[99], 0.0, places=9)

    def test_polyfit_cross_check(self):
        # Closed-form channel must match np.polyfit on the same window.
        df = _run(_random_walk_frame())
        closes = df["c"].to_numpy()
        for idx in (60, 150, 300):
            win = closes[idx - 49:idx + 1]
            coef = np.polyfit(np.arange(50), win, 1)
            fitted = np.polyval(coef, np.arange(50))
            resid_std = float(np.std(win - fitted))
            self.assertAlmostEqual(df["lr_slope"].iloc[idx], coef[0], places=6)
            self.assertAlmostEqual(df["lr_mid"].iloc[idx], fitted[-1], places=6)
            self.assertAlmostEqual(df["lr_std"].iloc[idx], resid_std, places=6)

    def test_long_on_lower_band_cross(self):
        closes = [100.0] * 50 + [90.0] + [100.0] * 20
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[50])
        self.assertTrue(df["long_entry"].any())

    def test_short_on_upper_band_cross(self):
        closes = [100.0] * 50 + [110.0] + [100.0] * 20
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].iloc[50])
        self.assertTrue(df["short_entry"].any())

    def test_long_exit_on_mid_cross(self):
        closes = [100.0] * 50 + [90.0, 100.0] + [100.0] * 20
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())
        self.assertGreater(int(df["long_exit"].idxmax()),
                           int(df["long_entry"].idxmax()))

    def test_no_lookahead(self):
        df1 = _run(_random_walk_frame())
        frame = _random_walk_frame()
        frame.loc[frame.index[-1], "c"] = frame["c"].iloc[-1] * 1.5
        df2 = _run(frame)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_warmup_gating(self):
        # No channel exists before 50 bars, so no band-cross signal.
        df = _run(_random_walk_frame())
        self.assertFalse(df["long_entry"].iloc[:50].any())
        self.assertFalse(df["short_entry"].iloc[:50].any())

    def test_registration_and_warmup(self):
        self.assertIn("linear_regression_channel", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["linear_regression_channel"].slug,
                         "linear_regression_channel")
        self.assertEqual(risk.WARMUP, 55)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
