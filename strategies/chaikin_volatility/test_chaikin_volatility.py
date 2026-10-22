"""Chaikin Volatility Expansion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chaikin_volatility import indicators, risk, signals
from strategies import base as B


def _frame(n=600, seed=7, drift=0.001, vol=0.01, range_frac=0.005):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, range_frac, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, range_frac, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _spike_frame(n=400, seed=11):
    """Flat range, then an expanding-range block in the middle.

    h-l equals the width profile exactly (o=c), so cv is ~0 outside
    the block and spikes hard inside it.
    """
    rng = np.random.default_rng(seed)
    c = 100 + np.cumsum(rng.normal(0, 0.2, n))
    o = c.copy()
    width = np.full(n, 0.3)
    width[150:220] = np.linspace(0.3, 6.0, 70)  # range expands 20x
    width[220:] = 0.3
    h = c + width / 2
    l = c - width / 2
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("cv", "ema_hl", "sma50", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_cv_formula_vs_hand_computation(self):
        ema_hl = B.ema(self.df["h"] - self.df["l"], 10)
        prev = ema_hl.shift(10)
        expect = (100 * (ema_hl - prev) / prev).dropna()
        got = self.ind["cv"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_cv_near_zero_on_constant_range(self):
        # Truly constant-width range (h-l = 0.4 exactly): the EMA of a
        # constant is constant, so the ROC of that EMA is zero.
        n = 400
        rng = np.random.default_rng(3)
        c = 100 + np.cumsum(rng.normal(0, 0.2, n))
        o = c.copy()
        h = c + 0.2
        l = c - 0.2
        v = rng.uniform(50, 150, n)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})
        cv = indicators.add_indicators(df)["cv"].iloc[100:]
        self.assertTrue((cv.abs() < 1e-8).all())

    def test_spike_detection_on_expanding_range(self):
        ind = indicators.add_indicators(_spike_frame())
        cv = ind["cv"].fillna(0)
        self.assertGreater(cv.iloc[150:220].max(), 5.0)
        # Before the expansion block, cv sits near zero.
        self.assertTrue((cv.iloc[80:140].abs() < 2.0).all())

    def test_warmup_nans(self):
        # cv(10,10) valid after ~19 bars; sma50 needs 50 bars.
        self.assertTrue(self.ind["cv"].iloc[:19].isna().all())
        self.assertFalse(self.ind["cv"].iloc[60:].isna().any())
        self.assertTrue(self.ind["sma50"].iloc[:49].isna().all())
        self.assertFalse(self.ind["sma50"].iloc[60:].isna().any())

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

    def test_threshold_cross_logic(self):
        # Entries fire exactly on cv crossing above +trigger, gated by
        # a valid sma50 (the filter is False — not NaN — where sma50
        # is not yet formed, so early crosses are correctly dropped).
        ind = indicators.add_indicators(_spike_frame())
        sig = signals.add_signals(ind)
        up = B.crossed_above(ind["cv"], signals._const_like(ind["cv"], 5.0))
        expect = (up.fillna(False) & ind["sma50"].notna())
        self.assertTrue((sig["long_entry"] | sig["short_entry"]
                         == expect).all())
        self.assertGreater(sig["long_entry"].sum() + sig["short_entry"].sum(), 0)

    def test_trend_filter_gates_longs(self):
        # In the spike block, entries only fire long when close > sma50
        # and only fire short when close < sma50.
        ind = indicators.add_indicators(_spike_frame())
        sig = signals.add_signals(ind)
        longs = sig["long_entry"]
        shorts = sig["short_entry"]
        if longs.sum():
            self.assertTrue((ind.loc[longs, "c"] > ind.loc[longs, "sma50"]).all())
        if shorts.sum():
            self.assertTrue((ind.loc[shorts, "c"] < ind.loc[shorts, "sma50"]).all())

    def test_no_longs_below_sma50_on_driven_frame(self):
        # Forced-downtrend frame: engineered crosses must all be short.
        n = 300
        rng = np.random.default_rng(5)
        c = 100 - np.linspace(0, 30, n) + rng.normal(0, 0.3, n)
        o = np.concatenate([[c[0]], c[:-1]])
        w = np.full(n, 0.2)
        w[120:180] = np.linspace(0.2, 4.0, 60)
        h = np.maximum(o, c) + w
        l = np.minimum(o, c) - w
        v = rng.uniform(50, 150, n)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_exits_fire_after_entry_block(self):
        # After the expansion block ends, cv rolls back over: exits fire.
        ind = indicators.add_indicators(_spike_frame())
        sig = signals.add_signals(ind)
        self.assertGreater(sig["long_exit"].iloc[220:].sum(), 0)

    def test_exits_equal_rollover_crosses(self):
        ind = indicators.add_indicators(_spike_frame())
        sig = signals.add_signals(ind)
        dn_trig = B.crossed_below(ind["cv"], signals._const_like(ind["cv"], 5.0))
        dn_zero = B.crossed_below(ind["cv"], signals._const_like(ind["cv"], 0.0))
        expect = (dn_trig | dn_zero).fillna(False).astype(bool)
        pd.testing.assert_series_equal(sig["long_exit"], expect,
                                       check_names=False)
        pd.testing.assert_series_equal(sig["short_exit"], expect,
                                       check_names=False)

    def test_no_lookahead(self):
        df = _spike_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 250
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 100)
        self.assertEqual(risk.WARMUP, 70)

    def test_registration(self):
        import strategies.chaikin_volatility as mod
        from strategies.registry import REGISTRY

        self.assertIn("chaikin_volatility", REGISTRY)
        self.assertIs(REGISTRY["chaikin_volatility"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "chaikin_volatility")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
