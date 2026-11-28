"""AO Saucer tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ao_saucer import indicators, risk, signals

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


def _df_with_ao(ao):
    """Flat-price frame with an explicit AO column (signals only read ao)."""
    ao = np.asarray(ao, float)
    n = len(ao)
    df = _df_from_c(np.full(n, 100.0))
    df["ao"] = ao
    return df


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _buy_saucer_ao():
    # AO: 1.0 x6, then 1.2, 1.0 (red), 1.1 (green) -> buy saucer at 8.
    return [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 1.0, 1.1, 1.1]


def _sell_saucer_ao():
    # Mirror below zero -> sell saucer at 8.
    return [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.2, -1.0, -1.1, -1.1]


class TestAoSaucer(unittest.TestCase):
    def test_ao_hand_computed_linear_trend(self):
        # median = 100 + t (slope 1): SMA(5) = t+98, SMA(34) = t+83.5
        # at bar t, so AO = 14.5 once both SMAs are warm.
        n = 60
        c = 100.0 + np.arange(n)
        df = _df(c - 1, c + 0.5, c - 0.5, c)
        ind = indicators.add_indicators(df)
        self.assertTrue(np.isnan(ind["ao"].iloc[32]))
        self.assertAlmostEqual(float(ind["ao"].iloc[33]), 14.5, places=6)
        self.assertAlmostEqual(float(ind["ao"].iloc[59]), 14.5, places=6)

    def test_ao_zero_on_flat_median(self):
        n = 60
        ind = indicators.add_indicators(
            _df(np.full(n, 100.0), np.full(n, 100.5),
                np.full(n, 99.5), np.full(n, 100.0)))
        self.assertAlmostEqual(float(ind["ao"].iloc[33]), 0.0, places=9)
        self.assertAlmostEqual(float(ind["ao"].iloc[59]), 0.0, places=9)

    def test_buy_saucer_fires(self):
        sig = signals.add_signals(_df_with_ao(_buy_saucer_ao()))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [8])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_sell_saucer_fires(self):
        sig = signals.add_signals(_df_with_ao(_sell_saucer_ao()))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [8])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_saucer_when_middle_bar_rises(self):
        # AO keeps rising through the middle bar: no red bar, no saucer.
        ao = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.2, 1.2]
        sig = signals.add_signals(_df_with_ao(ao))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_saucer_when_third_bar_falls_further(self):
        # Middle bar red, but the third bar falls again: no green turn.
        ao = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 1.0, 0.9, 0.9]
        sig = signals.add_signals(_df_with_ao(ao))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_saucer_below_zero_for_buy(self):
        # Same red->green turn shape, but entirely below zero: no buy.
        ao = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -0.8, -1.0, -0.9, -0.9]
        sig = signals.add_signals(_df_with_ao(ao))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_saucer_does_not_refire_while_ao_keeps_rising(self):
        # After the saucer at 8, AO keeps rising: no second entry.
        ao = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 1.0, 1.1, 1.2, 1.3, 1.4]
        sig = signals.add_signals(_df_with_ao(ao))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [8])

    def test_relaxed_strict_identical(self):
        # Provably identical: ao[i-1] > 0 + ao[i-1] < ao[i-2]
        # forces ao[i-2] > 0, so dropping the ao[i-2] check
        # changes nothing. Verify on a random AO series.
        rng = np.random.default_rng(7)
        ao = rng.normal(0, 1.0, 500)
        a = signals.add_signals(_df_with_ao(ao), strict=True)
        b = signals.add_signals(_df_with_ao(ao), strict=False)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue((a[col] == b[col]).all(), col)

    def test_long_exit_on_zero_cross(self):
        # Buy saucer at 8, AO crosses below zero at 11
        # (0.2 -> -0.1).
        ao = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 1.0, 1.1, 0.5, 0.2, -0.1, -0.2]
        sig = signals.add_signals(_df_with_ao(ao))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [8])
        self.assertIn(11, sig.index[sig["long_exit"]].tolist())
        self.assertNotIn(10, sig.index[sig["long_exit"]].tolist())

    def test_short_exit_on_zero_cross(self):
        ao = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.2, -1.0, -1.1, -0.5, -0.2, 0.1, 0.2]
        sig = signals.add_signals(_df_with_ao(ao))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [8])
        self.assertIn(11, sig.index[sig["short_exit"]].tolist())

    def test_long_exit_on_sell_saucer(self):
        # Buy at 8; AO falls through zero (exit at 10) and then
        # completes a sell saucer at 12 -- both exit the long.
        ao = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 1.0, 1.1, 0.5, -0.3, -0.2, -0.4, -0.4]
        sig = signals.add_signals(_df_with_ao(ao))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [12])
        self.assertIn(10, sig.index[sig["long_exit"]].tolist())
        self.assertIn(12, sig.index[sig["long_exit"]].tolist())

    def test_two_bar_exit_fires_where_zero_cross_does_not(self):
        # Buy saucer at 8, then two consecutive red AO bars (10->11)
        # while AO stays above zero: zero mode holds, two_bar exits.
        ao = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.2, 1.0, 1.1, 1.05, 0.9, 0.8, 0.7]
        zero = signals.add_signals(_df_with_ao(ao), exit_mode="zero")
        two = signals.add_signals(_df_with_ao(ao), exit_mode="two_bar")
        self.assertNotIn(11, zero.index[zero["long_exit"]].tolist())
        self.assertIn(11, two.index[two["long_exit"]].tolist())
        # Both modes agree on entries.
        self.assertEqual(zero.index[zero["long_entry"]].tolist(), [8])
        self.assertEqual(two.index[two["long_entry"]].tolist(), [8])

    def test_two_bar_exit_short_side(self):
        # Sell saucer at 8, then two consecutive green AO bars.
        ao = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.2, -1.0, -1.1, -1.05, -0.9, -0.8, -0.7]
        two = signals.add_signals(_df_with_ao(ao), exit_mode="two_bar")
        self.assertEqual(two.index[two["short_entry"]].tolist(), [8])
        self.assertIn(11, two.index[two["short_exit"]].tolist())

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("median", "ao", "atr14"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("median", "ao", "atr14"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.ao_saucer as mod

        self.assertEqual(mod.SPEC.slug, "ao_saucer")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 50)


if __name__ == "__main__":
    unittest.main()
