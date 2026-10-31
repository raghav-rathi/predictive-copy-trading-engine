"""Wyckoff upthrust tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wyckoff_upthrust import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.array(o, float), "h": np.array(h, float),
                         "l": np.array(l, float), "c": np.array(c, float),
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


def _flat_range(n=20):
    return ([100.0] * n, [110.0] * n, [90.0] * n, [100.0] * n)


class TestWyckoffUpthrust(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("range_high", "range_low", "upthrust", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_range_uses_prior_bars_only(self):
        # 20 flat bars (high 110), then a bar with high 200: the range
        # high ON that bar must still be 110, not 200.
        o, h, l, c = _flat_range(20)
        df = _run(_frame(o + [105.0], h + [200.0], l + [95.0], c + [105.0]))
        self.assertEqual(df["range_high"].iloc[20], 110.0)
        self.assertEqual(df["range_low"].iloc[20], 90.0)

    def test_upthrust_bar_triggers_short(self):
        o, h, l, c = _flat_range(20)
        df = _run(_frame(o + [105.0], h + [115.0], l + [95.0], c + [105.0]))
        self.assertTrue(df["upthrust"].iloc[20])
        self.assertTrue(df["short_entry"].iloc[20])

    def test_genuine_breakout_is_not_upthrust(self):
        # High above the range AND close above the range: a real
        # breakout, not a failed one.
        o, h, l, c = _flat_range(20)
        df = _run(_frame(o + [112.0], h + [115.0], l + [95.0], c + [112.0]))
        self.assertFalse(df["upthrust"].iloc[20])
        self.assertFalse(df["short_entry"].iloc[20])

    def test_no_breakout_is_not_upthrust(self):
        o, h, l, c = _flat_range(20)
        df = _run(_frame(o + [105.0], h + [108.0], l + [95.0], c + [105.0]))
        self.assertFalse(df["upthrust"].iloc[20])
        self.assertFalse(df["short_entry"].iloc[20])

    def test_close_below_range_low_is_not_upthrust(self):
        # Breaks above but closes below the range low: not an upthrust
        # close back inside the range.
        o, h, l, c = _flat_range(20)
        df = _run(_frame(o + [85.0], h + [115.0], l + [80.0], c + [85.0]))
        self.assertFalse(df["upthrust"].iloc[20])

    def test_short_exit_on_reclaim(self):
        # Flat range, upthrust bar, then a bar closing at 118 above
        # the prior-20-bar high of 115 -> reclaim exit.
        o, h, l, c = _flat_range(20)
        df = _run(_frame(o + [105.0, 118.0], h + [115.0, 120.0],
                         l + [95.0, 110.0], c + [105.0, 118.0]))
        self.assertTrue(df["short_entry"].iloc[20])
        self.assertTrue(df["short_exit"].iloc[21])

    def test_never_long(self):
        df = _run(_random_walk_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["long_exit"].any())

    def test_no_lookahead_last_bar(self):
        frame = _random_walk_frame()
        df1 = _run(frame)
        mod = frame.copy()
        mod.loc[mod.index[-1], "c"] = mod["c"].iloc[-1] * 1.5
        mod.loc[mod.index[-1], "h"] = mod["h"].iloc[-1] * 1.5
        df2 = _run(mod)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("wyckoff_upthrust", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 25)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertFalse(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
