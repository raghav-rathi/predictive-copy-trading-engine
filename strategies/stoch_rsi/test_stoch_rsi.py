"""Stochastic RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stoch_rsi import indicators, risk, signals
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


class TestStochRsi(unittest.TestCase):
    def test_bounds(self):
        # stoch %K/%D and raw stay within 0..100 after warmup
        df = indicators.add_indicators(_rand_df())
        for col in ("stoch_raw", "stoch_k", "stoch_d"):
            s = df[col].dropna()
            self.assertTrue(bool(((s >= 0) & (s <= 100)).all()), col)

    def test_flat_series_guards_zero_division(self):
        # dead-flat series: span is 0/0 -> raw pinned to 50, no NaN
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertFalse(df["stoch_raw"].iloc[40:].isna().any())
        self.assertTrue(bool((df["stoch_raw"].iloc[40:] == 50.0).all()))
        self.assertTrue(bool((df["stoch_k"].iloc[60:] == 50.0).all()))

    def test_warmup_nan_head(self):
        # rsi valid from bar 0 (B.rsi fills its own warmup), stoch
        # window needs 14 bars -> raw from 13, k from 15, d from 17
        df = indicators.add_indicators(_rand_df())
        self.assertTrue(df["stoch_raw"].iloc[:13].isna().all())
        self.assertTrue(df["stoch_k"].iloc[:13].isna().all())
        self.assertEqual(int(df["stoch_k"].first_valid_index()), 15)
        self.assertFalse(df["stoch_k"].iloc[60:].isna().any())
        self.assertFalse(df["stoch_d"].iloc[60:].isna().any())

    def test_k_is_sma_of_raw(self):
        # %K = SMA(3) of raw by construction
        df = indicators.add_indicators(_rand_df())
        expect = df["stoch_raw"].rolling(3, min_periods=3).mean()
        got, exp = df["stoch_k"].dropna(), expect.dropna().reindex(df["stoch_k"].dropna().index)
        self.assertTrue(bool(np.allclose(got, exp)))

    def test_deep_dump_then_bounce_fires_long(self):
        # one-directional dump pins RSI at its floor -> raw/k pinned to
        # 0; the V-bounce sends %K back through 20 from below
        c = np.concatenate([100.0 - 0.5 * np.arange(100),
                            50.0 + 2.0 * np.arange(120)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        # the entry fires on the bounce, not during the dump
        self.assertTrue(all(b >= 100 for b in entries))
        self.assertTrue(bool((sig["stoch_k"].iloc[80:100] < 20).all()))

    def test_sharp_rally_then_fade_fires_short(self):
        # one-directional rally pins RSI at its ceiling -> %K pinned to
        # 100; the fade sends %K back through 80 from above
        c = np.concatenate([100.0 + 0.5 * np.arange(100),
                            150.0 - 1.5 * np.arange(120)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        # the entry fires on the fade, not during the rally
        self.assertTrue(all(b >= 100 for b in entries))
        self.assertTrue(bool((sig["stoch_k"].iloc[80:100] > 80).all()))

    def test_exits_on_midline_cross(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        lv50 = pd.Series(50.0, index=sig.index)
        expect_le = crossed_below(sig["stoch_k"], lv50).fillna(False).astype(bool)
        expect_se = crossed_above(sig["stoch_k"], lv50).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_exit"] == expect_le).all()))
        self.assertTrue(bool((sig["short_exit"] == expect_se).all()))

    def test_signals_fire_on_random_walk(self):
        # on a noisy 600-bar walk all four signal columns fire at least once
        sig = signals.add_signals(indicators.add_indicators(_rand_df(600, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
            self.assertTrue(bool(sig[col].any()), col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("rsi", "stoch_raw", "stoch_k", "stoch_d"):
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
        import strategies.stoch_rsi as mod

        self.assertEqual(mod.SPEC.slug, "stoch_rsi")
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
