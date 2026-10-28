"""RSI + MACD confluence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_macd_combo import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _path(segments, start, prefix_bars=0):
    """segments = [(end, bars), ...]; joints shared, no jumps."""
    closes = [float(start)] * prefix_bars
    cur = start
    for end, bars in segments:
        seg = np.linspace(cur, end, bars + 1)
        closes.extend(seg[:-1].tolist())
        cur = end
    closes.append(cur)
    return _frame(closes)


def _random_walk_frame(n=300, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestRsiMacdCombo(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_path([(120, 40), (90, 40)], start=100, prefix_bars=40))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_flat_data_no_entries(self):
        df = _run(_frame([100.0] * 120))
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
        self.assertIn("rsi_macd_combo", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["rsi_macd_combo"].warmup_bars, risk.WARMUP)
        self.assertEqual(risk.WARMUP, 40)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertIsNone(risk.RISK.target_atr_mult)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)
        self.assertEqual(len(res.equity), len(df))

    def test_indicators_present(self):
        df = indicators.add_indicators(_path([(120, 40)], start=100, prefix_bars=40))
        for col in ("rsi", "macd", "macd_signal", "macd_hist", "atr"):
            self.assertIn(col, df.columns)
        self.assertFalse(df["rsi"].iloc[40:].isna().any())

    def test_long_on_rsi_cross_with_positive_hist(self):
        # Fall then sustained rise: RSI crosses above 50 while the
        # MACD histogram is positive.
        df = _run(_path([(80, 30), (110, 40)], start=100, prefix_bars=40))
        self.assertTrue(df["long_entry"].any())

    def test_short_on_rsi_cross_with_negative_hist(self):
        df = _run(_path([(120, 30), (90, 40)], start=100, prefix_bars=40))
        self.assertTrue(df["short_entry"].any())

    def test_hist_filter_blocks_divergent_cross(self):
        # A one-bar RSI blip above 50 while the histogram is still
        # negative must not fire: check the entry rule directly on a
        # hand-built frame where RSI crosses up but hist < 0.
        df = _frame([100.0] * 60)
        df = indicators.add_indicators(df)
        df.loc[50, "rsi"] = 49.0
        df.loc[51, "rsi"] = 51.0
        df.loc[51, "macd_hist"] = -0.5
        out = signals.add_signals(df)
        self.assertFalse(out.loc[51, "long_entry"])


if __name__ == "__main__":
    unittest.main()
