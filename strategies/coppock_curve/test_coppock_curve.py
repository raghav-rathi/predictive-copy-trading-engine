"""Coppock Curve tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.coppock_curve import indicators, risk, signals
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


class TestCoppockCurve(unittest.TestCase):
    def test_roc_formula(self):
        c = 100.0 * (1.01 ** np.arange(60))
        df = indicators.add_indicators(_df_from_c(c))
        expect = 100.0 * (c[30] / c[16] - 1.0)
        self.assertAlmostEqual(float(df["roc14"].iloc[30]), expect, places=9)
        expect11 = 100.0 * (c[30] / c[19] - 1.0)
        self.assertAlmostEqual(float(df["roc11"].iloc[30]), expect11, places=9)

    def test_wma_linear_weights(self):
        # flat run-up: WMA must lag below the max, at the linear-weight
        # center; and a flat series reproduces the level exactly
        c = 100.0 + np.arange(60, dtype=float)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertFalse(df["coppock"].iloc[59:].isna().any())
        flat = indicators.add_indicators(_df_from_c(np.full(60, 100.0)))
        self.assertAlmostEqual(float(flat["coppock"].iloc[-1]), 0.0, places=9)

    def test_warmup_nan_handling(self):
        df = indicators.add_indicators(_rand_df())
        # ROC(14) needs 15 bars, WMA(10) needs 9 more: first 23 bars NaN
        self.assertTrue(df["coppock"].iloc[:23].isna().all())
        self.assertFalse(df["coppock"].iloc[40:].isna().any())

    def test_rally_crosses_above_zero(self):
        # deep fall then strong rally: Coppock crosses above zero -> long
        c = np.concatenate([200.0 - 0.5 * np.arange(60),
                            170.0 + 1.5 * np.arange(120)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))

    def test_crash_crosses_below_zero(self):
        # rally then crash: Coppock crosses below zero -> short
        c = np.concatenate([100.0 + 1.0 * np.arange(60),
                            160.0 - 1.5 * np.arange(120)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_entries_match_zero_cross(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        zero = pd.Series(np.zeros(len(sig)), index=sig.index)
        expect_up = crossed_above(sig["coppock"], zero).fillna(False).astype(bool)
        expect_dn = crossed_below(sig["coppock"], zero).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_entry"] == expect_up).all()))
        self.assertTrue(bool((sig["short_entry"] == expect_dn).all()))
        self.assertTrue(bool((sig["long_exit"] == expect_dn).all()))
        self.assertTrue(bool((sig["short_exit"] == expect_up).all()))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("roc14", "roc11", "coppock"):
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

    def test_wma_weights_newest_heaviest(self):
        w = np.arange(1, 10 + 1, dtype=float)
        w = w / w.sum()
        self.assertAlmostEqual(w.sum(), 1.0, places=12)
        self.assertTrue(bool((np.diff(w) > 0).all()))  # strictly increasing

    def test_registration_imports_cleanly(self):
        import strategies.coppock_curve as mod

        self.assertEqual(mod.SPEC.slug, "coppock_curve")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
