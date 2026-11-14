"""GoNoGo Trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.gonogo_trend import indicators, risk, signals
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


def _swing_frame(n=800, seed=21, cycles=4):
    """Slow sine swings: GoNoGo states flip repeatedly both ways."""
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
        for col in ("gonogo_score", "gonogo_state", "gonogo_osc",
                    "ema9", "ema21", "ema50", "macd_hist", "adx",
                    "plus_di", "minus_di", "rsi", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_score_range_and_states(self):
        s = self.ind["gonogo_score"].dropna()
        self.assertTrue(((s >= -5) & (s <= 5)).all())
        st = self.ind["gonogo_state"].dropna()
        self.assertTrue(set(st.unique()) <= {-2.0, -1.0, 0.0, 1.0, 2.0})
        # state mapping is exact
        expect = np.where(s >= 4, 2.0, np.where(s >= 2, 1.0,
                          np.where(s <= -4, -2.0, np.where(s <= -2, -1.0, 0.0))))
        got = self.ind.loc[s.index, "gonogo_state"].to_numpy()
        self.assertTrue(np.array_equal(got, expect))

    def test_score_is_sum_of_five_components(self):
        # each component is -1/0/+1; recompute EMA alignment + RSI legs
        ema9, ema21, ema50 = self.ind["ema9"], self.ind["ema21"], self.ind["ema50"]
        s_ema = np.where((ema9 > ema21) & (ema21 > ema50), 1.0,
                         np.where((ema9 < ema21) & (ema21 < ema50), -1.0, 0.0))
        s_rsi = np.where(self.ind["rsi"] > 50, 1.0,
                         np.where(self.ind["rsi"] < 50, -1.0, 0.0))
        # score minus those two legs must be in [-3, 3] (the other 3 legs)
        rest = self.ind["gonogo_score"] - s_ema - s_rsi
        self.assertTrue(((rest.dropna() >= -3) & (rest.dropna() <= 3)).all())

    def test_oscillator_clamped(self):
        osc = self.ind["gonogo_osc"].dropna()
        self.assertTrue(((osc >= -6) & (osc <= 6)).all())

    def test_oscillator_formula(self):
        hist = self.ind["macd_hist"]
        z = hist / hist.rolling(50, min_periods=50).std()
        expect = (z + (self.ind["rsi"] - 50.0) / 25.0).clip(-6, 6)
        pd.testing.assert_series_equal(self.ind["gonogo_osc"], expect,
                                       check_names=False)

    def test_warmup_nans(self):
        # Donchian(50)/EMA(50) need 50 bars; oscillator z needs 50 more.
        self.assertTrue(self.ind["gonogo_score"].iloc[:49].isna().all())
        self.assertFalse(self.ind["gonogo_score"].iloc[60:].isna().any())
        self.assertFalse(self.ind["gonogo_osc"].iloc[100:].isna().any())

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

    def test_entries_only_on_state_transitions(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        st, prev = ind["gonogo_state"], ind["gonogo_state"].shift(1)
        longs = sig["long_entry"]
        self.assertTrue(((st[longs] >= 1) & (prev[longs] <= 0)).all())
        self.assertTrue((ind.loc[longs, "gonogo_osc"] > 0).all())
        shorts = sig["short_entry"]
        self.assertTrue(((st[shorts] <= -1) & (prev[shorts] >= 0)).all())
        self.assertTrue((ind.loc[shorts, "gonogo_osc"] < 0).all())

    def test_exits_are_state_returns(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        pd.testing.assert_series_equal(
            sig["long_exit"], (ind["gonogo_state"] <= 0).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], (ind["gonogo_state"] >= 0).fillna(False).astype(bool),
            check_names=False)

    def test_entries_fire_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 400
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        import strategies.gonogo_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("gonogo_trend", REGISTRY)
        self.assertIs(REGISTRY["gonogo_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "gonogo_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
