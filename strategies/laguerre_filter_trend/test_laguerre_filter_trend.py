"""Laguerre filter trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.laguerre_filter_trend import indicators, risk, signals
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
        for col in ("laguerre", "hl2", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_filter_of_constant_is_constant(self):
        df = _frame()
        df["h"] = 50.0
        df["l"] = 50.0
        df["c"] = 50.0
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["laguerre"], 50.0))

    def test_filter_tracks_step(self):
        # step from 100 to 120: filter must move most of the way within 60 bars
        df = _frame(n=200)
        df["h"] = np.where(np.arange(200) < 100, 100.0, 120.0)
        df["l"] = np.where(np.arange(200) < 100, 100.0, 120.0)
        df["c"] = df["h"]
        ind = indicators.add_indicators(df)
        self.assertLess(abs(ind["laguerre"].iloc[-1] - 120.0), 1.0)
        # gamma=0.8 is deliberately slow: ~+5 after 10 bars, most of the
        # way there only after ~60 bars
        self.assertGreater(ind["laguerre"].iloc[110], 102.0)
        self.assertGreater(ind["laguerre"].iloc[160], 115.0)

    def test_filter_matches_manual_recursion(self):
        x = (self.df["h"] + self.df["l"]) / 2.0
        g = 0.8
        l0 = l1 = l2 = l3 = float(x.iloc[0])
        expect = []
        for v in x:
            v = float(v)
            l0n = (1 - g) * v + g * l0
            l1n = -g * l0n + l0 + g * l1
            l2n = -g * l1n + l1 + g * l2
            l3n = -g * l2n + l2 + g * l3
            l0, l1, l2, l3 = l0n, l1n, l2n, l3n
            expect.append((l0 + 2 * l1 + 2 * l2 + l3) / 6.0)
        self.assertTrue(np.allclose(self.ind["laguerre"], expect, atol=1e-9))

    def test_no_nans_after_first_bar(self):
        self.assertFalse(self.ind["laguerre"].isna().any())
        self.assertFalse(self.ind["laguerre"].iloc[60:].isna().any())

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

    def test_slope_filter_applied(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        rising = ind["laguerre"] > ind["laguerre"].shift(1)
        falling = ind["laguerre"] < ind["laguerre"].shift(1)
        self.assertTrue((~sig["long_entry"] | rising.fillna(False)).all())
        self.assertTrue((~sig["short_entry"] | falling.fillna(False)).all())
        # every long entry is a price/filter cross-up
        cross_up = B.crossed_above(ind["c"], ind["laguerre"]).fillna(False)
        self.assertTrue((~sig["long_entry"] | cross_up).all())
        cross_dn = B.crossed_below(ind["c"], ind["laguerre"]).fillna(False)
        self.assertTrue((~sig["short_entry"] | cross_dn).all())

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        pd.testing.assert_series_equal(
            sig["long_exit"],
            B.crossed_below(ind["c"], ind["laguerre"]).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"],
            B.crossed_above(ind["c"], ind["laguerre"]).fillna(False).astype(bool),
            check_names=False)

    def test_crosses_fire_on_swing_frame(self):
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
        import strategies.laguerre_filter_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("laguerre_filter_trend", REGISTRY)
        self.assertIs(REGISTRY["laguerre_filter_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "laguerre_filter_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
