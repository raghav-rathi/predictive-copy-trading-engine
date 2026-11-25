"""Coppock Curve tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.coppock_curve_bull import indicators, risk, signals


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


def _rand_df(n=1500, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _trough_df():
    # long steady linear decline, then steady linear recovery: the
    # Coppock curve must turn up from below zero after the trough.
    # Linear (not exponential) moves keep the ROC monotone inside
    # each leg, so no spurious turns fire mid-leg.
    down = 100.0 - 0.05 * np.arange(900)
    up = down[-1] + 0.05 * np.arange(600)
    return _df_from_c(np.concatenate([down, up]))


class TestCoppockCurveBull(unittest.TestCase):
    def test_roc_formula(self):
        # flat-then-step: ROC(336) at bar 336+ should equal the step %
        c = np.concatenate([np.full(400, 100.0), np.full(400, 110.0)])
        df = indicators.add_indicators(_df_from_c(c))
        # at bar 736, price 110 vs 336 bars earlier (bar 400) price 110 -> 0%
        self.assertAlmostEqual(df["roc14"].iloc[736], 0.0, places=6)
        # at bar 735, price 110 vs bar 399 price 100 -> +10%
        self.assertAlmostEqual(df["roc14"].iloc[735], 10.0, places=6)
        # at bar 400, price 110 vs bar 64 price 100 -> also +10%
        self.assertAlmostEqual(df["roc14"].iloc[400], 10.0, places=6)

    def test_wma_front_weighted(self):
        # hand-check the WMA on a tiny window: weights newest-first
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        got = indicators._wma(s, 3)
        # window [3,4,5] weights [3,2,1] -> (3*5 + 2*4 + 1*3)/6 = 26/6
        self.assertAlmostEqual(got.iloc[4], 26.0 / 6.0, places=9)
        # window [2,3,4] weights [3,2,1] -> (3*4 + 2*3 + 1*2)/6 = 20/6
        self.assertAlmostEqual(got.iloc[3], 20.0 / 6.0, places=9)
        self.assertTrue(pd.isna(got.iloc[1]))

    def test_coppock_negative_in_decline_positive_in_rally(self):
        df = indicators.add_indicators(_trough_df())
        valid = df.dropna(subset=["coppock"])
        # deep in the decline the curve is well below zero
        self.assertTrue(bool((valid["coppock"].iloc[100:300] < 0).all()))
        # late in the recovery the curve is above zero
        self.assertTrue(bool((valid["coppock"].iloc[-100:] > 0).all()))

    def test_trough_fires_long_below_zero(self):
        sig = signals.add_signals(indicators.add_indicators(_trough_df()))
        longs = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(longs) > 0)
        # entries only while the curve is below zero
        self.assertTrue(bool((sig.loc[longs, "coppock"] < 0).all()))
        # entries happen after the trough (bar 900), not in the decline
        self.assertTrue(all(b >= 900 for b in longs))

    def test_peak_fires_short_above_zero(self):
        # mirror: slow rally, then a steeper rally, then decline — the
        # ROC (and so the curve) rises through the steep leg and falls
        # in the decline, giving a local peak above zero
        up = np.concatenate([
            100.0 + 0.02 * np.arange(450),
            109.0 + 0.08 * np.arange(450),
        ])
        dn = up[-1] - 0.05 * np.arange(600)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(np.concatenate([up, dn]))))
        shorts = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(shorts) > 0)
        self.assertTrue(bool((sig.loc[shorts, "coppock"] > 0).all()))
        # in the late rally / early decline region (curve peaks just
        # before the price peak — the WMA lags the ROC)
        self.assertTrue(all(b >= 800 for b in shorts))

    def test_exit_on_zero_cross_against_position(self):
        sig = signals.add_signals(indicators.add_indicators(_trough_df()))
        # after the trough the curve crosses zero upward: long_exit fires there
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(exits) > 0)
        # first exit at/after the zero cross, not during the decline
        self.assertTrue(all(b >= 900 for b in exits))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(2000, seed=5)))
        for col in ("roc14", "roc11", "coppock"):
            self.assertFalse(sig[col].iloc[600:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_wma_window_param_changes_curve(self):
        df240 = indicators.add_indicators(_rand_df(), wma_window=240)
        df120 = indicators.add_indicators(_rand_df(), wma_window=120)
        self.assertFalse(bool(np.allclose(
            df240["coppock"].iloc[600:], df120["coppock"].iloc[600:], equal_nan=True
        )))

    def test_no_lookahead_truncation(self):
        full = _rand_df(1500)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (900, 1400):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            for col in ("roc14", "roc11", "coppock", "turn_up", "turn_down"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.coppock_curve_bull as mod

        self.assertEqual(mod.SPEC.slug, "coppock_curve_bull")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 240)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 600)


if __name__ == "__main__":
    unittest.main()
