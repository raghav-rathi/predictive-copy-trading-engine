"""Rectangle breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rectangle_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, volumes=None):
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5 if highs is None else np.asarray(highs, dtype=float)
    l = np.minimum(o, c) - 0.5 if lows is None else np.asarray(lows, dtype=float)
    v = np.full(n, 100.0) if volumes is None else np.asarray(volumes, dtype=float)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _consolidation_then_breakout(breakout_vol=300.0, breakout_close=105.0):
    closes = [100.5 if k % 2 == 0 else 99.5 for k in range(36)]
    vols = [100.0] * 36
    closes.append(breakout_close)
    vols.append(breakout_vol)
    closes.append(breakout_close)
    vols.append(100.0)
    df = _frame(closes, volumes=vols)
    # force the breakout bar's range above the rectangle
    df.loc[36, "h"] = breakout_close + 0.5
    df.loc[36, "l"] = breakout_close - 0.5
    return df


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


class TestRectangleBreakout(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_breakout_fires(self):
        df = _run(_consolidation_then_breakout())
        self.assertTrue(df["long_entry"].any())
        self.assertEqual(int(df["long_entry"].idxmax()), 36)

    def test_breakout_without_volume_does_not_fire(self):
        df = _run(_consolidation_then_breakout(breakout_vol=100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        df = _run(_frame([100.0] * 60))
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
        self.assertIn("rectangle_breakout", registry.REGISTRY)
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
