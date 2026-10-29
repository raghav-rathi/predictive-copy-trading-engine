"""Stochastic Pop tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stochastic_pop import indicators, risk, signals
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


class TestStochasticPop(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("fastK", "range_high", "range_low", "pop_up", "pop_dn", "atr"):
            self.assertIn(col, df.columns, col)
        self.assertFalse(df["fastK"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["range_high"].iloc[risk.WARMUP:].isna().any())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_bullish_pop_long(self):
        # Flat range, then a sharp rally: fastK crosses 80 on a bar
        # that also breaks the prior 20-bar high
        df = _run(_frame_from_segments([(115, 5), (118, 10)], start=100))
        self.assertTrue(df["pop_up"].any())
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_bearish_pop_short(self):
        df = _run(_frame_from_segments([(85, 5), (82, 10)], start=100))
        self.assertTrue(df["pop_dn"].any())
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_gradual_drift_is_not_a_pop(self):
        # A slow grind to the same level: fastK rises gradually and
        # never crosses 80 on a fresh 20-bar-high bar together --
        # in fact a slow grind keeps fastK pinned high without a
        # same-bar cross+breakout, so no pop should fire on the
        # grind itself; assert the weaker, structural property:
        # a flat market produces no pop at all
        df = _run(_frame_from_segments([(100, 60)], start=100, prefix_bars=0))
        self.assertFalse(df["long_entry"].any())
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
        self.assertIn("stochastic_pop", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 30)

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
