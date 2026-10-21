"""Elder Triple Screen tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elder_triple_screen import indicators, risk, signals


def _frame(n=900, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestTripleScreenIndicators(unittest.TestCase):
    def setUp(self):
        self.df = indicators.add_indicators(_frame())

    def test_6h_aggregation_shape(self):
        h6 = indicators._to_6h(_frame())
        # 900 1h bars = exactly 150 6h-worth of time; depending on where the
        # first bar lands inside its bin this spans 150 or 151 bins
        self.assertIn(len(h6), (150, 151))
        self.assertTrue((h6["h"] >= h6[["o", "c"]].max(axis=1)).all())
        self.assertTrue((h6["l"] <= h6[["o", "c"]].min(axis=1)).all())

    def test_trend_columns_boolean_and_not_all_nan(self):
        for col in ("trend_up_6h", "trend_down_6h"):
            self.assertTrue(self.df[col].dtype == bool, col)
            # after warmup both regimes must have appeared on a random walk
            self.assertTrue(self.df[col].iloc[300:].any(), col)
            self.assertTrue((~self.df[col]).iloc[300:].any(), col)

    def test_trend_changes_only_at_6h_boundaries(self):
        # no lookahead: the mapped trend may only change on the first bar
        # of a new completed 6h bin, never mid-bin.
        h6ms = indicators.H6_MS
        changed = self.df["trend_up_6h"].astype(int).diff().fillna(0) != 0
        for i in self.df.index[changed]:
            if i == 0:
                continue
            self.assertNotEqual(
                self.df["t"].iloc[i] // h6ms, self.df["t"].iloc[i - 1] // h6ms
            )

    def test_first_6h_block_has_no_trend(self):
        # bars in the first 6h block read a not-yet-completed bin -> False
        self.assertFalse(self.df["trend_up_6h"].iloc[:6].any())
        self.assertFalse(self.df["trend_down_6h"].iloc[:6].any())

    def test_fi_ema2_follows_force_index(self):
        fi = self.df["fi"]
        self.assertTrue(fi.iloc[2:].notna().all())
        # ema(2) tracks fi closely but smoother
        corr = self.df["fi_ema2"].iloc[50:].corr(fi.iloc[50:])
        self.assertGreater(corr, 0.9)

    def test_atr_positive(self):
        self.assertTrue((self.df["atr"].dropna() > 0).all())

    def test_warmup_region_has_no_entries(self):
        sig = signals.add_signals(self.df)
        self.assertFalse(sig["long_entry"].iloc[: risk.WARMUP].any())
        self.assertFalse(sig["short_entry"].iloc[: risk.WARMUP].any())


class TestTripleScreenSignals(unittest.TestCase):
    def setUp(self):
        self.sig = signals.add_signals(indicators.add_indicators(_frame()))

    def test_signal_columns_exist_and_boolean(self):
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, self.sig.columns)
            self.assertTrue(self.sig[col].dtype == bool, col)
            self.assertFalse(self.sig[col].isna().any(), col)

    def test_entries_fire_on_trending_frame(self):
        self.assertGreater(self.sig["long_entry"].sum(), 0)
        self.assertGreater(self.sig["short_entry"].sum(), 0)

    def test_long_entry_requires_trend_and_wave_pullback(self):
        le = self.sig["long_entry"]
        self.assertTrue(self.sig.loc[le, "trend_up_6h"].all())
        fi2 = self.sig["fi_ema2"]
        self.assertTrue(((fi2[le] < 0) & (fi2.shift(1)[le] >= 0)).all())

    def test_exits_mirror_trend_flip(self):
        self.assertTrue(
            (self.sig["long_exit"] == ~self.sig["trend_up_6h"]).all()
        )
        self.assertTrue(
            (self.sig["short_exit"] == ~self.sig["trend_down_6h"]).all()
        )


class TestTripleScreenMeta(unittest.TestCase):
    def test_registration_imports_cleanly(self):
        import strategies.elder_triple_screen as mod

        self.assertEqual(mod.SPEC.slug, "elder_triple_screen")
        self.assertEqual(mod.SPEC.name, "Elder Triple Screen")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 200)


if __name__ == "__main__":
    unittest.main()
