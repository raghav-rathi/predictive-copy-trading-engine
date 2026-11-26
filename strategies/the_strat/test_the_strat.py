"""The Strat tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.the_strat import indicators, risk, signals


def _df_from_ohlc(o, h, l, c):
    o = np.asarray(o, float)
    h = np.asarray(h, float)
    l = np.asarray(l, float)
    c = np.asarray(c, float)
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df_from_ohlc(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _force_ftfc(df, daily=1, weekly=1):
    df = df.copy()
    df["ftfc_daily"] = daily
    df["ftfc_weekly"] = weekly
    return df


class TestTheStrat(unittest.TestCase):
    def test_classification_inside(self):
        # bar 1: lower high, higher low than bar 0 -> 1
        df = indicators.add_indicators(_df_from_ohlc(
            [100, 100], [100, 99], [90, 91], [95, 95]))
        self.assertEqual(int(df["strat_class"].iloc[1]), 1)

    def test_classification_2u_2d_3(self):
        df = indicators.add_indicators(_df_from_ohlc(
            [100, 100, 100, 100],
            [100, 102, 100, 103],   # bar1 2U, bar2 2D, bar3 3
            [90, 91, 88, 87],
            [95, 96, 94, 95]))
        self.assertEqual(int(df["strat_class"].iloc[1]), 2)
        self.assertEqual(int(df["strat_class"].iloc[2]), -2)
        self.assertEqual(int(df["strat_class"].iloc[3]), 3)

    def test_equal_high_low_is_inside(self):
        # identical range to the prior bar -> 1, not 2U/2D/3
        df = indicators.add_indicators(_df_from_ohlc(
            [100, 100], [100, 100], [90, 90], [95, 95]))
        self.assertEqual(int(df["strat_class"].iloc[1]), 1)

    def test_212_reversal_long_fires(self):
        # 2D, 1, 2U with FTFC green/green -> long at bar 3
        df = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 100, 99, 101],
            [90, 88, 89, 89.5],
            [95, 94, 95, 100])
        ind = _force_ftfc(indicators.add_indicators(df))
        self.assertEqual(ind["strat_class"].tolist(), [1, -2, 1, 2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [3])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_212_reversal_short_fires(self):
        # 2U, 1, 2D with FTFC red/red -> short at bar 3
        df = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 102, 101, 100],
            [90, 91, 92, 89],
            [95, 96, 95, 92])
        ind = _force_ftfc(indicators.add_indicators(df), daily=-1, weekly=-1)
        self.assertEqual(ind["strat_class"].tolist(), [1, 2, 1, -2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [3])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_312_reversal_fires_both_sides(self):
        # 3, 1, 2U -> long; 3, 1, 2D -> short
        df_long = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 102, 100, 101],
            [90, 88, 89, 90],
            [95, 95, 95, 100])
        ind = _force_ftfc(indicators.add_indicators(df_long))
        self.assertEqual(ind["strat_class"].tolist(), [1, 3, 1, 2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [3])

        df_short = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 102, 100, 99],
            [90, 88, 89, 87],
            [95, 95, 95, 90])
        ind = _force_ftfc(indicators.add_indicators(df_short), daily=-1, weekly=-1)
        self.assertEqual(ind["strat_class"].tolist(), [1, 3, 1, -2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [3])

    def test_22_reversal_fires(self):
        # 2D then 2U -> long at bar 2; 2U then 2D -> short at bar 2
        df_long = _df_from_ohlc(
            [100, 100, 100], [100, 100, 101], [90, 88, 89], [95, 94, 100])
        ind = _force_ftfc(indicators.add_indicators(df_long))
        self.assertEqual(ind["strat_class"].tolist(), [1, -2, 2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [2])

        df_short = _df_from_ohlc(
            [100, 100, 100], [100, 102, 101], [90, 91, 89], [95, 96, 92])
        ind = _force_ftfc(indicators.add_indicators(df_short), daily=-1, weekly=-1)
        self.assertEqual(ind["strat_class"].tolist(), [1, 2, -2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [2])

    def test_212_continuation_fires(self):
        # 2U, 1, 2U -> long; 2D, 1, 2D -> short
        df_long = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 102, 101, 103],
            [90, 91, 92, 92.5],
            [95, 96, 96, 100])
        ind = _force_ftfc(indicators.add_indicators(df_long))
        self.assertEqual(ind["strat_class"].tolist(), [1, 2, 1, 2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [3])

        df_short = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 100, 99, 98],
            [90, 88, 89, 86],
            [95, 94, 94, 90])
        ind = _force_ftfc(indicators.add_indicators(df_short), daily=-1, weekly=-1)
        self.assertEqual(ind["strat_class"].tolist(), [1, -2, 1, -2])
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [3])

    def test_ftfc_blocks_entry(self):
        # the same 2-1-2 long setup, but FTFC red -> no long entry;
        # and with FTFC unknown (0) -> no entry either side.
        df = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 100, 99, 101],
            [90, 88, 89, 89.5],
            [95, 94, 95, 100])
        ind = _force_ftfc(indicators.add_indicators(df), daily=-1, weekly=-1)
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))
        ind = _force_ftfc(indicators.add_indicators(df), daily=0, weekly=0)
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))
        # mixed FTFC (daily green, weekly red) also blocks
        ind = _force_ftfc(indicators.add_indicators(df), daily=1, weekly=-1)
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_ftfc_from_completed_blocks_only(self):
        # steady rise: daily turns +1 at bar 24 (first block done),
        # weekly stays 0 until bar 168.
        c = 100.0 + 0.1 * np.arange(400)
        ind = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((ind["ftfc_daily"].iloc[:24] == 0).all()))
        self.assertEqual(int(ind["ftfc_daily"].iloc[24]), 1)
        self.assertTrue(bool((ind["ftfc_weekly"].iloc[:168] == 0).all()))
        self.assertEqual(int(ind["ftfc_weekly"].iloc[168]), 1)
        # steady fall -> -1 on both
        c = 100.0 - 0.1 * np.arange(400)
        ind = indicators.add_indicators(_df_from_c(c))
        self.assertEqual(int(ind["ftfc_daily"].iloc[24]), -1)
        self.assertEqual(int(ind["ftfc_weekly"].iloc[168]), -1)

    def test_exit_is_opposite_setup(self):
        # a short setup printing is a long exit (and vice versa),
        # even when FTFC blocks the opposite entry.
        df = _df_from_ohlc(
            [100, 100, 100, 100],
            [100, 102, 101, 100],
            [90, 91, 92, 89],
            [95, 96, 95, 92])
        ind = _force_ftfc(indicators.add_indicators(df), daily=1, weekly=1)
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [3])
        self.assertFalse(bool(sig["short_entry"].any()))  # FTFC blocks entry

    def test_random_walk_signals_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(2000, seed=5)))
        for col in ("strat_class", "ftfc_daily", "ftfc_weekly", "atr14"):
            self.assertFalse(sig[col].iloc[200:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))
        # over 2000 bars both sides fire at least once
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("strat_class", "ftfc_daily", "ftfc_weekly", "atr14"):
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
        import strategies.the_strat as mod

        self.assertEqual(mod.SPEC.slug, "the_strat")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 200)


if __name__ == "__main__":
    unittest.main()
