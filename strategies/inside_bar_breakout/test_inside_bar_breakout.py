"""Unit tests for the inside_bar_breakout strategy (synthetic, network-free)."""

import unittest
from os.path import dirname, join
import sys

sys.path.insert(0, join(dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.inside_bar_breakout import indicators, signals, risk


def _df(n=30, seed=7):
    """Synthetic random-walk 1h OHLCV (structural contract tests only)."""
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 0.5, n))
    o = np.r_[100.0, c[:-1]]
    h = np.maximum(o, c) + rng.uniform(0.1, 0.6, n)
    l = np.minimum(o, c) - rng.uniform(0.1, 0.6, n)
    return pd.DataFrame(
        {"t": np.arange(n) * 3_600_000, "o": o, "h": h, "l": l, "c": c,
         "v": np.full(n, 1000.0)}
    )


def _flat(n=25):
    """Deterministic chop: o=100, h=102, l=98, c=100. No bar is inside another."""
    return pd.DataFrame({
        "t": np.arange(n) * 3_600_000,
        "o": np.full(n, 100.0),
        "h": np.full(n, 102.0),
        "l": np.full(n, 98.0),
        "c": np.full(n, 100.0),
        "v": np.full(n, 1000.0),
    })


def _set(df, i, o, h, l, c):
    df.loc[i, "o"], df.loc[i, "h"], df.loc[i, "l"], df.loc[i, "c"] = o, h, l, c
    return df


def _plant_inside(df, mother_i=9, inside_i=10, mother_o=100.0, mother_h=110.0,
                  mother_l=90.0, mother_c=105.0, in_o=104.0, in_h=108.0,
                  in_l=92.0, in_c=106.0):
    """Bull (or bear) mother at mother_i, strict inside bar at inside_i."""
    df = df.copy()
    _set(df, mother_i, mother_o, mother_h, mother_l, mother_c)
    _set(df, inside_i, in_o, in_h, in_l, in_c)
    return df


class TestInsideDetection(unittest.TestCase):
    def test_strict_inside_detected(self):
        df = indicators.add_indicators(_plant_inside(_flat()))
        self.assertTrue(df.loc[10, "inside"])

    def test_wick_poking_above_prior_high_not_inside(self):
        df = indicators.add_indicators(
            _plant_inside(_flat(), in_h=110.5)  # wick above mother high 110
        )
        self.assertFalse(df.loc[10, "inside"])

    def test_wick_poking_below_prior_low_not_inside(self):
        df = indicators.add_indicators(
            _plant_inside(_flat(), in_l=89.5)  # wick below mother low 90
        )
        self.assertFalse(df.loc[10, "inside"])

    def test_equal_high_not_inside(self):
        df = indicators.add_indicators(
            _plant_inside(_flat(), in_h=110.0)  # equal high -> not strict
        )
        self.assertFalse(df.loc[10, "inside"])

    def test_mother_levels_correct(self):
        df = indicators.add_indicators(_plant_inside(_flat()))
        self.assertEqual(df.loc[10, "mother_high"], 110.0)
        self.assertEqual(df.loc[10, "mother_low"], 90.0)
        self.assertTrue(pd.isna(df.loc[9, "mother_high"]))
        # Bar 11 is itself an inside bar vs bar 10's tight (108/92) range,
        # so its mother levels are bar 10's h/l.
        self.assertEqual(df.loc[11, "mother_high"], 108.0)
        self.assertEqual(df.loc[11, "mother_low"], 92.0)

    def test_mother_dir_bull(self):
        df = indicators.add_indicators(_plant_inside(_flat()))
        self.assertEqual(df.loc[10, "mother_dir"], 1)  # mother 105 > 100

    def test_mother_dir_bear(self):
        df = indicators.add_indicators(
            _plant_inside(_flat(), mother_o=110.0, mother_c=95.0))
        self.assertEqual(df.loc[10, "mother_dir"], -1)  # mother 95 < 110

    def test_active_levels_armed_on_inside_bar(self):
        df = indicators.add_indicators(_plant_inside(_flat()))
        self.assertEqual(df.loc[10, "active_mother_high"], 110.0)
        self.assertEqual(df.loc[10, "active_mother_low"], 90.0)


