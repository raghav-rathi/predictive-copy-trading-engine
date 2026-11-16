"""ARMS Index / TRIN tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.arms_index import indicators, risk, signals


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


def _trin_frame(n_up, n_down, up_vol, down_vol):
    """Frame whose first 10 bars have an exact up/down + volume mix."""
    n = n_up + n_down
    o = np.full(n, 100.0)
    c = np.array([101.0] * n_up + [99.0] * n_down)
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    v = np.array([float(up_vol)] * n_up + [float(down_vol)] * n_down)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _sig_frame(trin_values, up_vol=100.0, dn_vol=100.0):
    """Signal frame with a hand-built TRIN path."""
    n = len(trin_values)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 100.0,
        "trin": pd.Series(trin_values, dtype=float),
        "trin_up_vol": float(up_vol), "trin_dn_vol": float(dn_vol),
        "atr": 1.0,
    })


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("trin", "trin_up_vol", "trin_dn_vol", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_trin_analytic(self):
        # 7 up bars x vol 100, 3 down bars x vol 50:
        # (7/3) / (700/150) = (7/3)/(14/3) = 0.5.
        ind = indicators.add_indicators(_trin_frame(7, 3, 100, 50))
        self.assertAlmostEqual(ind["trin"].iloc[9], 0.5, places=9)

    def test_trin_neutral_is_one(self):
        # Equal counts and equal volumes -> TRIN = 1.
        ind = indicators.add_indicators(_trin_frame(5, 5, 100, 100))
        self.assertAlmostEqual(ind["trin"].iloc[9], 1.0, places=9)

    def test_trin_floors_at_one(self):
        # All 10 bars up, no down bars/volumes: (10/1)/(1000/1) = 0.01.
        ind = indicators.add_indicators(_trin_frame(10, 0, 100, 0))
        self.assertTrue(np.isfinite(ind["trin"].iloc[9]))
        self.assertAlmostEqual(ind["trin"].iloc[9], 0.01, places=9)

    def test_volume_sums_recorded(self):
        ind = indicators.add_indicators(_trin_frame(7, 3, 100, 50))
        self.assertAlmostEqual(ind["trin_up_vol"].iloc[9], 700.0)
        self.assertAlmostEqual(ind["trin_dn_vol"].iloc[9], 150.0)

    def test_trin_positive_and_finite(self):
        s = self.ind["trin"].dropna()
        self.assertTrue((s > 0).all())
        self.assertTrue(np.isfinite(s).all())

    def test_warmup_nans(self):
        self.assertTrue(self.ind["trin"].iloc[:9].isna().all())
        self.assertFalse(self.ind["trin"].iloc[9:].isna().any())

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

    def test_long_entry_on_washout_cross(self):
        # TRIN above 1.0, then crosses below 0.7.
        trin = [1.2, 1.3, 1.1, 1.05, 0.9, 0.8, 0.65, 0.6, 0.55]
        sig = signals.add_signals(_sig_frame(trin))
        self.assertTrue(sig["long_entry"].iloc[6])
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_no_long_without_prior_above_one(self):
        # Cross below 0.7 but TRIN never exceeded 1.0 beforehand.
        trin = [0.9, 0.85, 0.8, 0.75, 0.72, 0.65, 0.6]
        sig = signals.add_signals(_sig_frame(trin))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_short_entry_on_spike_cross(self):
        # TRIN below 1.0, then crosses above 1.5.
        trin = [0.8, 0.7, 0.9, 0.95, 1.1, 1.3, 1.6, 1.8, 2.0]
        sig = signals.add_signals(_sig_frame(trin))
        self.assertTrue(sig["short_entry"].iloc[6])
        self.assertEqual(sig["short_entry"].sum(), 1)

    def test_no_short_without_prior_below_one(self):
        trin = [1.1, 1.2, 1.3, 1.4, 1.45, 1.6, 1.8]
        sig = signals.add_signals(_sig_frame(trin))
        self.assertEqual(sig["short_entry"].sum(), 0)

    def test_zero_volume_skips_entry(self):
        trin = [1.2, 1.3, 1.1, 1.05, 0.9, 0.8, 0.65, 0.6, 0.55]
        sig = signals.add_signals(_sig_frame(trin, up_vol=0.0))
        self.assertEqual(sig["long_entry"].sum(), 0)
        sig2 = signals.add_signals(_sig_frame(trin, dn_vol=0.0))
        self.assertEqual(sig2["long_entry"].sum(), 0)

    def test_exit_in_band(self):
        trin = [1.2, 1.3, 1.1, 1.05, 0.95, 0.9, 0.85, 1.2]
        sig = signals.add_signals(_sig_frame(trin))
        self.assertTrue(sig["long_exit"].iloc[4])
        self.assertTrue(sig["short_exit"].iloc[4])
        self.assertFalse(sig["long_exit"].iloc[7])

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
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 20)

    def test_registration(self):
        import strategies.arms_index as mod
        from strategies.registry import REGISTRY

        self.assertIn("arms_index", REGISTRY)
        self.assertIs(REGISTRY["arms_index"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "arms_index")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
