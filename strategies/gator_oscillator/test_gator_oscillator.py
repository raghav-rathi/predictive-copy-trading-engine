"""Gator Oscillator states tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.gator_oscillator import indicators, risk, signals
from strategies import base as B


def _frame(n=600, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _uptrend_frame(n=800, seed=3):
    """Steady rally: the fan should order lips > teeth > jaw."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.002, 0.003, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _downtrend_frame(n=800, seed=11):
    """Steady decline: the fan should order lips < teeth < jaw."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(-0.002, 0.003, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("alligator_jaw", "alligator_teeth", "alligator_lips",
                    "gator_upper", "gator_lower",
                    "gator_upper_green", "gator_lower_green",
                    "gator_eats", "gator_sleeps", "fan_bull", "fan_bear",
                    "atr"):
            self.assertIn(col, self.ind.columns)

    def test_smma_recursion_vs_hand_computation(self):
        # ewm(alpha=1/n, adjust=False) must equal the Wilder recursion
        # y[i] = (y[i-1]*(n-1) + x[i]) / n seeded with y[0] = x[0].
        n = 8
        x = np.arange(1.0, 51.0)
        got = indicators.smma(pd.Series(x), n)
        expect = np.empty_like(x)
        y = x[0]
        for i, xi in enumerate(x):
            if i == 0:
                y = xi
            else:
                y = (y * (n - 1) + xi) / n
            expect[i] = y
        got_n, expect_n = got.iloc[n - 1:].to_numpy(), expect[n - 1:]
        self.assertTrue(np.allclose(got_n, expect_n, atol=1e-9))
        self.assertTrue(got.iloc[: n - 1].isna().all())

    def test_forward_displacement_uses_only_past_data(self):
        # Shifted balance lines must equal the UNshifted SMMA displaced
        # forward by k bars: jaw at bar j is SMMA state at bar j-k.
        median = (self.df["h"] + self.df["l"]) / 2
        jaw_raw = indicators.smma(median, 13)
        got = self.ind["alligator_jaw"]
        pd.testing.assert_series_equal(
            got.iloc[8:].reset_index(drop=True),
            jaw_raw.iloc[:-8].reset_index(drop=True),
            check_names=False)
        # The first 8 displaced bars are NaN regardless of earlier data:
        self.assertTrue(got.iloc[:8].isna().all())

    def test_histogram_values_vs_manual_abs_diffs(self):
        median = (self.df["h"] + self.df["l"]) / 2
        jaw = indicators.smma(median, 13).shift(8)
        teeth = indicators.smma(median, 8).shift(5)
        lips = indicators.smma(median, 5).shift(3)
        upper_expect = (jaw - teeth).abs()
        lower_expect = -(teeth - lips).abs()
        pd.testing.assert_series_equal(self.ind["gator_upper"], upper_expect,
                                       check_names=False)
        pd.testing.assert_series_equal(self.ind["gator_lower"], lower_expect,
                                       check_names=False)
        self.assertTrue((self.ind["gator_upper"].dropna() >= 0).all())
        self.assertTrue((self.ind["gator_lower"].dropna() <= 0).all())

    def test_green_red_coloring_is_bar_to_bar_change(self):
        u = self.ind["gator_upper"]
        l = self.ind["gator_lower"]
        expect_upper = (u.diff() > 0).fillna(False)
        # |lower| rises when the negative lower value falls.
        expect_lower = (l.diff() < 0).fillna(False)
        pd.testing.assert_series_equal(self.ind["gator_upper_green"],
                                       expect_upper.astype(bool),
                                       check_names=False)
        pd.testing.assert_series_equal(self.ind["gator_lower_green"],
                                       expect_lower.astype(bool),
                                       check_names=False)

    def test_fan_bull_on_uptrend(self):
        ind = indicators.add_indicators(_uptrend_frame())
        self.assertTrue(ind["fan_bull"].iloc[-50:].any())
        self.assertFalse(ind["fan_bear"].iloc[-50:].any())

    def test_fan_bear_on_downtrend(self):
        ind = indicators.add_indicators(_downtrend_frame())
        self.assertTrue(ind["fan_bear"].iloc[-50:].any())
        self.assertFalse(ind["fan_bull"].iloc[-50:].any())

    def test_eats_sleeps_are_mutually_exclusive_states(self):
        ind = self.ind
        eats = ind["gator_eats"].fillna(False)
        sleeps = ind["gator_sleeps"].fillna(False)
        self.assertFalse((eats & sleeps).any())
        # eats => both histograms green; sleeps => both red
        eat_idx = eats[eats].index
        self.assertTrue(ind.loc[eat_idx, "gator_upper_green"].all())
        self.assertTrue(ind.loc[eat_idx, "gator_lower_green"].all())
        sleep_idx = sleeps[sleeps].index
        self.assertTrue((~ind.loc[sleep_idx, "gator_upper_green"]).all())
        self.assertTrue((~ind.loc[sleep_idx, "gator_lower_green"]).all())

    def test_states_fire_on_chop_frame(self):
        # Random-walk chop must produce both expansions and contractions.
        self.assertGreater(self.ind["gator_eats"].sum(), 0)
        self.assertGreater(self.ind["gator_sleeps"].sum(), 0)

    def test_warmup_nans(self):
        # SMMA(13) needs 13 bars, jaw displacement adds 8: first valid jaw
        # at bar 20, well inside WARMUP=40.
        self.assertTrue(self.ind["alligator_jaw"].iloc[:20].isna().all())
        self.assertFalse(self.ind["alligator_jaw"].iloc[40:].isna().any())

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)


class TestSignals(unittest.TestCase):
    def setUp(self):
        self.ind = indicators.add_indicators(_frame())
        self.sig = signals.add_signals(self.ind)

    def test_columns_boolean_no_nan(self):
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, self.sig.columns)
            self.assertTrue(self.sig[col].dtype == bool, col)
            self.assertFalse(self.sig[col].isna().any(), col)

    def test_entries_require_eats_flip(self):
        eats = self.ind["gator_eats"].fillna(False)
        eats_flip = (eats & ~eats.shift(1).fillna(False)).fillna(False)
        self.assertTrue(((~self.sig["long_entry"]) | eats_flip).all())
        self.assertTrue(((~self.sig["short_entry"]) | eats_flip).all())

    def test_entries_require_matching_fan(self):
        longs = self.sig["long_entry"]
        self.assertTrue(self.ind.loc[longs, "fan_bull"].all())
        shorts = self.sig["short_entry"]
        self.assertTrue(self.ind.loc[shorts, "fan_bear"].all())

    def test_exits_on_sleeps(self):
        sleeps = self.sig["gator_sleeps"]
        self.assertTrue((self.sig.loc[sleeps, "long_exit"]).all())
        self.assertTrue((self.sig.loc[sleeps, "short_exit"]).all())

    def test_exits_on_fan_flip(self):
        fb = self.ind["fan_bear"].fillna(False)
        self.assertTrue((self.sig.loc[fb, "long_exit"]).all())
        fu = self.ind["fan_bull"].fillna(False)
        self.assertTrue((self.sig.loc[fu, "short_exit"]).all())

    def test_entries_fire_on_chop_frame(self):
        # Chop must generate both long and short setups over 600 bars.
        self.assertGreater(self.sig["long_entry"].sum(), 0)
        self.assertGreater(self.sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)

    def test_registration(self):
        import strategies.gator_oscillator as mod
        from strategies.registry import REGISTRY

        self.assertIn("gator_oscillator", REGISTRY)
        self.assertIs(REGISTRY["gator_oscillator"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "gator_oscillator")
        self.assertEqual(mod.SPEC.name, "Gator Oscillator States")
        self.assertEqual(mod.SPEC.source_name, "Gator Oscillator (Bill Williams)")
        self.assertEqual(
            mod.SPEC.source_url,
            "https://www.ifcmfa.com/en/ntx-indicators/gator-oscillator")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__),
                         {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
