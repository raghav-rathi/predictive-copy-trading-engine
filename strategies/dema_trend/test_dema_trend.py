"""DEMA Trend Cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dema_trend import indicators, risk, signals
from strategies import base as B


def _frame(n=600, seed=7, drift=0.0005, vol=0.01, base=100.0):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = base * np.exp(np.cumsum(rets))
    o = np.concatenate([[base], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _swing_frame(n=800, seed=21, cycles=3):
    """Slow sine swings: DEMA(21)/DEMA(55) cross in both directions."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, cycles * 2 * np.pi, n)
    c = 100 + 25 * np.sin(x) + rng.normal(0, 0.4, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _step_frame(step_at=400, n=800, lo=100.0, hi=110.0):
    c = np.array([lo] * step_at + [hi] * (n - step_at), dtype=float)
    o = np.concatenate([[lo], c[:-1]])
    h = np.maximum(o, c) * 1.0005
    l = np.minimum(o, c) * 0.9995
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("dema_fast", "dema_slow", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_dema_formula_vs_hand_computation(self):
        c = self.df["c"]
        ema1 = B.ema(c, 21)
        ema2 = B.ema(ema1, 21)
        expect = (2.0 * ema1 - ema2).dropna()
        got = self.ind["dema_fast"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_dema_slow_formula(self):
        c = self.df["c"]
        ema1 = B.ema(c, 55)
        expect = (2.0 * ema1 - B.ema(ema1, 55)).dropna()
        got = self.ind["dema_slow"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_dema_lag_less_than_ema_on_step(self):
        # After a clean step up, DEMA(21) must be closer to the new level
        # than plain EMA(21) — that lag reduction is the whole point.
        df = _step_frame()
        d = indicators.dema(df["c"], 21)
        e = B.ema(df["c"], 21)
        for j in (405, 410):
            self.assertLess(
                abs(float(d.iloc[j]) - 110.0),
                abs(float(e.iloc[j]) - 110.0),
                f"bar {j}: dema={d.iloc[j]:.3f} ema={e.iloc[j]:.3f}")

    def test_dema_converges_to_price_in_flat(self):
        df = _frame(vol=0.0, drift=0.0)
        d = indicators.add_indicators(df)["dema_fast"].dropna()
        self.assertTrue(np.allclose(d, 100.0, atol=1e-6))

    def test_warmup_nans(self):
        # DEMA(55) needs ~2*(55-1) = 108 bars before first valid value,
        # comfortably inside WARMUP=140.
        self.assertTrue(self.ind["dema_slow"].iloc[:108].isna().all())
        self.assertFalse(self.ind["dema_slow"].iloc[140:].isna().any())

    def test_default_params_are_21_55(self):
        default = indicators.add_indicators(self.df)
        explicit = indicators.add_indicators(self.df, fast=21, slow=55)
        pd.testing.assert_series_equal(
            default["dema_fast"], explicit["dema_fast"], check_names=False)
        pd.testing.assert_series_equal(
            default["dema_slow"], explicit["dema_slow"], check_names=False)

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

    def test_crosses_fire_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_entries_are_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        f, s = ind["dema_fast"], ind["dema_slow"]
        pd.testing.assert_series_equal(
            sig["long_entry"], B.crossed_above(f, s).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_entry"], B.crossed_below(f, s).fillna(False).astype(bool),
            check_names=False)

    def test_exits_fire_on_opposite_cross(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        f, s = ind["dema_fast"], ind["dema_slow"]
        pd.testing.assert_series_equal(
            sig["long_exit"], B.crossed_below(f, s).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], B.crossed_above(f, s).fillna(False).astype(bool),
            check_names=False)

    def test_no_signals_on_flat_chop(self):
        # Constant price: the two DEMAs coincide exactly, no crosses at all.
        df = _frame(vol=0.0, drift=0.0)
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(sig[col].sum(), 0, col)

    def test_no_entry_and_exit_same_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertEqual((sig["long_entry"] & sig["long_exit"]).sum(), 0)
        self.assertEqual((sig["short_entry"] & sig["short_exit"]).sum(), 0)

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 450
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 140)

    def test_registration(self):
        import strategies.dema_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("dema_trend", REGISTRY)
        self.assertIs(REGISTRY["dema_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "dema_trend")
        self.assertEqual(mod.SPEC.name, "DEMA Trend Cross")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
