"""Detrended Price Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.detrended_price_osc import indicators, risk, signals


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


class TestDpo(unittest.TestCase):
    def test_dpo_formula_close_minus_displaced_sma(self):
        df = indicators.add_indicators(_rand_df(400))
        sma20 = df["c"].rolling(20, min_periods=20).mean()
        expect = df["c"] - sma20.shift(11)
        self.assertTrue(bool(np.allclose(df["dpo"].iloc[40:], expect.iloc[40:], atol=1e-9, equal_nan=True)))

    def test_dpo_positive_in_uptrend_negative_in_downtrend(self):
        up = indicators.add_indicators(_df_from_c(100.0 + 1.0 * np.arange(200)))
        self.assertTrue(bool((up["dpo"].iloc[60:] > 0).all()))
        down = indicators.add_indicators(_df_from_c(300.0 - 1.0 * np.arange(200)))
        self.assertTrue(bool((down["dpo"].iloc[60:] < 0).all()))

    def test_dpo_zero_on_flat_series(self):
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertTrue(bool(np.allclose(df["dpo"].iloc[40:], 0.0, atol=1e-9)))

    def test_dpo_nan_until_sma_plus_shift(self):
        df = indicators.add_indicators(_rand_df(100))
        # SMA(20) valid from bar 19, shifted 11 -> DPO valid from bar 30
        self.assertTrue(df["dpo"].iloc[:30].isna().all())
        self.assertFalse(df["dpo"].iloc[30:].isna().any())

    def test_uptrend_fires_long_not_short(self):
        c = np.concatenate([np.full(100, 100.0), 100.0 + 1.0 * np.arange(200)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].iloc[40:].any()))
        self.assertFalse(bool(sig["short_entry"].iloc[40:].any()))

    def test_downtrend_fires_short_not_long(self):
        c = np.concatenate([np.full(100, 400.0), 400.0 - 1.0 * np.arange(200)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["short_entry"].iloc[40:].any()))
        self.assertFalse(bool(sig["long_entry"].iloc[40:].any()))

    def test_random_walk_fires_both_directions(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(sig["dpo"].iloc[60:].isna().any())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_exits_are_opposite_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_period_param_changes_displacement(self):
        d10 = indicators.add_indicators(_rand_df(200), period=10)
        d20 = indicators.add_indicators(_rand_df(200), period=20)
        # period 10 -> shift 6, valid from bar 15; period 20 -> shift 11, valid from bar 30
        self.assertFalse(d10["dpo"].iloc[15:30].isna().any())
        self.assertTrue(d20["dpo"].iloc[15:30].isna().all())

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            av, bv = ind_full["dpo"].iloc[j], ind_tr["dpo"].iloc[j]
            self.assertTrue((pd.isna(av) and pd.isna(bv)) or av == bv, j)
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.detrended_price_osc as mod

        self.assertEqual(mod.SPEC.slug, "detrended_price_osc")
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
        self.assertEqual(risk.WARMUP, 35)


if __name__ == "__main__":
    unittest.main()
