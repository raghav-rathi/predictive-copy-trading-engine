"""Anchored VWAP tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.anchored_vwap import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

START = 1704067200000  # 2024-01-01 00:00 UTC


def _frame_rows(rows):
    n = len(rows)
    arr = np.array(rows, dtype=float)
    return pd.DataFrame({
        "t": (START + np.arange(n) * 3_600_000).astype("int64"),
        "o": arr[:, 0], "h": arr[:, 1], "l": arr[:, 2],
        "c": arr[:, 3], "v": arr[:, 4],
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


def _long_rows():
    # V bottom (swing low near bar 30), rise to 110, then six
    # wide bars whose closes (99) sit below the swing-low
    # AVWAP while their high typical prices (104) lift it, so
    # the AVWAP is rising when the recovery bar closes above it.
    rows = []
    p = 120.0
    for _ in range(30):
        rows.append((p, p + 0.05, p - 0.05, p, 100)); p -= 1.0
    for _ in range(20):
        rows.append((p, p + 0.05, p - 0.05, p, 100)); p += 1.0
    for _ in range(6):
        rows.append((100, 115, 98, 99, 100))
    rows.append((99, 105, 98, 104, 100))
    for _ in range(5):
        rows.append((104, 104.05, 103.95, 104, 100))
    return rows


def _short_rows():
    # Mirror: inverted-V top, fall to 90, then six wide bars
    # whose closes (101) sit above the swing-high AVWAP while
    # their low typical prices pull it down, then a bar closing
    # below it.
    rows = []
    p = 80.0
    for _ in range(30):
        rows.append((p, p + 0.05, p - 0.05, p, 100)); p += 1.0
    for _ in range(20):
        rows.append((p, p + 0.05, p - 0.05, p, 100)); p -= 1.0
    for _ in range(6):
        rows.append((100, 102, 85, 101, 100))
    rows.append((101, 102, 95, 96, 100))
    for _ in range(5):
        rows.append((96, 96.05, 95.95, 96, 100))
    return rows


class TestAnchoredVwap(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("avwap_low", "avwap_high"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].isna().any(), col)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_cross_above_rising_low_avwap(self):
        df = _run(_frame_rows(_long_rows()))
        self.assertTrue(df["long_entry"].iloc[56])
        self.assertTrue(df["avwap_low_rising"].iloc[56])
        self.assertFalse(df["short_entry"].iloc[:57].any())

    def test_short_cross_below_falling_high_avwap(self):
        df = _run(_frame_rows(_short_rows()))
        self.assertTrue(df["short_entry"].iloc[56])
        self.assertTrue(df["avwap_high_falling"].iloc[56])
        self.assertFalse(df["long_entry"].iloc[:57].any())

    def test_long_exit_on_cross_back_below(self):
        rows = _long_rows() + [(104, 104.05, 103.95, 104, 100),
                               (100, 100.05, 99.95, 99, 100)]
        df = _run(_frame_rows(rows))
        self.assertTrue(df["long_entry"].iloc[56])
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_short_exit_on_cross_back_above(self):
        rows = _short_rows() + [(96, 96.05, 95.95, 96, 100),
                                (100, 102, 99.95, 101, 100)]
        df = _run(_frame_rows(rows))
        self.assertTrue(df["short_entry"].iloc[56])
        self.assertTrue(df["short_exit"].iloc[-1])

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
        import strategies.anchored_vwap as pkg  # noqa: F401
        self.assertIn("anchored_vwap", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["anchored_vwap"].slug, "anchored_vwap")
        self.assertEqual(risk.WARMUP, 30)

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
