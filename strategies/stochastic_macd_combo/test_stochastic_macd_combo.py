"""Stochastic + MACD dual-confirmation tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.stochastic_macd_combo import indicators, risk, signals


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


class TestStochasticMacdCombo(unittest.TestCase):
    def test_stoch_k_bounded_0_to_100_after_warmup(self):
        ind = indicators.add_indicators(_rand_df(800, seed=5))
        k = ind["stoch_k"].iloc[20:]
        self.assertFalse(k.isna().any())
        self.assertTrue(bool(((k >= 0) & (k <= 100)).all()))

    def test_stoch_k_100_at_range_high_0_at_range_low(self):
        # monotonically rising closes with zero spread: close is the
        # 14-bar high AND the 14-bar low is an earlier close -> %K = 100
        c_up = 100.0 + 2.0 * np.arange(100)
        ind_up = indicators.add_indicators(_df_from_c(c_up, spread=0.0))
        self.assertTrue(bool(np.allclose(ind_up["stoch_k"].iloc[20:], 100.0)))
        # monotonically falling closes with zero spread -> %K = 0
        c_dn = 300.0 - 2.0 * np.arange(100)
        ind_dn = indicators.add_indicators(_df_from_c(c_dn, spread=0.0))
        self.assertTrue(bool(np.allclose(ind_dn["stoch_k"].iloc[20:], 0.0)))

    def test_stoch_d_is_sma_of_k_and_hist_matches_macd(self):
        ind = indicators.add_indicators(_rand_df())
        expected_d = B.sma(ind["stoch_k"], 3)
        valid = expected_d.notna()
        self.assertTrue(bool(np.allclose(ind.loc[valid, "stoch_d"], expected_d[valid])))
        m = B.macd(ind["c"])
        valid_m = m["macd_hist"].notna()
        self.assertTrue(bool(np.allclose(ind.loc[valid_m, "macd_hist"], m.loc[valid_m, "macd_hist"])))

    def test_flat_series_k_is_neutral_50(self):
        ind = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        # high == low on every bar, so the range is 0 and %K falls back to 50
        self.assertTrue(bool((ind["stoch_k"].iloc[20:] == 50.0).all()))

    def test_entries_require_macd_agreement(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool((sig["long_entry"] & (sig["macd_hist"] <= 0)).any()))
        self.assertFalse(bool((sig["short_entry"] & (sig["macd_hist"] >= 0)).any()))

    def test_entries_require_extreme_k(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool((sig["long_entry"] & (sig["stoch_k"] >= 30)).any()))
        self.assertFalse(bool((sig["short_entry"] & (sig["stoch_k"] <= 70)).any()))

    def test_signals_match_manual_logic(self):
        ind = indicators.add_indicators(_rand_df(400, seed=7))
        sig = signals.add_signals(ind)
        cross_up = B.crossed_above(ind["stoch_k"], ind["stoch_d"]).fillna(False)
        cross_dn = B.crossed_below(ind["stoch_k"], ind["stoch_d"]).fillna(False)
        exp_long = (cross_up & (ind["stoch_k"] < 30) & (ind["macd_hist"] > 0)).fillna(False)
        exp_short = (cross_dn & (ind["stoch_k"] > 70) & (ind["macd_hist"] < 0)).fillna(False)
        exp_long_exit = (cross_dn | (ind["macd_hist"] < 0)).fillna(False)
        exp_short_exit = (cross_up | (ind["macd_hist"] > 0)).fillna(False)
        self.assertTrue(bool((sig["long_entry"] == exp_long.astype(bool)).all()))
        self.assertTrue(bool((sig["short_entry"] == exp_short.astype(bool)).all()))
        self.assertTrue(bool((sig["long_exit"] == exp_long_exit.astype(bool)).all()))
        self.assertTrue(bool((sig["short_exit"] == exp_short_exit.astype(bool)).all()))

    def test_down_then_up_fires_long(self):
        # sharp fall then sharp rise: oversold %K cross up with MACD turning positive
        c = np.concatenate([400.0 - 2.0 * np.arange(150), 100.0 + 2.0 * np.arange(150)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))

    def test_up_then_down_fires_short(self):
        c = np.concatenate([100.0 + 2.0 * np.arange(150), 400.0 - 2.0 * np.arange(150)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("stoch_k", "stoch_d", "macd", "macd_signal", "macd_hist"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("stoch_k", "stoch_d", "macd", "macd_signal", "macd_hist"):
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
        import strategies.stochastic_macd_combo as mod

        self.assertEqual(mod.SPEC.slug, "stochastic_macd_combo")
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
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
