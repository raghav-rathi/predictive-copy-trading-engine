"""Accelerator Oscillator (Bill Williams) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.accelerator_oscillator import indicators, risk, signals


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


def _sig_frame(ac_vals):
    """Minimal frame with hand-built ac columns for pure signal-logic tests."""
    ac = pd.Series(ac_vals, dtype=float)
    return pd.DataFrame({
        "ac": ac,
        "ac_green": (ac > ac.shift(1)).astype(bool),
        "ac_red": (ac < ac.shift(1)).astype(bool),
        "atr": np.ones(len(ac)),
    })


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("med", "ao", "ac", "ac_green", "ac_red", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_ao_formula_hand_computation(self):
        med = (self.df["h"] + self.df["l"]) / 2.0
        for j in (50, 150, 300):
            sma5 = med.iloc[j - 4: j + 1].mean()
            sma34 = med.iloc[j - 33: j + 1].mean()
            self.assertAlmostEqual(self.ind["ao"].iloc[j], sma5 - sma34, places=9)

    def test_ac_formula_hand_computation(self):
        ao = self.ind["ao"]
        for j in (50, 150, 300):
            expect = ao.iloc[j] - ao.iloc[j - 4: j + 1].mean()
            self.assertAlmostEqual(self.ind["ac"].iloc[j], expect, places=9)

    def test_color_is_change_not_level(self):
        ac = self.ind["ac"].dropna()
        green = self.ind["ac_green"].loc[ac.index]
        red = self.ind["ac_red"].loc[ac.index]
        pd.testing.assert_series_equal(
            green, (ac > ac.shift(1)).astype(bool), check_names=False)
        pd.testing.assert_series_equal(
            red, (ac < ac.shift(1)).astype(bool), check_names=False)
        # The color is NOT the level: green bars exist below zero,
        # red bars exist above zero, and warmup bars are colorless.
        self.assertTrue(((ac < 0) & green).any())
        self.assertTrue(((ac > 0) & red).any())
        self.assertFalse((self.ind["ac_green"] | self.ind["ac_red"]).iloc[:37].any())

    def test_warmup_nans(self):
        # ao needs SMA(med,34): first valid at bar 33. ac needs
        # SMA(ao,5): first valid at bar 37. Both inside WARMUP=50.
        self.assertTrue(self.ind["ao"].iloc[:33].isna().all())
        self.assertTrue(self.ind["ac"].iloc[:37].isna().all())
        self.assertFalse(self.ind["ac"].iloc[40:].isna().any())

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(_sig_frame([0.1, 0.2, 0.3, 0.4]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_two_bar_with_trend_long_fires(self):
        # ac>0 with two consecutive green bars -> long.
        sig = signals.add_signals(_sig_frame([0.50, 0.55, 0.62]))
        self.assertTrue(bool(sig["long_entry"].iloc[2]))
        self.assertFalse(bool(sig["long_entry"].iloc[1]))  # only 1 green bar
        self.assertFalse(bool(sig["short_entry"].iloc[2]))

    def test_two_bar_countertrend_does_not_fire(self):
        # ac<0 with only two green bars: NOT a long (counter-trend
        # needs three).
        sig = signals.add_signals(_sig_frame([-0.30, -0.25, -0.20]))
        self.assertFalse(bool(sig["long_entry"].iloc[2]))

    def test_three_bar_countertrend_long_fires(self):
        # ac<0 with three consecutive green bars -> long.
        sig = signals.add_signals(_sig_frame([-0.30, -0.25, -0.20, -0.15]))
        self.assertTrue(bool(sig["long_entry"].iloc[3]))

    def test_short_symmetry(self):
        # with-trend: ac<0, 2 red bars -> short; counter-trend above
        # zero needs 3 red bars.
        sig = signals.add_signals(_sig_frame([-0.50, -0.55, -0.62]))
        self.assertTrue(bool(sig["short_entry"].iloc[2]))
        sig2 = signals.add_signals(_sig_frame([0.30, 0.25, 0.20]))
        self.assertFalse(bool(sig2["short_entry"].iloc[2]))
        sig3 = signals.add_signals(_sig_frame([0.30, 0.25, 0.20, 0.15]))
        self.assertTrue(bool(sig3["short_entry"].iloc[3]))

    def test_zero_line_never_generates_signal_alone(self):
        # ac crosses the zero line on alternating bars but never
        # strings together 2 same-color bars: no signal anywhere.
        sig = signals.add_signals(_sig_frame([-0.2, 0.2, -0.2, 0.2, -0.2, 0.2]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(bool(sig[col].any()), col)

    def test_flat_bars_are_not_green(self):
        # Strict >: flat bars (ac == ac.shift(1)) count as red.
        sig = signals.add_signals(_sig_frame([0.5, 0.5, 0.5, 0.6, 0.7]))
        self.assertFalse(bool(sig["long_entry"].iloc[2]))
        self.assertTrue(bool(sig["long_entry"].iloc[4]))

    def test_exit_on_two_bars_against_color(self):
        # Long armed on 2 greens above zero; 2 consecutive red bars
        # flip the color against the position -> long_exit.
        sig = signals.add_signals(_sig_frame([0.50, 0.55, 0.62, 0.58, 0.52]))
        self.assertTrue(bool(sig["long_entry"].iloc[2]))
        self.assertFalse(bool(sig["long_exit"].iloc[2]))
        self.assertTrue(bool(sig["long_exit"].iloc[4]))
        self.assertFalse(bool(sig["long_entry"].iloc[4]))

    def test_opposite_entry_is_an_exit(self):
        # A fresh short entry condition is itself a long exit.
        sig = signals.add_signals(_sig_frame([-0.50, -0.55, -0.62]))
        self.assertTrue(bool(sig["short_entry"].iloc[2]))
        self.assertTrue(bool(sig["long_exit"].iloc[2]))

    def test_no_lookahead(self):
        df = indicators.add_indicators(_frame())
        full = signals.add_signals(df)
        j = 350
        trunc = signals.add_signals(df.iloc[: j + 1])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]), col)


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 50)

    def test_registration(self):
        import strategies.accelerator_oscillator as mod
        from strategies.registry import REGISTRY

        self.assertIn("accelerator_oscillator", REGISTRY)
        self.assertIs(REGISTRY["accelerator_oscillator"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "accelerator_oscillator")
        self.assertEqual(mod.SPEC.name, "Accelerator Oscillator")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
