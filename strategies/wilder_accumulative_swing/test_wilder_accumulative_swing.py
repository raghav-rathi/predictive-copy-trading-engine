"""Wilder Accumulative Swing Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wilder_accumulative_swing import indicators, risk, signals
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


def _trend_series():
    # 20 rising bars, 20 falling bars, 20 rising bars: ASI follows
    # price, so it must cross its EMA down then up.
    up1 = [100.0 + 1.0 * i for i in range(20)]
    dn = [up1[-1] - 1.5 * (i + 1) for i in range(20)]
    up2 = [dn[-1] + 1.5 * (i + 1) for i in range(20)]
    closes = up1 + dn + up2
    opens = [closes[0]] + closes[:-1]
    highs = [max(o, c) + 0.5 for o, c in zip(opens, closes)]
    lows = [min(o, c) - 0.5 for o, c in zip(opens, closes)]
    return opens, highs, lows, closes


class TestWilderAccumulativeSwing(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("si", "asi", "asi_ema", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_hand_computed_si_and_asi(self):
        # Bar 0: O=C=100, H=101, L=99. Bar 1: O=100, C=110, H=112, L=100.
        # num = (110-100) + 0.5*(110-100) + 0.25*(100-100) = 15.
        # R = max(112-100, 100-100, 112-100) = 12. SI = 50*15/12 = 62.5.
        df = _run(_frame([100.0, 100.0], [101.0, 112.0],
                         [99.0, 100.0], [100.0, 110.0]))
        self.assertEqual(df["si"].iloc[0], 0.0)
        self.assertEqual(df["asi"].iloc[0], 0.0)
        self.assertAlmostEqual(df["si"].iloc[1], 62.5, places=9)
        self.assertAlmostEqual(df["asi"].iloc[1], 62.5, places=9)

    def test_hand_computed_second_si(self):
        # Add bar 2: O=110, C=120, H=122, L=110.
        # num = 10 + 5 + 2.5 = 17.5; R = max(12, 0, 12) = 12;
        # SI = 50*17.5/12 = 72.9167; ASI = 62.5 + 72.9167 = 135.4167.
        df = _run(_frame([100.0, 100.0, 110.0], [101.0, 112.0, 122.0],
                         [99.0, 100.0, 110.0], [100.0, 110.0, 120.0]))
        self.assertAlmostEqual(df["si"].iloc[2], 50 * 17.5 / 12, places=9)
        self.assertAlmostEqual(df["asi"].iloc[2], 62.5 + 50 * 17.5 / 12, places=9)

    def test_flat_bar_r_zero_guard(self):
        n = 30
        df = _run(_frame([100.0] * n, [100.0] * n, [100.0] * n, [100.0] * n))
        self.assertTrue((df["si"] == 0.0).all())
        self.assertTrue((df["asi"] == 0.0).all())
        self.assertFalse(df["si"].isna().any())

    def test_asi_is_cumsum_of_si(self):
        df = _run(_random_walk_frame())
        pd.testing.assert_series_equal(
            df["asi"], df["si"].cumsum(), check_names=False)

    def test_cross_down_then_up_on_reversals(self):
        o, h, l, c = _trend_series()
        df = _run(_frame(o, h, l, c))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue(df["long_entry"].any())
        # The short must come before the final long (fall then rise).
        self.assertLess(df["short_entry"].idxmax(), df["long_entry"].idxmax())

    def test_entries_match_asi_ema_cross(self):
        o, h, l, c = _trend_series()
        df = _run(_frame(o, h, l, c))
        # Every long entry sits on ASI above its EMA, every short below.
        self.assertTrue((df.loc[df["long_entry"], "asi"]
                         > df.loc[df["long_entry"], "asi_ema"]).all())
        self.assertTrue((df.loc[df["short_entry"], "asi"]
                         < df.loc[df["short_entry"], "asi_ema"]).all())

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
        self.assertIn("wilder_accumulative_swing", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 20)

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
