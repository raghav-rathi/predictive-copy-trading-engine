"""Engulfing pattern reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.engulfing_pattern import indicators, risk, signals


def _frame_full(o, c, h=None, l=None):
    o = np.asarray(o, dtype=float)
    c = np.asarray(c, dtype=float)
    n = len(c)
    if h is None:
        h = np.maximum(o, c) * 1.001
    if l is None:
        l = np.minimum(o, c) * 0.999
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("ema20", "bullish_eng", "bearish_eng", "atr"):
            self.assertIn(col, ind.columns)
        self.assertTrue(ind["bullish_eng"].dtype == bool)
        self.assertTrue(ind["bearish_eng"].dtype == bool)

    def test_bullish_engulfing_hand_built(self):
        # Prior bar red (o=110 > c=100); current bar green whose body
        # [99, 111] fully covers the prior body [100, 110].
        o = [108.0, 110.0, 99.0]
        c = [110.0, 100.0, 111.0]
        ind = indicators.add_indicators(_frame_full(o, c))
        self.assertTrue(ind["bullish_eng"].iloc[2])
        self.assertFalse(ind["bearish_eng"].iloc[2])
        # equality at the boundaries counts as full coverage
        o2 = [108.0, 110.0, 100.0]
        c2 = [110.0, 100.0, 110.0]
        ind2 = indicators.add_indicators(_frame_full(o2, c2))
        self.assertTrue(ind2["bullish_eng"].iloc[2])

    def test_bearish_engulfing_mirror(self):
        # Prior bar green (o=100 < c=110); current bar red whose body
        # [111, 99] fully covers the prior body [100, 110].
        o = [98.0, 100.0, 111.0]
        c = [100.0, 110.0, 99.0]
        ind = indicators.add_indicators(_frame_full(o, c))
        self.assertTrue(ind["bearish_eng"].iloc[2])
        self.assertFalse(ind["bullish_eng"].iloc[2])

    def test_partial_engulf_rejected(self):
        # Current close 109 < prior open 110: the body is NOT fully
        # covered, so this is a hammer-ish bar, not an engulfing.
        o = [108.0, 110.0, 99.0]
        c = [110.0, 100.0, 109.0]
        ind = indicators.add_indicators(_frame_full(o, c))
        self.assertFalse(ind["bullish_eng"].iloc[2])
        # Same-side mirror: prior green, current red, close 101 > open 100.
        o2 = [98.0, 100.0, 111.0]
        c2 = [100.0, 110.0, 101.0]
        ind2 = indicators.add_indicators(_frame_full(o2, c2))
        self.assertFalse(ind2["bearish_eng"].iloc[2])

    def test_wick_only_engulf_rejected(self):
        # The wicks (95/115) engulf the prior body (100/110) but the
        # body itself (105/106) sits inside it: indecision, not reversal.
        o = [108.0, 110.0, 105.0]
        c = [110.0, 100.0, 106.0]
        h = [109.0, 111.0, 115.0]
        l = [107.0, 99.0, 95.0]
        ind = indicators.add_indicators(_frame_full(o, c, h, l))
        self.assertFalse(ind["bullish_eng"].iloc[2])

    def test_doji_bars_never_engulf(self):
        # Flat bodies (c == o) are neither bullish nor bearish bodies,
        # so a doji can never be an engulfing bar either way.
        o = [100.0, 100.0, 100.0]
        c = [100.0, 100.0, 100.0]
        ind = indicators.add_indicators(_frame_full(o, c))
        self.assertFalse(ind["bullish_eng"].iloc[2])
        self.assertFalse(ind["bearish_eng"].iloc[2])

    def test_ema20_matches_reference(self):
        df = _frame()
        ind = indicators.add_indicators(df)
        ref = df["c"].ewm(span=20, adjust=False, min_periods=20).mean()
        pd.testing.assert_series_equal(ind["ema20"], ref, check_names=False)

    def test_atr_present_and_nan_warmup_only(self):
        ind = indicators.add_indicators(_frame())
        self.assertIn("atr", ind.columns)
        # EMA(20) has min_periods=20: NaN only in the first 19 bars.
        self.assertTrue(ind["ema20"].iloc[:19].isna().all())
        self.assertFalse(ind["ema20"].iloc[19:].isna().any())

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

    def test_trend_filter_blocks_countertrend_bullish_engulf(self):
        # Steady downtrend then a textbook bullish engulfing: the
        # pattern is detected but the close sits below EMA(20), so no
        # long entry (counter-trend engulfings are vetoed).
        c = 120.0 - np.arange(42.0)  # linear decline, ~1/bar
        df = _frame_from_close(c)
        df = df.copy()
        df.loc[41, "c"] = 82.0  # bullish pop: green body [80, 82] fully covers the red [80, 81]
        df.loc[41, "h"] = 82.0 * 1.001
        df.loc[41, "l"] = 80.0 * 0.999
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        j = 41
        self.assertTrue(ind["bullish_eng"].iloc[j], "pattern must be detected")
        self.assertGreater(ind["ema20"].iloc[j], ind["c"].iloc[j],
                           "close must be below EMA(20) in the downtrend")
        self.assertEqual(sig["long_entry"].sum(), 0,
                         "counter-trend bullish engulfing must not enter")

    def test_trend_filter_allows_withtrend_bullish_engulf(self):
        # Steady uptrend with a red bar followed by a green bar that
        # fully covers it: pattern fires and close > EMA(20), so the
        # dip-buy long enters on the closed engulfing bar.
        c = 80.0 + np.arange(42.0)
        df = _frame_from_close(c)
        df = df.copy()
        df.loc[40, "o"], df.loc[40, "c"] = 121.0, 120.0  # red bar
        df.loc[41, "c"] = 122.0                          # green engulfs: [120,122] covers [120,121]
        for j in (40, 41):  # keep h/l consistent after the overrides
            df.loc[j, "h"] = max(df.loc[j, "o"], df.loc[j, "c"]) * 1.001
            df.loc[j, "l"] = min(df.loc[j, "o"], df.loc[j, "c"]) * 0.999
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        self.assertTrue(ind["bullish_eng"].iloc[41], "pattern must be detected")
        self.assertLess(ind["ema20"].iloc[41], ind["c"].iloc[41],
                        "close must be above EMA(20) in the uptrend")
        self.assertTrue(sig["long_entry"].iloc[41])
        self.assertFalse(sig["short_entry"].iloc[41])

    def test_trend_filter_blocks_countertrend_bearish_engulf(self):
        # Steady uptrend then a textbook bearish engulfing: detected
        # but close > EMA(20), so no short entry.
        c = 80.0 + np.arange(42.0)
        df = _frame_from_close(c)
        df = df.copy()
        df.loc[40, "o"], df.loc[40, "c"] = 119.0, 120.0  # green bar
        df.loc[41, "c"] = 118.0                          # red engulfs: [118,120] covers [119,120]
        for j in (40, 41):  # keep h/l consistent after the overrides
            df.loc[j, "h"] = max(df.loc[j, "o"], df.loc[j, "c"]) * 1.001
            df.loc[j, "l"] = min(df.loc[j, "o"], df.loc[j, "c"]) * 0.999
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        j = 41
        self.assertTrue(ind["bearish_eng"].iloc[j], "pattern must be detected")
        self.assertLess(ind["ema20"].iloc[j], ind["c"].iloc[j])
        self.assertEqual(sig["short_entry"].sum(), 0,
                         "counter-trend bearish engulfing must not enter")

    def test_exits_on_opposite_pattern(self):
        # A bearish engulfing closes any long; a bullish engulfing
        # closes any short — the pattern's own negation is the exit.
        o = [98.0, 100.0, 111.0, 111.0, 99.0]
        c = [100.0, 110.0, 99.0, 100.0, 111.0]
        sig = signals.add_signals(indicators.add_indicators(_frame_full(o, c)))
        self.assertTrue(sig["bearish_eng"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[2])
        self.assertFalse(sig["short_exit"].iloc[2])
        self.assertTrue(sig["bullish_eng"].iloc[4])
        self.assertTrue(sig["short_exit"].iloc[4])
        self.assertFalse(sig["long_exit"].iloc[4])

    def test_no_signals_during_ema_warmup(self):
        # While EMA(20) is still NaN, the trend comparisons are False:
        # no entries may fire, and there must be no NaN leakage.
        df = _frame(n=60)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        self.assertTrue(ind["ema20"].iloc[:19].isna().all())
        self.assertEqual(sig["long_entry"].iloc[:19].sum(), 0)
        self.assertEqual(sig["short_entry"].iloc[:19].sum(), 0)

    def test_entry_and_exit_never_same_bar_same_side(self):
        for seed in (1, 2, 3):
            sig = signals.add_signals(indicators.add_indicators(_frame(seed=seed)))
            self.assertFalse((sig["long_entry"] & sig["long_exit"]).any(), f"seed={seed}")
            self.assertFalse((sig["short_entry"] & sig["short_exit"]).any(), f"seed={seed}")

    def test_no_lookahead(self):
        df = _frame(n=800, seed=11)
        full = signals.add_signals(indicators.add_indicators(df))
        j = 420
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.engulfing_pattern as mod
        from strategies.registry import REGISTRY

        self.assertIn("engulfing_pattern", REGISTRY)
        self.assertIs(REGISTRY["engulfing_pattern"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "engulfing_pattern")
        self.assertEqual(mod.SPEC.name, "Engulfing Pattern Reversal")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
