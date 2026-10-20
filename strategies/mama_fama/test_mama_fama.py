"""Ehlers MAMA/FAMA cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mama_fama import indicators, risk, signals


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


class TestMamaFama(unittest.TestCase):
    def test_sustained_rally_mama_above_fama(self):
        # steady climb: the adaptive alpha opens up, MAMA leads FAMA
        c = 100.0 + 2.0 * np.arange(200)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertGreater(float(df["mama"].iloc[-1]), float(df["fama"].iloc[-1]))

    def test_sustained_fall_mama_below_fama(self):
        c = 300.0 - 2.0 * np.arange(200)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertLess(float(df["mama"].iloc[-1]), float(df["fama"].iloc[-1]))

    def test_flat_price_converges_no_nan(self):
        c = np.full(250, 100.0)
        df = indicators.add_indicators(_df_from_c(c))
        for col in ("mama", "fama", "mama_alpha", "mama_period"):
            self.assertFalse(bool(df[col].isna().any()), col)
            self.assertTrue(bool(np.isfinite(df[col].to_numpy()).all()), col)
        # both averages settle at the flat price
        self.assertAlmostEqual(float(df["mama"].iloc[-1]), 100.0, places=6)
        self.assertAlmostEqual(float(df["fama"].iloc[-1]), 100.0, places=6)

    def test_cross_above_fires_long_entry(self):
        # fall then rally: forces a MAMA/FAMA cross above somewhere
        c = np.concatenate([300.0 - 2.0 * np.arange(120),
                            60.0 + 2.0 * np.arange(160)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        cross_up = (sig["mama"] > sig["fama"]) & (
            sig["mama"].shift(1) <= sig["fama"].shift(1))
        self.assertGreater(int(cross_up.sum()), 0)
        expect = (cross_up.fillna(False) & (sig["c"] > sig["mama"]))
        self.assertTrue(bool((sig["long_entry"] == expect).all()))
        self.assertTrue(bool((sig["long_entry"] & expect).any()))

    def test_cross_below_fires_short_entry(self):
        # rally then fall: forces a MAMA/FAMA cross below somewhere
        c = np.concatenate([100.0 + 2.0 * np.arange(120),
                            340.0 - 2.0 * np.arange(160)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        cross_dn = (sig["mama"] < sig["fama"]) & (
            sig["mama"].shift(1) >= sig["fama"].shift(1))
        self.assertGreater(int(cross_dn.sum()), 0)
        expect = (cross_dn.fillna(False) & (sig["c"] < sig["mama"]))
        self.assertTrue(bool((sig["short_entry"] == expect).all()))
        self.assertTrue(bool((sig["short_entry"] & expect).any()))

    def test_exits_are_opposite_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        cross_up = ((sig["mama"] > sig["fama"]) & (
            sig["mama"].shift(1) <= sig["fama"].shift(1))).fillna(False)
        cross_dn = ((sig["mama"] < sig["fama"]) & (
            sig["mama"].shift(1) >= sig["fama"].shift(1))).fillna(False)
        self.assertTrue(bool((sig["long_exit"] == cross_dn).all()))
        self.assertTrue(bool((sig["short_exit"] == cross_up).all()))

    def test_alpha_stays_within_limits(self):
        # choppy sine: period estimator swings, alpha must stay clamped
        c = 100.0 + 5.0 * np.sin(np.arange(300) / 2.0)
        for fl in (0.4, 0.5, 0.6):
            df = indicators.add_indicators(_df_from_c(c), fast_limit=fl)
            a = df["mama_alpha"]
            self.assertTrue(bool(((a >= 0.05 - 1e-12) & (a <= fl + 1e-12)).all()), fl)

    def test_period_stays_within_clamp(self):
        df = indicators.add_indicators(_rand_df(400))
        p = df["mama_period"].iloc[80:]
        self.assertTrue(bool(((p >= 6.0 - 1e-9) & (p <= 50.0 + 1e-9)).all()))
        # seed is the textbook 20-bar starting period
        self.assertEqual(float(df["mama_period"].iloc[0]), 20.0)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("mama", "fama", "mama_alpha", "mama_period"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        self.assertEqual(float(sig["mama"].iloc[0]), 100.0)
        self.assertEqual(float(sig["fama"].iloc[0]), 100.0)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.mama_fama as mod

        self.assertEqual(mod.SPEC.slug, "mama_fama")
        self.assertEqual(mod.SPEC.name, "Ehlers MAMA/FAMA Cross")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
