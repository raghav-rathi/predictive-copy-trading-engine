"""TEMA trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tema_trend import indicators, risk, signals
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


class TestTemaTrend(unittest.TestCase):
    def test_tema_hand_computed(self):
        n = 400
        c = 100.0 + 0.3 * np.arange(n) + np.sin(np.arange(n) / 9.0)
        df = indicators.add_indicators(_df_from_c(c))
        s = pd.Series(c)
        e1 = B.ema(s, 20)
        e2 = B.ema(e1, 20)
        e3 = B.ema(e2, 20)
        exp = 3 * e1 - 3 * e2 + e3
        got = df["tema_fast"]
        mask = exp.notna()
        self.assertTrue(np.allclose(got[mask], exp[mask], rtol=1e-9))
        self.assertEqual(int(got.isna().sum()), int(exp.isna().sum()))

    def test_tema_slow_and_sma_hand_computed(self):
        n = 400
        c = 100.0 + 0.3 * np.arange(n) + np.sin(np.arange(n) / 9.0)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(np.allclose(
            df["tema_slow"].dropna(),
            indicators.tema(pd.Series(c), 50).dropna(), rtol=1e-9))
        self.assertTrue(np.allclose(
            df["sma_regime"].dropna(),
            B.sma(pd.Series(c), 200).dropna(), rtol=1e-9))

    def test_tema_tracks_faster_than_ema(self):
        # step up: TEMA should reach the new level faster than a plain EMA(20)
        n = 400
        c = np.where(np.arange(n) < 200, 100.0, 120.0)
        df = indicators.add_indicators(_df_from_c(c))
        ema20 = B.ema(pd.Series(c), 20)
        mid = df["tema_fast"].iloc[210]
        self.assertGreater(mid, ema20.iloc[210])  # TEMA less lag on the step

    def test_parameters_propagate(self):
        df = indicators.add_indicators(_df_from_c(100.0 + 0.3 * np.arange(400)),
                                       fast=10, slow=30, regime=100)
        s = pd.Series(100.0 + 0.3 * np.arange(400))
        self.assertTrue(np.allclose(df["tema_fast"].dropna(),
                                    indicators.tema(s, 10).dropna(), rtol=1e-9))
        self.assertTrue(np.allclose(df["tema_slow"].dropna(),
                                    indicators.tema(s, 30).dropna(), rtol=1e-9))
        self.assertTrue(np.allclose(df["sma_regime"].dropna(),
                                    B.sma(s, 100).dropna(), rtol=1e-9))

    def test_cross_up_above_sma200_fires_long(self):
        # long basing below SMA200 then a sharp rally: cross-up with c > SMA200
        n = 700
        i = np.arange(n)
        c = np.where(i < 400, 100.0 + 5.0 * np.sin(i / 30.0),
                     100.0 + 5.0 * np.sin(400 / 30.0) + 0.8 * (i - 400))
        df = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(df)
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        for j in idx:
            self.assertLessEqual(df["tema_fast"].iloc[j - 1], df["tema_slow"].iloc[j - 1])
            self.assertGreater(df["tema_fast"].iloc[j], df["tema_slow"].iloc[j])
            self.assertGreater(df["c"].iloc[j], df["sma_regime"].iloc[j])

    def test_regime_filter_blocks_longs_below_sma200(self):
        # a crash: TEMA cross-ups happen while price sits below SMA200 --
        # every such cross must be filtered out of long_entry
        n = 700
        i = np.arange(n)
        c = np.where(i < 400, 200.0 + 5.0 * np.sin(i / 30.0),
                     120.0 + 5.0 * np.sin(i / 30.0))
        df = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(df)
        cross_up = (((df["tema_fast"].shift(1) <= df["tema_slow"].shift(1)) &
                     (df["tema_fast"] > df["tema_slow"])).fillna(False))
        blocked = cross_up & (df["c"] < df["sma_regime"])
        self.assertGreater(int(blocked.sum()), 0)  # the test is meaningful
        self.assertFalse(bool((sig["long_entry"] & blocked).any()))
        # and no long_entry may ever fire below the SMA200 filter
        self.assertFalse(bool((sig["long_entry"] & (df["c"] < df["sma_regime"])).any()))

    def test_signal_logic_exact_formulas(self):
        n = 500
        i = np.arange(n)
        c = 100.0 + 0.3 * i + np.sin(i / 9.0)
        df = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(df)
        fast, slow, regime = df["tema_fast"], df["tema_slow"], df["sma_regime"]
        cross_up = ((fast.shift(1) <= slow.shift(1)) & (fast > slow)).fillna(False)
        cross_dn = ((fast.shift(1) >= slow.shift(1)) & (fast < slow)).fillna(False)
        self.assertTrue(bool((sig["long_entry"] == (cross_up & (df["c"] > regime)).fillna(False)).all()))
        self.assertTrue(bool((sig["short_entry"] == (cross_dn & (df["c"] < regime)).fillna(False)).all()))
        self.assertTrue(bool((sig["long_exit"] == cross_dn).all()))
        self.assertTrue(bool((sig["short_exit"] == cross_up).all()))

    def test_no_lookahead_truncation(self):
        n = 600
        i = np.arange(n)
        c = 100.0 + 0.3 * i + np.sin(i / 9.0)
        full = _df_from_c(c)
        ind_full = indicators.add_indicators(full)
        for j in (400, 550):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("tema_fast", "tema_slow", "sma_regime"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        n = 500
        i = np.arange(n)
        c = 100.0 + 0.3 * i + np.sin(i / 9.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.tema_trend as mod

        self.assertEqual(mod.SPEC.slug, "tema_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertIn("tema", mod.SPEC.source_url)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 260)


if __name__ == "__main__":
    unittest.main()