class TestExpiry(unittest.TestCase):
    def _quiet(self):
        # Inside bar at 10 (mother high 110 / low 90); bars 11-15 hover at
        # 101 (no breakout); bar 16 breaks up on the 6th bar after the setup.
        df = _plant_inside(_flat())
        for i in range(11, 16):
            # Wide bar (112/88): not inside bar 10's (108/92) range, no re-arm.
            _set(df, i, 101.0, 112.0, 88.0, 101.0)
        _set(df, 16, 113.0, 116.0, 112.0, 115.0)
        return df

    def test_setup_expires_after_five_bars(self):
        df = indicators.add_indicators(self._quiet())
        # Armed on bars 10..14 (5 bars incl. the inside bar), NaN from 15 on.
        self.assertEqual(df.loc[14, "active_mother_high"], 110.0)
        self.assertTrue(pd.isna(df.loc[15, "active_mother_high"]))
        self.assertTrue(pd.isna(df.loc[16, "active_mother_high"]))

    def test_breakout_after_expiry_no_signal(self):
        df = signals.add_signals(indicators.add_indicators(self._quiet()))
        self.assertFalse(df.loc[16, "long_entry"])

    def test_breakout_inside_window_signals(self):
        df = _plant_inside(_flat())
        _set(df, 13, 108.0, 109.0, 107.0, 108.0)  # close below 110
        _set(df, 14, 111.0, 113.0, 109.0, 112.0)  # close crosses above 110
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig.loc[14, "long_entry"])

    def test_new_inside_bar_resets_window(self):
        df = _plant_inside(_flat())
        _set(df, 12, 100.0, 103.0, 99.0, 101.0)      # wide, not inside flat bar
        _set(df, 13, 101.5, 102.5, 99.5, 101.0)      # inside bar vs bar 12
        ind = indicators.add_indicators(df)
        self.assertTrue(ind.loc[13, "inside"])
        self.assertEqual(ind.loc[13, "mother_high"], 103.0)
        # Re-armed window runs 13..17 with the NEW levels, then expires.
        self.assertEqual(ind.loc[17, "active_mother_high"], 103.0)
        self.assertTrue(pd.isna(ind.loc[18, "active_mother_high"]))


class TestEntries(unittest.TestCase):
    def test_breakout_up_triggers_long_only(self):
        df = _plant_inside(_flat())
        _set(df, 12, 108.0, 109.0, 107.0, 108.0)
        _set(df, 13, 111.0, 113.0, 109.0, 112.0)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig.loc[13, "long_entry"])
        self.assertFalse(sig.loc[13, "short_entry"])

    def test_breakout_down_triggers_short_only(self):
        df = _plant_inside(_flat())
        _set(df, 12, 92.0, 93.0, 91.0, 92.0)
        _set(df, 13, 89.0, 91.0, 88.0, 88.5)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig.loc[13, "short_entry"])
        self.assertFalse(sig.loc[13, "long_entry"])

    def test_same_bar_both_breaks_prefers_bull_mother_long(self):
        df = pd.DataFrame({
            "c": [100.0, 100.0, 100.0],
            "active_mother_high": [100.0, 100.0, 90.0],
            "active_mother_low": [80.0, 80.0, 105.0],
            "active_mother_dir": [1, 1, 1],
        })
        sig = signals.add_signals(df)
        # bar 2: 100 > 90 (up cross) AND 100 < 105 (down cross) -> tie
        self.assertTrue(sig.loc[2, "long_entry"])
        self.assertFalse(sig.loc[2, "short_entry"])

    def test_same_bar_both_breaks_prefers_bear_mother_short(self):
        df = pd.DataFrame({
            "c": [100.0, 100.0, 100.0],
            "active_mother_high": [100.0, 100.0, 90.0],
            "active_mother_low": [80.0, 80.0, 105.0],
            "active_mother_dir": [-1, -1, -1],
        })
        sig = signals.add_signals(df)
        self.assertTrue(sig.loc[2, "short_entry"])
        self.assertFalse(sig.loc[2, "long_entry"])

    def test_exits_on_opposite_signal(self):
        df = _plant_inside(_flat())
        _set(df, 11, 108.0, 109.0, 107.0, 108.0)
        _set(df, 12, 111.0, 113.0, 109.0, 112.0)  # long entry here
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig.loc[12, "long_entry"])
        self.assertTrue(sig.loc[12, "short_exit"])    # opposite of long entry
        self.assertFalse(sig.loc[12, "long_exit"])


class TestContracts(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_df(n=300)))
        for col in ["long_entry", "short_entry", "long_exit", "short_exit"]:
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_warmup_nan(self):
        ind = indicators.add_indicators(_df(n=100))
        # ATR(14): NaN for the first 13 bars.
        self.assertTrue(ind["atr"].iloc[:13].isna().all())
        self.assertFalse(ind["atr"].iloc[13:].isna().any())
        # Armed levels are NaN until the first inside bar forms.
        idx = ind.index[ind["inside"]].min()
        if pd.notna(idx):
            self.assertTrue(
                ind["active_mother_high"].loc[:idx - 1].isna().all())

    def test_long_exit_equals_short_entry_and_short_exit_equals_long_entry(self):
        sig = signals.add_signals(indicators.add_indicators(_df(n=300)))
        self.assertTrue((sig["long_exit"] == sig["short_entry"]).all())
        self.assertTrue((sig["short_exit"] == sig["long_entry"]).all())

    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.5)
        self.assertIsNone(r.trail_atr_mult)
        self.assertEqual(r.target_atr_mult, 2.0)
        self.assertEqual(r.max_hold_bars, 48)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertEqual(r.fee_rate, 0.00045)
        self.assertEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
