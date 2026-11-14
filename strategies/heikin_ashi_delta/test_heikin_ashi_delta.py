"""Heikin Ashi delta tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.heikin_ashi_delta import indicators, risk, signals
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
    """Slow sine swings: HA delta changes sign repeatedly in both directions."""
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
        for col in ("ha_open", "ha_close", "ha_delta", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_ha_close_is_ohlc_average(self):
        expect = (self.df["o"] + self.df["h"] + self.df["l"] + self.df["c"]) / 4.0
        pd.testing.assert_series_equal(self.ind["ha_close"], expect, check_names=False)

    def test_ha_open_seeded_and_recursive(self):
        self.assertEqual(self.ind["ha_open"].iloc[0], self.df["o"].iloc[0])
        for i in (1, 2, 10, 100):
            expect = (self.ind["ha_open"].iloc[i - 1] + self.ind["ha_close"].iloc[i - 1]) / 2.0
            self.assertAlmostEqual(self.ind["ha_open"].iloc[i], expect, places=9)

    def test_delta_is_close_minus_open(self):
        pd.testing.assert_series_equal(
            self.ind["ha_delta"], self.ind["ha_close"] - self.ind["ha_open"],
            check_names=False)

    def test_no_nans_after_warmup(self):
        self.assertFalse(self.ind[["ha_open", "ha_close", "ha_delta"]].isna().any().any())

    def test_uptrend_gives_positive_delta(self):
        # Monotonic rally: HA delta should be positive almost everywhere.
        n = 200
        c = np.linspace(100, 200, n)
        o = np.concatenate([[100.0], c[:-1]])
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": c * 1.001, "l": o * 0.999, "c": c,
            "v": np.full(n, 100.0)})
        ind = indicators.add_indicators(df)
        self.assertTrue((ind["ha_delta"].iloc[10:] > 0).all())

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

    def test_entries_match_delta_sign(self):
        ind = indicators.add_indicators(_frame())
        sig = signals.add_signals(ind)
        longs = sig["long_entry"]
        self.assertTrue((ind.loc[longs, "ha_close"] > ind.loc[longs, "ha_open"]).all())
        shorts = sig["short_entry"]
        self.assertTrue((ind.loc[shorts, "ha_close"] < ind.loc[shorts, "ha_open"]).all())
        # every long entry is a zero-cross up (or a turn after >=3 negatives)
        d = ind["ha_delta"]
        cross_up = B.crossed_above(d, 0).fillna(False)
        neg_run = (d.shift(1) < 0) & (d.shift(2) < 0) & (d.shift(3) < 0)
        expect = (cross_up | ((d > 0) & neg_run)).fillna(False)
        pd.testing.assert_series_equal(sig["long_entry"], expect, check_names=False)

    def test_exits_are_zero_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        d = ind["ha_delta"]
        pd.testing.assert_series_equal(
            sig["long_exit"], B.crossed_below(d, 0).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], B.crossed_above(d, 0).fillna(False).astype(bool),
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
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.heikin_ashi_delta as mod
        from strategies.registry import REGISTRY

        self.assertIn("heikin_ashi_delta", REGISTRY)
        self.assertIs(REGISTRY["heikin_ashi_delta"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "heikin_ashi_delta")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
