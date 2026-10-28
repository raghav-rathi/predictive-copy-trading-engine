"""PPO signal-line cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ppo_cross import indicators, risk, signals
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


class TestPpoCross(unittest.TestCase):
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
        self.assertIn("ppo_cross", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["ppo_cross"].warmup_bars, risk.WARMUP)
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
        for col in ("ppo", "ppo_signal", "ppo_hist", "atr"):
            self.assertIn(col, df.columns)
        self.assertFalse(df["ppo"].iloc[40:].isna().any())

    def test_ppo_crosses_on_trend_change(self):
        # PPO rises above its signal line on the up-leg and falls below
        # it on the down-leg.
        df = _run(_path([(140, 50), (90, 50)], start=100, prefix_bars=40))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["short_entry"].any())

    def test_ppo_is_percentage_normalised(self):
        # Same percentage path at 10x price level gives (near-)identical
        # PPO readings: normalisation removes the price level.
        df1 = indicators.add_indicators(_path([(140, 50)], start=100, prefix_bars=40))
        df2 = indicators.add_indicators(_path([(1400, 50)], start=1000, prefix_bars=40))
        a = df1["ppo"].iloc[40:].to_numpy()
        b = df2["ppo"].iloc[40:].to_numpy()
        np.testing.assert_allclose(a, b, rtol=1e-6, atol=1e-9)


if __name__ == "__main__":
    unittest.main()
