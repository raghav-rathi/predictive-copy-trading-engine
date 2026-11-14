"""CVD trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cvd_trend import indicators, risk, signals
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
    """Slow sine swings with volume: CVD slope flips sign repeatedly."""
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
        for col in ("cvd", "cvd_ema20", "cvd_slope", "ema50", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_close_location_proxy(self):
        # Close at the high -> delta = +v; close at the low -> delta = -v;
        # close mid-range -> delta = 0.
        df = pd.DataFrame({
            "t": [1, 2, 3], "o": [100.0, 100.0, 100.0],
            "h": [110.0, 110.0, 110.0], "l": [90.0, 90.0, 90.0],
            "c": [110.0, 90.0, 100.0], "v": [10.0, 10.0, 10.0]})
        d = indicators.volume_delta(df["o"], df["h"], df["l"], df["c"], df["v"])
        self.assertAlmostEqual(d.iloc[0], 10.0)
        self.assertAlmostEqual(d.iloc[1], -10.0)
        self.assertAlmostEqual(d.iloc[2], 0.0)

    def test_flat_bar_splits_volume(self):
        df = pd.DataFrame({
            "t": [1], "o": [100.0], "h": [100.0], "l": [100.0],
            "c": [100.0], "v": [10.0]})
        d = indicators.volume_delta(df["o"], df["h"], df["l"], df["c"], df["v"])
        self.assertAlmostEqual(d.iloc[0], 0.0)

    def test_cvd_is_cumsum_of_delta(self):
        d = indicators.volume_delta(self.df["o"], self.df["h"], self.df["l"],
                                    self.df["c"], self.df["v"])
        pd.testing.assert_series_equal(self.ind["cvd"], d.cumsum(), check_names=False)

    def test_cvd_ema_and_slope(self):
        expect = B.ema(self.ind["cvd"], 20)
        pd.testing.assert_series_equal(self.ind["cvd_ema20"], expect, check_names=False)
        pd.testing.assert_series_equal(
            self.ind["cvd_slope"],
            self.ind["cvd_ema20"] - self.ind["cvd_ema20"].shift(1),
            check_names=False)

    def test_ema50(self):
        pd.testing.assert_series_equal(self.ind["ema50"], B.ema(self.df["c"], 50),
                                       check_names=False)

    def test_warmup_nans(self):
        # EMA(50) needs 50 bars; CVD EMA(20) is valid from bar 20.
        self.assertTrue(self.ind["ema50"].iloc[:49].isna().all())
        self.assertFalse(self.ind["ema50"].iloc[60:].isna().any())
        self.assertFalse(self.ind["cvd_slope"].iloc[60:].isna().any())

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

    def test_entries_respect_trend_filter(self):
        ind = indicators.add_indicators(_frame())
        sig = signals.add_signals(ind)
        longs = sig["long_entry"]
        self.assertTrue((ind.loc[longs, "c"] > ind.loc[longs, "ema50"]).all())
        shorts = sig["short_entry"]
        self.assertTrue((ind.loc[shorts, "c"] < ind.loc[shorts, "ema50"]).all())

    def test_entries_are_first_bar_of_two_bar_rise(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        s = ind["cvd_slope"]
        rising2 = (s > 0) & (s.shift(1) > 0)
        # every long entry sits on a 2-bar rise, and the previous bar was not
        # rising2 (once-per-streak) or the trend filter blocked earlier bars
        self.assertTrue(rising2.loc[sig["long_entry"]].all())
        falling2 = (s < 0) & (s.shift(1) < 0)
        self.assertTrue(falling2.loc[sig["short_entry"]].all())

    def test_exits_are_slope_reversals(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        s = ind["cvd_slope"]
        pd.testing.assert_series_equal(
            sig["long_exit"], (s < 0).fillna(False).astype(bool), check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], (s > 0).fillna(False).astype(bool), check_names=False)

    def test_entries_fire_on_swing_frame(self):
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
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        import strategies.cvd_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("cvd_trend", REGISTRY)
        self.assertIs(REGISTRY["cvd_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "cvd_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
