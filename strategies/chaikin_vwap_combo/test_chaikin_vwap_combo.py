"""Chaikin Money Flow + session VWAP tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chaikin_vwap_combo import indicators, risk, signals


def _df_from_c(c, spread=0.2, vol=100.0):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, vol)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


class TestChaikinVwapCombo(unittest.TestCase):
    def test_mfm_bounds_and_formula(self):
        # close at high -> +1; close at low -> -1; close at midpoint -> 0
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(3) * 3_600_000).astype("int64"),
            "o": [10.0, 10.0, 10.0],
            "h": [12.0, 12.0, 12.0],
            "l": [8.0, 8.0, 8.0],
            "c": [12.0, 8.0, 10.0],
            "v": [100.0, 100.0, 100.0],
        })
        out = indicators.add_indicators(df)
        self.assertAlmostEqual(out["mfm"].iloc[0], 1.0, places=9)
        self.assertAlmostEqual(out["mfm"].iloc[1], -1.0, places=9)
        self.assertAlmostEqual(out["mfm"].iloc[2], 0.0, places=9)

    def test_mfm_zero_on_zero_range_bar(self):
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(25) * 3_600_000).astype("int64"),
            "o": np.full(25, 100.0),
            "h": np.full(25, 100.0),
            "l": np.full(25, 100.0),
            "c": np.full(25, 100.0),
            "v": np.full(25, 100.0),
        })
        out = indicators.add_indicators(df)
        self.assertTrue(bool((out["mfm"] == 0.0).all()))
        self.assertTrue(bool((out["cmf"].iloc[20:] == 0.0).all()))

    def test_cmf_positive_when_closes_near_highs(self):
        # every bar closes at its high -> CMF(20) = +1
        n = 60
        c = 100.0 + np.arange(n, dtype=float)
        o = np.concatenate([[c[0]], c[:-1]])
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": c, "l": c - 1.0, "c": c, "v": np.full(n, 100.0),
        })
        out = indicators.add_indicators(df)
        self.assertTrue(bool((out["cmf"].iloc[20:] > 0.9).all()))

    def test_cmf_negative_when_closes_near_lows(self):
        n = 60
        c = 100.0 - np.arange(n, dtype=float)
        o = np.concatenate([[c[0]], c[:-1]])
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": c + 1.0, "l": c, "c": c, "v": np.full(n, 100.0),
        })
        out = indicators.add_indicators(df)
        self.assertTrue(bool((out["cmf"].iloc[20:] < -0.9).all()))

    def test_vwap_day_resets_each_utc_day(self):
        # two UTC days of flat price: VWAP equals the flat price each day
        n = 48
        t0 = 1_700_000_000_000  # 2023-11-14 22:13:20 UTC; use exact midnight anchor below
        # anchor to a UTC midnight: 2023-11-15 00:00 UTC = 1700006400000
        t = (1_700_006_400_000 + np.arange(n) * 3_600_000).astype("int64")
        c = np.concatenate([np.full(24, 100.0), np.full(24, 200.0)])
        df = pd.DataFrame({
            "t": t, "o": c, "h": c + 0.1, "l": c - 0.1, "c": c, "v": np.full(n, 10.0),
        })
        out = indicators.add_indicators(df)
        self.assertTrue(bool(np.allclose(out["vwap_day"].iloc[:24], 100.0)))
        self.assertTrue(bool(np.allclose(out["vwap_day"].iloc[24:], 200.0)))

    def test_distribution_then_accumulation_fires_long(self):
        # closes near lows (CMF < 0, price below VWAP) then near highs
        n = 200
        c = np.concatenate([100.0 - 0.2 * np.arange(100), 80.0 + 0.3 * np.arange(100)])
        o = np.concatenate([[c[0]], c[:-1]])
        # first half closes at low, second half closes at high
        h = np.where(np.arange(n) < 100, c + 1.0, c + 0.1)
        l = np.where(np.arange(n) < 100, c - 0.1, c - 1.0)
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0),
        })
        sig = signals.add_signals(indicators.add_indicators(df))
        longs = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(longs) > 0)
        self.assertTrue(all(b >= 100 for b in longs))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_accumulation_then_distribution_fires_short(self):
        n = 200
        c = np.concatenate([100.0 + 0.2 * np.arange(100), 120.0 - 0.3 * np.arange(100)])
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.where(np.arange(n) < 100, c + 0.1, c + 1.0)
        l = np.where(np.arange(n) < 100, c - 1.0, c - 0.1)
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0),
        })
        sig = signals.add_signals(indicators.add_indicators(df))
        shorts = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(shorts) > 0)
        self.assertTrue(all(b >= 100 for b in shorts))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("mfm", "mfv", "cmf", "vwap_day", "atr"):
            self.assertFalse(sig[col].iloc[30:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any() or sig["short_entry"].any()))

    def test_cmf_window_param_changes_curve(self):
        df20 = indicators.add_indicators(_rand_df(), cmf_window=20)
        df10 = indicators.add_indicators(_rand_df(), cmf_window=10)
        self.assertFalse(bool(np.allclose(
            df20["cmf"].iloc[20:], df10["cmf"].iloc[20:], equal_nan=True
        )))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            for col in ("mfm", "mfv", "cmf", "vwap_day", "atr"):
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
        import strategies.chaikin_vwap_combo as mod

        self.assertEqual(mod.SPEC.slug, "chaikin_vwap_combo")
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
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
