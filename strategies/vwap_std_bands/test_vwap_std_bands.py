"""VWAP std bands tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vwap_std_bands import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

START = 1704067200000  # 2024-01-01 00:00 UTC


def _frame(pairs):
    o = np.array([p[0] for p in pairs], dtype=float)
    c = np.array([p[1] for p in pairs], dtype=float)
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    n = len(pairs)
    return pd.DataFrame({
        "t": (START + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    return pd.DataFrame({
        "t": (START + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": h, "l": l, "c": c, "v": rng.uniform(50, 150, n),
    })


def _sine_prefix():
    return [(100 + 2 * np.sin(i * 0.7), 100 + 2 * np.sin(i * 0.7))
            for i in range(40)]


def _long_pairs():
    # Dip breaches the -2 sigma band (bar 42, close 92 below
    # lower_2 ~94.9) and the recovery bar 44 closes back above it.
    return (_sine_prefix() + [(100, 100), (98, 96), (96, 92),
                              (92, 94), (94, 97), (97, 99), (99, 100)])


def _short_pairs():
    # Mirror spike: bar 42 close 108 above upper_2 ~104.7,
    # bar 44 closes back below it.
    return (_sine_prefix() + [(100, 100), (102, 104), (104, 108),
                              (108, 106), (106, 103), (103, 101),
                              (101, 100)])


class TestVwapStdBands(unittest.TestCase):
    def test_indicator_columns_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("vwap", "vwap_sigma", "vwap_upper_1", "vwap_lower_1",
                    "vwap_upper_2", "vwap_lower_2"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].isna().any(), col)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())

    def test_band_ordering(self):
        df = _run(_random_walk_frame())
        self.assertTrue((df["vwap_upper_2"] >= df["vwap_upper_1"]).all())
        self.assertTrue((df["vwap_upper_1"] >= df["vwap"]).all())
        self.assertTrue((df["vwap"] >= df["vwap_lower_1"]).all())
        self.assertTrue((df["vwap_lower_1"] >= df["vwap_lower_2"]).all())
        self.assertTrue((df["vwap_sigma"] >= 0).all())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_recovery_above_minus_2sigma(self):
        df = _run(_frame(_long_pairs()))
        self.assertLessEqual(df["c"].iloc[42], df["vwap_lower_2"].iloc[42])
        self.assertGreater(df["c"].iloc[44], df["vwap_lower_2"].iloc[44])
        self.assertTrue(df["long_entry"].iloc[44])

    def test_short_recovery_below_plus_2sigma(self):
        df = _run(_frame(_short_pairs()))
        self.assertGreaterEqual(df["c"].iloc[42], df["vwap_upper_2"].iloc[42])
        self.assertLess(df["c"].iloc[44], df["vwap_upper_2"].iloc[44])
        self.assertTrue(df["short_entry"].iloc[44])

    def test_long_exit_at_vwap_midline(self):
        df = _run(_frame(_long_pairs()))
        self.assertTrue(df["long_entry"].iloc[44])
        # Bar 45 closes at 99, at/above the session VWAP (~98.99).
        self.assertTrue(df["long_exit"].iloc[45])

    def test_short_exit_at_vwap_midline(self):
        df = _run(_frame(_short_pairs()))
        self.assertTrue(df["short_entry"].iloc[44])
        # Bar 45 closes at 101, at/below the session VWAP (~101.02).
        self.assertTrue(df["short_exit"].iloc[45])

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        import strategies.vwap_std_bands as pkg  # noqa: F401
        self.assertIn("vwap_std_bands", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["vwap_std_bands"].slug, "vwap_std_bands")
        self.assertEqual(risk.WARMUP, 25)

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
