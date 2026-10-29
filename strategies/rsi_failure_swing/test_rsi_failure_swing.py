"""RSI failure-swing tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_failure_swing import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame_from_segments(segments, start, prefix_bars=30):
    closes = [float(start)] * prefix_bars
    cur = float(start)
    for end, bars in segments:
        seg = np.linspace(cur, end, bars + 1)
        closes.extend(seg[:-1].tolist())
        cur = end
    closes.append(cur)
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestRsiFailureSwing(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("rsi", "rsi_fs_dir", "atr"):
            self.assertIn(col, df.columns, col)
        self.assertFalse(df["rsi"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["rsi_fs_dir"].isna().any())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_bullish_failure_swing_on_synthetic_rsi(self):
        # RSI path: flat, plunge to 20 (<30), rally to 44, dip to a
        # higher low 28, rally through 44 -> bullish trigger
        rsi = np.array([50.0] * 8 + [48, 44, 38, 30, 24, 20, 26, 32, 38, 44,
                                     40, 36, 30, 28, 34, 40, 46, 50], dtype=float)
        d = indicators.failure_swing_dir(rsi)
        self.assertTrue((d == 1).any())
        self.assertFalse((d == -1).any())

    def test_bearish_failure_swing_on_synthetic_rsi(self):
        # Mirror: surge to 80 (>70), fall to 56, rally to a lower
        # high 72, fall through 56 -> bearish trigger
        rsi = np.array([50.0] * 8 + [52, 56, 62, 70, 76, 80, 74, 68, 62, 56,
                                     60, 64, 68, 72, 66, 60, 54, 50], dtype=float)
        d = indicators.failure_swing_dir(rsi)
        self.assertTrue((d == -1).any())
        self.assertFalse((d == 1).any())

    def test_no_trigger_without_extreme_first_leg(self):
        # Same shape but the first low only reaches 35 (never <30):
        # not a failure swing
        rsi = np.array([50.0] * 8 + [48, 46, 42, 38, 35, 38, 42, 46,
                                     44, 40, 38, 44, 48], dtype=float)
        d = indicators.failure_swing_dir(rsi)
        self.assertFalse((d == 1).any())

    def test_no_trigger_when_second_low_is_lower(self):
        # Second low undercuts the first: momentum is NOT failing
        rsi = np.array([50.0] * 8 + [48, 44, 38, 30, 24, 20, 26, 32, 38, 44,
                                     40, 36, 30, 24, 18, 26, 34, 46], dtype=float)
        d = indicators.failure_swing_dir(rsi)
        self.assertFalse((d == 1).any())

    def test_bullish_end_to_end_on_price(self):
        # Steep drop (RSI plunges below 30), rebound, shallow dip,
        # rally: the RSI second low should sit above the first
        df = _run(_frame_from_segments(
            [(85, 6), (95, 10), (90, 12), (100, 10)], start=100))
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        df = _run(_frame_from_segments([(100, 60)], start=100, prefix_bars=0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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
        self.assertIn("rsi_failure_swing", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 50)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)
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
