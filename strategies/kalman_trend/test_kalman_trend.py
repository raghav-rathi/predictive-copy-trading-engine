"""Kalman filter trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kalman_trend import indicators, risk, signals


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


class TestKalmanTrend(unittest.TestCase):
    def test_constant_price_kf_converges(self):
        c = np.full(200, 100.0)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertFalse(bool(df["kf"].isna().any()))
        self.assertAlmostEqual(float(df["kf"].iloc[-1]), 100.0, delta=1e-3)
        self.assertAlmostEqual(float(df["kf_slope"].iloc[-1]), 0.0, delta=1e-3)

    def test_sustained_rally_slope_positive(self):
        # steady climb: the velocity state tracks the drift with
        # essentially zero steady-state lag; slope stays positive
        c = 100.0 + 2.0 * np.arange(200)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((df["kf_slope"].iloc[-100:] > 0).all()))
        self.assertTrue(bool(((df["c"] - df["kf"]).abs().iloc[-100:] < 0.5).all()))

    def test_sustained_fall_slope_negative(self):
        c = 300.0 - 2.0 * np.arange(200)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((df["kf_slope"].iloc[-100:] < 0).all()))
        self.assertTrue(bool(((df["c"] - df["kf"]).abs().iloc[-100:] < 0.5).all()))

    def test_cross_above_with_positive_slope_fires_long(self):
        # flat, one-bar dip (correctly prints a short signal at the dip),
        # then a rally: cross above on the first rally bar with the filter
        # already rising -> long
        c = np.concatenate(
            [np.full(80, 100.0), [99.0], 99.0 + 2.0 * np.arange(1, 61)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["short_entry"].iloc[80]))
        self.assertTrue(bool(sig["long_entry"].iloc[81]))

    def test_cross_above_nonpositive_slope_no_long(self):
        # hand-built indicator frame: cross above fires, but the filter is
        # still falling -> slope confirmation must block the long entry
        df = _df_from_c([100.0, 100.0, 105.0])
        df["kf"] = [100.0, 101.0, 104.9]
        df["kf_slope"] = [0.0, 1.0, -0.1]
        df["atr"] = 1.0
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_entry"].iloc[-1] == False))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_cross_below_with_negative_slope_fires_short(self):
        # flat, one-bar pop (correctly prints a long signal at the pop),
        # then a steady fall: cross below on the first fall bar with the
        # filter already falling -> short
        c = np.concatenate(
            [np.full(80, 100.0), [101.0], 101.0 - 2.0 * np.arange(1, 61)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].iloc[80]))
        self.assertTrue(bool(sig["short_entry"].iloc[81]))

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_rand_df())
        sig = signals.add_signals(ind)
        from strategies.base import crossed_above, crossed_below

        self.assertTrue(
            bool((sig["long_exit"] == crossed_below(ind["c"], ind["kf"]).fillna(False)).all())
        )
        self.assertTrue(
            bool((sig["short_exit"] == crossed_above(ind["c"], ind["kf"]).fillna(False)).all())
        )

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
            for col in ("kf", "kf_slope"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv))
                    or abs(av - bv) < 1e-9,
                    (col, j),
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_short_series_no_crash(self):
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5]))
        )
        for col in ("kf", "kf_slope"):
            self.assertFalse(sig[col].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_r_kwarg_accepted_and_changes_filter(self):
        base = _df_from_c(100.0 + 0.5 * np.arange(200))
        d1 = indicators.add_indicators(base)
        d2 = indicators.add_indicators(base, r=2.0)
        # larger measurement noise -> filter trusts measurements less ->
        # different (smoother) estimate
        self.assertFalse(bool((d1["kf"] == d2["kf"]).all()))
        sig = signals.add_signals(indicators.add_indicators(base, r=0.5))
        self.assertFalse(bool(sig["long_entry"].isna().any()))

    def test_registration_imports_cleanly(self):
        import strategies.kalman_trend as mod

        self.assertEqual(mod.SPEC.slug, "kalman_trend")
        self.assertEqual(mod.SPEC.name, "Kalman Filter Trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
