"""Wavelet-trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wavelet_trend import indicators, risk, signals
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
    c = 100 + np.linspace(0, 40, n) + rng.normal(0, 0.5, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestFilters(unittest.TestCase):
    def test_db4_lowpass_sums_to_sqrt2(self):
        self.assertAlmostEqual(float(indicators.DB4_H.sum()), np.sqrt(2), places=12)

    def test_db4_highpass_sums_to_zero(self):
        self.assertAlmostEqual(float(indicators.DB4_G.sum()), 0.0, places=12)

    def test_transform_has_left_inverse(self):
        # Symmetric extension makes the transform overcomplete
        # (88 coefficients for a 64-sample window), so it is not
        # square-orthogonal -- but Tinv @ T == I to machine precision.
        t, tinv, n_approx, coeff_len = indicators.build_transform_matrices(64, 3)
        self.assertEqual(t.shape, (88, 64))
        self.assertEqual(tinv.shape, (64, 88))
        self.assertEqual(n_approx, 15)
        np.testing.assert_allclose(tinv @ t, np.eye(64), atol=1e-10)

    def test_perfect_reconstruction_full_coefficients(self):
        rng = np.random.default_rng(3)
        x = rng.normal(0, 1, 64)
        a, ds, sizes = indicators._wavedec(x, 3)
        recon = indicators._waverec(a, ds, sizes)
        np.testing.assert_allclose(recon, x, atol=1e-10)

    def test_approximation_is_smoother_than_raw(self):
        rng = np.random.default_rng(5)
        x = np.linspace(0, 10, 64) + rng.normal(0, 2.0, 64)
        approx = indicators.dwt_approx(x)
        self.assertLess(np.std(np.diff(approx)), np.std(np.diff(x)))
        # approximation tracks the trend, not the noise
        self.assertGreater(np.corrcoef(approx, np.linspace(0, 10, 64))[0, 1], 0.9)

    def test_approximation_of_constant_is_constant(self):
        approx = indicators.dwt_approx(np.full(64, 7.0))
        np.testing.assert_allclose(approx, 7.0, atol=1e-10)

    def test_approximation_of_linear_is_linear(self):
        # db4 has 4 vanishing moments: the approx of a line is the
        # line, up to the small symmetric-extension edge bias
        # (interior accurate to ~0.07 on a 0-10 ramp, last value
        # ~0.17 low); a periodic extension would err by ~5.7 here.
        x = np.linspace(0, 10, 64)
        approx = indicators.dwt_approx(x)
        np.testing.assert_allclose(approx[8:56], x[8:56], atol=0.1)
        self.assertLess(np.max(np.abs(approx - x)), 0.3)
        self.assertAlmostEqual(approx[-1], 10.0, delta=0.3)


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("wav_approx", "wav_slope", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_warmup_nans(self):
        self.assertTrue(self.ind["wav_approx"].iloc[:63].isna().all())
        self.assertFalse(self.ind["wav_approx"].iloc[63:].isna().any())

    def test_slope_is_5bar_diff(self):
        pd.testing.assert_series_equal(
            self.ind["wav_slope"], self.ind["wav_approx"].diff(5), check_names=False)

    def test_approx_tracks_uptrend(self):
        ind = indicators.add_indicators(_trend_frame())
        a = ind["wav_approx"].dropna()
        self.assertGreater(a.iloc[-1], a.iloc[0])
        self.assertGreater((ind["wav_slope"].dropna() > 0).mean(), 0.7)

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

    def test_entries_need_slope_turn_and_position_vs_approx(self):
        ind = indicators.add_indicators(_trend_frame())
        sig = signals.add_signals(ind)
        slope_up = (ind["wav_slope"] > 0) & (ind["wav_slope"].shift(1) <= 0)
        expect = (slope_up & (ind["c"] > ind["wav_approx"])).fillna(False)
        pd.testing.assert_series_equal(sig["long_entry"], expect.astype(bool),
                                       check_names=False)

    def test_uptrend_frame_produces_longs(self):
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
        self.assertEqual(risk.RISK.target_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.WARMUP, 64)

    def test_registration(self):
        import strategies.wavelet_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("wavelet_trend", REGISTRY)
        self.assertIs(REGISTRY["wavelet_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "wavelet_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
