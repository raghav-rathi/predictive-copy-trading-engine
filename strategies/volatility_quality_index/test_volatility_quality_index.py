"""VQI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.volatility_quality_index import indicators, risk, signals
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


def _trend_frame(n=500, seed=21):
    rng = np.random.default_rng(seed)
    c = 100 + np.linspace(0, 40, n) + rng.normal(0, 0.3, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestVqiMath(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("vqi_eff", "vqi_s", "vqi", "vqi_chg10", "vqi_gate",
                    "ema20", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_efficiency_analytic(self):
        # e_t = (c_t - c_{t-1}) / TR_t, |e| <= 1 by construction
        tr = B.true_range(self.df["h"], self.df["l"], self.df["c"])
        expect = (self.df["c"].diff() / tr).fillna(0.0)
        # TR == 0 rows are forced to 0; none occur in this frame
        pd.testing.assert_series_equal(self.ind["vqi_eff"], expect, check_names=False)
        self.assertTrue((self.ind["vqi_eff"].abs() <= 1.0 + 1e-9).all())

    def test_efficiency_of_pure_trend_is_plus_one(self):
        # Every bar closes at its high with no gap: e_t = +1.
        n = 100
        c = 100 + np.arange(n, dtype=float)
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": c - 1, "h": c, "l": c - 1, "c": c, "v": 100.0})
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["vqi_eff"].iloc[1:], 1.0))

    def test_s_is_10bar_sum_of_efficiency(self):
        expect = self.ind["vqi_eff"].rolling(10, min_periods=10).sum()
        pd.testing.assert_series_equal(self.ind["vqi_s"], expect, check_names=False)

    def test_vqi_is_wma14_of_s(self):
        expect = indicators.wma(self.ind["vqi_s"], 14)
        pd.testing.assert_series_equal(self.ind["vqi"], expect, check_names=False)

    def test_wma_weights_analytic(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        got = indicators.wma(s, 2)
        # WMA(2): (1*x_{i-1} + 2*x_i)/3
        self.assertAlmostEqual(got.iloc[1], (1 * 1 + 2 * 2) / 3.0)
        self.assertAlmostEqual(got.iloc[3], (1 * 3 + 2 * 4) / 3.0)

    def test_chg10_is_10bar_diff(self):
        expect = self.ind["vqi"].diff(10)
        pd.testing.assert_series_equal(self.ind["vqi_chg10"], expect, check_names=False)

    def test_gate_definition(self):
        chg = self.ind["vqi_chg10"]
        med = chg.abs().rolling(50, min_periods=50).median()
        expect = (chg.abs() >= 0.5 * med).fillna(False)
        pd.testing.assert_series_equal(self.ind["vqi_gate"], expect, check_names=False)

    def test_warmup_nans(self):
        self.assertTrue(self.ind["vqi"].iloc[:22].isna().all())
        self.assertFalse(self.ind["vqi"].iloc[23:].isna().any())

    def test_trending_series_has_positive_vqi(self):
        ind = indicators.add_indicators(_trend_frame())
        self.assertGreater(ind["vqi"].dropna().median(), 0)

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

    def test_entries_match_chg_and_gate(self):
        ind = indicators.add_indicators(_trend_frame())
        sig = signals.add_signals(ind)
        expect_long = ((ind["vqi_chg10"] > 0) & ind["vqi_gate"]).fillna(False)
        pd.testing.assert_series_equal(sig["long_entry"], expect_long.astype(bool),
                                       check_names=False)

    def test_gate_blocks_small_changes(self):
        # Build a frame whose VQI change is tiny: gate must block entries.
        df = _frame()
        df["c"] = 100.0  # flat closes -> e = 0, VQI change = 0
        df["h"] = 101.0
        df["l"] = 99.0
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig["long_entry"].sum(), 0)
        self.assertEqual(sig["short_entry"].sum(), 0)

    def test_trend_frame_produces_longs(self):
        sig = signals.add_signals(indicators.add_indicators(_trend_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _trend_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 300
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.target_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.volatility_quality_index as mod
        from strategies.registry import REGISTRY

        self.assertIn("volatility_quality_index", REGISTRY)
        self.assertIs(REGISTRY["volatility_quality_index"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "volatility_quality_index")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
