"""FFT dominant-cycle tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fft_dominant_cycle import indicators, risk, signals
from strategies import base as B


def _frame(n=600, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _sine_frame(n=600, seed=21, period=32, amp=10.0):
    rng = np.random.default_rng(seed)
    x = np.arange(n)
    c = 100 + amp * np.sin(2 * np.pi * x / period) + rng.normal(0, 0.3, n)
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
        for col in ("fft_cycle", "fft_slope", "sma50", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_warmup_nans(self):
        self.assertTrue(self.ind["fft_cycle"].iloc[:127].isna().all())
        self.assertFalse(self.ind["fft_cycle"].iloc[127:].isna().any())
        self.assertTrue(self.ind["sma50"].iloc[:49].isna().all())

    def test_pure_sine_recovered(self):
        # A clean 32-bar sine (period inside 8-64) should dominate the
        # reconstruction: the cycle correlates strongly with the sine.
        ind = indicators.add_indicators(_sine_frame(period=32))
        cyc = ind["fft_cycle"].dropna().to_numpy()
        x = np.arange(len(cyc))
        s = np.sin(2 * np.pi * (x + 127) / 32.0)
        self.assertGreater(abs(np.corrcoef(cyc, s)[0, 1]), 0.8)

    def test_out_of_band_sine_suppressed(self):
        # A 4-bar sine (period < 8) must NOT dominate the reconstruction.
        ind = indicators.add_indicators(_sine_frame(period=4, amp=10.0))
        cyc = ind["fft_cycle"].dropna().to_numpy()
        x = np.arange(len(cyc))
        s = np.sin(2 * np.pi * (x + 127) / 4.0)
        self.assertLess(abs(np.corrcoef(cyc, s)[0, 1]), 0.5)

    def test_constant_series_cycle_near_zero(self):
        df = _frame()
        df["c"] = 50.0
        df["h"] = 50.0
        df["l"] = 50.0
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["fft_cycle"].dropna(), 0.0, atol=1e-9))

    def test_slope_is_cycle_diff(self):
        pd.testing.assert_series_equal(
            self.ind["fft_slope"], self.ind["fft_cycle"].diff(), check_names=False)

    def test_sma50_analytic(self):
        expect = self.df["c"].rolling(50, min_periods=50).mean()
        pd.testing.assert_series_equal(self.ind["sma50"], expect, check_names=False)

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

    def test_entries_need_slope_turn_and_trend_filter(self):
        ind = indicators.add_indicators(_sine_frame())
        sig = signals.add_signals(ind)
        slope_up = (ind["fft_slope"] > 0) & (ind["fft_slope"].shift(1) <= 0)
        expect_long = (slope_up & (ind["c"] > ind["sma50"])).fillna(False)
        pd.testing.assert_series_equal(sig["long_entry"], expect_long.astype(bool),
                                       check_names=False)

    def test_exits_include_slope_flip(self):
        ind = indicators.add_indicators(_sine_frame())
        sig = signals.add_signals(ind)
        slope_dn = (ind["fft_slope"] < 0) & (ind["fft_slope"].shift(1) >= 0)
        self.assertTrue((sig["long_exit"] >= slope_dn.fillna(False)).all())

    def test_signals_fire_on_sine_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_sine_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _sine_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 400
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.target_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 180)

    def test_registration(self):
        import strategies.fft_dominant_cycle as mod
        from strategies.registry import REGISTRY

        self.assertIn("fft_dominant_cycle", REGISTRY)
        self.assertIs(REGISTRY["fft_dominant_cycle"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "fft_dominant_cycle")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
