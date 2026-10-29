"""Kicker pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kicker_pattern import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(pairs):
    """pairs: list of (open, close). h/l padded around the body."""
    o = np.array([p[0] for p in pairs], dtype=float)
    c = np.array([p[1] for p in pairs], dtype=float)
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    n = len(pairs)
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


class TestKickerPattern(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        self.assertIn("kicker_dir", df.columns)
        self.assertIn("atr", df.columns)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["kicker_dir"].isna().any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_bullish_kicker_long(self):
        # black candle 100 -> 95, then white candle gapping beyond
        # the first open: open 101, close 108 (body 7 of range 7.1)
        pairs = [(100, 100)] * 20 + [(100, 95), (101, 108)]
        df = _run(_frame(pairs))
        self.assertEqual(df["kicker_dir"].iloc[-1], 1)
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_bearish_kicker_short(self):
        pairs = [(100, 100)] * 20 + [(100, 105), (99, 92)]
        df = _run(_frame(pairs))
        self.assertEqual(df["kicker_dir"].iloc[-1], -1)
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_no_gap_no_kicker(self):
        # second candle reverses but opens INSIDE the first open:
        # black 100 -> 95, white open 98 (below first open 100)
        pairs = [(100, 100)] * 20 + [(100, 95), (98, 104)]
        df = _run(_frame(pairs))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_weak_second_body_no_kicker(self):
        # gap present but second candle has a tiny body vs wide
        # wicks (body 0.2 vs range 10.2), so it is not a kicker
        pairs = [(100, 100)] * 20 + [(100, 90), (101, 101.2)]
        o = np.array([p[0] for p in pairs], dtype=float)
        c = np.array([p[1] for p in pairs], dtype=float)
        h = np.maximum(o, c) + 5.0
        l = np.minimum(o, c) - 5.0
        n = len(pairs)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        wide = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                             "v": np.full(n, 100.0)})
        df2 = _run(wide)
        self.assertFalse(df2["long_entry"].any())

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
        self.assertIn("kicker_pattern", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 20)

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
