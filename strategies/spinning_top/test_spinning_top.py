"""Spinning top tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.spinning_top import indicators, risk, signals


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


def _base_bars(n=30, o=99.5, c=100.3, hi=100.5, lo=98.5):
    # body 0.8 on a 2.0 range -> NOT a spinning top (body > 30% of range)
    return _df_ohlc(
        np.full(n, o), np.full(n, hi), np.full(n, lo), np.full(n, c)
    )


class TestSpinningTop(unittest.TestCase):
    def test_candle_anatomy_math(self):
        df = indicators.add_indicators(
            _df_ohlc([100.0], [110.0], [90.0], [100.5])
        )
        self.assertEqual(df["rng"].iloc[0], 20.0)
        self.assertEqual(df["body"].iloc[0], 0.5)
        self.assertEqual(df["upper_wick"].iloc[0], 9.5)
        self.assertEqual(df["lower_wick"].iloc[0], 10.0)
        self.assertTrue(bool(df["is_spinning_top"].iloc[0]))

    def test_big_body_is_not_a_top(self):
        # body 8 on a 20 range (40%) -> not a spinning top
        df = indicators.add_indicators(
            _df_ohlc([100.0], [110.0], [90.0], [108.0])
        )
        self.assertFalse(bool(df["is_spinning_top"].iloc[0]))

    def test_one_sided_wick_is_not_a_top(self):
        # lower wick only 1.0 (5% of range) -> not a spinning top
        df = indicators.add_indicators(
            _df_ohlc([100.0], [110.0], [99.0], [100.5])
        )
        self.assertFalse(bool(df["is_spinning_top"].iloc[0]))

    def test_flat_bar_is_not_a_top(self):
        # truly flat bars (h == l == o == c): zero range, rng > 0 guard
        n = 200
        df = indicators.add_indicators(
            _df_ohlc(np.full(n, 100.0), np.full(n, 100.0),
                     np.full(n, 100.0), np.full(n, 100.0))
        )
        self.assertFalse(bool(df["is_spinning_top"].iloc[60:].any()))

    def test_swing_windows_exclude_current_bar(self):
        df = indicators.add_indicators(_base_bars(30))
        # swing_low at bar 25 = min low of bars 5..24 = 98.5
        self.assertEqual(df["swing_low"].iloc[25], 98.5)
        self.assertEqual(df["swing_high"].iloc[25], 100.5)
        self.assertTrue(df["swing_low"].iloc[:20].isna().all())

    def test_top_at_swing_low_fires_long(self):
        base = _base_bars(30)
        # top bar: low 90 breaks the prior 20-bar low (98.5), high 100
        # stays inside the prior 20-bar high (100.5) -> long only
        top = _df_ohlc([96.0], [100.0], [90.0], [96.3])
        full = pd.concat([base, top], ignore_index=True)
        sig = signals.add_signals(indicators.add_indicators(full))
        self.assertTrue(bool(sig["long_entry"].iloc[30]))
        self.assertFalse(bool(sig["short_entry"].iloc[30]))

    def test_top_at_swing_high_fires_short(self):
        base = _base_bars(30)
        # top bar: high 101 breaks the prior 20-bar high (100.5), low 99
        # stays above the prior 20-bar low (98.5) -> short only
        top = _df_ohlc([99.8], [101.0], [99.0], [100.0])
        full = pd.concat([base, top], ignore_index=True)
        sig = signals.add_signals(indicators.add_indicators(full))
        self.assertTrue(bool(sig["short_entry"].iloc[30]))
        self.assertFalse(bool(sig["long_entry"].iloc[30]))

    def test_top_mid_range_fires_nothing(self):
        # spinning top fully inside the prior range: low 99.5 above the
        # prior 20-bar low (98.5), high 100.4 below the prior high (100.5)
        base = _base_bars(30)
        top = _df_ohlc([100.0], [100.4], [99.5], [100.1])
        full = pd.concat([base, top], ignore_index=True)
        ind = indicators.add_indicators(full)
        self.assertTrue(bool(ind["is_spinning_top"].iloc[30]))
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].iloc[30]))
        self.assertFalse(bool(sig["short_entry"].iloc[30]))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("rng", "body", "swing_low", "swing_high"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        # NOTE: no mutual-exclusion assert here — a single wide spinning
        # top can break both swing extremes at once and fire both sides,
        # which is the spec as written.

    def test_exits_are_opposite_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_swing_lookback_param_changes_window(self):
        df10 = indicators.add_indicators(_rand_df(600, seed=9), swing_lookback=10)
        df40 = indicators.add_indicators(_rand_df(600, seed=9), swing_lookback=40)
        # wider window: swing low can only be lower-or-equal, swing high higher-or-equal
        self.assertTrue(bool((df40["swing_low"].iloc[100:] <= df10["swing_low"].iloc[100:] + 1e-9).all()))
        self.assertTrue(bool((df40["swing_high"].iloc[100:] >= df10["swing_high"].iloc[100:] - 1e-9).all()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("rng", "body", "is_spinning_top", "swing_low", "swing_high"):
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
        import strategies.spinning_top as mod

        self.assertEqual(mod.SPEC.slug, "spinning_top")
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
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
