"""Vortex Indicator crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vortex import indicators, risk, signals
from strategies import base as B


def _frame(n=400, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _trend_frame(n=600, seed=11):
    """Up-trend then down-trend: crosses should fire in both legs."""
    rng = np.random.default_rng(seed)
    up = np.linspace(100, 160, n // 2) + rng.normal(0, 1.0, n // 2)
    dn = np.linspace(160, 90, n - n // 2) + rng.normal(0, 1.0, n - n // 2)
    c = np.concatenate([up, dn])
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.003, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.003, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("vi_pos", "vi_neg", "vi_spread", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_vi_nonnegative(self):
        v = self.ind.dropna(subset=["vi_pos", "vi_neg"])
        self.assertTrue((v["vi_pos"] >= 0).all())
        self.assertTrue((v["vi_neg"] >= 0).all())

    def test_vi_reasonable_upper_bound(self):
        # VM sums are bounded by TR sums except on gap/overlap bars; values
        # stay modest on a smooth random walk.
        v = self.ind["vi_pos"].dropna()
        self.assertLess(v.max(), 3.0)

    def test_vi_warmup_nans(self):
        n = 14
        # TR is NaN at bar 0, so the first n bars have no complete window.
        self.assertEqual(self.ind["vi_pos"].iloc[:n].isna().sum(), n)
        self.assertFalse(self.ind["vi_pos"].iloc[n:].isna().any())

    def test_vi_spread_consistency(self):
        v = self.ind.dropna(subset=["vi_pos", "vi_neg"])
        self.assertTrue(
            np.allclose(v["vi_spread"], v["vi_pos"] - v["vi_neg"], atol=1e-9)
        )

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)

    def test_flat_bars_no_crash(self):
        df = _frame()
        df.loc[:, ["o", "h", "l", "c"]] = 100.0
        out = indicators.add_indicators(df)
        self.assertEqual(len(out), len(df))


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_entries_are_crosses(self):
        ind = indicators.add_indicators(_trend_frame())
        sig = signals.add_signals(ind)
        pos, neg = ind["vi_pos"], ind["vi_neg"]
        exp_long = (B.crossed_above(pos, neg)).fillna(False).astype(bool)
        exp_short = (B.crossed_below(pos, neg)).fillna(False).astype(bool)
        pd.testing.assert_series_equal(sig["long_entry"], exp_long, check_names=False)
        pd.testing.assert_series_equal(sig["short_entry"], exp_short, check_names=False)

    def test_exits_mirror_entries(self):
        sig = signals.add_signals(indicators.add_indicators(_trend_frame()))
        pd.testing.assert_series_equal(sig["long_exit"], sig["short_entry"], check_names=False)
        pd.testing.assert_series_equal(sig["short_exit"], sig["long_entry"], check_names=False)

    def test_crosses_fire_on_trending_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_trend_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        # A signal on the full frame must equal the signal computed on the
        # truncated frame at the same bar index.
        full = signals.add_signals(indicators.add_indicators(_trend_frame()))
        j = 300
        trunc = signals.add_signals(indicators.add_indicators(_trend_frame().iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.vortex as mod
        from strategies.registry import REGISTRY

        self.assertIn("vortex", REGISTRY)
        self.assertIs(REGISTRY["vortex"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "vortex")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
