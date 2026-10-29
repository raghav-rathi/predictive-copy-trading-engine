"""Counterattack lines tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.counterattack_lines import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(pairs):
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


class TestCounterattackLines(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        self.assertIn("counterattack_dir", df.columns)
        self.assertIn("atr", df.columns)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["counterattack_dir"].isna().any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_bullish_counterattack_long(self):
        # downtrend prefix (closes 110 -> 101), then black
        # 100 -> 92, then white gapping down at the open (88)
        # and closing back at 92 — exactly the prior close,
        # same-size body (8 vs 8... white body is 4; use 84->92
        # for an 8-point body: open 84 gaps below close 92)
        pairs = [(110 - i, 110 - i) for i in range(20)]
        pairs += [(100, 92), (84, 92)]
        df = _run(_frame(pairs))
        self.assertEqual(df["counterattack_dir"].iloc[-1], 1)
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_bearish_counterattack_short(self):
        pairs = [(90 + i, 90 + i) for i in range(20)]
        pairs += [(100, 108), (116, 108)]
        df = _run(_frame(pairs))
        self.assertEqual(df["counterattack_dir"].iloc[-1], -1)
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_piercing_too_deep_is_not_counterattack(self):
        # bullish shape, but the white candle closes well ABOVE
        # the prior close (98 vs 92): that is a piercing-style
        # push into the body, not a counterattack stalemate.
        # ATR here is small (flat prefix + 8-point bodies), so
        # 0.2*ATR tolerance (~0.3) is far below the 6-point gap.
        pairs = [(110 - i, 110 - i) for i in range(20)]
        pairs += [(100, 92), (84, 98)]
        df = _run(_frame(pairs))
        self.assertFalse(df["long_entry"].any())

    def test_mismatched_size_no_counterattack(self):
        # same closes, but the white body (2) is far smaller than
        # the black body (10): ratio 0.2 < 2/3, rejected
        pairs = [(110 - i, 110 - i) for i in range(20)]
        pairs += [(100, 90), (88, 90)]
        df = _run(_frame(pairs))
        self.assertFalse(df["long_entry"].any())

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
        self.assertIn("counterattack_lines", registry.REGISTRY)
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
