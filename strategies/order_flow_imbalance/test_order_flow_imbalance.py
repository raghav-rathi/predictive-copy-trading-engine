"""Order-flow imbalance tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.order_flow_imbalance import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

START = 1704067200000  # 2024-01-01 00:00 UTC


def _frame(rows):
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


NEUTRAL = (100, 101, 99, 100, 100)   # doji: delta 0
GREEN = (100, 102, 99, 101, 100)     # delta = +100/3
RED = (101, 102, 99, 99, 100)       # delta = -200/3, closes below EMA


def _long_rows():
    # 25 neutral bars (imbalance 0, EMA settles at 100), then
    # green bars: imbalance 0.067, 0.133, 0.200, 0.267 -> the
    # +0.25 cross lands on the 4th green bar (index 28) with
    # close 101 above EMA(20).
    return [NEUTRAL] * 25 + [GREEN] * 6


def _short_rows():
    return [NEUTRAL] * 25 + [RED] * 6


class TestOrderFlowImbalance(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("bar_delta", "ema20"):
            self.assertIn(col, df.columns)
        self.assertFalse(df["imbalance"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["ema20"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())

    def test_imbalance_bounded_and_delta_clipped(self):
        df = _run(_random_walk_frame())
        imb = df["imbalance"].dropna()
        self.assertTrue(((imb >= -1.0) & (imb <= 1.0)).all())
        self.assertTrue((df["bar_delta"].abs() <= df["v"] + 1e-9).all())

    def test_bar_delta_values(self):
        df = indicators.add_indicators(_frame([GREEN, RED, NEUTRAL]))
        # GREEN needs 5 bars for a defined imbalance, but delta
        # itself is per-bar: +100/3, -200/3, 0.
        self.assertAlmostEqual(df["bar_delta"].iloc[0], 100 / 3, places=6)
        self.assertAlmostEqual(df["bar_delta"].iloc[1], -200 / 3, places=6)
        self.assertAlmostEqual(df["bar_delta"].iloc[2], 0.0, places=6)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_cross_above_plus_025(self):
        df = _run(_frame(_long_rows()))
        self.assertLessEqual(df["imbalance"].iloc[27], 0.25)
        self.assertGreater(df["imbalance"].iloc[28], 0.25)
        self.assertGreater(df["c"].iloc[28], df["ema20"].iloc[28])
        self.assertTrue(df["long_entry"].iloc[28])
        self.assertFalse(df["short_entry"].any())

    def test_short_cross_below_minus_025(self):
        df = _run(_frame(_short_rows()))
        # 2nd red bar (index 26): imbalance -0.267 crosses -0.25.
        self.assertGreaterEqual(df["imbalance"].iloc[25], -0.25)
        self.assertLess(df["imbalance"].iloc[26], -0.25)
        self.assertLess(df["c"].iloc[26], df["ema20"].iloc[26])
        self.assertTrue(df["short_entry"].iloc[26])
        self.assertFalse(df["long_entry"].any())

    def test_long_exit_on_zero_cross(self):
        rows = _long_rows() + [RED] * 6
        df = _run(_frame(rows))
        self.assertTrue(df["long_entry"].iloc[28])
        self.assertTrue(df["long_exit"].iloc[28:].any())

    def test_short_exit_on_zero_cross(self):
        rows = _short_rows() + [GREEN] * 6
        df = _run(_frame(rows))
        self.assertTrue(df["short_entry"].iloc[26])
        self.assertTrue(df["short_exit"].iloc[26:].any())

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
        import strategies.order_flow_imbalance as pkg  # noqa: F401
        self.assertIn("order_flow_imbalance", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["order_flow_imbalance"].slug,
                         "order_flow_imbalance")
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
