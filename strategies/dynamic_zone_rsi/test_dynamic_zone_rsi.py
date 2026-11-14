"""Dynamic Zones RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dynamic_zone_rsi import indicators, risk, signals
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
    """Slow sine swings: RSI oscillates through its dynamic zones repeatedly."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, cycles * 2 * np.pi, n)
    c = 100 + 25 * np.sin(x) + rng.normal(0, 0.4, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _crafted_frame():
    """Hand-made RSI path: dip below the buy zone then bounce; push above
    the sell zone then fade; RSI crosses 50 both ways."""
    rsi = pd.Series([20.0, 15.0, 10.0, 25.0, 60.0, 85.0, 70.0, 45.0, 55.0])
    n = len(rsi)
    df = pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0, "v": 100.0,
        "rsi": rsi,
        "buy_zone": 18.0,
        "sell_zone": 82.0,
        "atr": 1.0,
    })
    return df


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("rsi", "buy_zone", "sell_zone", "rsi_bb_mid",
                    "rsi_bb_upper", "rsi_bb_lower", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_rsi_matches_base(self):
        expect = B.rsi(self.df["c"], 14).dropna()
        got = self.ind["rsi"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_zones_are_rolling_percentiles(self):
        rsi = self.ind["rsi"]
        expect_buy = rsi.rolling(70, min_periods=70).quantile(0.12)
        expect_sell = rsi.rolling(70, min_periods=70).quantile(0.88)
        pd.testing.assert_series_equal(self.ind["buy_zone"], expect_buy,
                                       check_names=False)
        pd.testing.assert_series_equal(self.ind["sell_zone"], expect_sell,
                                       check_names=False)

    def test_zones_ordered_and_bounded(self):
        z = self.ind.dropna(subset=["buy_zone", "sell_zone"])
        self.assertTrue((z["buy_zone"] <= z["sell_zone"]).all())
        self.assertTrue((z["buy_zone"] >= 0).all() and (z["buy_zone"] <= 100).all())
        self.assertTrue((z["sell_zone"] >= 0).all() and (z["sell_zone"] <= 100).all())

    def test_bollinger_variant_is_mean_plus_0p8_sigma(self):
        rsi = self.ind["rsi"]
        mid = rsi.rolling(20, min_periods=20).mean()
        sd = rsi.rolling(20, min_periods=20).std()
        pd.testing.assert_series_equal(self.ind["rsi_bb_mid"], mid,
                                       check_names=False)
        pd.testing.assert_series_equal(self.ind["rsi_bb_upper"], mid + 0.8 * sd,
                                       check_names=False)
        pd.testing.assert_series_equal(self.ind["rsi_bb_lower"], mid - 0.8 * sd,
                                       check_names=False)

    def test_warmup_nans(self):
        # base.rsi never returns NaN (it fills with 0/100), so RSI is
        # valid from bar 0 and the 70-bar percentile zones first form
        # at bar 69 -- all formed well inside WARMUP=100.
        self.assertTrue(self.ind["buy_zone"].iloc[:69].isna().all())
        self.assertFalse(self.ind["buy_zone"].iloc[69:].isna().any())
        self.assertFalse(self.ind["sell_zone"].iloc[69:].isna().any())

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

    def test_crafted_bounce_and_fade(self):
        sig = signals.add_signals(_crafted_frame())
        # RSI 10 -> 25 crosses back above buy zone 18: long at index 3.
        self.assertTrue(bool(sig["long_entry"].iloc[3]))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        # RSI 85 -> 70 crosses back below sell zone 82: short at index 6.
        self.assertTrue(bool(sig["short_entry"].iloc[6]))
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        # RSI 70 -> 45 crosses below 50: long exit at index 7.
        self.assertTrue(bool(sig["long_exit"].iloc[7]))
        # RSI 45 -> 55 crosses above 50: short exit at index 8.
        self.assertTrue(bool(sig["short_exit"].iloc[8]))

    def test_entries_require_the_dip(self):
        # RSI flat at 50, zones at 18/82: no cross back, no entries.
        df = _crafted_frame()
        df["rsi"] = 50.0
        sig = signals.add_signals(df)
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

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
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.WARMUP, 100)

    def test_registration(self):
        import strategies.dynamic_zone_rsi as mod
        from strategies.registry import REGISTRY

        self.assertIn("dynamic_zone_rsi", REGISTRY)
        self.assertIs(REGISTRY["dynamic_zone_rsi"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "dynamic_zone_rsi")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
