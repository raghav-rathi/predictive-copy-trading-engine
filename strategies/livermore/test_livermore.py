"""Livermore trend-system tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.livermore import indicators, risk, signals
from strategies.base import crossed_above, crossed_below


def _df_ohlc(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.full(n, 100.0)}
    )


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df_ohlc(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


class TestLivermore(unittest.TestCase):
    def test_breakout_levels_are_prior_window(self):
        c = 100.0 + 2.0 * np.arange(100)
        df = indicators.add_indicators(_df_from_c(c))
        # at bar 50: prior 20-bar high = h[49] = c[49] + 0.2 = 198.2;
        # prior 20-bar low = l[30] = min(o[30], c[30]) - 0.2 = 157.8
        # (o[30] = c[29] = 158 < c[30] = 160, so the low uses the open)
        self.assertAlmostEqual(df["brk_high"].iloc[50], 198.2)
        self.assertAlmostEqual(df["brk_low"].iloc[50], 157.8)
        self.assertTrue(df["brk_high"].iloc[:20].isna().all())

    def test_higher_lows_true_on_rising_series(self):
        c = 100.0 + 2.0 * np.arange(100)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool(df["higher_lows"].iloc[60:].all()))
        self.assertFalse(bool(df["lower_highs"].iloc[60:].any()))

    def test_lower_highs_true_on_falling_series(self):
        c = 400.0 - 2.0 * np.arange(100)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool(df["lower_highs"].iloc[60:].all()))
        self.assertFalse(bool(df["higher_lows"].iloc[60:].any()))

    def test_steady_ramp_fires_long(self):
        c = 100.0 + 2.0 * np.arange(200)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_steady_decline_fires_short(self):
        c = 400.0 - 2.0 * np.arange(200)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_flat_series_fires_nothing(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(np.full(200, 100.0))))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_breakout_without_higher_lows_fires_no_long(self):
        # spike above the 20-bar high after FLAT lows: the 10-bar low
        # ending 10 bars ago equals the one ending 20 bars ago, so
        # higher_lows is False and the breakout alone must not fire
        c = np.concatenate([np.full(60, 100.0), [130.0], np.full(20, 130.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        # the spike bar is index 60; no long entry may fire on it
        self.assertFalse(bool(sig["long_entry"].iloc[60]))

    def test_exit_after_reversal(self):
        # ramp up 60 bars (long fires), then a sharp fall through the
        # prior 10-bar low -> long_exit must fire
        c = np.concatenate([
            100.0 + 2.0 * np.arange(60),
            220.0 - 5.0 * np.arange(1, 31),
        ])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(exits) > 0)
        self.assertTrue(all(b >= 60 for b in exits))

    def test_exits_match_10bar_break_formula(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        expect_le = crossed_below(sig["c"], sig["exit_low"]).fillna(False).astype(bool)
        expect_se = crossed_above(sig["c"], sig["exit_high"]).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_exit"] == expect_le).all()))
        self.assertTrue(bool((sig["short_exit"] == expect_se).all()))

    def test_signals_boolean_no_nan_fire_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("brk_high", "brk_low", "low10_a", "low10_b"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_breakout_lookback_param_widens_level(self):
        df10 = indicators.add_indicators(_rand_df(600, seed=9), breakout_lookback=10)
        df30 = indicators.add_indicators(_rand_df(600, seed=9), breakout_lookback=30)
        # wider window: prior high can only be higher-or-equal, prior low lower-or-equal
        self.assertTrue(bool((df30["brk_high"].iloc[100:] >= df10["brk_high"].iloc[100:] - 1e-9).all()))
        self.assertTrue(bool((df30["brk_low"].iloc[100:] <= df10["brk_low"].iloc[100:] + 1e-9).all()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("brk_high", "brk_low", "low10_a", "low10_b", "higher_lows"):
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
        import strategies.livermore as mod

        self.assertEqual(mod.SPEC.slug, "livermore")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
