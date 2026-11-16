"""DeMark pivots tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.demark_pivots import indicators, risk, signals


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


def _day_frame(day_o, day_c, day_h=110.0, day_l=90.0, n_after=6):
    """24 identical 'day' bars, then n_after bars to read levels from."""
    n = 24 + n_after
    o = np.array([day_o] * 24 + [100.0] * n_after, dtype=float)
    c = np.array([day_c] * 24 + [100.0] * n_after, dtype=float)
    h = np.array([day_h] * 24 + [101.0] * n_after, dtype=float)
    l = np.array([day_l] * 24 + [99.0] * n_after, dtype=float)
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _sig_frame(closes, r1=105.0, s1=95.0):
    """Signal frame with hand-built closes and flat R1/S1 levels."""
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    c = pd.Series(closes, dtype=float)
    return pd.DataFrame({
        "t": t, "o": c, "h": c + 1.0, "l": c - 1.0, "c": c, "v": 100.0,
        "demark_x": 200.0, "demark_r1": float(r1), "demark_s1": float(s1),
        "atr": 1.0,
    })


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("demark_x", "demark_r1", "demark_s1", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_pivot_close_below_open(self):
        # Day: H=110, L=90, C=95, O=100 (C<O): X=110+180+95=385,
        # R1=192.5-90=102.5, S1=192.5-110=82.5.
        ind = indicators.add_indicators(_day_frame(100.0, 95.0))
        self.assertAlmostEqual(ind["demark_x"].iloc[24], 385.0)
        self.assertAlmostEqual(ind["demark_r1"].iloc[24], 102.5)
        self.assertAlmostEqual(ind["demark_s1"].iloc[24], 82.5)

    def test_pivot_close_above_open(self):
        # Day: H=110, L=90, C=105, O=100 (C>O): X=220+90+105=415,
        # R1=207.5-90=117.5, S1=207.5-110=97.5.
        ind = indicators.add_indicators(_day_frame(100.0, 105.0))
        self.assertAlmostEqual(ind["demark_x"].iloc[24], 415.0)
        self.assertAlmostEqual(ind["demark_r1"].iloc[24], 117.5)
        self.assertAlmostEqual(ind["demark_s1"].iloc[24], 97.5)

    def test_pivot_close_equals_open(self):
        # Day: H=110, L=90, C=100, O=100: X=110+90+200=400,
        # R1=200-90=110, S1=200-110=90.
        ind = indicators.add_indicators(_day_frame(100.0, 100.0))
        self.assertAlmostEqual(ind["demark_x"].iloc[24], 400.0)
        self.assertAlmostEqual(ind["demark_r1"].iloc[24], 110.0)
        self.assertAlmostEqual(ind["demark_s1"].iloc[24], 90.0)

    def test_r1_above_s1(self):
        self.assertTrue((self.ind["demark_r1"].dropna()
                         > self.ind["demark_s1"].dropna()).all())

    def test_warmup_nans(self):
        self.assertTrue(self.ind["demark_r1"].iloc[:24].isna().all())
        self.assertFalse(self.ind["demark_r1"].iloc[24:].isna().any())

    def test_levels_use_prior_day_only(self):
        # Levels at bar 24 must not change if later bars change.
        df = _day_frame(100.0, 95.0)
        ind1 = indicators.add_indicators(df)
        df2 = df.copy()
        df2.loc[25, "h"] = 500.0
        ind2 = indicators.add_indicators(df2)
        self.assertAlmostEqual(ind1["demark_r1"].iloc[24],
                               ind2["demark_r1"].iloc[24])

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

    def test_long_entry_after_two_closes_above_r1(self):
        # Closes: below R1, then two above -> entry on the 2nd hold bar.
        sig = signals.add_signals(_sig_frame([100.0, 104.0, 106.0, 107.0, 108.0]))
        self.assertTrue(sig["long_entry"].iloc[3])
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_no_long_on_single_close_above(self):
        sig = signals.add_signals(_sig_frame([100.0, 104.0, 106.0]))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_no_long_while_already_above(self):
        # Already above for 3 bars: no fresh break, no entry.
        sig = signals.add_signals(_sig_frame([106.0, 107.0, 108.0, 109.0]))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_short_entry_after_two_closes_below_s1(self):
        sig = signals.add_signals(_sig_frame([100.0, 96.0, 94.0, 93.0, 92.0]))
        self.assertTrue(sig["short_entry"].iloc[3])
        self.assertEqual(sig["short_entry"].sum(), 1)

    def test_long_exit_back_inside_band(self):
        # Long is open; close falls below R1 -> exit.
        sig = signals.add_signals(_sig_frame([106.0, 107.0, 104.0]))
        self.assertTrue(sig["long_exit"].iloc[2])

    def test_long_exit_on_opposite_level_touch(self):
        # Close still above R1 but the low touches S1 -> exit.
        df = _sig_frame([106.0, 107.0, 108.0])
        df.loc[2, "l"] = 95.0  # touches S1 exactly
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_exit"].iloc[2])

    def test_short_exit_on_opposite_level_touch(self):
        df = _sig_frame([94.0, 93.0, 92.0])
        df.loc[2, "h"] = 105.0  # touches R1 exactly
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_exit"].iloc[2])

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
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 48)

    def test_registration(self):
        import strategies.demark_pivots as mod
        from strategies.registry import REGISTRY

        self.assertIn("demark_pivots", REGISTRY)
        self.assertIs(REGISTRY["demark_pivots"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "demark_pivots")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
