"""Bayesian changepoint tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bayesian_changepoint import indicators, risk, signals


def _frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _step_frame(n=400, change_at=200, seed=11):
    """Returns drift +2%/bar, then -2%/bar after ``change_at``."""
    rng = np.random.default_rng(seed)
    rets = np.where(np.arange(n) < change_at, 0.02, -0.02) + rng.normal(0, 0.005, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestBocd(unittest.TestCase):
    def test_p_change_in_unit_interval(self):
        pc, pm, rl = indicators.bocd(np.random.default_rng(1).normal(0, 0.01, 300))
        self.assertTrue(((pc >= 0) & (pc <= 1)).all())
        self.assertTrue(np.isfinite(pm).all())
        self.assertTrue((rl >= 0).all())

    def test_detects_mean_shift(self):
        rng = np.random.default_rng(2)
        rets = np.concatenate([rng.normal(0.02, 0.005, 200),
                               rng.normal(-0.02, 0.005, 200)])
        pc, pm, rl = indicators.bocd(rets)
        # a changepoint should fire within 10 bars of the shift
        self.assertGreater(pc[200:211].max(), 0.5)

    def test_post_mean_sign_follows_regime(self):
        rng = np.random.default_rng(2)
        rets = np.concatenate([rng.normal(0.02, 0.005, 200),
                               rng.normal(-0.02, 0.005, 200)])
        pc, pm, rl = indicators.bocd(rets)
        self.assertGreater(np.median(pm[100:200]), 0)
        self.assertLess(np.median(pm[250:400]), 0)

    def test_no_false_alarm_on_stationary_series(self):
        rng = np.random.default_rng(4)
        pc, pm, rl = indicators.bocd(rng.normal(0, 0.01, 400))
        # a few spurious detections are fine; the detector must not
        # fire on most bars of a stationary series
        self.assertLess((pc > 0.5).mean(), 0.1)

    def test_run_length_resets_after_changepoint(self):
        rng = np.random.default_rng(2)
        rets = np.concatenate([rng.normal(0.02, 0.005, 200),
                               rng.normal(-0.02, 0.005, 200)])
        pc, pm, rl = indicators.bocd(rets)
        j = int(np.argmax(pc[200:211])) + 200
        self.assertLess(rl[j + 1], rl[j - 1])

    def test_empty_and_short_inputs(self):
        pc, pm, rl = indicators.bocd(np.array([]))
        self.assertEqual(len(pc), 0)
        pc, pm, rl = indicators.bocd(np.array([0.01]))
        self.assertEqual(len(pc), 1)
        self.assertEqual(pc[0], 0.0)

    def test_higher_hazard_fires_more(self):
        rng = np.random.default_rng(6)
        rets = rng.normal(0, 0.01, 400)
        pc_lo, _, _ = indicators.bocd(rets, hazard=0.001)
        pc_hi, _, _ = indicators.bocd(rets, hazard=0.1)
        self.assertGreaterEqual((pc_hi > 0.5).sum(), (pc_lo > 0.5).sum())

    def test_deterministic(self):
        rng = np.random.default_rng(8)
        rets = rng.normal(0.005, 0.01, 200)
        a = indicators.bocd(rets)
        b = indicators.bocd(rets)
        for x, y in zip(a, b):
            np.testing.assert_array_equal(x, y)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("bocd_p_change", "bocd_post_mean", "bocd_run_length", "atr"):
            self.assertIn(col, ind.columns)

    def test_no_nans(self):
        ind = indicators.add_indicators(_frame())
        for col in ("bocd_p_change", "bocd_post_mean", "bocd_run_length"):
            self.assertFalse(ind[col].isna().any(), col)

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_entries_match_cp_and_mean_sign(self):
        ind = indicators.add_indicators(_step_frame())
        sig = signals.add_signals(ind)
        cp = ind["bocd_p_change"] > 0.5
        expect_long = (cp & (ind["bocd_post_mean"] > 0)).fillna(False)
        expect_short = (cp & (ind["bocd_post_mean"] < 0)).fillna(False)
        pd.testing.assert_series_equal(sig["long_entry"], expect_long.astype(bool),
                                       check_names=False)
        pd.testing.assert_series_equal(sig["short_entry"], expect_short.astype(bool),
                                       check_names=False)

    def test_step_frame_fires_both_sides(self):
        # Three regimes (-, +, -): the two changepoints must fire a
        # short, then a long, then a short. (A two-regime frame that
        # starts in the + regime fires no long entry -- there is no
        # changepoint at the series start.)
        rng = np.random.default_rng(13)
        n = 450
        rets = np.where(np.arange(n) < 150, -0.02,
                        np.where(np.arange(n) < 300, 0.02, -0.02)) \
            + rng.normal(0, 0.005, n)
        c = 100 * np.exp(np.cumsum(rets))
        o = np.concatenate([[100.0], c[:-1]])
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": h, "l": l, "c": c, "v": 100.0})
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _step_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 250
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))

    def test_exits_include_next_changepoint(self):
        ind = indicators.add_indicators(_step_frame())
        sig = signals.add_signals(ind)
        cp = (ind["bocd_p_change"] > 0.5).fillna(False)
        self.assertTrue((sig["long_exit"] >= cp).all())
        self.assertTrue((sig["short_exit"] >= cp).all())


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.WARMUP, 50)
        self.assertEqual(indicators.HAZARD, 0.01)

    def test_registration(self):
        import strategies.bayesian_changepoint as mod
        from strategies.registry import REGISTRY

        self.assertIn("bayesian_changepoint", REGISTRY)
        self.assertIs(REGISTRY["bayesian_changepoint"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "bayesian_changepoint")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
