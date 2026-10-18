"""Raschke 3/10 tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.raschke_3_10 import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _df_from_c(c):
    """Degenerate bars with fixed 0.05 spread so median == close."""
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    return _ohlcv(o, h, l, c)


class TestRaschke310(unittest.TestCase):
    def test_osc_formula_hand_computed(self):
        # median = (h+l)/2; osc = SMA3 - SMA10, signal = SMA16(osc)
        n = 60
        med = np.linspace(100.0, 120.0, n)
        h = med + 1.0
        l = med - 1.0
        o = np.concatenate([[med[0]], med[:-1]])
        df = indicators.add_indicators(_ohlcv(o, h, l, med))
        got = df["osc_3_10"].iloc[-1]
        exp = med[-3:].mean() - med[-10:].mean()
        self.assertAlmostEqual(got, exp, places=9)
        osc = pd.Series(med).rolling(3, min_periods=3).mean() - pd.Series(med).rolling(10, min_periods=10).mean()
        exp_sig = osc.iloc[-16:].mean()
        self.assertAlmostEqual(df["osc_3_10_signal"].iloc[-1], exp_sig, places=9)

    def test_long_entry_needs_cross_up_and_positive_osc(self):
        n = 200
        i = np.arange(n)
        c = 100.0 + 1.5 * np.sin(i / 7.0) + 0.20 * i
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        osc = ind["osc_3_10"].to_numpy()
        s = ind["osc_3_10_signal"].to_numpy()
        for j in idx:
            self.assertGreater(osc[j], s[j])
            self.assertLessEqual(osc[j - 1], s[j - 1])
            self.assertGreater(osc[j], 0.0)

    def test_short_entry_needs_cross_dn_and_negative_osc(self):
        n = 200
        i = np.arange(n)
        c = 100.0 + 1.5 * np.sin(i / 7.0) - 0.20 * i
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        osc = ind["osc_3_10"].to_numpy()
        s = ind["osc_3_10_signal"].to_numpy()
        for j in idx:
            self.assertLess(osc[j], s[j])
            self.assertGreaterEqual(osc[j - 1], s[j - 1])
            self.assertLess(osc[j], 0.0)

    def test_trend_filter_blocks_cross_without_drift(self):
        # cross above the signal with osc <= 0 must not fire a long
        n = 60
        df = indicators.add_indicators(_df_from_c(100.0 + np.zeros(n))).copy()
        osc = np.full(n, -1.0)
        sg = np.full(n, -0.5)
        osc[30] = -0.4  # crosses above signal but stays negative
        df["osc_3_10"] = osc
        df["osc_3_10_signal"] = sg
        sig = signals.add_signals(df)
        self.assertFalse(bool(sig["long_entry"].iloc[30]))

    def test_exit_on_cross_back(self):
        n = 200
        i = np.arange(n)
        c = 100.0 + 3.0 * np.sin(i / 5.0) + 0.02 * i
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        from strategies import base as B
        cross_dn = (B.crossed_below(ind["osc_3_10"], ind["osc_3_10_signal"]).fillna(False))
        self.assertTrue(bool((sig["long_exit"] == cross_dn).all()))
        cross_up = (B.crossed_above(ind["osc_3_10"], ind["osc_3_10_signal"]).fillna(False))
        self.assertTrue(bool((sig["short_exit"] == cross_up).all()))

    def test_no_lookahead_truncation(self):
        n = 250
        i = np.arange(n)
        full = _df_from_c(100.0 + 3.0 * np.sin(i / 5.0) + 0.02 * i)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (150, 220):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            self.assertAlmostEqual(ind_full["osc_3_10"].iloc[j], ind_tr["osc_3_10"].iloc[j], places=12)
            self.assertAlmostEqual(
                ind_full["osc_3_10_signal"].iloc[j], ind_tr["osc_3_10_signal"].iloc[j], places=12
            )
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        n = 200
        i = np.arange(n)
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_c(100.0 + 3.0 * np.sin(i / 5.0)))
        )
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        from strategies import raschke_3_10 as mod
        from strategies.registry import REGISTRY
        self.assertIn("raschke_3_10", REGISTRY)
        self.assertIs(REGISTRY["raschke_3_10"], mod.SPEC)


if __name__ == "__main__":
    unittest.main()
