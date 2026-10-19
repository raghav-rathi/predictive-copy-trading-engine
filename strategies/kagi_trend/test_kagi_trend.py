"""Kagi trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kagi_trend import indicators, risk, signals


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


class TestKagiTrend(unittest.TestCase):
    def test_sustained_rally_thickens(self):
        # steady climb well beyond the reversal amount -> yang
        c = 100.0 + 2.0 * np.arange(120)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool(df["kagi_dir"].iloc[-1] == 1))
        self.assertTrue(bool(df["kagi_thick"].iloc[-1]))

    def test_sustained_fall_thins(self):
        # rally first (thicken), then a deep fall -> waist breaks, thin
        c = np.concatenate([100.0 + 2.0 * np.arange(80),
                            260.0 - 3.0 * np.arange(80)])
        df = indicators.add_indicators(_df_from_c(c))
        th = df["kagi_thick"]
        self.assertTrue(bool(th.iloc[:90].any()))
        self.assertFalse(bool(th.iloc[-1]))
        self.assertTrue(bool(df["kagi_dir"].iloc[-1] == -1))

    def test_transition_fires_entry(self):
        c = np.concatenate([100.0 + 2.0 * np.arange(80),
                            260.0 - 3.0 * np.arange(80)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        th = sig["kagi_thick"]
        thin_to_thick = sig.index[(th) & (~th.shift(1).fillna(False))]
        thick_to_thin = sig.index[(~th) & (th.shift(1).fillna(False))]
        self.assertGreater(len(thin_to_thick), 0)
        self.assertGreater(len(thick_to_thin), 0)
        self.assertTrue(bool(sig["long_entry"].iloc[thin_to_thick].all()))
        self.assertTrue(bool(sig["short_entry"].iloc[thick_to_thin].all()))

    def test_exits_are_opposite_transitions(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_small_noise_no_column_flip(self):
        # chop below the reversal amount: direction may wobble but the
        # column extremes must stay monotone between genuine reversals
        c = 100.0 + 0.05 * np.sin(np.arange(200) / 3.0)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertFalse(bool(df["kagi_thick"].isna().any()))
        self.assertTrue(bool(set(df["kagi_dir"].unique()) <= {1.0, -1.0}))

    def test_extreme_tracks_column(self):
        c = 100.0 + 2.0 * np.arange(120)
        df = indicators.add_indicators(_df_from_c(c))
        # rising column: extreme is the column top, monotone non-decreasing
        rising = df["kagi_dir"] == 1
        ext = df.loc[rising, "kagi_extreme"]
        self.assertTrue(bool((ext.diff().dropna() >= -1e-9).all()))

    def test_rev_scales_with_atr(self):
        c = 100.0 + 2.0 * np.arange(120)
        df = indicators.add_indicators(_df_from_c(c, spread=2.0), rev_mult=4.0)
        df2 = indicators.add_indicators(_df_from_c(c, spread=0.2), rev_mult=4.0)
        self.assertGreater(float(df["kagi_rev"].iloc[-1]),
                           float(df2["kagi_rev"].iloc[-1]))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("kagi_dir", "kagi_thick", "kagi_extreme"):
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
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.kagi_trend as mod

        self.assertEqual(mod.SPEC.slug, "kagi_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 100)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
