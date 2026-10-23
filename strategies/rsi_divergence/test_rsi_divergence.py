"""RSI(14) swing-pivot divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_divergence import indicators, risk, signals
from strategies import base as B


def _frame_from_close(c):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _geom(a, b, n):
    return a * (b / a) ** (np.arange(n) / (n - 1))


def _frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c)


def _regular_bullish_series():
    """Grind down (deep RSI trough at bar 47), bounce, sharp lower low at
    bar 60. Pivot lows (47, 60): price 99.8 -> 95.8 (LL), RSI ~19 -> ~30
    (HL). Expect long_entry + short_exit at the confirmation bar 63."""
    return np.concatenate([
        _geom(100, 133.5, 30),        # 0..29 rise
        _geom(133.5, 100, 19)[1:],    # 30..47 grind down
        _geom(100, 115, 12)[1:],      # 48..58 bounce
        [104.0, 96.0, 97.0, 98.0],    # 59..62 sharp V, pivot low at 60
        _geom(98, 100, 28)[1:],       # 63..89 drift up
    ])


def _regular_bearish_series():
    """Rise, sharp spike (RSI ~100 at bar 31), decline, slow grind to a
    higher high at bar 67. Pivot highs (31, 67): price 140.3 -> 142.3
    (HH), RSI ~100 -> ~82 (LH). Expect short_entry + long_exit at bar 70."""
    return np.concatenate([
        _geom(100, 130, 30),          # 0..29 rise
        [135.0, 140.0],               # 30..31 spike, pivot high at 31
        _geom(140, 110, 19)[1:],      # 32..49 decline
        _geom(110, 142, 19)[1:],      # 50..67 grind up, pivot high at 67
        _geom(142, 135, 23)[1:],      # 68..89 drift down
    ])


def _hidden_bullish_series():
    """Uptrend with two pullbacks. Pivot lows (35, 60): price 131.7 ->
    135.7 (HL), RSI ~66 -> ~40 (LL). Expect long_entry + short_exit at
    bar 63. (The pivot-high pair (29, 50) is a regular bearish on this
    series and fires short_entry at bar 53 -- real concurrent behavior.)"""
    return np.concatenate([
        _geom(100, 140, 30),          # 0..29 rise
        _geom(140, 132, 7)[1:],      # 30..35 pullback, pivot low at 35
        _geom(132, 150, 16)[1:],     # 36..50 rally, pivot high at 50
        _geom(150, 136, 11)[1:],     # 51..60 pullback, pivot low at 60
        _geom(136, 145, 30)[1:],     # 61..89 rally
    ])


def _hidden_bearish_series():
    """Downtrend with two rallies. Pivot highs (35, 60): price 108.2 ->
    106.2 (LH), RSI ~36 -> ~65 (HH). Expect short_entry + long_exit at
    bar 63. (The pivot-low pair (29, 50) is a regular bullish and fires
    long_entry at bar 53 -- real concurrent behavior.)"""
    return np.concatenate([
        _geom(140, 100, 30),          # 0..29 decline
        _geom(100, 108, 7)[1:],      # 30..35 rally, pivot high at 35
        _geom(108, 88, 16)[1:],      # 36..50 decline, pivot low at 50
        _geom(88, 106, 11)[1:],      # 51..60 rally, pivot high at 60
        _geom(106, 100, 30)[1:],     # 61..89 drift down
    ])


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("rsi14", "pivot_high", "pivot_low", "pivot_high_price",
                    "pivot_high_rsi", "pivot_low_price", "pivot_low_rsi", "atr"):
            self.assertIn(col, ind.columns)

    def test_rsi14_matches_base_rsi(self):
        df = _frame()
        ind = indicators.add_indicators(df)
        pd.testing.assert_series_equal(ind["rsi14"], B.rsi(df["c"], 14),
                                       check_names=False)

    def test_pivot_marks_match_spec(self):
        # Single V: strict rise, dip to 90 at bar 23, strict rise after.
        # Bar 23 must be the only swing low (l[23] == min(l[20..26])).
        c = np.concatenate([
            _geom(100, 101, 20),                       # 0..19 strict rise
            [97.0, 94.0, 92.0, 90.0, 92.0, 94.0, 96.0, 98.0],  # 20..27 V
            _geom(98, 99, 13)[1:],                     # 28..40 strict rise
        ])
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertTrue(ind["pivot_low"].iloc[23],
                        "bar 23 must be marked a swing low")
        self.assertFalse(ind["pivot_high"].iloc[23])
        self.assertEqual(ind["pivot_low"].iloc[:20].sum(), 0)
        self.assertEqual(ind["pivot_low"].iloc[28:].sum(), 0)
        # helper columns store price + rsi at the pivot bar, NaN elsewhere
        self.assertAlmostEqual(ind["pivot_low_price"].iloc[23],
                               ind["l"].iloc[23])
        self.assertAlmostEqual(ind["pivot_low_rsi"].iloc[23],
                               ind["rsi14"].iloc[23])
        self.assertTrue(np.isnan(ind["pivot_low_price"].iloc[22]))

    def test_pivot_confirmation_delay(self):
        # Regular-bullish series: second pivot low at bar 60, confirmed at
        # bar 63. With data only through bar 62 the pair is unconfirmable:
        # no entry may fire; with bar 63 present the entry fires at 63.
        df = _frame_from_close(_regular_bullish_series())
        early = signals.add_signals(
            indicators.add_indicators(df.iloc[:63]))  # bars 0..62
        self.assertEqual(early["long_entry"].sum(), 0)
        self.assertEqual(early["short_entry"].sum(), 0)
        full = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(full["long_entry"].iloc[63],
                        "entry must fire on the confirmation bar")

    def test_no_lookahead(self):
        df = _frame(n=400, seed=11)
        full = signals.add_signals(indicators.add_indicators(df))
        for j in (120, 250, 399):
            trunc = signals.add_signals(
                indicators.add_indicators(df.iloc[: j + 1]))
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(full[col].iloc[j]),
                                 bool(trunc[col].iloc[j]),
                                 f"{col} at bar {j}")

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

    def test_nan_warmup(self):
        # 50-bar frame: RSI NaN for the first 13 bars -- signals must still
        # be boolean with no NaN anywhere.
        sig = signals.add_signals(indicators.add_indicators(_frame(n=50)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_regular_bullish_detected(self):
        ind = indicators.add_indicators(
            _frame_from_close(_regular_bullish_series()))
        self.assertTrue(ind["pivot_low"].iloc[47])
        self.assertTrue(ind["pivot_low"].iloc[60])
        # price lower low, RSI higher low (comfortable margins)
        self.assertLess(ind["pivot_low_price"].iloc[60],
                        ind["pivot_low_price"].iloc[47])
        self.assertGreater(ind["pivot_low_rsi"].iloc[60],
                           ind["pivot_low_rsi"].iloc[47])
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[63])
        self.assertTrue(sig["short_exit"].iloc[63])
        self.assertFalse(sig["long_exit"].iloc[63])

    def test_regular_bearish_detected(self):
        ind = indicators.add_indicators(
            _frame_from_close(_regular_bearish_series()))
        self.assertTrue(ind["pivot_high"].iloc[31])
        self.assertTrue(ind["pivot_high"].iloc[67])
        self.assertGreater(ind["pivot_high_price"].iloc[67],
                           ind["pivot_high_price"].iloc[31])
        self.assertLess(ind["pivot_high_rsi"].iloc[67],
                        ind["pivot_high_rsi"].iloc[31])
        sig = signals.add_signals(ind)
        self.assertTrue(sig["short_entry"].iloc[70])
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["short_exit"].iloc[70])

    def test_hidden_bullish_detected(self):
        ind = indicators.add_indicators(
            _frame_from_close(_hidden_bullish_series()))
        self.assertTrue(ind["pivot_low"].iloc[35])
        self.assertTrue(ind["pivot_low"].iloc[60])
        # price higher low, RSI lower low
        self.assertGreater(ind["pivot_low_price"].iloc[60],
                           ind["pivot_low_price"].iloc[35])
        self.assertLess(ind["pivot_low_rsi"].iloc[60],
                        ind["pivot_low_rsi"].iloc[35])
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[63])
        self.assertTrue(sig["short_exit"].iloc[63])
        # the (29, 50) high pair on this series is a genuine regular
        # bearish -- it must fire exactly there and nowhere else
        self.assertTrue(sig["short_entry"].iloc[53])

    def test_hidden_bearish_detected(self):
        ind = indicators.add_indicators(
            _frame_from_close(_hidden_bearish_series()))
        self.assertTrue(ind["pivot_high"].iloc[35])
        self.assertTrue(ind["pivot_high"].iloc[60])
        # price lower high, RSI higher high
        self.assertLess(ind["pivot_high_price"].iloc[60],
                        ind["pivot_high_price"].iloc[35])
        self.assertGreater(ind["pivot_high_rsi"].iloc[60],
                           ind["pivot_high_rsi"].iloc[35])
        sig = signals.add_signals(ind)
        self.assertTrue(sig["short_entry"].iloc[63])
        self.assertTrue(sig["long_exit"].iloc[63])
        # the (29, 50) low pair on this series is a genuine regular
        # bullish -- it must fire exactly there and nowhere else
        self.assertTrue(sig["long_entry"].iloc[53])

    def test_no_double_fire_on_same_pair(self):
        # Each confirmed pivot pair fires exactly once, on the
        # confirmation bar of the newly confirmed pivot.
        sig = signals.add_signals(indicators.add_indicators(
            _frame_from_close(_regular_bullish_series())))
        self.assertEqual(sig["long_entry"].sum(), 1)
        self.assertEqual(sig["short_exit"].sum(), 1)
        sig2 = signals.add_signals(indicators.add_indicators(
            _frame_from_close(_regular_bearish_series())))
        self.assertEqual(sig2["short_entry"].sum(), 1)
        self.assertEqual(sig2["long_exit"].sum(), 1)

    def test_exits_only_on_opposite_divergence(self):
        # Regular bullish fires long_entry + short_exit, never long_exit.
        sig = signals.add_signals(indicators.add_indicators(
            _frame_from_close(_regular_bullish_series())))
        self.assertEqual(sig["long_exit"].sum(), 0)
        self.assertEqual(sig["short_entry"].sum(), 0)
        # Regular bearish fires short_entry + long_exit, never short_exit.
        sig2 = signals.add_signals(indicators.add_indicators(
            _frame_from_close(_regular_bearish_series())))
        self.assertEqual(sig2["short_exit"].sum(), 0)
        self.assertEqual(sig2["long_entry"].sum(), 0)


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        import strategies.rsi_divergence as mod
        from strategies.registry import REGISTRY

        self.assertIn("rsi_divergence", REGISTRY)
        self.assertIs(REGISTRY["rsi_divergence"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "rsi_divergence")
        self.assertEqual(mod.SPEC.name, "RSI(14) Swing-Pivot Divergence")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
