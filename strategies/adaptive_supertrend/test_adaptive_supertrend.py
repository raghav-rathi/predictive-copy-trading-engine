"""Adaptive Supertrend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adaptive_supertrend import indicators, risk, signals
from strategies import base as B


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


def _swing_frame(n=700, seed=21, cycles=3):
    """Slow sine swings: Supertrend flips repeatedly in both directions."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, cycles * 2 * np.pi, n)
    c = 100 + 25 * np.sin(x) + rng.normal(0, 0.4, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("chop", "k_mult", "atr", "supertrend", "supertrend_dir"):
            self.assertIn(col, self.ind.columns)

    def test_choppiness_formula(self):
        tr = B.true_range(self.df["h"], self.df["l"], self.df["c"])
        sum_tr = tr.rolling(14, min_periods=14).sum()
        rng = (self.df["h"].rolling(14, min_periods=14).max()
               - self.df["l"].rolling(14, min_periods=14).min())
        expect = (100 * np.log10(sum_tr / rng.replace(0, np.nan))
                  / np.log10(14)).dropna()
        got = self.ind["chop"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_chop_range(self):
        got = self.ind["chop"].dropna()
        self.assertTrue(((got >= 0) & (got <= 100)).all())

    def test_k_mapping(self):
        chop = self.ind["chop"]
        k = self.ind["k_mult"]
        self.assertTrue(((k[chop < 38] == 2.0)).all())
        self.assertTrue(((k[chop > 62] == 4.0)).all())
        mid = chop[(chop >= 38) & (chop <= 62)]
        self.assertTrue(((k.loc[mid.index] == 3.0)).all())
        self.assertTrue(set(k.dropna().unique()) <= {2.0, 3.0, 4.0})
        # NaN chop (warmup) maps to the classic default k=3.0.
        self.assertTrue((k[chop.isna()] == 3.0).all())

    def test_fixed_k_matches_base_supertrend(self):
        # With a constant k=3.0 the adaptive loop must reproduce
        # strategies.base.supertrend(10, 3.0) exactly.
        k = pd.Series(np.full(len(self.df), 3.0), index=self.df.index)
        got = indicators.adaptive_supertrend(
            self.df["h"], self.df["l"], self.df["c"], k, 10)
        expect = B.supertrend(self.df["h"], self.df["l"], self.df["c"], 10, 3.0)
        pd.testing.assert_series_equal(
            got["supertrend"], expect["supertrend"], check_names=False)
        pd.testing.assert_series_equal(
            got["supertrend_dir"], expect["supertrend_dir"], check_names=False)

    def test_fixed_k2_matches_base_supertrend(self):
        k = pd.Series(np.full(len(self.df), 2.0), index=self.df.index)
        got = indicators.adaptive_supertrend(
            self.df["h"], self.df["l"], self.df["c"], k, 10)
        expect = B.supertrend(self.df["h"], self.df["l"], self.df["c"], 10, 2.0)
        pd.testing.assert_series_equal(
            got["supertrend"], expect["supertrend"], check_names=False)
        pd.testing.assert_series_equal(
            got["supertrend_dir"], expect["supertrend_dir"], check_names=False)

    def test_direction_only_pm1_after_warmup(self):
        d = self.ind["supertrend_dir"].dropna()
        self.assertTrue(set(d.unique()) <= {1.0, -1.0})

    def test_line_sits_on_correct_side(self):
        # In an uptrend the line is the lower band (below close);
        # in a downtrend the upper band (above close).
        ind = self.ind.dropna(subset=["supertrend_dir"])
        up = ind[ind["supertrend_dir"] == 1]
        dn = ind[ind["supertrend_dir"] == -1]
        self.assertTrue((up["supertrend"] <= up["c"]).all())
        self.assertTrue((dn["supertrend"] >= dn["c"]).all())

    def test_warmup_nans(self):
        self.assertTrue(self.ind["chop"].iloc[:13].isna().all())
        self.assertFalse(self.ind["chop"].iloc[14:].isna().any())
        self.assertTrue(self.ind["supertrend_dir"].iloc[:9].isna().all())
        self.assertFalse(self.ind["supertrend_dir"].iloc[20:].isna().any())

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

    def test_entries_are_direction_flips(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        d = ind["supertrend_dir"]
        prev = d.shift(1)
        pd.testing.assert_series_equal(
            sig["long_entry"], ((d == 1) & (prev == -1)).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_entry"], ((d == -1) & (prev == 1)).fillna(False).astype(bool),
            check_names=False)

    def test_exits_are_opposite_flips(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        pd.testing.assert_series_equal(
            sig["long_exit"], sig["short_entry"], check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], sig["long_entry"], check_names=False)

    def test_flips_fire_both_ways_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.adaptive_supertrend as mod
        from strategies.registry import REGISTRY

        self.assertIn("adaptive_supertrend", REGISTRY)
        self.assertIs(REGISTRY["adaptive_supertrend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "adaptive_supertrend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
