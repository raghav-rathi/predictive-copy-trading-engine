"""Jurik RSX tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.jurik_rsx import indicators, risk, signals


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _trend_frame(n=300, start=100.0, step=0.5):
    c = start + step * np.arange(n)
    o = np.concatenate([[start], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _sig_frame(rsx_values):
    """Signal frame with a hand-built RSX path."""
    n = len(rsx_values)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 100.0,
        "rsx": pd.Series(rsx_values, dtype=float), "atr": 1.0,
    })


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("rsx", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_stage_cascade_first_value_analytic(self):
        # length 14: f18 = 3/16 = 0.1875. Single unit impulse, all state 0.
        # Stage 1: a=0.1875, b=0.03515625, out=0.263671875.
        # Stage 2: a=0.0494384765625, b=0.00926971435546875,
        #          out=0.06952285766601562.
        # Stage 3: a=54675/4194304, b=164025/67108864,
        #          out=2460375/134217728 = 0.018331222236156464.
        out = indicators._stage_cascade(np.array([1.0, 0.0, 0.0]), 14)
        self.assertAlmostEqual(out[0], 0.018331222236156464, places=12)
        self.assertTrue(np.all(np.isfinite(out)))

    def test_flat_market_is_neutral_50(self):
        df = _frame()
        df["c"] = 100.0
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["rsx"].dropna(), 50.0))

    def test_strong_uptrend_is_high(self):
        ind = indicators.add_indicators(_trend_frame(step=0.5))
        self.assertGreater(ind["rsx"].iloc[-1], 70.0)

    def test_strong_downtrend_is_low(self):
        ind = indicators.add_indicators(_trend_frame(step=-0.5))
        self.assertLess(ind["rsx"].iloc[-1], 30.0)

    def test_bounded_zero_to_100(self):
        s = self.ind["rsx"].dropna()
        self.assertTrue(((s >= 0.0) & (s <= 100.0)).all())

    def test_smoother_than_rsi(self):
        # RSX bar-to-bar jitter should be well below plain RSI's.
        from strategies import base as B
        rsi = B.rsi(self.df["c"], 14).dropna()
        rsx = self.ind["rsx"].dropna()
        self.assertLess(rsx.diff().abs().mean(), rsi.diff().abs().mean())

    def test_warmup_nans(self):
        # First emission after length + 1 inputs (index 14).
        self.assertTrue(self.ind["rsx"].iloc[:14].isna().all())
        self.assertFalse(self.ind["rsx"].iloc[14:].isna().any())

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_rising_cross_above_50(self):
        sig = signals.add_signals(_sig_frame([40.0, 45.0, 49.0, 52.0, 58.0, 65.0]))
        self.assertTrue(sig["long_entry"].iloc[3])
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_no_long_when_falling_through_50(self):
        # Cross above 50 while falling is impossible by construction;
        # instead: a flat crawl across 50 is blocked by the flat filter.
        sig = signals.add_signals(_sig_frame(
            [49.6, 49.7, 49.8, 49.9, 50.0, 50.1, 50.2]))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_flat_filter_blocks_entry(self):
        # RSX creeps across 50 in 0.1 steps: |ΔRSX| < 0.5 for 3+ bars.
        sig = signals.add_signals(_sig_frame(
            [49.7, 49.8, 49.9, 50.0, 50.1, 50.2, 50.3]))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_short_entry_on_falling_cross_below_50(self):
        sig = signals.add_signals(_sig_frame([60.0, 55.0, 51.0, 48.0, 42.0, 35.0]))
        self.assertTrue(sig["short_entry"].iloc[3])
        self.assertEqual(sig["short_entry"].sum(), 1)

    def test_long_exit_at_80(self):
        sig = signals.add_signals(_sig_frame([60.0, 70.0, 79.0, 81.0, 85.0]))
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_short_exit_at_20(self):
        sig = signals.add_signals(_sig_frame([40.0, 30.0, 21.0, 19.0, 15.0]))
        self.assertTrue(sig["short_exit"].iloc[3])

    def test_long_exit_on_cross_back(self):
        sig = signals.add_signals(_sig_frame([60.0, 55.0, 51.0, 48.0, 45.0]))
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_entries_fire_on_random_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertGreater(sig["long_entry"].sum() + sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.target_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 45)

    def test_registration(self):
        import strategies.jurik_rsx as mod
        from strategies.registry import REGISTRY

        self.assertIn("jurik_rsx", REGISTRY)
        self.assertIs(REGISTRY["jurik_rsx"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "jurik_rsx")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
