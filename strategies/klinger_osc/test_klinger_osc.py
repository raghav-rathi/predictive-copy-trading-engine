"""Klinger Volume Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.klinger_osc import indicators, risk, signals
from strategies.base import crossed_above, crossed_below


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


def _frame(n=300, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestKlingerIndicators(unittest.TestCase):
    def test_cm_accumulates_in_persistent_trend(self):
        # steady rise: trend == +1 after bar 0, so cm = cumulative sum of dm
        c = 100.0 + 2.0 * np.arange(60)
        df = indicators.add_indicators(_df_from_c(c))
        dm = df["dm"].to_numpy()
        self.assertAlmostEqual(df["cm"].iloc[0], dm[0], places=12)
        for i in range(1, 60):
            self.assertAlmostEqual(df["cm"].iloc[i], df["cm"].iloc[i - 1] + dm[i], places=10)

    def test_cm_loop_invariant(self):
        # for every bar: persistent trend -> cm[i] = cm[i-1] + dm[i];
        # flipped trend   -> cm[i] = dm[i-1] + dm[i]
        rng = np.random.default_rng(9)
        c = 100.0 + np.cumsum(rng.normal(0, 1.0, 200))
        df = indicators.add_indicators(_df_from_c(c))
        trend = df["trend"].to_numpy()
        dm = df["dm"].to_numpy()
        cm = df["cm"].to_numpy()
        for i in range(1, len(df)):
            expect = (cm[i - 1] + dm[i]) if trend[i] == trend[i - 1] else (dm[i - 1] + dm[i])
            self.assertAlmostEqual(cm[i], expect, places=10, msg=f"bar {i}")
        self.assertAlmostEqual(cm[0], dm[0], places=12)

    def test_vf_zero_when_cm_zero(self):
        # degenerate h == l -> dm == 0 -> cm == 0 -> vf must be 0, not NaN/inf
        n = 100
        c = np.full(n, 100.0)
        df = _df_from_c(c, spread=0.0)
        ind = indicators.add_indicators(df)
        self.assertTrue((ind["cm"] == 0.0).all())
        self.assertTrue(np.isfinite(ind["vf"].to_numpy()).all())
        self.assertTrue((ind["vf"] == 0.0).all())
        # EMA warmup bars are NaN by design (min_periods); the rest is 0
        self.assertTrue(np.isfinite(ind["kvo"].dropna().to_numpy()).all())
        self.assertTrue((ind["kvo"].dropna() == 0.0).all())

    def test_flat_series_kvo_decays_to_zero(self):
        # constant price: volume force tends to a constant, so the
        # EMA(34)-EMA(55) difference must decay toward 0 (min_periods
        # leaves NaN for the first 54 bars)
        df = indicators.add_indicators(_df_from_c(np.full(400, 100.0)))
        kvo = df["kvo"].dropna()
        self.assertGreater(len(kvo), 300)
        self.assertTrue(np.isfinite(kvo).all())
        tail = np.abs(kvo.iloc[-50:])
        self.assertTrue((tail.diff().dropna() < 0).all(),
                        "kvo magnitude should decay monotonically on a flat series")
        self.assertLess(float(np.abs(kvo.iloc[-1])), 10.0)  # peak ~2000: decayed 200x

    def test_kvo_moves_away_on_trend(self):
        # sustained rally: kvo should push above its signal at some point
        c = 100.0 + 2.0 * np.arange(150)
        df = indicators.add_indicators(_df_from_c(c, vol=150.0))
        self.assertTrue(bool((df["kvo"] > df["ksig"]).iloc[60:].any()))
        self.assertTrue(np.isfinite(df["kvo"].dropna()).all())

    def test_columns_shape_and_finiteness(self):
        df = indicators.add_indicators(_frame(300))
        for col in ("tp", "trend", "dm", "cm", "vf", "kvo", "ksig"):
            self.assertIn(col, df.columns, col)
            self.assertEqual(len(df[col]), 300, col)
        self.assertTrue(np.isfinite(df["vf"]).all())
        self.assertTrue(set(df["trend"].unique()) <= {1.0, -1.0})

    def test_short_series_no_crash(self):
        df = indicators.add_indicators(_df_from_c([100.0, 101.0]))
        self.assertEqual(len(df), 2)
        self.assertAlmostEqual(df["cm"].iloc[0], df["dm"].iloc[0])


class TestKlingerSignals(unittest.TestCase):
    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_frame(600)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_entries_match_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_frame(600)))
        expect_up = crossed_above(sig["kvo"], sig["ksig"]).fillna(False).astype(bool)
        expect_dn = crossed_below(sig["kvo"], sig["ksig"]).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_entry"] == expect_up).all()))
        self.assertTrue(bool((sig["short_entry"] == expect_dn).all()))
        self.assertTrue(bool((sig["long_exit"] == expect_dn).all()))
        self.assertTrue(bool((sig["short_exit"] == expect_up).all()))

    def test_trend_turns_fire_both_sides(self):
        # three trend legs: up, down, up -> kvo must cross its signal up and down
        rng = np.random.default_rng(5)
        rets = np.concatenate([
            rng.normal(0.003, 0.01, 400),
            rng.normal(-0.003, 0.01, 400),
            rng.normal(0.003, 0.01, 400),
        ])
        c = 100 * np.exp(np.cumsum(rets))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()), "no long_entry on up legs")
        self.assertTrue(bool(sig["short_entry"].any()), "no short_entry on down leg")

    def test_no_lookahead_truncation(self):
        full = _frame(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("kvo", "ksig", "vf", "cm"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue((pd.isna(av) and pd.isna(bv)) or av == bv, (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)


class TestKlingerRegistration(unittest.TestCase):
    def test_registration_imports_cleanly(self):
        import strategies.klinger_osc as mod

        self.assertEqual(mod.SPEC.slug, "klinger_osc")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
