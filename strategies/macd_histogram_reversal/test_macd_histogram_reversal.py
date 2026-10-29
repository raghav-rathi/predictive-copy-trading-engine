"""MACD histogram reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_histogram_reversal import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


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


def _indicator_frame(hist):
    n = len(hist)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": np.zeros(n), "h": np.zeros(n), "l": np.zeros(n),
        "c": np.zeros(n), "v": np.zeros(n),
        "macd": np.zeros(n), "macd_signal": np.zeros(n),
        "macd_hist": np.asarray(hist, dtype=float),
        "atr": np.ones(n),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestMacdHistogramReversal(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("macd", "macd_signal", "macd_hist", "atr"):
            self.assertIn(col, df.columns, col)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_entry_on_trough_flip_below_zero(self):
        # Histogram falls -3 -> -5, then ticks up to -4: trough flip,
        # still below zero.
        df = signals.add_signals(_indicator_frame([-3.0, -5.0, -4.0]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_peak_flip_above_zero(self):
        df = signals.add_signals(_indicator_frame([3.0, 5.0, 4.0]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_on_monotonic_move_or_wrong_sign(self):
        # Monotonic decline is not a flip.
        df = signals.add_signals(_indicator_frame([-5.0, -4.0, -3.0]))
        self.assertFalse(df["long_entry"].any())
        # Trough flip above zero is chasing, not an Elder buy.
        df = signals.add_signals(_indicator_frame([3.0, 1.0, 2.0]))
        self.assertFalse(df["long_entry"].any())
        # Peak flip below zero is not a sell.
        df = signals.add_signals(_indicator_frame([-3.0, -1.0, -2.0]))
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        df = _run(_random_walk_frame(n=300, seed=11))
        flat = pd.DataFrame({"t": df["t"], "o": 100.0, "h": 100.0,
                             "l": 100.0, "c": 100.0, "v": 100.0})
        out = _run(flat)
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].any())

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
        self.assertIn("macd_histogram_reversal", registry.REGISTRY)
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
