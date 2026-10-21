"""Woodies CCI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.woodies_cci import indicators, risk, signals
from strategies.base import crossed_above, crossed_below


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


class TestWoodiesCci(unittest.TestCase):
    def test_rally_puts_cci14_positive(self):
        # sustained rally: tp far above its mean -> cci14 stays positive
        c = 100.0 + 1.5 * np.arange(200)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertFalse(df["cci14"].iloc[40:].isna().any())
        self.assertTrue(bool((df["cci14"].iloc[40:] > 0).all()))

    def test_flat_series_guards_zero_division(self):
        # dead-flat series: mean deviation is 0 -> CCI pinned to 0, no NaN
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertFalse(df["cci14"].iloc[30:].isna().any())
        self.assertTrue(bool((df["cci14"].iloc[30:] == 0.0).all()))
        self.assertTrue(bool((df["turbo"].iloc[30:] == 0.0).all()))

    def test_warmup_nan_head(self):
        # CCI(14) needs 14 bars for the MA plus 14 for the mean-deviation
        df = indicators.add_indicators(_rand_df())
        self.assertTrue(df["cci14"].iloc[:20].isna().all())
        self.assertFalse(df["cci14"].iloc[60:].isna().any())
        # turbo is the faster line: valid earlier than cci14
        self.assertFalse(df["turbo"].iloc[60:].isna().any())

    def test_sustained_rally_no_long_entry_without_pullback(self):
        # straight-line rally: trend qualifies, but cci14 >> 50 means no
        # pullback setup, so no long_entry should fire
        c = 100.0 + 3.0 * np.arange(200)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_rally_then_shallow_pullback_fires_long(self):
        # strong rally (trend qualifies: cci14 stays > 0 the whole
        # time), then a shallow 6-bar dip: cci14 pulls back into the
        # [0, 50] reject zone while the turbo dips below zero and hooks
        # back up -> long_entry fires on the hook
        c = np.concatenate([
            100.0 + 2.0 * np.arange(150),
            398.0 - 0.6 * np.arange(1, 7),
            394.4 + 2.0 * np.arange(150),
        ])
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((df["cci14"].iloc[145:165] > 0).all()))
        sig = signals.add_signals(df)
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        # the entry fires on the resume, after the dip starts (bar 150)
        self.assertTrue(all(b >= 150 for b in entries))

    def test_exits_on_zero_line_cross(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        zero = pd.Series(0.0, index=sig.index)
        expect_le = crossed_below(sig["cci14"], zero).fillna(False).astype(bool)
        expect_se = crossed_above(sig["cci14"], zero).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_exit"] == expect_le).all()))
        self.assertTrue(bool((sig["short_exit"] == expect_se).all()))

    def test_signals_fire_on_random_walk(self):
        # on a noisy 800-bar walk the pattern entries fire at least once each side
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertTrue(bool(sig["long_exit"].any()))
        self.assertTrue(bool(sig["short_exit"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_trend_bars_param_changes_qualifier(self):
        # a stricter trend_bars fires no more often than a looser one
        df = indicators.add_indicators(_rand_df(600, seed=9))
        strict = signals.add_signals(df, trend_bars=9)
        loose = signals.add_signals(df, trend_bars=4)
        self.assertLessEqual(int(strict["long_entry"].sum()), int(loose["long_entry"].sum()))
        self.assertLessEqual(int(strict["short_entry"].sum()), int(loose["short_entry"].sum()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("tp", "cci14", "turbo"):
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
        import strategies.woodies_cci as mod

        self.assertEqual(mod.SPEC.slug, "woodies_cci")
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
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
