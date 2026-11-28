"""Consecutive up/down days fade tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.streak_fade import indicators, risk, signals

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


def _streak_series():
    """Closes: 100, 101, 102, 103, 104, 105 (5 up closes),
    then 104, 103, 102, 101, 100 (4 down closes)."""
    c = [100.0, 101.0, 102.0, 103.0, 104.0, 105.0,
         104.0, 103.0, 102.0, 101.0, 100.0]
    c += [100.0] * 20
    return _df_from_c(c)


class TestStreakFade(unittest.TestCase):
    def test_up_streak_counts_consecutive_up_closes(self):
        ind = indicators.add_indicators(_streak_series())
        self.assertEqual(ind["up_streak"].iloc[:6].tolist(), [0, 1, 2, 3, 4, 5])
        self.assertEqual(ind["down_streak"].iloc[:6].tolist(), [0, 0, 0, 0, 0, 0])

    def test_down_streak_counts_and_resets_up(self):
        ind = indicators.add_indicators(_streak_series())
        # Bar 6 is the first down close: up resets, down starts.
        self.assertEqual(int(ind["up_streak"].iloc[6]), 0)
        self.assertEqual(int(ind["down_streak"].iloc[6]), 1)
        self.assertEqual(ind["down_streak"].iloc[6:11].tolist(), [1, 2, 3, 4, 5])

    def test_flat_close_resets_both_streaks(self):
        c = [100.0, 101.0, 102.0, 102.0, 103.0] + [103.0] * 20
        ind = indicators.add_indicators(_df_from_c(c))
        self.assertEqual(int(ind["up_streak"].iloc[3]), 0)
        self.assertEqual(int(ind["down_streak"].iloc[3]), 0)
        self.assertEqual(int(ind["up_streak"].iloc[4]), 1)

    def test_sma10_hand_computed(self):
        c = list(range(100, 130))
        ind = indicators.add_indicators(_df_from_c(c))
        # SMA(10) of closes 100..109 at bar 9 = 104.5.
        self.assertAlmostEqual(float(ind["sma10"].iloc[9]), 104.5, places=6)
        self.assertTrue(np.isnan(ind["sma10"].iloc[8]))

    def test_short_fires_once_on_fourth_up_close(self):
        sig = signals.add_signals(indicators.add_indicators(_streak_series()))
        # 4th up close is bar 4 (closes 101,102,103,104);
        # the 5th up close (bar 5) must NOT re-fire.
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [4])
        self.assertFalse(bool(sig["long_entry"].iloc[:6].any()))

    def test_long_fires_once_on_fourth_down_close(self):
        sig = signals.add_signals(indicators.add_indicators(_streak_series()))
        # Down closes start at bar 6; the 4th is bar 9.
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [9])
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [4])

    def test_no_entry_at_streak_three(self):
        c = [100.0, 101.0, 102.0, 103.0, 102.0] + [102.0] * 20
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_long_exit_on_cross_above_sma10(self):
        # 10 flat bars (so SMA(10) is valid), then 4 down closes
        # (long entry at bar 13), then a rally crossing above
        # SMA(10) at bar 14.
        c = [110.0] * 10 + [109.0, 108.0, 107.0, 106.0, 112.0, 113.0] + [113.0] * 10
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [13])
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertIn(14, exits)

    def test_short_exit_on_cross_below_sma10(self):
        c = [90.0] * 10 + [91.0, 92.0, 93.0, 94.0, 88.0, 87.0] + [87.0] * 10
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [13])
        self.assertIn(14, sig.index[sig["short_exit"]].tolist())

    def test_opposite_entry_exits(self):
        # Short at bar 4; a 4-down streak ending at bar 9 is a
        # long entry and must also exit the short.
        sig = signals.add_signals(indicators.add_indicators(_streak_series()))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [9])
        self.assertIn(9, sig.index[sig["short_exit"]].tolist())

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("up_streak", "down_streak", "sma10"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("up_streak", "down_streak", "sma10"):
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
        import strategies.streak_fade as mod

        self.assertEqual(mod.SPEC.slug, "streak_fade")
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
        self.assertEqual(risk.WARMUP, 20)


if __name__ == "__main__":
    unittest.main()
