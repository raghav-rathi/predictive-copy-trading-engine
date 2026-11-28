"""Popgun bar-pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.popgun import indicators, risk, signals

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


def _popgun_series():
    """Flat 100 closes; bar 5 is an inside bar (h 101.5 / l 98.5
    inside bar 4's 102.5 / 97.5), bar 6 is an outside bar
    (h 103 / l 97) -> popgun at 6, bracket 103 / 97, live
    bars 6..11. Bar 7 closes at 104 (long breakout).
    """
    n = 30
    c = np.full(n, 100.0)
    c[7] = 104.0
    h = np.full(n, 102.5)
    l = np.full(n, 97.5)
    h[5] = 101.5
    l[5] = 98.5
    h[6] = 103.0
    l[6] = 97.0
    o = np.full(n, 100.0)
    return _df(o, h, l, c)


class TestPopgun(unittest.TestCase):
    def test_inside_outside_popgun_flags(self):
        ind = indicators.add_indicators(_popgun_series())
        self.assertTrue(bool(ind["inside"].iloc[5]))
        self.assertFalse(bool(ind["inside"].iloc[6]))
        self.assertTrue(bool(ind["outside"].iloc[6]))
        self.assertFalse(bool(ind["outside"].iloc[5]))
        self.assertEqual(ind.index[ind["popgun"]].tolist(), [6])

    def test_no_popgun_without_inside_first(self):
        # Outside bar at 6 with a normal (non-inside) bar 5: no popgun.
        df = _popgun_series()
        df.loc[5, "h"] = 103.0  # bar 5 no longer inside bar 4
        ind = indicators.add_indicators(df)
        self.assertFalse(bool(ind["popgun"].any()))

    def test_no_popgun_without_outside_second(self):
        # Inside bar at 5, but bar 6 fails to engulf it: bar 6
        # (h 101.0 / l 98.0) is neither inside bar 5 (its low
        # is lower) nor outside it (its high is lower), and no
        # later bar forms a popgun either.
        df = _popgun_series()
        df.loc[6, "h"] = 101.0
        df.loc[6, "l"] = 98.0
        ind = indicators.add_indicators(df)
        self.assertFalse(bool(ind["popgun"].any()))

    def test_bracket_levels_and_validity(self):
        # Popgun at bar 6 (high 103.0, low 97.0): bracket live
        # bars 6..11, expired from bar 12.
        ind = indicators.add_indicators(_popgun_series())
        for i in (6, 7, 8, 9, 10, 11):
            self.assertAlmostEqual(float(ind["popgun_high"].iloc[i]), 103.0, places=6)
            self.assertAlmostEqual(float(ind["popgun_low"].iloc[i]), 97.0, places=6)
            self.assertTrue(bool(ind["popgun_armed"].iloc[i]))
        self.assertTrue(np.isnan(ind["popgun_high"].iloc[12]))
        self.assertTrue(np.isnan(ind["popgun_low"].iloc[12]))
        self.assertFalse(bool(ind["popgun_armed"].iloc[12]))

    def test_validity_param_shortens_bracket(self):
        ind = indicators.add_indicators(_popgun_series(), validity_bars=3)
        self.assertAlmostEqual(float(ind["popgun_high"].iloc[9]), 103.0, places=6)
        self.assertTrue(np.isnan(ind["popgun_high"].iloc[10]))

    def test_long_fires_on_cross_above_popgun_high(self):
        sig = signals.add_signals(indicators.add_indicators(_popgun_series()))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [7])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_fires_on_cross_below_popgun_low(self):
        df = _popgun_series()
        df.loc[7, "c"] = 96.0
        df.loc[7, "l"] = 95.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [7])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_entry_after_bracket_expiry(self):
        # Breakout close lands at bar 12, one bar past the
        # 5-bar validity (bars 7..11): no entry.
        df = _popgun_series()
        df.loc[7, "c"] = 100.0
        df.loc[12, "c"] = 104.0
        df.loc[12, "h"] = 104.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_entry_without_a_cross(self):
        # Close rises to 102.5 (still below the armed high
        # 103.0) for the whole validity window: level touch
        # without a cross never fires.
        df = _popgun_series()
        df.loc[7, "c"] = 102.5
        df.loc[8, "c"] = 102.5
        df.loc[9, "c"] = 102.5
        df.loc[10, "c"] = 102.5
        df.loc[11, "c"] = 102.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_newer_popgun_rearms_bracket(self):
        # Popgun at bar 6 (high 103.0) and a second popgun at
        # bar 8: bar 7 inside bar 6 (h 102 / l 98), bar 8
        # outside (h 104 / l 96). Bracket switches to 104/96.
        df = _popgun_series()
        df.loc[7, "c"] = 100.0
        df.loc[7, "h"] = 102.0
        df.loc[7, "l"] = 98.0
        df.loc[8, "h"] = 104.0
        df.loc[8, "l"] = 96.0
        ind = indicators.add_indicators(df)
        self.assertTrue(bool(ind["popgun"].iloc[8]))
        self.assertAlmostEqual(float(ind["popgun_high"].iloc[8]), 104.0, places=6)
        self.assertAlmostEqual(float(ind["popgun_low"].iloc[8]), 96.0, places=6)
        # And the re-armed bracket stays live through bar 13.
        self.assertAlmostEqual(float(ind["popgun_high"].iloc[13]), 104.0, places=6)
        self.assertTrue(np.isnan(ind["popgun_high"].iloc[14]))

    def test_exit_on_close_below_arming_popgun_low(self):
        # Long at bar 7 (close 104), then a close below the
        # arming popgun low (97.0) at bar 9 exits.
        df = _popgun_series()
        df.loc[9, "c"] = 96.0
        df.loc[9, "l"] = 95.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [7])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [9])

    def test_opposite_entry_exits(self):
        # Long at bar 7; a short entry at bar 9 (close crosses
        # below the armed low 97.0) also exits the long.
        df = _popgun_series()
        df.loc[9, "c"] = 96.0
        df.loc[9, "l"] = 95.5
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
        ind.loc[19, "popgun_high"] = 100.0
        ind.loc[19, "popgun_low"] = 95.0
        ind.loc[20, "popgun_high"] = 90.0
        ind.loc[20, "popgun_low"] = 110.0
        ind.loc[20, "popgun_armed"] = True
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].iloc[20]))
        self.assertFalse(bool(sig["short_entry"].iloc[20]))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("atr14",):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "inside", "outside", "popgun", "popgun_armed"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("inside", "outside", "popgun", "atr14",
                        "popgun_high", "popgun_low", "popgun_armed"):
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
        import strategies.popgun as mod

        self.assertEqual(mod.SPEC.slug, "popgun")
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
        self.assertEqual(risk.WARMUP, 10)


if __name__ == "__main__":
    unittest.main()
