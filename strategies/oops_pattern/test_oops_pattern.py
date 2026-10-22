"""Oops gap-reversion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.oops_pattern import indicators, risk, signals
from strategies import base as B

T0 = 1_700_000_000_000
H = 3_600_000


def _cols(n):
    t = (T0 + np.arange(n) * H).astype("int64")
    return t


def _base(n=140):
    """Flat 100.0 frame, h=100.5 / l=99.5 -- no gaps anywhere."""
    o = np.full(n, 100.0)
    c = np.full(n, 100.0)
    h = np.full(n, 100.5)
    l = np.full(n, 99.5)
    v = np.full(n, 100.0)
    t = _cols(n)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _gap_down_frame():
    """Gap-down at bar 72, reclaimed at bar 73, nothing after.

    Completed prior session for bar 72 = bars 25..48, floored at l=99.0
    so prev_day_low[72] = 99.0.
    """
    df = _base()
    df.loc[25:48, "l"] = 99.0
    df.loc[72, ["o", "h", "l", "c"]] = [98.5, 98.9, 98.3, 98.8]
    df.loc[73, ["o", "h", "l", "c"]] = [99.0, 99.4, 98.9, 99.2]
    return df


def _gap_up_frame():
    """Gap-up at bar 72, reclaimed (below) at bar 73. Short mirror."""
    df = _base()
    df.loc[25:48, "h"] = 101.0
    df.loc[72, ["o", "h", "l", "c"]] = [101.5, 101.6, 101.1, 101.2]
    df.loc[73, ["o", "h", "l", "c"]] = [101.0, 101.1, 100.7, 100.8]
    return df


def _expired_frame():
    """Gap-down at 72, but close never reclaims within 24 bars."""
    df = _gap_down_frame()
    df.loc[73:, ["o", "h", "l", "c"]] = [98.8, 98.9, 98.7, 98.8]
    return df


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_base())
        for col in ("prev_day_high", "prev_day_low", "gap_down",
                    "gap_up", "atr"):
            self.assertIn(col, ind.columns)

    def test_session_range_is_completed_session_only(self):
        ind = indicators.add_indicators(_gap_down_frame())
        # bar 72's completed prior session = bars 25..48
        self.assertAlmostEqual(ind["prev_day_low"].iloc[72], 99.0)
        self.assertAlmostEqual(ind["prev_day_high"].iloc[72], 100.5)

    def test_no_future_leak(self):
        df = _gap_down_frame()
        df.loc[60, "l"] = 90.0   # inside the current (incomplete) session
        df.loc[100, "l"] = 90.0  # in the future
        ind = indicators.add_indicators(df)
        # neither spike may move bar 72's completed-session range
        self.assertAlmostEqual(ind["prev_day_low"].iloc[72], 99.0)

    def test_gap_flags_boolean_no_nan(self):
        ind = indicators.add_indicators(_base())
        for col in ("gap_down", "gap_up"):
            self.assertTrue(ind[col].dtype == bool, col)
            self.assertFalse(ind[col].isna().any(), col)
        self.assertFalse(ind["gap_down"].any())
        self.assertFalse(ind["gap_up"].any())

    def test_gap_detection(self):
        ind = indicators.add_indicators(_gap_down_frame())
        self.assertTrue(ind["gap_down"].iloc[72])
        self.assertFalse(ind["gap_up"].iloc[72])
        self.assertFalse(ind["gap_down"].iloc[73])  # o == prev low, not a gap
        self.assertEqual(ind["gap_down"].sum(), 1)

    def test_warmup_nans(self):
        ind = indicators.add_indicators(_base())
        # rolling(24).min needs 24 bars (first at 23), shift(24) -> 47
        self.assertTrue(ind["prev_day_low"].iloc[:47].isna().all())
        self.assertFalse(ind["prev_day_low"].iloc[47:].isna().any())

    def test_session_param(self):
        ind = indicators.add_indicators(_base(), session=12)
        self.assertTrue(ind["prev_day_low"].iloc[:23].isna().all())
        self.assertFalse(ind["prev_day_low"].iloc[23:].isna().any())

    def test_does_not_mutate_input(self):
        df = _base()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def _sig(self, df):
        return signals.add_signals(indicators.add_indicators(df))

    def test_columns_boolean_no_nan(self):
        sig = self._sig(_base())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_fires_only_after_reclaim(self):
        sig = self._sig(_gap_down_frame())
        self.assertFalse(sig["long_entry"].iloc[72])  # gap bar, no reclaim
        self.assertTrue(sig["long_entry"].iloc[73])   # close back > 99.0
        self.assertFalse(sig["short_entry"].any())

    def test_short_mirror(self):
        sig = self._sig(_gap_up_frame())
        self.assertFalse(sig["short_entry"].iloc[72])
        self.assertTrue(sig["short_entry"].iloc[73])   # close back < 101.0
        self.assertFalse(sig["long_entry"].any())

    def test_no_entries_without_gap(self):
        sig = self._sig(_base())
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_one_entry_per_gap(self):
        # price stays above the reclaimed low for the rest of the
        # session: the buy stop must not re-trigger on later bars.
        sig = self._sig(_gap_down_frame())
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_signals_expire_after_24_bars(self):
        sig = self._sig(_expired_frame())
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_exits_are_opposite_oops(self):
        sig = self._sig(_gap_down_frame())
        pd.testing.assert_series_equal(
            sig["long_exit"], sig["short_entry"], check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], sig["long_entry"], check_names=False)

    def test_no_lookahead(self):
        df = _gap_down_frame()
        full = self._sig(df)
        for j in (73, 90):
            trunc = self._sig(df.iloc[: j + 1])
            for col in ("long_entry", "short_entry"):
                self.assertEqual(bool(full[col].iloc[j]),
                                 bool(trunc[col].iloc[j]),
                                 f"bar {j} col {col}")


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 48)

    def test_registration(self):
        import strategies.oops_pattern as mod
        from strategies.registry import REGISTRY

        self.assertIn("oops_pattern", REGISTRY)
        self.assertIs(REGISTRY["oops_pattern"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "oops_pattern")
        self.assertEqual(mod.SPEC.name, "Oops Gap Reversion")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__),
                         {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
