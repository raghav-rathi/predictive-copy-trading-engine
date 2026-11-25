"""Ichimoku Kumo breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.ichimoku_kumo_breakout import indicators, risk, signals


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


class TestIchimokuKumoBreakout(unittest.TestCase):
    def test_tenkan_kijun_match_manual_formula(self):
        df = _rand_df()
        ind = indicators.add_indicators(df)
        exp_tk = (df["h"].rolling(9).max() + df["l"].rolling(9).min()) / 2
        exp_kj = (df["h"].rolling(26).max() + df["l"].rolling(26).min()) / 2
        valid = exp_tk.notna()
        self.assertTrue(bool(np.allclose(ind.loc[valid, "tenkan"], exp_tk[valid])))
        valid = exp_kj.notna()
        self.assertTrue(bool(np.allclose(ind.loc[valid, "kijun"], exp_kj[valid])))

    def test_senkou_spans_are_shifted_26(self):
        df = _rand_df(400)
        ind = indicators.add_indicators(df)
        # senkou_a at bar j = (tenkan + kijun)/2 at bar j-26
        j = 200
        self.assertAlmostEqual(
            ind["senkou_a"].iloc[j],
            (ind["tenkan"].iloc[j - 26] + ind["kijun"].iloc[j - 26]) / 2,
        )
        exp_sb = (df["h"].rolling(52).max() + df["l"].rolling(52).min()) / 2
        self.assertAlmostEqual(ind["senkou_b"].iloc[j], exp_sb.iloc[j - 26])

    def test_cloud_top_bottom_are_span_extremes(self):
        ind = indicators.add_indicators(_rand_df(400))
        valid = ind["senkou_a"].notna() & ind["senkou_b"].notna()
        self.assertTrue(
            bool(np.allclose(
                ind.loc[valid, "cloud_top"],
                np.maximum(ind.loc[valid, "senkou_a"], ind.loc[valid, "senkou_b"]),
            ))
        )
        self.assertTrue(
            bool(np.allclose(
                ind.loc[valid, "cloud_bottom"],
                np.minimum(ind.loc[valid, "senkou_a"], ind.loc[valid, "senkou_b"]),
            ))
        )
        self.assertTrue(bool((ind.loc[valid, "cloud_top"] >= ind.loc[valid, "cloud_bottom"]).all()))

    def test_chikou_never_copied(self):
        ind = indicators.add_indicators(_rand_df())
        self.assertNotIn("chikou", ind.columns)

    def test_fall_then_rise_fires_long(self):
        # V-shape: a long fall puts price below the cloud with
        # tenkan < kijun; on the rise tenkan crosses above kijun
        # first, then price breaks above the cloud top
        c = np.concatenate([400.0 - 2.0 * np.arange(150), 100.0 + 2.0 * np.arange(200)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 150 for b in entries))
        for b in entries:
            self.assertGreater(sig["tenkan"].iloc[b], sig["kijun"].iloc[b])

    def test_rise_then_fall_fires_short(self):
        c = np.concatenate([100.0 + 2.0 * np.arange(150), 400.0 - 2.0 * np.arange(200)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 150 for b in entries))
        for b in entries:
            self.assertLess(sig["tenkan"].iloc[b], sig["kijun"].iloc[b])

    def test_exits_are_level_conditions_on_cloud_edges(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        valid = sig["cloud_top"].notna()
        self.assertTrue(bool((sig.loc[valid, "long_exit"] == (sig.loc[valid, "c"] < sig.loc[valid, "cloud_top"])).all()))
        self.assertTrue(bool((sig.loc[valid, "short_exit"] == (sig.loc[valid, "c"] > sig.loc[valid, "cloud_bottom"])).all()))

    def test_entries_require_tenkan_kijun_agreement(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool((sig["long_entry"] & (sig["tenkan"] <= sig["kijun"])).any()))
        self.assertFalse(bool((sig["short_entry"] & (sig["tenkan"] >= sig["kijun"])).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("tenkan", "kijun", "senkou_a", "senkou_b", "cloud_top", "cloud_bottom"):
            self.assertFalse(sig[col].iloc[120:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("tenkan", "kijun", "senkou_a", "senkou_b", "cloud_top", "cloud_bottom"):
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
        self.assertNotIn("chikou", sig.columns)

    def test_registration_imports_cleanly(self):
        import strategies.ichimoku_kumo_breakout as mod

        self.assertEqual(mod.SPEC.slug, "ichimoku_kumo_breakout")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
