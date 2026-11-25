"""Percentage Price Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.ppo_oscillator import indicators, risk, signals


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


class TestPpoOscillator(unittest.TestCase):
    def test_ppo_formula_matches_manual_ema(self):
        df = _rand_df()
        ind = indicators.add_indicators(df)
        ema12 = B.ema(df["c"], 12)
        ema26 = B.ema(df["c"], 26)
        expected = 100.0 * (ema12 - ema26) / ema26
        valid = expected.notna()
        self.assertTrue(bool(np.allclose(ind.loc[valid, "ppo"], expected[valid])))

    def test_signal_is_ema_of_ppo_and_hist_is_difference(self):
        ind = indicators.add_indicators(_rand_df())
        expected_sig = B.ema(ind["ppo"], 9)
        valid = expected_sig.notna()
        self.assertTrue(bool(np.allclose(ind.loc[valid, "ppo_signal"], expected_sig[valid])))
        valid2 = ind["ppo"].notna() & ind["ppo_signal"].notna()
        self.assertTrue(
            bool(np.allclose(ind.loc[valid2, "ppo_hist"],
                             ind.loc[valid2, "ppo"] - ind.loc[valid2, "ppo_signal"]))
        )

    def test_ppo_positive_in_uptrend_negative_in_downtrend(self):
        c = np.concatenate([100.0 + 2.0 * np.arange(150), 400.0 - 2.0 * np.arange(150)])
        ind = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((ind["ppo"].iloc[60:140] > 0).all()))
        self.assertTrue(bool((ind["ppo"].iloc[220:290] < 0).all()))

    def test_ppo_zero_when_emas_equal(self):
        # flat series: EMA(12) == EMA(26) == price, so PPO is 0 after spin-up
        ind = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertTrue(bool(np.allclose(ind["ppo"].iloc[60:], 0.0, atol=1e-9)))

    def test_rise_dip_rise_fires_long_with_positive_ppo(self):
        # rise, shallow dip (PPO stays positive but crosses below its
        # signal line), rise again: the second leg crosses up while PPO > 0
        c = np.concatenate([
            100.0 + 2.0 * np.arange(120),
            340.0 - 0.5 * np.arange(20),
            330.0 + 2.0 * np.arange(120),
        ])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 140 for b in entries))
        for b in entries:
            self.assertGreater(sig["ppo"].iloc[b], 0.0)

    def test_fall_bounce_fall_fires_short_with_negative_ppo(self):
        c = np.concatenate([
            400.0 - 2.0 * np.arange(120),
            160.0 + 0.5 * np.arange(20),
            170.0 - 2.0 * np.arange(120),
        ])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 140 for b in entries))
        for b in entries:
            self.assertLess(sig["ppo"].iloc[b], 0.0)

    def test_entries_require_correct_ppo_sign(self):
        # a signal-line cross up while PPO < 0 must NOT fire a long
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool((sig["long_entry"] & (sig["ppo"] <= 0)).any()))
        self.assertFalse(bool((sig["short_entry"] & (sig["ppo"] >= 0)).any()))

    def test_exits_are_opposite_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        cross_up = B.crossed_above(sig["ppo"], sig["ppo_signal"]).fillna(False)
        cross_dn = B.crossed_below(sig["ppo"], sig["ppo_signal"]).fillna(False)
        self.assertTrue(bool((sig["long_exit"] == cross_dn.astype(bool)).all()))
        self.assertTrue(bool((sig["short_exit"] == cross_up.astype(bool)).all()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("ppo", "ppo_signal", "ppo_hist"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("ppo", "ppo_signal", "ppo_hist"):
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
        import strategies.ppo_oscillator as mod

        self.assertEqual(mod.SPEC.slug, "ppo_oscillator")
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
