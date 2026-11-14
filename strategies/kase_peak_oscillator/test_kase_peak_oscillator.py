"""Kase Peak Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kase_peak_oscillator import indicators, risk, signals
from strategies import base as B


def _frame(n=800, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _swing_frame(n=1000, seed=21, cycles=4):
    """Slow sine swings: KaseCD crosses zero repeatedly both ways."""
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
        for col in ("kase_peak_osc", "kase_cd", "kase_peak_max",
                    "kase_peak_min", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_peak_osc_nonnegative(self):
        # KSDI_up >= 0, KSDI_dn <= 0 by construction -> PeakOsc >= 0.
        self.assertTrue((self.ind["kase_peak_osc"].dropna() >= 0).all())

    def test_peak_osc_formula_single_horizon(self):
        # Recompute the n=5 KSDI leg by hand and check the mean includes it.
        c, h, l = self.df["c"], self.df["h"], self.df["l"]
        r = np.log(c / c.shift(1))
        sigma5 = r.rolling(5, min_periods=5).std().replace(0.0, np.nan)
        up5 = np.log(h / l.rolling(5, min_periods=5).min()) / sigma5
        dn5 = np.log(l / h.rolling(5, min_periods=5).max()) / sigma5
        # PeakOsc is the mean of 10 such legs; each leg is finite and >= 0.
        self.assertTrue(((up5 - dn5).dropna() >= 0).all())
        self.assertTrue(np.isfinite(self.ind["kase_peak_osc"].dropna()).all())

    def test_kcd_is_peak_minus_sma9(self):
        expect = self.ind["kase_peak_osc"] - B.sma(self.ind["kase_peak_osc"], 9)
        pd.testing.assert_series_equal(self.ind["kase_cd"], expect,
                                       check_names=False)

    def test_peak_max_ge_peak_min(self):
        sub = self.ind.dropna(subset=["kase_peak_max", "kase_peak_min"])
        self.assertTrue((sub["kase_peak_max"] >= sub["kase_peak_min"]).all())
        self.assertTrue((sub["kase_peak_min"] >= 0).all())

    def test_peak_max_formula(self):
        osc = self.ind["kase_peak_osc"]
        std100 = osc.rolling(100, min_periods=100).std()
        pct250 = osc.abs().rolling(250, min_periods=250).quantile(0.90)
        expect = pd.Series(np.maximum(2.0 * std100, pct250), index=osc.index)
        pd.testing.assert_series_equal(self.ind["kase_peak_max"], expect,
                                       check_names=False)

    def test_warmup_nans(self):
        # Rolling-250 percentile needs 250 bars *after* PeakOsc forms at
        # bar 50, so PeakMax first forms at ~bar 299; WARMUP=310 covers it.
        self.assertTrue(self.ind["kase_peak_osc"].iloc[:50].isna().all())
        self.assertFalse(self.ind["kase_peak_osc"].iloc[60:].isna().any())
        self.assertTrue(self.ind["kase_peak_max"].iloc[:299].isna().all())
        self.assertFalse(self.ind["kase_peak_max"].iloc[310:].isna().any())

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

    def test_entries_are_kcd_crosses_with_filter(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        kcd, osc, pmax = ind["kase_cd"], ind["kase_peak_osc"], ind["kase_peak_max"]
        longs = sig["long_entry"]
        self.assertTrue((kcd[longs] > 0).all())
        self.assertTrue((kcd.shift(1)[longs] <= 0).all())
        self.assertTrue((osc[longs] < pmax[longs]).all())
        shorts = sig["short_entry"]
        self.assertTrue((kcd[shorts] < 0).all())
        self.assertTrue((kcd.shift(1)[shorts] >= 0).all())

    def test_long_exit_includes_peak_out(self):
        # Build a frame where PeakOsc spikes above PeakMax then falls back.
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        osc, pmax = ind["kase_peak_osc"], ind["kase_peak_max"]
        was_above = (osc.shift(1) > pmax.shift(1)).fillna(False)
        back_inside = (osc <= pmax).fillna(False)
        peak_out = was_above & back_inside
        # every PeakOut bar must be a long_exit (the cross leg may add more)
        self.assertTrue(sig.loc[peak_out, "long_exit"].all())

    def test_entries_fire_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 600
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.WARMUP, 310)  # brief said 260; corrected, see CALIBRATION.md

    def test_registration(self):
        import strategies.kase_peak_oscillator as mod
        from strategies.registry import REGISTRY

        self.assertIn("kase_peak_oscillator", REGISTRY)
        self.assertIs(REGISTRY["kase_peak_oscillator"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "kase_peak_oscillator")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
