"""Holy Grail tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.lbr_holy_grail import indicators, risk, signals


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


class TestHolyGrailIndicators(unittest.TestCase):
    def setUp(self):
        self.df = indicators.add_indicators(_frame())

    def test_adx_columns_present(self):
        for col in ("adx", "plus_di", "minus_di", "ema20"):
            self.assertIn(col, self.df.columns, col)
        self.assertTrue(self.df["adx"].iloc[60:].notna().all())

    def test_ema20_tracks_price(self):
        # on a steady rally ema20 sits below the close
        c = 100.0 + 2.0 * np.arange(300)
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(
            pd.DataFrame(
                {
                    "t": (1_700_000_000_000 + np.arange(300) * 3_600_000).astype("int64"),
                    "o": o,
                    "h": np.maximum(o, c) + 0.2,
                    "l": np.minimum(o, c) - 0.2,
                    "c": c,
                    "v": np.full(300, 100.0),
                }
            )
        )
        self.assertTrue((df["ema20"].iloc[60:] < df["c"].iloc[60:]).all())

    def test_atr_positive(self):
        self.assertTrue((self.df["atr"].dropna() > 0).all())


class TestHolyGrailSignals(unittest.TestCase):
    def setUp(self):
        self.sig = signals.add_signals(indicators.add_indicators(_frame()))

    def test_signal_columns_exist_and_boolean(self):
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, self.sig.columns)
            self.assertTrue(self.sig[col].dtype == bool, col)
            self.assertFalse(self.sig[col].isna().any(), col)

    def test_entries_fire_on_trending_frames(self):
        # uptrend frame fires longs; downtrend frame fires shorts
        self.assertGreater(self.sig["long_entry"].sum(), 0)
        short_sig = signals.add_signals(
            indicators.add_indicators(_frame(drift=-0.001, seed=20))
        )
        self.assertGreater(short_sig["short_entry"].sum(), 0)

    def test_long_entry_implies_prior_touch_and_breakout(self):
        le = self.sig["long_entry"]
        for i in self.sig.index[le]:
            self.assertLess(i, len(self.sig))
            prev = self.sig.iloc[i - 1]
            # touch bar: dipped to the average, closed back above, in regime
            self.assertLessEqual(prev["l"], prev["ema20"])
            self.assertGreater(prev["c"], prev["ema20"])
            self.assertGreater(prev["adx"], indicators.ADX_THRESH)
            # entry bar: close above the touch bar's high (buy-stop)
            self.assertGreater(self.sig["c"].iloc[i], prev["h"])

    def test_short_entry_implies_prior_touch_and_breakdown(self):
        se = self.sig["short_entry"]
        for i in self.sig.index[se]:
            prev = self.sig.iloc[i - 1]
            self.assertGreaterEqual(prev["h"], prev["ema20"])
            self.assertLess(prev["c"], prev["ema20"])
            self.assertGreater(prev["adx"], indicators.ADX_THRESH)
            self.assertLess(self.sig["c"].iloc[i], prev["l"])

    def test_no_entries_before_adx_spinup(self):
        # ADX(14) needs ~27 bars before it can be valid+rising; nothing
        # may fire before that.
        self.assertFalse(self.sig["long_entry"].iloc[:20].any())
        self.assertFalse(self.sig["short_entry"].iloc[:20].any())

    def test_exits_cover_average_cross_and_adx_fade(self):
        expected = (self.sig["c"] < self.sig["ema20"]) | (
            self.sig["adx"] < indicators.ADX_EXIT
        )
        self.assertTrue((self.sig["long_exit"] == expected.fillna(False)).all())


class TestHolyGrailMeta(unittest.TestCase):
    def test_registration_imports_cleanly(self):
        import strategies.lbr_holy_grail as mod

        self.assertEqual(mod.SPEC.slug, "lbr_holy_grail")
        self.assertEqual(mod.SPEC.name, "Holy Grail")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 100)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
