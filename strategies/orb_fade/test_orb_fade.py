"""Opening-range breakout-failure fade tests. Network-free, synthetic data only.

Base series: flat 100 with h=101 / l=99 on every bar, so each
UTC day's opening range is or_high=101 / or_low=99 from the
04:00 bar on. Bars are hourly from 2023-11-15 00:00 UTC, so
bar 24k is 00:00 of day k.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.orb_fade import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC


def _df(o, h, l, c, v=None):
    o = np.asarray(o, float)
    h = np.asarray(h, float)
    l = np.asarray(l, float)
    c = np.asarray(c, float)
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _flat_days(n_days=3, close=100.0, spread=1.0):
    """Flat series: every day's opening range is 101 / 99."""
    n = n_days * 24
    c = np.full(n, close)
    o = c.copy()
    h = c + spread
    l = c - spread
    v = np.full(n, 100.0)
    return o, h, l, c, v


class TestOrbFade(unittest.TestCase):
    def test_or_range_computed(self):
        ind = indicators.add_indicators(_df(*_flat_days(2)))
        # NaN on the range bars (00:00-03:00), filled from 04:00.
        self.assertTrue(np.isnan(ind["or_high"].iloc[3]))
        self.assertTrue(np.isnan(ind["or_low"].iloc[3]))
        self.assertAlmostEqual(float(ind["or_high"].iloc[4]), 101.0, places=6)
        self.assertAlmostEqual(float(ind["or_low"].iloc[4]), 99.0, places=6)
        self.assertAlmostEqual(float(ind["or_high"].iloc[23]), 101.0, places=6)
        # Day 1 starts over: NaN at bar 27 (03:00), filled at 28 (04:00).
        self.assertTrue(np.isnan(ind["or_high"].iloc[27]))
        self.assertAlmostEqual(float(ind["or_high"].iloc[28]), 101.0, places=6)
        self.assertTrue(bool(ind["new_day"].iloc[0]))
        self.assertFalse(bool(ind["new_day"].iloc[1]))
        self.assertTrue(bool(ind["new_day"].iloc[24]))

    def test_no_entries_on_flat_series(self):
        sig = signals.add_signals(indicators.add_indicators(_df(*_flat_days(3))))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["or_break_up"].any()))
        self.assertFalse(bool(sig["or_break_down"].any()))

    def test_upside_break_then_failure_shorts(self):
        # Bar 5 (05:00): close 102 crosses above or_high 101
        # -> upside break. Bar 6: close 100.5 back below 101
        # -> failed break, SHORT.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 102.5, 100.0, 102.0
        o[6], h[6], l[6], c[6] = 102.0, 102.5, 100.0, 100.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["or_break_up"]].tolist(), [5])
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [6])
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_downside_break_then_failure_longs(self):
        # Bar 5: close 98 crosses below or_low 99 -> downside
        # break. Bar 6: close 99.5 back above 99 -> LONG.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 100.0, 97.5, 98.0
        o[6], h[6], l[6], c[6] = 98.0, 100.0, 98.0, 99.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["or_break_down"]].tolist(), [5])
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [6])
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["long_exit"].any()))

    def test_no_failure_after_window_expiry(self):
        # Break at bar 5, closes stay above or_high through
        # bar 11 (6 bars after the break); the dip below at
        # bar 12 is 7 bars late: no entry.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 102.5, 100.0, 102.0
        for i in range(6, 12):
            o[i], h[i], l[i], c[i] = 102.0, 102.5, 100.0, 102.0
        o[12], h[12], l[12], c[12] = 102.0, 102.5, 100.0, 100.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["or_break_up"]].tolist(), [5])
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_failure_then_new_break_rearms(self):
        # Break up at 5, close 98 at 6 fails the upside break
        # (SHORT at 6) AND breaks down through or_low (arms a
        # downside setup); close 99.5 at 7 fails that break
        # too (LONG at 7, which exits the short).
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 102.5, 100.0, 102.0
        o[6], h[6], l[6], c[6] = 102.0, 102.5, 97.5, 98.0
        o[7], h[7], l[7], c[7] = 98.0, 100.0, 98.0, 99.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [6])
        self.assertEqual(sig.index[sig["or_break_down"]].tolist(), [6])
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [7])
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [7])

    def test_first_failure_only(self):
        # Break at 5, failure at 6 (SHORT); closes stay below
        # or_high at 7 and 8: no second short entry.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 102.5, 100.0, 102.0
        for i in (6, 7, 8):
            o[i], h[i], l[i], c[i] = 102.0, 102.5, 100.0, 100.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [6])

    def test_short_exit_on_reclaim_above_or_high(self):
        # Short at 6 (failed upside break); close 102 at 7
        # reclaims or_high 101 -> the break was real, exit.
        # Bars 8-13 hold 102 so the fresh break armed at 7
        # is not itself failed by the flat tail.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 102.5, 100.0, 102.0
        o[6], h[6], l[6], c[6] = 102.0, 102.5, 100.0, 100.5
        o[7], h[7], l[7], c[7] = 100.5, 102.5, 100.0, 102.0
        for i in range(8, 14):
            o[i], h[i], l[i], c[i] = 102.0, 102.5, 100.0, 102.0
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [6])
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [7])
        self.assertEqual(sig.index[sig["or_break_up"]].tolist(), [5, 7])

    def test_long_exit_on_break_below_or_low(self):
        # Long at 6 (failed downside break); close 98 at 7
        # breaks or_low 99 again -> the break was real, exit.
        # Bars 8-13 hold 98 so the fresh break armed at 7
        # is not itself failed by the flat tail.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 100.0, 97.5, 98.0
        o[6], h[6], l[6], c[6] = 98.0, 100.0, 98.0, 99.5
        o[7], h[7], l[7], c[7] = 99.5, 100.0, 97.5, 98.0
        for i in range(8, 14):
            o[i], h[i], l[i], c[i] = 98.0, 100.0, 97.5, 98.0
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [6])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [7])
        self.assertEqual(sig.index[sig["or_break_down"]].tolist(), [5, 7])

    def test_opposite_fade_entry_exits(self):
        # Short at 6 (failed upside break); a downside break
        # at 8 and its failure at 9 enter LONG and exit the short.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 102.5, 100.0, 102.0
        o[6], h[6], l[6], c[6] = 102.0, 102.5, 100.0, 100.5
        o[7], h[7], l[7], c[7] = 100.5, 101.0, 100.0, 100.0
        o[8], h[8], l[8], c[8] = 100.0, 100.5, 97.5, 98.0
        o[9], h[9], l[9], c[9] = 98.0, 100.0, 98.0, 99.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [6])
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [9])
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [9])

    def test_new_day_cancels_pending(self):
        # Upside break at bar 23 (23:00, last bar of day 0).
        # Day 1's range bars close at 101 (at the high); the
        # 04:00 bar closes 100.5, below the old or_high -- but
        # the pending setup died at the day boundary: no entry.
        o, h, l, c, v = _flat_days(2)
        o[22], h[22], l[22], c[22] = 100.0, 101.0, 100.0, 100.5
        o[23], h[23], l[23], c[23] = 100.5, 102.5, 100.0, 102.0
        for i in range(24, 28):
            o[i], h[i], l[i], c[i] = 101.0, 101.0, 99.0, 101.0
        o[28], h[28], l[28], c[28] = 101.0, 101.5, 100.0, 100.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["or_break_up"]].tolist(), [23])
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_or_window_8(self):
        # With or_n=8 the range is bars 00:00-07:00: NaN at
        # bar 7, filled from bar 8.
        ind = indicators.add_indicators(_df(*_flat_days(2)), or_n=8)
        self.assertTrue(np.isnan(ind["or_high"].iloc[7]))
        self.assertAlmostEqual(float(ind["or_high"].iloc[8]), 101.0, places=6)
        self.assertAlmostEqual(float(ind["or_low"].iloc[8]), 99.0, places=6)

    def test_failure_window_param(self):
        # Break at 5, dip below at 12 (7 bars later): no entry
        # with the shipped 6-bar window, an entry with 12 bars.
        o, h, l, c, v = _flat_days(3)
        o[5], h[5], l[5], c[5] = 100.0, 102.5, 100.0, 102.0
        for i in range(6, 12):
            o[i], h[i], l[i], c[i] = 102.0, 102.5, 100.0, 102.0
        o[12], h[12], l[12], c[12] = 102.0, 102.5, 100.0, 100.5
        df = indicators.add_indicators(_df(o, h, l, c, v))
        sig6 = signals.add_signals(df)
        self.assertFalse(bool(sig6["short_entry"].any()))
        sig12 = signals.add_signals(df, failure_bars=12)
        self.assertEqual(sig12.index[sig12["short_entry"]].tolist(), [12])

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "new_day", "or_break_up", "or_break_down"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        # or_high/or_low are NaN by design on the 00:00-03:00
        # bars, but filled on every bar from 04:00 on.
        flat = signals.add_signals(indicators.add_indicators(_df(*_flat_days(2))))
        self.assertTrue(flat["or_high"].iloc[0:4].isna().all())
        self.assertFalse(flat["or_high"].iloc[4:24].isna().any())
        self.assertFalse(flat["or_low"].iloc[4:24].isna().any())

    def test_no_same_bar_both_entries_random(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (200, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("or_high", "or_low", "new_day"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("or_break_up", "or_break_down", "fail_up_level",
                        "fail_down_level", "long_entry", "short_entry",
                        "long_exit", "short_exit"):
                av, bv = sig_full[col].iloc[j], sig_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.orb_fade as mod

        self.assertEqual(mod.SPEC.slug, "orb_fade")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
