"""Efficiency Ratio tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.efficiency_ratio import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes * 1.001,
                         "l": closes * 0.999, "c": closes,
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


def _uptrend_with_dip_recovery():
    base = [100.0 + 0.05 * i for i in range(240)]
    dip = [base[-1] - 0.6 * (i + 1) for i in range(14)]
    rec = [dip[-1] + 0.8 * (i + 1) for i in range(16)]
    return base + dip + rec


def _downtrend_with_rally_pullback():
    base = [120.0 - 0.05 * i for i in range(240)]
    rally = [base[-1] + 0.6 * (i + 1) for i in range(14)]
    fall = [rally[-1] - 0.8 * (i + 1) for i in range(16)]
    return base + rally + fall


class TestEfficiencyRatio(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("er", "ema9", "ema21", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_er_hand_computed_steady_trend(self):
        # +1 per bar: 10-bar change = 10, path = 10, ER = 1.0.
        df = indicators.add_indicators(_frame([100.0 + i for i in range(40)]))
        self.assertAlmostEqual(df["er"].iloc[20], 1.0, places=9)

    def test_er_zero_on_flat_and_on_round_trip(self):
        df = indicators.add_indicators(_frame([100.0] * 40))
        self.assertEqual(df["er"].iloc[20], 0.0)
        alt = [100.0 if i % 2 == 0 else 101.0 for i in range(40)]
        df = indicators.add_indicators(_frame(alt))
        self.assertEqual(df["er"].iloc[20], 0.0)

    def test_er_bounded_zero_to_one(self):
        df = _run(_random_walk_frame())
        er = df["er"].iloc[risk.WARMUP:]
        self.assertTrue(((er >= 0.0) & (er <= 1.0)).all())

    def test_long_on_cross_with_high_er(self):
        df = _run(_frame(_uptrend_with_dip_recovery()))
        self.assertTrue(df["long_entry"].any())
        # Every long entry must sit on an efficient bar.
        self.assertTrue((df.loc[df["long_entry"], "er"] > 0.3).all())

    def test_short_on_cross_with_high_er(self):
        df = _run(_frame(_downtrend_with_rally_pullback()))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue((df.loc[df["short_entry"], "er"] > 0.3).all())

    def test_no_entry_when_inefficient(self):
        # Alternating closes: ER is identically 0, so no cross may enter.
        alt = [100.0 if i % 2 == 0 else 101.0 for i in range(300)]
        df = _run(_frame(alt))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exit_ignores_er(self):
        # Hand-built EMA columns: cross up with ER high enters long,
        # cross down with ER = 0 still exits.
        df = pd.DataFrame({
            "ema9": [10.0, 11.0, 11.0, 11.0, 10.0],
            "ema21": [10.0, 10.5, 10.5, 10.5, 10.5],
            "er": [0.9, 0.9, 0.9, 0.9, 0.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["long_exit"].iloc[4])

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_last_bar_change_keeps_earlier_signals(self):
        closes = _uptrend_with_dip_recovery()
        df1 = _run(_frame(closes))
        closes2 = list(closes)
        closes2[-1] = closes2[-1] * 1.5
        df2 = _run(_frame(closes2))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("efficiency_ratio", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["efficiency_ratio"].slug,
                         "efficiency_ratio")
        self.assertEqual(risk.WARMUP, 30)

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
