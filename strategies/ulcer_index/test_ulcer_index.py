"""Ulcer Index regime-gate tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ulcer_index import indicators, risk, signals
from strategies import base as B


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _flat(n):
    return np.full(n, 100.0)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("ulcer", "donchian_high_20", "donchian_low_20",
                    "donchian_low_10", "atr"):
            self.assertIn(col, ind.columns)

    def test_ulcer_formula_vs_hand_computation(self):
        # Hand-computed UI: closes [100 x10, 100, 99, 98, 97], n=14.
        # At the last bar the trailing 14-bar window is exactly those
        # closes; peak=100, pctdd = [0]*10 + [0,-1,-2,-3];
        # UI = sqrt((0+1+4+9)/14) = 1.0.
        # (the squared-mean needs a full 14 valid pctdd bars, so the
        # series is padded to 31 bars; the trailing window is unchanged)
        c = [100.0] * 27 + [100.0, 99.0, 98.0, 97.0]
        df = _frame_from_close(c)
        got = indicators.ulcer(df["c"], 14).iloc[-1]
        self.assertAlmostEqual(got, 1.0, places=9)

    def test_ulcer_series_matches_reference(self):
        df = _frame()
        n = 14
        c = df["c"]
        peak = c.rolling(n, min_periods=n).max()
        pctdd = 100.0 * (c - peak) / peak
        expect = np.sqrt((pctdd ** 2).rolling(n, min_periods=n).mean())
        got = indicators.ulcer(c, n)
        pd.testing.assert_series_equal(got, expect, check_names=False)

    def test_ulcer_zero_on_flat_series(self):
        # Constant close: percent drawdown is 0 everywhere -> UI == 0.
        got = indicators.ulcer(_frame_from_close(_flat(200))["c"], 14).dropna()
        self.assertTrue((got.abs() < 1e-9).all(),
                        f"expected UI==0 on flat series, got max {got.abs().max()}")

    def test_ulcer_small_on_monotonically_rising_series(self):
        # Rising series: UI measures only the small intra-window depth
        # (prior closes just below the trailing peak), never a panic read.
        c = 100.0 * np.exp(np.arange(200) * 0.001)  # always rising
        df = _frame_from_close(c)
        got = indicators.ulcer(df["c"], 14).dropna()
        self.assertTrue((got < 2.0).all(),
                        f"expected tiny UI on rising series, got max {got.max()}")

    def test_ulcer_spikes_on_sharp_drop(self):
        c = np.concatenate([_flat(60), np.linspace(100, 60, 14)])  # -40% crash
        df = _frame_from_close(c)
        got = indicators.ulcer(df["c"], 14)
        self.assertTrue(np.nanmax(got) > 10.0, "UI should spike past 10 on a 40% crash")

    def test_ulcer_asymmetry_persistence(self):
        # UI is a downside gauge: a -50% drop makes the index SPIKE
        # (>10) at the moment of the drawdown, while a +30% jump of
        # equal construction leaves nothing lasting — once the trailing
        # window passes the jump, the peak is the new level and UI ~ 0.
        up = np.concatenate([_flat(60), [130.0] * 40])
        dn = np.concatenate([_flat(60), [50.0] * 40])
        got_up = indicators.ulcer(_frame_from_close(up)["c"], 14)
        got_dn = indicators.ulcer(_frame_from_close(dn)["c"], 14)
        self.assertGreater(got_dn.iloc[60], 10.0)   # panic spike at the drop
        self.assertLess(got_up.iloc[-1], 1e-9)       # jump fully absorbed

    def test_donchian_levels(self):
        df = _frame()
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["donchian_high_20"].dropna(),
                                    df["h"].rolling(20, min_periods=20).max().dropna()))
        self.assertTrue(np.allclose(ind["donchian_low_10"].dropna(),
                                    df["l"].rolling(10, min_periods=10).min().dropna()))

    def test_donchian_high_above_close_always(self):
        ind = indicators.add_indicators(_frame())
        valid = ind.dropna()
        self.assertTrue((valid["donchian_high_20"] >= valid["c"] - 1e-9).all())

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_only_no_short_entries_ever(self):
        for seed in (1, 2, 3):
            sig = signals.add_signals(indicators.add_indicators(_frame(seed=seed)))
            self.assertEqual(sig["short_entry"].sum(), 0, f"seed={seed}")
            self.assertEqual(sig["short_exit"].sum(), 0, f"seed={seed}")

    def test_entry_requires_calm_regime(self):
        # Breakout to 130 IMMEDIATELY after a -50% crash: the prior-bar
        # ulcer is far above 5, so the regime gate must veto the entry
        # even though the raw Donchian breakout fires.
        c = np.concatenate([_flat(30), np.linspace(100, 50, 10), [130.0] * 20])
        df = _frame_from_close(c)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        raw_breakout = B.crossed_above(
            ind["c"], ind["donchian_high_20"].shift(1)).fillna(False)
        self.assertTrue(raw_breakout.iloc[40], "the raw breakout must fire at bar 40")
        self.assertGreater(ind["ulcer"].iloc[39], 5.0)
        self.assertEqual(sig["long_entry"].sum(), 0,
                         "crash-regime breakout must be gated out")
        # Same breakout from a calm flat regime: prior-bar ulcer ~ 0,
        # so the entry fires.
        calm_c = np.concatenate([_flat(40), [130.0] * 10])
        calm_sig = signals.add_signals(indicators.add_indicators(_frame_from_close(calm_c)))
        self.assertGreater(calm_sig["long_entry"].sum(), 0,
                           "calm-regime breakout should enter")

    def test_panic_exit_fires(self):
        # Deep crash forces ulcer > 10 -> long_exit on every bar the UI is hot.
        c = np.concatenate([_flat(60), np.linspace(100, 55, 14)])
        sig = signals.add_signals(indicators.add_indicators(_frame_from_close(c)))
        ind = indicators.add_indicators(_frame_from_close(c))
        panic = ind["ulcer"] > 10.0
        self.assertTrue(panic.any(), "expected panic regime in crash series")
        self.assertTrue(sig.loc[panic, "long_exit"].all())

    def test_donchian_breakout_exit_fires(self):
        # Flat top, then a close below the prior 10-bar low -> long_exit.
        c = np.concatenate([_flat(60), [80.0] * 10])
        sig = signals.add_signals(indicators.add_indicators(_frame_from_close(c)))
        self.assertTrue(sig["long_exit"].iloc[60])

    def test_no_lookahead(self):
        df = _frame(n=800, seed=11)
        full = signals.add_signals(indicators.add_indicators(df))
        j = 420
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "long_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.ulcer_index as mod
        from strategies.registry import REGISTRY

        self.assertIn("ulcer_index", REGISTRY)
        self.assertIs(REGISTRY["ulcer_index"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "ulcer_index")
        self.assertEqual(mod.SPEC.name, "Ulcer Index Regime Gate")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
