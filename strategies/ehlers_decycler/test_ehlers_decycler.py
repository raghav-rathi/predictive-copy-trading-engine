"""Decycler trend-engine tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_decycler import indicators, risk, signals
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


def _step_frame(n=400, step_at=200, up=1.0):
    """Clean regime flip: flat 100, then step to 120 (up) or 80 (down)."""
    c = np.where(np.arange(n) >= step_at, 100.0 + 20.0 * up, 100.0)
    c = c.astype(float)
    o = np.concatenate([[c[0]], c[:-1]])
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
        for col in ("hp", "decycler", "alpha", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_alpha_matches_hand_computation(self):
        w = 0.707 * 2.0 * math.pi / 20
        expect = (math.cos(w) + math.sin(w) - 1.0) / math.cos(w)
        self.assertAlmostEqual(indicators.filter_alpha(20), expect, places=12)
        # alpha must sit in (0, 1) for a stable 2-pole Butterworth HP
        self.assertTrue(0.0 < expect < 1.0)

    def test_highpass_recursion_matches_hand_loop(self):
        c = self.df["c"].to_numpy(dtype=float)
        a = indicators.filter_alpha(20)
        hp = np.zeros(len(c))
        a1, a2 = 1.0 - a / 2.0, 1.0 - a
        for i in range(2, len(c)):
            hp[i] = (a1 * a1 * (c[i] - 2 * c[i - 1] + c[i - 2])
                     + 2 * a2 * hp[i - 1] - a2 * a2 * hp[i - 2])
        self.assertTrue(np.allclose(self.ind["hp"].to_numpy(), hp, atol=1e-12))
        self.assertEqual(self.ind["hp"].iloc[0], 0.0)
        self.assertEqual(self.ind["hp"].iloc[1], 0.0)

    def test_decycler_equals_close_minus_hp(self):
        self.assertTrue(np.allclose(
            self.ind["decycler"].to_numpy(),
            (self.ind["c"] - self.ind["hp"]).to_numpy(), atol=1e-12))

    def test_decycler_tracks_linear_trend_closely(self):
        # On a pure linear trend the high-pass output decays to ~0, so the
        # decycler should hug the price line after the filter spins up.
        n = 400
        c = 100.0 + 0.5 * np.arange(n)
        df = _frame(n).copy()
        df["c"] = c
        df["o"] = np.concatenate([[c[0]], c[:-1]])
        df["h"] = np.maximum(df["o"], df["c"]) * 1.0005
        df["l"] = np.minimum(df["o"], df["c"]) * 0.9995
        ind = indicators.add_indicators(df, period=20)
        resid = (ind["decycler"] - c).iloc[100:]
        self.assertLess(resid.abs().max(), 1.0)  # << bar-to-bar move of 0.5

    def test_decycler_attenuates_pure_cycle(self):
        # A fast sine (period 5, well under cutoff 20) is passed by the
        # HP filter with |H|~0.98 and stripped out: the decycler's
        # residual amplitude |1-H|~0.30, i.e. strongly attenuated
        # relative to the raw sine amplitude (the Butterworth's phase
        # shift means cycles near the cutoff only attenuate, never
        # cancel fully).
        n = 400
        x = np.linspace(0, n / 5 * 2 * np.pi, n)
        c = 100.0 + 10.0 * np.sin(x)
        df = _frame(n).copy()
        df["c"] = c
        df["o"] = np.concatenate([[c[0]], c[:-1]])
        df["h"] = np.maximum(df["o"], df["c"]) * 1.0005
        df["l"] = np.minimum(df["o"], df["c"]) * 0.9995
        ind = indicators.add_indicators(df, period=20)
        d = ind["decycler"].iloc[150:] - 100.0
        # steady-state amplitude ~3.0 (|1-H| ~ 0.30 x 10); keep margin
        # for the start-up transient but require real attenuation.
        self.assertLess(d.abs().max(), 4.0)

    def test_no_nan_on_first_bars(self):
        # hp[0..1] = 0 by construction, so hp/decycler are defined from
        # bar 0 (ATR still NaN early — that is the risk layer's column).
        self.assertFalse(self.ind["hp"].iloc[:2].isna().any())
        self.assertFalse(self.ind["decycler"].iloc[:2].isna().any())
        self.assertFalse(self.ind["decycler"].isna().any())

    def test_no_lookahead(self):
        full = signals.add_signals(self.ind)
        j = 350
        trunc = signals.add_signals(
            indicators.add_indicators(self.df.iloc[: j + 1]))
        self.assertAlmostEqual(float(full["decycler"].iloc[j]),
                               float(trunc["decycler"].iloc[j]), places=10)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))

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

    def test_cross_signals_fire_on_step_flip(self):
        sig = signals.add_signals(
            indicators.add_indicators(_step_frame(up=1.0)))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertEqual(sig["short_entry"].sum(), 0)
        sig_dn = signals.add_signals(
            indicators.add_indicators(_step_frame(up=-1.0)))
        self.assertGreater(sig_dn["short_entry"].sum(), 0)
        self.assertEqual(sig_dn["long_entry"].sum(), 0)

    def test_long_entry_requires_rising_decycler(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        ind = indicators.add_indicators(_frame())
        longs = sig["long_entry"]
        self.assertTrue(((ind["decycler"] > ind["decycler"].shift(1))
                         .loc[longs].fillna(False)).all())
        shorts = sig["short_entry"]
        self.assertTrue(((ind["decycler"] < ind["decycler"].shift(1))
                         .loc[shorts].fillna(False)).all())

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_frame())
        sig = signals.add_signals(ind)
        c, d = ind["c"], ind["decycler"]
        pd.testing.assert_series_equal(
            sig["long_exit"], B.crossed_below(c, d).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], B.crossed_above(c, d).fillna(False).astype(bool),
            check_names=False)

    def test_entries_are_crosses_of_close_over_decycler(self):
        ind = indicators.add_indicators(_step_frame(up=1.0))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["long_entry"]][0]
        self.assertTrue(ind["c"].iloc[idx] > ind["decycler"].iloc[idx])
        self.assertLessEqual(ind["c"].iloc[idx - 1],
                             ind["decycler"].iloc[idx - 1])


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        import strategies.ehlers_decycler as mod
        from strategies.registry import REGISTRY

        self.assertIn("ehlers_decycler", REGISTRY)
        self.assertIs(REGISTRY["ehlers_decycler"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "ehlers_decycler")
        self.assertEqual(mod.SPEC.name, "Decycler Trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
