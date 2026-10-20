"""Hikkake false-breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.hikkake import indicators, risk, signals


def _df(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.full(n, v)}
    )


def _rand_df(n=400, seed=7):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 0.8, n))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.3
    l = np.minimum(o, c) - 0.3
    return _df(o, h, l, c)


def _hikkake_setup(bullish=True):
    """Build a synthetic hikkake on a flat base: an inside bar, a trap
    bar, then a confirming close."""
    n = 30
    o = np.full(n, 100.0)
    h = o + 1.0
    l = o - 1.0
    c = o.copy()
    # bar 20: inside bar (range inside bar 19)
    i = 20
    h[i] = h[i - 1] - 0.2
    l[i] = l[i - 1] + 0.2
    c[i] = (h[i] + l[i]) / 2
    # bar 21: trap bar
    if bullish:
        h[i + 1] = h[i] - 0.3   # lower high
        l[i + 1] = l[i] - 0.6   # lower low  -> failed breakdown
        c[i + 1] = l[i + 1] + 0.1
    else:
        h[i + 1] = h[i] + 0.6   # higher high
        l[i + 1] = l[i] + 0.3   # higher low -> failed breakout
        c[i + 1] = h[i + 1] - 0.1
    # bar 22: confirmation close back through the inside bar's range
    if bullish:
        c[i + 2] = h[i] + 0.5   # close above inside high
    else:
        c[i + 2] = l[i] - 0.5   # close below inside low
    h[i + 2] = max(h[i + 2], c[i + 2]) + 0.1
    l[i + 2] = min(l[i + 2], c[i + 2]) - 0.1
    return _df(o, h, l, c)


class TestHikkake(unittest.TestCase):
    def test_inside_bar_detected(self):
        df = indicators.add_indicators(_hikkake_setup())
        self.assertTrue(bool(df["inside_bar"].iloc[20]))
        self.assertFalse(bool(df["inside_bar"].iloc[19]))

    def test_bull_trap_detected(self):
        df = indicators.add_indicators(_hikkake_setup(bullish=True))
        self.assertTrue(bool(df["bull_trap"].iloc[21]))
        self.assertFalse(bool(df["bear_trap"].iloc[21]))
        # trap level is the inside bar's high (bar 20)
        self.assertAlmostEqual(df["trap_high"].iloc[21], df["h"].iloc[20])

    def test_bear_trap_detected(self):
        df = indicators.add_indicators(_hikkake_setup(bullish=False))
        self.assertTrue(bool(df["bear_trap"].iloc[21]))
        self.assertFalse(bool(df["bull_trap"].iloc[21]))
        self.assertAlmostEqual(df["trap_low"].iloc[21], df["l"].iloc[20])

    def test_bull_confirmation_fires_entry(self):
        sig = signals.add_signals(indicators.add_indicators(_hikkake_setup(True)))
        self.assertTrue(bool(sig["long_entry"].iloc[22]))
        self.assertFalse(bool(sig["short_entry"].iloc[22]))

    def test_bear_confirmation_fires_entry(self):
        sig = signals.add_signals(indicators.add_indicators(_hikkake_setup(False)))
        self.assertTrue(bool(sig["short_entry"].iloc[22]))
        self.assertFalse(bool(sig["long_entry"].iloc[22]))

    def test_trap_bar_own_close_can_confirm(self):
        # trap bar snaps back and closes through the inside range itself
        df = _hikkake_setup(True)
        df.loc[21, "c"] = df.loc[20, "h"] + 0.4
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(bool(sig["long_entry"].iloc[21]))

    def test_unconfirmed_trap_expires(self):
        # no confirmation within 3 bars -> no entry ever
        df = _hikkake_setup(True)
        for j in (22, 23, 24, 25):
            df.loc[j, "c"] = (df.loc[j, "h"] + df.loc[j, "l"]) / 2
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_late_confirmation_ignored(self):
        # confirmation on the 4th bar after the trap (outside the window)
        df = _hikkake_setup(True)
        df.loc[22, "c"] = (df.loc[22, "h"] + df.loc[22, "l"]) / 2
        df.loc[23, "c"] = (df.loc[23, "h"] + df.loc[23, "l"]) / 2
        df.loc[24, "c"] = (df.loc[24, "h"] + df.loc[24, "l"]) / 2
        df.loc[25, "c"] = df.loc[20, "h"] + 1.0
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].iloc[25]))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exits_are_opposite_entries(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("inside_bar", "bull_trap", "bear_trap"):
                self.assertEqual(bool(ind_full[col].iloc[j]),
                                 bool(ind_tr[col].iloc[j]), (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry"):
                self.assertEqual(bool(sig_full[col].iloc[j]),
                                 bool(sig_tr[col].iloc[j]), (col, j))

    def test_one_entry_per_trap(self):
        # confirming closes on 2 consecutive bars -> only the first fires
        df = _hikkake_setup(True)
        df.loc[23, "c"] = df.loc[20, "h"] + 0.3
        df.loc[23, "h"] = df.loc[23, "c"] + 0.2
        sig = signals.add_signals(indicators.add_indicators(df))
        entries = sig.index[sig["long_entry"]]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], 22)

    def test_short_series_no_crash(self):
        sig = signals.add_signals(
            indicators.add_indicators(_df([1, 2], [2, 3], [0.5, 1.5], [1.5, 2.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.hikkake as mod

        self.assertEqual(mod.SPEC.slug, "hikkake")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertEqual(risk.RISK.max_hold_bars, 20)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
