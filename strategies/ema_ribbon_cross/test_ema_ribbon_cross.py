"""EMA ribbon expansion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ema_ribbon_cross import indicators, risk, signals


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


class TestEmaRibbonCross(unittest.TestCase):
    def test_ema_columns_monotone_in_uptrend(self):
        c = 100.0 + 0.5 * np.arange(300)
        df = indicators.add_indicators(_df_from_c(c))
        tail = df.iloc[200:]
        self.assertTrue(bool((tail["ema8"] > tail["ema13"]).all()))
        self.assertTrue(bool((tail["ema13"] > tail["ema21"]).all()))
        self.assertTrue(bool((tail["ema21"] > tail["ema34"]).all()))
        self.assertTrue(bool((tail["ema34"] > tail["ema55"]).all()))
        self.assertTrue(bool(tail["aligned_bull"].all()))

    def test_aligned_bear_in_downtrend(self):
        c = 400.0 - 0.5 * np.arange(300)
        df = indicators.add_indicators(_df_from_c(c))
        tail = df.iloc[200:]
        self.assertTrue(bool(tail["aligned_bear"].all()))
        self.assertFalse(bool(tail["aligned_bull"].any()))

    def test_ribbon_width_sign_matches_trend(self):
        up = indicators.add_indicators(_df_from_c(100.0 + 0.5 * np.arange(300)))
        dn = indicators.add_indicators(_df_from_c(400.0 - 0.5 * np.arange(300)))
        self.assertTrue(bool((up["ribbon_width"].iloc[200:] > 0).all()))
        self.assertTrue(bool((dn["ribbon_width"].iloc[200:] < 0).all()))

    def test_compression_true_on_flat_series(self):
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        # flat: ribbon width ~0, so |width| sits at its 20-bar minimum
        self.assertTrue(bool(df["compression"].iloc[100:].any()))
        self.assertTrue(bool(df["comp_recent"].iloc[100:].any()))

    def test_flat_then_rise_fires_long(self):
        c = np.concatenate([np.full(120, 100.0), 100.0 + 0.5 * np.arange(200)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 120 for b in entries))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_flat_then_fall_fires_short(self):
        c = np.concatenate([np.full(120, 100.0), 100.0 - 0.5 * np.arange(200)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 120 for b in entries))

    def test_exit_when_fast_ema_breaks_alignment(self):
        # rise then sharp fall: long_exit (ema8 < ema13) must fire after the turn
        c = np.concatenate(
            [np.full(120, 100.0), 100.0 + 0.5 * np.arange(150), 175.0 - 1.0 * np.arange(150)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(exits) > 0)
        self.assertTrue(all(b >= 270 for b in exits))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("ema8", "ema13", "ema21", "ema34", "ema55", "ribbon_width"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_compression_window_param_changes_flag(self):
        df10 = indicators.add_indicators(_rand_df(), compression_window=10)
        df40 = indicators.add_indicators(_rand_df(), compression_window=40)
        # different windows must not produce identical compression flags
        self.assertFalse(bool((df10["compression"] == df40["compression"]).all()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            for col in ("ema8", "ema55", "ribbon_width", "compression", "comp_recent",
                        "aligned_bull", "aligned_bear"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.ema_ribbon_cross as mod

        self.assertEqual(mod.SPEC.slug, "ema_ribbon_cross")
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
