"""Smoothed Heikin-Ashi tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.heikin_ashi_smoothed import indicators, risk, signals
from strategies.registry import REGISTRY


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _signal_frame(sc, so):
    n = len(sc)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    c = np.full(n, 100.0)
    return pd.DataFrame({
        "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
        "ha_close_smooth": sc, "ha_open_smooth": so,
    })


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("ha_open", "ha_close", "ha_high", "ha_low",
                    "ha_open_smooth", "ha_close_smooth", "atr"):
            self.assertIn(col, ind.columns)

    def test_ha_close_formula(self):
        df = _frame_from_close([100.0, 102.0, 101.0, 103.0])
        ind = indicators.add_indicators(df)
        # ha_close[1] = (o + h + l + c) / 4 from bar 1's own OHLC.
        o, h, l, c = df["o"].iloc[1], df["h"].iloc[1], df["l"].iloc[1], df["c"].iloc[1]
        self.assertAlmostEqual(float(ind["ha_close"].iloc[1]), (o + h + l + c) / 4.0)

    def test_ha_open_recursion(self):
        df = _frame_from_close([100.0, 102.0, 101.0, 103.0])
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["ha_open"].iloc[0]),
                               (df["o"].iloc[0] + df["c"].iloc[0]) / 2.0)
        self.assertAlmostEqual(
            float(ind["ha_open"].iloc[2]),
            (float(ind["ha_open"].iloc[1]) + float(ind["ha_close"].iloc[1])) / 2.0)

    def test_ha_high_low_bracket(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertTrue((ind["ha_high"] >= ind["ha_close"]).all())
        self.assertTrue((ind["ha_low"] <= ind["ha_close"]).all())

    def test_no_lookahead_indicators(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("ha_open", "ha_close", "ha_open_smooth", "ha_close_smooth"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:200].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_flat_data_no_entries(self):
        n = 200
        flat = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0), "h": np.full(n, 100.0),
            "l": np.full(n, 100.0), "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
        })
        sig = signals.add_signals(indicators.add_indicators(flat))
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_crafted_long_cross_fires(self):
        # Smoothed close crosses above smoothed open at bar 2.
        df = _signal_frame(
            sc=np.array([99.0, 99.0, 101.0]),
            so=np.array([100.0, 100.0, 100.0]),
        )
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["short_exit"].iloc[2])
        self.assertFalse(sig["short_entry"].any())

    def test_crafted_short_cross_fires(self):
        df = _signal_frame(
            sc=np.array([101.0, 101.0, 99.0]),
            so=np.array([100.0, 100.0, 100.0]),
        )
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[2])
        self.assertFalse(sig["long_entry"].any())

    def test_v_reversal_pipeline_enters_long(self):
        # 30 bars down 130 -> 100, then 30 bars up 100 -> 130.
        down = np.linspace(130, 100, 31)[:-1]
        up = np.linspace(100, 130, 31)
        c = np.concatenate([down, up])
        df = _frame_from_close(c, seed=3)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].any())

    def test_no_lookahead_signals(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        full = signals.add_signals(indicators.add_indicators(df))
        trunc = signals.add_signals(indicators.add_indicators(short))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )


class TestRiskAndRegistry(unittest.TestCase):
    def test_registered(self):
        self.assertIn("heikin_ashi_smoothed", REGISTRY)
        self.assertEqual(REGISTRY["heikin_ashi_smoothed"].warmup_bars, risk.WARMUP)

    def test_risk_config_sane(self):
        r = risk.RISK
        self.assertGreater(r.stop_atr_mult, 0)
        self.assertGreater(r.risk_frac, 0)
        self.assertLessEqual(r.max_leverage, 3.0)
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.5)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 168)
        self.assertTrue(r.allow_longs and r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 30)

    def test_backtest_smoke(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)
        self.assertIn("net_pnl_usd", m)


if __name__ == "__main__":
    unittest.main()
