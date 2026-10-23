"""SMI Ergodic oscillator crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.smi_ergodic import indicators, risk, signals
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


def _independent_ema(s, n):
    """Independent EMA loop matching pandas ewm(adjust=False) semantics:
    recursion starts at the first non-NaN value (acc = that value),
    min_periods=n counts non-NaN observations."""
    s = np.asarray(s, dtype=float)
    a = 2.0 / (n + 1)
    y = np.full_like(s, np.nan)
    idx = np.flatnonzero(~np.isnan(s))
    acc = s[idx[0]]
    for k, t in enumerate(idx):
        if k > 0:
            acc = (1 - a) * acc + a * s[t]
        if k >= n - 1:
            y[t] = acc
    return pd.Series(y, index=getattr(s, "index", None))


def _crash_then_bounce():
    # 300 flat, -40% crash over 30 bars, bounce to 120 over 40, flat.
    # smi pins near -100 through the crash, then hooks up from deep
    # oversold -> forces a zone-gated long_entry.
    return np.concatenate(
        [_flat(300), np.linspace(100, 60, 30), np.linspace(60, 120, 40), _flat(50)]
    )


def _rally_then_fade():
    # mirror: rally then fade back down -> zone-gated short_entry.
    return np.concatenate(
        [_flat(300), np.linspace(100, 140, 30), np.linspace(140, 80, 40), _flat(50)]
    )


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("smi", "smi_signal", "atr"):
            self.assertIn(col, ind.columns)

    def test_smi_formula_vs_independent_double_ema(self):
        # Hand-check the double-smoothed ergodic ratio against an
        # independent loop implementation of EMA (no shared code path
        # with indicators.py beyond the pandas ewm it reimplements).
        df = _frame()
        m = df["c"].diff()
        e1 = _independent_ema(m, 5)
        num = _independent_ema(e1, 20)
        a1 = _independent_ema(m.abs(), 5)
        den = _independent_ema(a1, 20)
        expect = (100.0 * num / den.where(den != 0.0)).mask(den == 0.0, 0.0)
        got = indicators.smi_ergodic(df["c"].diff())
        pd.testing.assert_series_equal(got, expect, check_names=False)

    def test_smi_bounded_within_100(self):
        # |ema(m)| <= ema(|m|) by the triangle inequality, so the ratio
        # is mathematically bounded by +/-100 (modulo float epsilon).
        for seed in (1, 2, 3, 42):
            smi = indicators.smi_ergodic(_frame(n=1000, seed=seed)["c"].diff())
            valid = smi.dropna()
            self.assertTrue((valid.abs() <= 100.0 + 1e-6).all(),
                            f"seed={seed}: smi out of bounds, max {valid.abs().max()}")

    def test_zero_division_guard_flat_series(self):
        # Flat series: momentum is exactly 0, denominator is 0 ->
        # guard yields 0, not NaN or inf, after the warmup band.
        got = indicators.smi_ergodic(_frame_from_close(_flat(300))["c"].diff())
        self.assertFalse(np.isinf(got.dropna()).any())
        self.assertTrue((got.dropna() == 0.0).all(),
                        "flat-series smi must be exactly 0 after warmup")

    def test_smi_sign_follows_momentum(self):
        # Steady rise -> smi positive; steady fall -> smi negative.
        up = 100.0 * np.exp(np.arange(300) * 0.002)
        dn = 100.0 * np.exp(-np.arange(300) * 0.002)
        smi_up = indicators.smi_ergodic(_frame_from_close(up)["c"].diff()).dropna()
        smi_dn = indicators.smi_ergodic(_frame_from_close(dn)["c"].diff()).dropna()
        self.assertTrue((smi_up > 90.0).all(), "rising series should pin smi near +100")
        self.assertTrue((smi_dn < -90.0).all(), "falling series should pin smi near -100")

    def test_signal_is_ema_of_smi(self):
        df = _frame()
        ind = indicators.add_indicators(df)
        expect = _independent_ema(ind["smi"], 5)
        pd.testing.assert_series_equal(ind["smi_signal"], expect, check_names=False)

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)

    def test_warmup_nan_band(self):
        # m = c.diff() has a leading NaN; inner ema(5) is first valid at
        # index 5, outer ema(20) at index 24. The first 24 bars must be
        # NaN, and no NaN may remain after bar 120.
        ind = indicators.add_indicators(_frame(n=500))
        self.assertTrue(ind["smi"].iloc[:24].isna().all())
        self.assertFalse(ind["smi"].iloc[24:].isna().any())
        self.assertFalse(ind["smi_signal"].iloc[120:].isna().any())


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_requires_oversold_hook(self):
        # Crash pins smi near -100, then the bounce hooks it back above
        # the signal line: at least one long_entry, and every entry's
        # prior-bar smi must be at/below -40 (the zone gate holds).
        sig = signals.add_signals(
            indicators.add_indicators(_frame_from_close(_crash_then_bounce())))
        entries = sig["long_entry"]
        self.assertGreater(entries.sum(), 0, "oversold hook must produce a long entry")
        prior_smi = sig["smi"].shift(1)[entries]
        self.assertTrue((prior_smi <= -40.0).all(),
                        f"every long entry needs prior-bar smi <= -40, got {prior_smi.values}")

    def test_short_entry_requires_overbought_hook(self):
        sig = signals.add_signals(
            indicators.add_indicators(_frame_from_close(_rally_then_fade())))
        entries = sig["short_entry"]
        self.assertGreater(entries.sum(), 0, "overbought hook must produce a short entry")
        prior_smi = sig["smi"].shift(1)[entries]
        self.assertTrue((prior_smi >= 40.0).all(),
                        f"every short entry needs prior-bar smi >= 40, got {prior_smi.values}")

    def test_zone_gate_vetoes_midband_cross(self):
        # Alternating-sign steps keep the double-smoothed momentum near
        # zero while |m| stays positive, so the scale-invariant smi
        # hovers in the mid-band: smi crosses its signal repeatedly but
        # never reaches +/-40, so NO zone-gated entries may fire even
        # though raw crosses happen.
        steps = np.tile([0.5, -0.5], 400)
        c = 100.0 + np.cumsum(steps)
        ind = indicators.add_indicators(_frame_from_close(c))
        sig = signals.add_signals(ind)
        self.assertLess(ind["smi"].dropna().abs().max(), 40.0,
                        "alternating-step series must stay inside the zones")
        raw_up = B.crossed_above(ind["smi"], ind["smi_signal"]).fillna(False)
        raw_dn = B.crossed_below(ind["smi"], ind["smi_signal"]).fillna(False)
        self.assertTrue((raw_up | raw_dn).any(),
                        "the veto test is vacuous unless raw crosses occur")
        self.assertEqual(sig["long_entry"].sum(), 0, "mid-band crosses must not enter long")
        self.assertEqual(sig["short_entry"].sum(), 0, "mid-band crosses must not enter short")

    def test_exits_are_opposite_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        smi, sl = sig["smi"], sig["smi_signal"]
        expect_long_exit = B.crossed_below(smi, sl).fillna(False).astype(bool)
        expect_short_exit = B.crossed_above(smi, sl).fillna(False).astype(bool)
        pd.testing.assert_series_equal(sig["long_exit"], expect_long_exit, check_names=False)
        pd.testing.assert_series_equal(sig["short_exit"], expect_short_exit, check_names=False)

    def test_exit_fires_after_entry(self):
        # In the crash-then-bounce series the long hook eventually
        # mean-reverts and smi crosses back below its signal.
        sig = signals.add_signals(
            indicators.add_indicators(_frame_from_close(_crash_then_bounce())))
        first_entry = sig["long_entry"].idxmax()
        self.assertTrue(sig["long_exit"].iloc[first_entry:].any(),
                        "a long_exit cross should follow the entry")

    def test_no_lookahead(self):
        df = _frame(n=800, seed=11)
        full = signals.add_signals(indicators.add_indicators(df))
        j = 420
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))

    def test_no_nan_after_warmup(self):
        sig = signals.add_signals(indicators.add_indicators(_frame(n=500)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].iloc[120:].isna().any(), col)


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 120)

    def test_registration(self):
        import strategies.smi_ergodic as mod
        from strategies.registry import REGISTRY

        self.assertIn("smi_ergodic", REGISTRY)
        self.assertIs(REGISTRY["smi_ergodic"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "smi_ergodic")
        self.assertEqual(mod.SPEC.name, "SMI Ergodic Oscillator Crossover")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
