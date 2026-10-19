"""Murrey Math tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.murray_math import indicators, risk, signals
from strategies import base as B


def _df_from_ohlc(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.full(n, 100.0)}
    )


def _rand_df(n=300, seed=7):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + rng.uniform(0, 0.5, n)
    l = np.minimum(o, c) - rng.uniform(0, 0.5, n)
    return _df_from_ohlc(o, h, l, c)


class TestMurrayMath(unittest.TestCase):
    def test_frame_octave_hand_computed(self):
        df = indicators.add_indicators(_rand_df(300), frame=64)
        hi = df["h"].rolling(64, min_periods=64).max()
        lo = df["l"].rolling(64, min_periods=64).min()
        octv = (hi - lo) / 8.0
        mask = hi.notna()
        self.assertTrue(np.allclose(df["mm_hi"][mask], hi[mask], rtol=1e-9))
        self.assertTrue(np.allclose(df["mm_lo"][mask], lo[mask], rtol=1e-9))
        self.assertTrue(np.allclose(df["mm_octave"][mask], octv[mask], rtol=1e-9))
        self.assertTrue(np.allclose(df["mm_L0"][mask], lo[mask], rtol=1e-9))
        self.assertTrue(np.allclose(df["mm_L8"][mask], hi[mask], rtol=1e-9))
        self.assertTrue(
            np.allclose(df["mm_L4"][mask], lo[mask] + 4 * octv[mask], rtol=1e-9)
        )
        self.assertTrue(df["mm_mid"].equals(df["mm_L4"]))
        # frame not filled at the start
        self.assertTrue(bool(df["mm_hi"].iloc[:63].isna().all()))
        self.assertFalse(bool(df["mm_hi"].iloc[63:].isna().any()))

    def test_touch_columns_exact(self):
        df = indicators.add_indicators(_rand_df(300), frame=64, zone_tol=0.10)
        octv = df["mm_octave"]
        exp_b = (df["l"] <= df["mm_L0"] + 0.10 * octv).fillna(False)
        exp_t = (df["h"] >= df["mm_L8"] - 0.10 * octv).fillna(False)
        exp_zb = (df["l"] <= df["mm_L1"] + 0.10 * octv).fillna(False)
        exp_zt = (df["h"] >= df["mm_L7"] - 0.10 * octv).fillna(False)
        self.assertTrue(bool((df["mm_touch_0_8"].fillna(False) == exp_b).all()))
        self.assertTrue(bool((df["mm_touch_8_8"].fillna(False) == exp_t).all()))
        self.assertTrue(bool((df["mm_touch_bottom"].fillna(False) == exp_zb).all()))
        self.assertTrue(bool((df["mm_touch_top"].fillna(False) == exp_zt).all()))

    def test_long_entry_reversal_logic(self):
        # V shape: crash into the frame low, then reclaim L1 -> long_entry
        n = 200
        fall = 100.0 - 0.5 * np.arange(100)
        rise = 50.0 + 0.5 * np.arange(100)
        c = np.concatenate([fall, rise])
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.1
        l = np.minimum(o, c) - 0.1
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(o, h, l, c)))
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        for j in idx:
            self.assertGreater(sig["c"].iloc[j], sig["mm_L1"].iloc[j])
            self.assertLessEqual(sig["c"].iloc[j - 1], sig["mm_L1"].iloc[j - 1])
            self.assertTrue(bool(sig["mm_touch_bottom"].iloc[j - 2 : j + 1].fillna(False).any()))

    def test_short_entry_reversal_logic(self):
        n = 200
        rise = 50.0 + 0.5 * np.arange(100)
        fall = 100.0 - 0.5 * np.arange(100)
        c = np.concatenate([rise, fall])
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.1
        l = np.minimum(o, c) - 0.1
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(o, h, l, c)))
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        for j in idx:
            self.assertLess(sig["c"].iloc[j], sig["mm_L7"].iloc[j])
            self.assertGreaterEqual(sig["c"].iloc[j - 1], sig["mm_L7"].iloc[j - 1])
            self.assertTrue(bool(sig["mm_touch_top"].iloc[j - 2 : j + 1].fillna(False).any()))

    def test_exit_at_mid_pivot(self):
        # strong V recovery: entry fires, then price reaches 4/8 -> long_exit
        fall = 100.0 - 0.5 * np.arange(100)
        rise = 50.0 + 1.5 * np.arange(100)
        c = np.concatenate([fall, rise])
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.1
        l = np.minimum(o, c) - 0.1
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(o, h, l, c)))
        le = sig.index[sig["long_entry"]]
        self.assertGreater(len(le), 0)
        later = sig["long_exit"].iloc[le[0] :]
        self.assertTrue(bool(later.any()))
        k = le[0] + int(np.argmax(later.to_numpy()))
        self.assertTrue(bool(sig["long_exit"].iloc[k]))

    def test_signal_formulas_exact(self):
        df = indicators.add_indicators(_rand_df(400), frame=32)
        sig = signals.add_signals(df, touch_lookback=3)
        c, L1, L4, L7 = df["c"], df["mm_L1"], df["mm_mid"], df["mm_L7"]
        rb = (df["mm_touch_bottom"].rolling(3, min_periods=1).max() > 0).fillna(False)
        rt = (df["mm_touch_top"].rolling(3, min_periods=1).max() > 0).fillna(False)
        self.assertTrue(bool((sig["long_entry"] == (B.crossed_above(c, L1) & rb).fillna(False).astype(bool)).all()))
        self.assertTrue(bool((sig["short_entry"] == (B.crossed_below(c, L7) & rt).fillna(False).astype(bool)).all()))
        exp_lx = (B.crossed_above(c, L4) | df["mm_touch_top"].fillna(False)).fillna(False).astype(bool)
        exp_sx = (B.crossed_below(c, L4) | df["mm_touch_bottom"].fillna(False)).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_exit"] == exp_lx).all()))
        self.assertTrue(bool((sig["short_exit"] == exp_sx).all()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full, frame=64)
        for j in (150, 250):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1], frame=64)
            for col in ("mm_L0", "mm_L4", "mm_L8", "mm_touch_bottom", "mm_touch_top"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue((pd.isna(av) and pd.isna(bv)) or av == bv, (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(400)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(20)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.murray_math as mod

        self.assertEqual(mod.SPEC.slug, "murray_math")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 80)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 100)


if __name__ == "__main__":
    unittest.main()
