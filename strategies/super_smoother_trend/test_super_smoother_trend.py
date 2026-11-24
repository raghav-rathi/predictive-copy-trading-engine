"""SuperSmoother trend crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.super_smoother_trend import indicators, risk, signals
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


class TestSuperSmootherTrend(unittest.TestCase):
    def test_flat_series_lines_equal_price(self):
        # constant input: the recursion is exact up to float rounding,
        # both filters sit on price (tolerance ~1e-9, not exact ==)
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertFalse(df["ss_fast"].isna().any())
        self.assertFalse(df["ss_slow"].isna().any())
        self.assertTrue(bool(np.allclose(df["ss_fast"], 100.0, atol=1e-9)))
        self.assertTrue(bool(np.allclose(df["ss_slow"], 100.0, atol=1e-9)))

    def test_sustained_rally_fast_above_slow(self):
        # steady ramp: the fast filter lags less, so it rides above slow
        c = 100.0 + 1.0 * np.arange(300)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((df["ss_fast"].iloc[100:] > df["ss_slow"].iloc[100:]).all()))

    def test_sustained_decline_fast_below_slow(self):
        c = 400.0 - 1.0 * np.arange(300)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((df["ss_fast"].iloc[100:] < df["ss_slow"].iloc[100:]).all()))

    def test_step_up_fires_long_after_jump(self):
        # flat, then a step up: fast reacts first and crosses above slow
        # shortly after the jump. (A Butterworth step response rings, so
        # a brief cross back can occur; the settled state is what must
        # hold: fast above slow once both filters have absorbed the step.)
        c = np.concatenate([np.full(100, 100.0), np.full(100, 110.0)])
        df = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_entry"].iloc[100:140].any()))
        self.assertTrue(bool((df["ss_fast"].iloc[-20:] > df["ss_slow"].iloc[-20:]).all()))

    def test_step_down_fires_short_after_drop(self):
        c = np.concatenate([np.full(100, 100.0), np.full(100, 90.0)])
        df = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["short_entry"].iloc[100:140].any()))
        self.assertTrue(bool((df["ss_fast"].iloc[-20:] < df["ss_slow"].iloc[-20:]).all()))

    def test_no_nan_anywhere(self):
        # seeded recursion: no NaN head at all, unlike rolling indicators
        df = indicators.add_indicators(_rand_df(800, seed=3))
        self.assertFalse(df["ss_fast"].isna().any())
        self.assertFalse(df["ss_slow"].isna().any())
        self.assertFalse(df["ss_fast"].iloc[risk.WARMUP:].isna().any())

    def test_period_params_change_lines(self):
        df = _rand_df(400, seed=9)
        a = indicators.add_indicators(df, fast_n=10, slow_n=30)
        b = indicators.add_indicators(df, fast_n=5, slow_n=20)
        self.assertFalse(bool((a["ss_fast"].iloc[100:] == b["ss_fast"].iloc[100:]).all()))
        self.assertFalse(bool((a["ss_slow"].iloc[100:] == b["ss_slow"].iloc[100:]).all()))

    def test_exits_are_opposite_crosses(self):
        df = indicators.add_indicators(_rand_df(600, seed=7))
        sig = signals.add_signals(df)
        cross_up = crossed_above(df["ss_fast"], df["ss_slow"]).fillna(False).astype(bool)
        cross_down = crossed_below(df["ss_fast"], df["ss_slow"]).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_entry"] == cross_up).all()))
        self.assertTrue(bool((sig["short_entry"] == cross_down).all()))
        self.assertTrue(bool((sig["long_exit"] == cross_down).all()))
        self.assertTrue(bool((sig["short_exit"] == cross_up).all()))

    def test_signals_fire_on_random_walk(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertTrue(bool(sig["long_exit"].any()))
        self.assertTrue(bool(sig["short_exit"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("ss_fast", "ss_slow"):
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
        import strategies.super_smoother_trend as mod

        self.assertEqual(mod.SPEC.slug, "super_smoother_trend")
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
