"""Prior UTC-day high/low breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.prev_day_high_low import indicators, risk, signals

T0 = 1767225600000  # 2026-01-01 00:00 UTC (a UTC midnight)


def _pdh_frame(n_days=25, close_overrides=None, narrow_day=None):
    """25 UTC days of 1h bars; each day high 102 (bar 5), low 98 (bar 10),
    closes flat 100 unless overridden.  narrow_day: a day with range 1
    (no 102/98 spikes) to trip the range filter."""
    n = n_days * 24
    t = T0 + np.arange(n) * 3_600_000
    c = np.full(n, 100.0)
    o = c.copy()
    h = np.full(n, 100.5)
    l = np.full(n, 99.5)
    v = np.full(n, 100.0)
    for d in range(n_days):
        if d == narrow_day:
            continue
        h[d * 24 + 5] = 102.0
        l[d * 24 + 10] = 98.0
    if close_overrides:
        for b, (cc, hh, ll) in close_overrides.items():
            c[b], h[b], l[b] = cc, hh, ll
    return pd.DataFrame({"t": t.astype("int64"), "o": o, "h": h,
                         "l": l, "c": c, "v": v})


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


# Day 21 (bars 504+) breaks out: closes 101, 102, 102.2 at bars
# 510-512; the 0.1% filter level is 102 * 1.001 = 102.102.
LONG_BREAK = {510: (101.0, 101.5, 100.5), 511: (102.0, 102.5, 101.5),
              512: (102.2, 102.3, 102.1)}
# Day 21 breaks down: closes 99, 98, 97.8; filter level 98 * 0.999 = 97.902.
SHORT_BREAK = {510: (99.0, 99.5, 98.5), 511: (98.0, 98.5, 97.5),
               512: (97.8, 97.9, 97.7)}


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("pdh", "pdl", "pd_range", "pd_range_med20",
                    "range_ok", "is_new_day", "atr"):
            self.assertIn(col, ind.columns)

    def test_prior_day_levels(self):
        ind = indicators.add_indicators(_pdh_frame())
        # day 0 has no prior day
        self.assertTrue(np.isnan(ind["pdh"].iloc[0]))
        self.assertTrue(np.isnan(ind["pdl"].iloc[0]))
        # day 1 carries day 0's high/low
        self.assertAlmostEqual(ind["pdh"].iloc[24], 102.0)
        self.assertAlmostEqual(ind["pdl"].iloc[24], 98.0)
        self.assertAlmostEqual(ind["pdh"].iloc[47], 102.0)
        self.assertAlmostEqual(ind["pdl"].iloc[47], 98.0)

    def test_levels_do_not_use_current_day(self):
        # day 2's pdh must still be day 1's high even though day 2's
        # own high prints later in the day
        df = _pdh_frame()
        df.loc[50, "h"] = 105.0  # day 2 bar 2 spikes to 105
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["pdh"].iloc[50], 102.0)
        self.assertAlmostEqual(ind["pdh"].iloc[72], 105.0)  # day 3 sees it

    def test_range_and_median(self):
        ind = indicators.add_indicators(_pdh_frame())
        self.assertAlmostEqual(ind["pd_range"].iloc[504], 4.0)
        # 20 prior days of range 4 -> median 4.0 from day 21 on
        self.assertAlmostEqual(ind["pd_range_med20"].iloc[504], 4.0)
        self.assertTrue(ind["range_ok"].iloc[504])

    def test_range_filter_rejects_narrow_day(self):
        ind = indicators.add_indicators(_pdh_frame(narrow_day=20))
        # day 21's prior-day range is 1.0 vs 20-day median 4.0
        self.assertAlmostEqual(ind["pd_range"].iloc[504], 1.0)
        self.assertFalse(ind["range_ok"].iloc[504])

    def test_is_new_day(self):
        ind = indicators.add_indicators(_pdh_frame())
        self.assertTrue(ind["is_new_day"].iloc[0])
        self.assertTrue(ind["is_new_day"].iloc[24])
        self.assertTrue(ind["is_new_day"].iloc[48])
        self.assertFalse(ind["is_new_day"].iloc[25])
        self.assertFalse(ind["is_new_day"].iloc[47])

    def test_warmup_nans(self):
        ind = indicators.add_indicators(_frame())
        self.assertTrue(ind["pdh"].iloc[:24].isna().all())

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_breakout(self):
        df = _pdh_frame(close_overrides=LONG_BREAK)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(sig["long_entry"].iloc[511])  # 102 <= 102.102
        self.assertTrue(sig["long_entry"].iloc[512])   # 102.2 > 102.102
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_short_entry_on_breakdown(self):
        df = _pdh_frame(close_overrides=SHORT_BREAK)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(sig["short_entry"].iloc[511])  # 98 > 97.902
        self.assertTrue(sig["short_entry"].iloc[512])   # 97.8 < 97.902
        self.assertEqual(sig["short_entry"].sum(), 1)

    def test_no_entry_when_range_filtered(self):
        df = _pdh_frame(close_overrides=LONG_BREAK, narrow_day=20)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_long_exit_on_close_back_inside(self):
        ov = dict(LONG_BREAK)
        ov[513] = (102.5, 103.0, 102.0)  # holds above pdh 102
        ov[514] = (102.5, 103.0, 102.0)
        ov[515] = (101.5, 102.0, 101.0)  # close back under pdh 102
        df = _pdh_frame(close_overrides=ov)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].iloc[512])
        self.assertTrue(sig["long_exit"].iloc[515])
        self.assertFalse(sig["long_exit"].iloc[514])

    def test_long_exit_at_midnight(self):
        # breakout holds through day 21; first bar of day 22 is flat
        ov = dict(LONG_BREAK)
        for b in range(513, 528):
            ov[b] = (103.0, 103.5, 102.5)
        df = _pdh_frame(close_overrides=ov)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].iloc[512])
        self.assertFalse(sig["long_exit"].iloc[527])
        self.assertTrue(sig["long_exit"].iloc[528])  # first bar, new day

    def test_no_lookahead(self):
        df = _pdh_frame(close_overrides=LONG_BREAK)
        full = signals.add_signals(indicators.add_indicators(df))
        j = 512
        trunc = signals.add_signals(
            indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertEqual(risk.WARMUP, 48)

    def test_registration(self):
        import strategies.prev_day_high_low as mod
        from strategies.registry import REGISTRY

        self.assertIn("prev_day_high_low", REGISTRY)
        self.assertIs(REGISTRY["prev_day_high_low"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "prev_day_high_low")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
