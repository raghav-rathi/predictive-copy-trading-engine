"""DPO zero-line cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.detrended_price_oscillator import indicators, risk, signals
from strategies import base as B


def _frame(n=600, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _swing_frame(n=900, seed=21, drift=0.2):
    """Trend + fast cycles: DPO crosses zero repeatedly; the trend filter
    admits longs on +drift frames and shorts on -drift frames."""
    rng = np.random.default_rng(seed)
    t_ = np.arange(n)
    c = 100 + drift * t_ + 4 * np.sin(2 * np.pi * t_ / 60) + rng.normal(0, 0.3, n)
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
        for col in ("dpo", "sma_ma", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_dpo_matches_hand_computation(self):
        # n=6 -> lag = 6//2 + 1 = 4
        c = pd.Series([float(i) for i in range(1, 31)], name="c")
        got = indicators.dpo(c, 6)
        lag = 4
        ma = c.rolling(6, min_periods=6).mean()
        for j in range(lag + 5, len(c)):
            expect = c.iloc[j] - ma.iloc[j - lag]
            self.assertAlmostEqual(got.iloc[j], expect, places=9)

    def test_shift_offset_correctness(self):
        # DPO's displacement is exactly n//2 + 1 bars back.
        n, lag = 20, 20 // 2 + 1
        ma = self.df["c"].rolling(n, min_periods=n).mean()
        j = 500
        self.assertAlmostEqual(
            self.ind["dpo"].iloc[j],
            self.df["c"].iloc[j] - ma.iloc[j - lag],
            places=9,
        )
        # A one-bar-off lag would give a different value.
        wrong = self.df["c"].iloc[j] - ma.iloc[j - lag + 1]
        self.assertNotAlmostEqual(self.ind["dpo"].iloc[j], wrong, places=6)

    def test_nan_before_spinup_free_after(self):
        # First valid DPO: SMA(20) needs 20 bars, displaced by 11 -> bar 30.
        self.assertTrue(self.ind["dpo"].iloc[:30].isna().all())
        self.assertFalse(self.ind["dpo"].iloc[30:].isna().any())
        # Trend SMA(50) is the binding constraint: first valid at bar 49.
        self.assertTrue(self.ind["sma_ma"].iloc[:49].isna().all())
        self.assertFalse(self.ind["sma_ma"].iloc[50:].isna().any())

    def test_trend_sma_is_sma50(self):
        expect = B.sma(self.df["c"], 50).dropna()
        got = self.ind["sma_ma"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)

    def test_custom_n_respected(self):
        ind10 = indicators.add_indicators(self.df, n=10)
        lag = 10 // 2 + 1
        ma = self.df["c"].rolling(10, min_periods=10).mean()
        j = 400
        self.assertAlmostEqual(
            ind10["dpo"].iloc[j],
            self.df["c"].iloc[j] - ma.iloc[j - lag],
            places=9,
        )


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_trend_filter_admits_longs_only_in_uptrend(self):
        ind = indicators.add_indicators(_swing_frame(drift=0.2))
        sig = signals.add_signals(ind)
        longs = sig["long_entry"]
        self.assertGreater(longs.sum(), 0)
        self.assertTrue((ind.loc[longs, "c"] > ind.loc[longs, "sma_ma"]).all())
        self.assertTrue((ind.loc[longs, "dpo"] > 0).all())
        self.assertEqual(sig["short_entry"].sum(), 0)  # filtered out

    def test_trend_filter_admits_shorts_only_in_downtrend(self):
        ind = indicators.add_indicators(_swing_frame(drift=-0.2, seed=22))
        sig = signals.add_signals(ind)
        shorts = sig["short_entry"]
        self.assertGreater(shorts.sum(), 0)
        self.assertTrue((ind.loc[shorts, "c"] < ind.loc[shorts, "sma_ma"]).all())
        self.assertTrue((ind.loc[shorts, "dpo"] < 0).all())
        self.assertEqual(sig["long_entry"].sum(), 0)  # filtered out

    def test_exits_are_opposite_zero_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        zero = pd.Series(0.0, index=ind.index)
        pd.testing.assert_series_equal(
            sig["long_exit"],
            B.crossed_below(ind["dpo"], zero).fillna(False).astype(bool),
            check_names=False,
        )
        pd.testing.assert_series_equal(
            sig["short_exit"],
            B.crossed_above(ind["dpo"], zero).fillna(False).astype(bool),
            check_names=False,
        )

    def test_crosses_fire_on_swing_frame(self):
        up = signals.add_signals(indicators.add_indicators(_swing_frame(drift=0.2)))
        self.assertGreater(up["long_entry"].sum(), 0)
        self.assertGreater(up["long_exit"].sum(), 0)
        self.assertGreater(up["short_exit"].sum(), 0)
        dn = signals.add_signals(
            indicators.add_indicators(_swing_frame(drift=-0.2, seed=22)))
        self.assertGreater(dn["short_entry"].sum(), 0)
        self.assertGreater(dn["short_exit"].sum(), 0)
        self.assertGreater(dn["long_exit"].sum(), 0)

    def test_exits_ignore_trend_filter(self):
        # A long exit can fire while price is still above the trend SMA.
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        lx = sig["long_exit"]
        self.assertTrue((ind.loc[lx, "c"] > ind.loc[lx, "sma_ma"]).any())

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 450
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        import strategies.detrended_price_oscillator as mod
        from strategies.registry import REGISTRY

        self.assertIn("detrended_price_oscillator", REGISTRY)
        self.assertIs(REGISTRY["detrended_price_oscillator"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "detrended_price_oscillator")
        self.assertEqual(mod.SPEC.name, "DPO Zero-Line Cross")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
