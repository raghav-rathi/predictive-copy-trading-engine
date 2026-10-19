"""Chande Forecast Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chande_forecast_osc import indicators, risk, signals
from strategies import base as B


def _df_from_c(c):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _hand_forecast(c, n=20):
    """Reference: np.polyfit per trailing window, extrapolated one step."""
    m = len(c)
    out = np.full(m, np.nan)
    x = np.arange(n, dtype=float)
    for i in range(n, m):
        y = c[i - n : i]
        a, b = np.polyfit(x, y, 1)
        out[i] = a * n + b
    return out


class TestChandeForecastOsc(unittest.TestCase):
    def test_tsf_matches_polyfit_extrapolation(self):
        n = 120
        i = np.arange(n)
        c = 100.0 + 0.3 * i + 2.0 * np.sin(i / 7.0)
        df = indicators.add_indicators(_df_from_c(c))
        exp = _hand_forecast(c, 20)
        got = df["tsf_prev"].to_numpy()
        mask = ~np.isnan(exp)
        self.assertTrue(np.allclose(got[mask], exp[mask], rtol=1e-9))
        self.assertTrue(bool(np.isnan(got[:20]).all()))

    def test_fo_formula_hand_computed(self):
        n = 120
        i = np.arange(n)
        c = 100.0 + 0.3 * i + 2.0 * np.sin(i / 7.0)
        df = indicators.add_indicators(_df_from_c(c))
        tsf = _hand_forecast(c, 20)
        exp = (c - tsf) / c * 100.0
        got = df["fo"].to_numpy()
        mask = ~np.isnan(exp)
        self.assertTrue(np.allclose(got[mask], exp[mask], rtol=1e-9))

    def test_signal_is_3bar_sma_of_fo(self):
        n = 120
        i = np.arange(n)
        c = 100.0 + 0.3 * i + 2.0 * np.sin(i / 7.0)
        df = indicators.add_indicators(_df_from_c(c))
        exp = B.sma(df["fo"], 3)
        mask = exp.notna()
        self.assertTrue(np.allclose(df["fo_signal"][mask], exp[mask], rtol=1e-12))

    def test_linear_series_forecast_is_exact(self):
        # perfect linear trend: OLS recovers the line, forecast exact,
        # FO ~ 0
        n = 60
        c = 50.0 + 1.5 * np.arange(n)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(np.allclose(df["tsf_prev"].iloc[20:], c[20:], rtol=1e-9))
        self.assertTrue(
            np.allclose(df["fo"].iloc[22:].fillna(0.0), 0.0, atol=1e-6)
        )

    def test_signal_logic_exact_formulas(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.2 * i + 8.0 * np.sin(i / 15.0)
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        fo, fs = ind["fo"], ind["fo_signal"]
        x_up = B.crossed_above(fo, fs).fillna(False)
        x_dn = B.crossed_below(fo, fs).fillna(False)
        self.assertTrue(
            bool(((sig["long_entry"] == (x_up & (fo > 0))).fillna(False).all()))
        )
        self.assertTrue(
            bool(((sig["short_entry"] == (x_dn & (fo < 0))).fillna(False).all()))
        )
        self.assertTrue(bool((sig["long_exit"] == x_dn.astype(bool)).all()))
        self.assertTrue(bool((sig["short_exit"] == x_up.astype(bool)).all()))

    def _gated_frame(self, n, fo_sign: int):
        """Deterministic indicator frame: FO oscillates around a signal
        line placed so every cross-up happens with FO > 0 (fo_sign=+1)
        or every cross-down with FO < 0 (fo_sign=-1)."""
        i = np.arange(n, dtype=float)
        df = indicators.add_indicators(_df_from_c(100.0 + i))
        df["fo"] = fo_sign * (0.4 * np.sin(i / 5.0))
        df["fo_signal"] = fo_sign * 0.1
        return df

    def test_long_entry_needs_positive_fo(self):
        n = 200
        ind = self._gated_frame(n, fo_sign=+1)
        sig = signals.add_signals(ind)
        x_up = B.crossed_above(ind["fo"], ind["fo_signal"]).fillna(False)
        self.assertGreater(sig["long_entry"].sum(), 0)
        # every long fires exactly on a cross-up with fo > 0
        self.assertTrue(bool(((sig["long_entry"] == x_up).fillna(False)).all()))
        for j in sig.index[sig["long_entry"]]:
            self.assertGreater(float(ind["fo"].iloc[j]), 0.0)
        # same FO shape but negative: no longs, shorts fire instead
        sig_neg = signals.add_signals(self._gated_frame(n, fo_sign=-1))
        self.assertEqual(sig_neg["long_entry"].sum(), 0)
        self.assertGreater(sig_neg["short_entry"].sum(), 0)

    def test_exit_on_cross_back(self):
        # downtrend series: shorts fire, and short_exit matches the
        # cross back above the signal line exactly
        n = 500
        c = np.concatenate([100.0 + 0.8 * np.arange(250),
                            300.0 - 0.8 * np.arange(250)])
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        se = sig.index[sig["short_entry"]]
        self.assertGreater(len(se), 0)
        exp = B.crossed_above(ind["fo"], ind["fo_signal"]).fillna(False).astype(bool)
        self.assertTrue(bool((sig["short_exit"] == exp).all()))
        # an exit fires after the first entry
        self.assertTrue(bool(sig["short_exit"].iloc[se[0] + 1 :].any()))

    def test_no_lookahead_truncation(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.2 * i + 8.0 * np.sin(i / 15.0)
        full = _df_from_c(c)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (120, 290):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("tsf_prev", "fo", "fo_signal"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                )
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.2 * i + 8.0 * np.sin(i / 15.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.chande_forecast_osc as mod

        self.assertEqual(mod.SPEC.slug, "chande_forecast_osc")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )
        self.assertIn("mql5.com", mod.SPEC.source_url)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 40)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
