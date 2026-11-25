"""KAMA cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kama_cross import indicators, risk, signals


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


class TestKamaCross(unittest.TestCase):
    def test_kama_seeded_at_first_close(self):
        df = indicators.add_indicators(_rand_df())
        self.assertEqual(df["kama_fast"].iloc[0], df["c"].iloc[0])
        self.assertEqual(df["kama_slow"].iloc[0], df["c"].iloc[0])

    def test_flat_series_kama_equals_close(self):
        # flat: ER = 0, SC = slow constant, KAMA seeded at close never moves
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertTrue(bool(np.allclose(df["kama_fast"].iloc[1:], 100.0)))
        self.assertTrue(bool(np.allclose(df["kama_slow"].iloc[1:], 100.0)))

    def test_kama_stays_within_close_range(self):
        # KAMA_t is a convex combo of KAMA_{t-1} and C_t (SC in (0, 1)),
        # so it can never leave the range of closes seen so far
        df = indicators.add_indicators(_rand_df(800, seed=5))
        for col in ("kama_fast", "kama_slow"):
            running_min = df["c"].expanding().min()
            running_max = df["c"].expanding().max()
            self.assertTrue(bool((df[col] >= running_min - 1e-9).all()))
            self.assertTrue(bool((df[col] <= running_max + 1e-9).all()))

    def test_kama_tracks_linear_uptrend_below_close(self):
        c = 100.0 + 0.5 * np.arange(200)
        df = indicators.add_indicators(_df_from_c(c))
        tail = df.iloc[60:]
        self.assertTrue(bool((np.diff(tail["kama_fast"]) > 0).all()))
        self.assertTrue(bool((np.diff(tail["kama_slow"]) > 0).all()))
        self.assertTrue(bool((tail["kama_fast"] < tail["c"]).all()))
        self.assertTrue(bool((tail["kama_slow"] < tail["c"]).all()))

    def test_slow_kama_converges_further_after_a_step(self):
        # step 100 -> 110, then flat: both KAMAs race up while the step
        # is inside their ER window, then stall once ER drops to 0.
        # The slow KAMA's 20-bar window holds the step longer, so it
        # converges (essentially) fully while the fast one stalls short.
        c = np.concatenate([np.full(100, 100.0), np.full(60, 110.0)])
        df = indicators.add_indicators(_df_from_c(c))
        self.assertGreater(float(df["kama_slow"].iloc[130]), float(df["kama_fast"].iloc[130]))
        self.assertAlmostEqual(float(df["kama_slow"].iloc[130]), 110.0, places=2)
        self.assertLess(abs(float(df["kama_fast"].iloc[130]) - 110.0), 0.1)

    def test_er_period_param_changes_kama(self):
        df1 = indicators.add_indicators(_rand_df(), er_fast=5)
        df2 = indicators.add_indicators(_rand_df(), er_fast=10)
        self.assertFalse(bool(np.allclose(df1["kama_fast"], df2["kama_fast"])))
        # the slow KAMA is untouched by the fast ER parameter
        self.assertTrue(bool(np.allclose(df1["kama_slow"], df2["kama_slow"])))

    def test_fast_and_slow_differ_on_noisy_data(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertFalse(bool(np.allclose(df["kama_fast"], df["kama_slow"])))

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_exits_are_opposite_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("kama_fast", "kama_slow", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("kama_fast", "kama_slow", "atr14"):
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
        import strategies.kama_cross as mod

        self.assertEqual(mod.SPEC.slug, "kama_cross")
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
