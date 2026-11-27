"""NR7 volatility-expansion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.atr_expansion_breakout import indicators, risk, signals

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


def _nr7_series():
    """Ranges [5,5,5,5,5,5,4,...]: bar 6 is the NR7 (range 4 <
    each of the previous six 5s); bar 7 breaks out above its
    high. Closes sit at 100 throughout except the breakout.
    """
    n = 30
    c = np.full(n, 100.0)
    c[7] = 101.0
    # h/l chosen so ranges are 5,5,5,5,5,5,4 then 5s again.
    h = np.full(n, 102.5)
    l = np.full(n, 97.5)
    h[6] = 102.0
    l[6] = 98.0
    o = np.full(n, 100.0)
    return _df(o, h, l, c)


class TestAtrExpansionBreakout(unittest.TestCase):
    def test_nr7_flag_strictly_narrowest_of_seven(self):
        # Ranges 5,5,5,5,5,5,4: only bar 6 is strictly less
        # than each of its six predecessors.
        ind = indicators.add_indicators(_nr7_series())
        self.assertEqual(ind.index[ind["nr7"]].tolist(), [6])
        self.assertAlmostEqual(float(ind["nr_range"].iloc[6]), 4.0, places=6)
        self.assertAlmostEqual(float(ind["nr_range"].iloc[5]), 5.0, places=6)

    def test_nr7_requires_strictly_less(self):
        # All ranges equal (5): no bar is strictly narrower
        # than its predecessors, so no NR7 ever fires.
        n = 30
        ind = indicators.add_indicators(
            _df(np.full(n, 100.0), np.full(n, 102.5),
                np.full(n, 97.5), np.full(n, 100.0)))
        self.assertFalse(bool(ind["nr7"].any()))

    def test_atr14_hand_computed_constant_range(self):
        # Constant true range 2.0 (h-l=2, flat closes): Wilder
        # ATR(14) settles at exactly 2.0 from bar 13 on.
        n = 40
        ind = indicators.add_indicators(
            _df(np.full(n, 100.0), np.full(n, 101.0),
                np.full(n, 99.0), np.full(n, 100.0)))
        self.assertTrue(np.isnan(ind["atr14"].iloc[12]))
        self.assertAlmostEqual(float(ind["atr14"].iloc[13]), 2.0, places=6)
        self.assertAlmostEqual(float(ind["atr14"].iloc[39]), 2.0, places=6)

    def test_bracket_levels_and_validity(self):
        # NR7 at bar 6 (high 102.0, low 98.0): bracket live
        # bars 6..9, expired from bar 10.
        ind = indicators.add_indicators(_nr7_series())
        for i in (6, 7, 8, 9):
            self.assertAlmostEqual(float(ind["nr7_high"].iloc[i]), 102.0, places=6)
            self.assertAlmostEqual(float(ind["nr7_low"].iloc[i]), 98.0, places=6)
            self.assertTrue(bool(ind["nr7_armed"].iloc[i]))
        self.assertTrue(np.isnan(ind["nr7_high"].iloc[10]))
        self.assertTrue(np.isnan(ind["nr7_low"].iloc[10]))
        self.assertFalse(bool(ind["nr7_armed"].iloc[10]))

    def test_long_fires_on_cross_above_nr7_high(self):
        # Close 100 -> 101 crosses above the armed high 102?
        # No: 101 < 102. Use a breakout close of 103 at bar 7.
        df = _nr7_series()
        df.loc[7, "c"] = 103.0
        df.loc[7, "h"] = 103.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [7])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_fires_on_cross_below_nr7_low(self):
        df = _nr7_series()
        df.loc[7, "c"] = 97.0
        df.loc[7, "l"] = 96.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [7])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_entry_after_bracket_expiry(self):
        # Breakout close lands at bar 10, one bar past the
        # 3-bar validity (bars 7..9): no entry.
        df = _nr7_series()
        df.loc[10, "c"] = 103.0
        df.loc[10, "h"] = 103.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_entry_without_a_cross(self):
        # Close rises to 101.5 (still below the armed high
        # 102.0) for the whole validity window: level touch
        # without a cross never fires.
        df = _nr7_series()
        df.loc[7, "c"] = 101.5
        df.loc[8, "c"] = 101.5
        df.loc[9, "c"] = 101.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_newer_nr7_rearms_bracket(self):
        # NR7 at bar 6 (high 102.0) and a second, tighter NR7
        # at bar 8 (range 3, high 101.5): the bracket levels
        # switch to the newer bar's high/low.
        df = _nr7_series()
        df.loc[8, "h"] = 101.5
        df.loc[8, "l"] = 98.5
        ind = indicators.add_indicators(df)
        self.assertTrue(bool(ind["nr7"].iloc[8]))
        self.assertAlmostEqual(float(ind["nr7_high"].iloc[8]), 101.5, places=6)
        self.assertAlmostEqual(float(ind["nr7_low"].iloc[8]), 98.5, places=6)
        # And the re-armed bracket stays live through bar 11.
        self.assertAlmostEqual(float(ind["nr7_high"].iloc[11]), 101.5, places=6)
        self.assertTrue(np.isnan(ind["nr7_high"].iloc[12]))

    def test_exit_on_close_below_arming_nr7_low(self):
        # Long at bar 7 (close 103), then a close below the
        # arming NR7 low (98.0) at bar 9 exits.
        df = _nr7_series()
        df.loc[7, "c"] = 103.0
        df.loc[7, "h"] = 103.5
        df.loc[9, "c"] = 97.0
        df.loc[9, "l"] = 96.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [7])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [9])

    def test_opposite_entry_exits(self):
        # Long at bar 7; a short entry at bar 9 (close crosses
        # below the armed low 98.0) also exits the long.
        df = _nr7_series()
        df.loc[7, "c"] = 103.0
        df.loc[7, "h"] = 103.5
        df.loc[9, "c"] = 97.0
        df.loc[9, "l"] = 96.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [9])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [9])

    def test_both_triggers_same_bar_enters_neither(self):
        # Artificial bracket where the levels cross between
        # bars (high 100 -> 90, low 95 -> 110): a close of 100
        # after 97 crosses above the new high AND below the
        # new low. The guard enters neither side.
        n = 30
        c = np.full(n, 97.0)
        c[20] = 100.0
        df = _df_from_c(c)
        ind = indicators.add_indicators(df)
        ind.loc[19, "nr7_high"] = 100.0
        ind.loc[19, "nr7_low"] = 95.0
        ind.loc[20, "nr7_high"] = 90.0
        ind.loc[20, "nr7_low"] = 110.0
        ind.loc[20, "nr7_armed"] = True
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].iloc[20]))
        self.assertFalse(bool(sig["short_entry"].iloc[20]))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("nr_range", "atr14"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "nr7", "nr7_armed"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("nr_range", "nr7", "atr14", "nr7_high",
                        "nr7_low", "nr7_armed"):
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
        import strategies.atr_expansion_breakout as mod

        self.assertEqual(mod.SPEC.slug, "atr_expansion_breakout")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
