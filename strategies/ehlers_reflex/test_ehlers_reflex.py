"""Reflex Zero-Lag tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_reflex import indicators, risk, signals


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _trend_frame(n=400, seed=3, slope=0.0015, down_first=False):
    """Sustained linear rally then sustained linear selloff (or the
    reverse with down_first=True): Reflex must flip sign at the
    flip point."""
    rng = np.random.default_rng(seed)
    half = n // 2
    if down_first:
        dn = 100 * (1 - slope) ** np.arange(half)
        up = dn[-1] * (1 + slope) ** np.arange(1, n - half + 1)
        c = np.concatenate([dn, up])
    else:
        up = 100 * (1 + slope) ** np.arange(half)
        dn = up[-1] * (1 - slope) ** np.arange(1, n - half + 1)
        c = np.concatenate([up, dn])
    c = c * (1 + rng.normal(0, 0.0005, n))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _chop_frame(n=500, seed=11):
    """Mean-reverting chop: Reflex must stay bounded near zero."""
    rng = np.random.default_rng(seed)
    x = np.sin(np.linspace(0, 30 * np.pi, n)) * 2.0 + rng.normal(0, 0.5, n)
    c = 100 + x
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("reflex", "filt", "sum_", "ms", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_supersmoother_coeffs(self):
        # a1 = exp(-1.414*pi/20); spot-check filter against a direct
        # re-implementation of the recursion.
        x = self.df["c"].to_numpy()
        p = 20
        a1 = np.exp(-1.414 * np.pi / p)
        b1 = 2 * a1 * np.cos(np.deg2rad(1.414 * 180 / p))
        c2, c3 = b1, -a1 * a1
        c1 = 1 - c2 - c3
        expect = np.empty(len(x))
        expect[0] = x[0]
        for i in range(1, len(x)):
            prev2 = expect[i - 2] if i > 1 else x[0]
            expect[i] = c1 * (x[i] + x[i - 1]) / 2 + c2 * expect[i - 1] + c3 * prev2
        self.assertTrue(np.allclose(self.ind["filt"].to_numpy(), expect,
                                    rtol=1e-12, equal_nan=True))

    def test_ms_initialization_and_recursion(self):
        # MS seeds with the first valid Sum^2, then recurses as
        # 0.04*Sum^2 + 0.96*MS_prev.
        s = self.ind["sum_"].to_numpy()
        m = self.ind["ms"].to_numpy()
        first = int(np.argmax(~np.isnan(s)))
        self.assertAlmostEqual(m[first], s[first] ** 2, places=10)
        for i in range(first + 1, first + 20):
            expect = 0.04 * s[i] ** 2 + 0.96 * m[i - 1]
            self.assertAlmostEqual(m[i], expect, places=8)

    def test_reflex_is_sum_over_sqrt_ms(self):
        s = self.ind["sum_"]
        m = self.ind["ms"]
        expect = s / np.sqrt(m).replace(0.0, np.nan)
        got = self.ind["reflex"]
        mask = expect.notna()
        self.assertTrue(np.allclose(got[mask], expect[mask], atol=1e-12))

    def test_no_nan_or_inf_after_warmup(self):
        tail = self.ind.iloc[risk.WARMUP:]
        for col in ("reflex", "filt", "sum_", "ms"):
            self.assertFalse(tail[col].isna().any(), col)
            self.assertTrue(np.isfinite(tail[col].to_numpy()).all(), col)

    def test_reflex_positive_on_sustained_rally(self):
        ind = indicators.add_indicators(_trend_frame())
        rally = ind.iloc[100:180]["reflex"]
        self.assertGreater((rally > 0).mean(), 0.8)

    def test_reflex_negative_on_sustained_selloff(self):
        ind = indicators.add_indicators(_trend_frame())
        sell = ind.iloc[220:380]["reflex"]
        self.assertGreater((sell < 0).mean(), 0.8)

    def test_reflex_bounded_on_chop(self):
        # MS normalization keeps the oscillator bounded-ish when there
        # is no trend: z-score-like, |Reflex| rarely escapes ~3.
        ind = indicators.add_indicators(_chop_frame())
        r = ind.iloc[risk.WARMUP:]["reflex"]
        self.assertLess((r.abs() > 5).mean(), 0.01)

    def test_ms_nonnegative(self):
        m = self.ind["ms"].dropna()
        self.assertTrue((m >= 0).all())

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_zero_cross_entry_logic(self):
        ind = indicators.add_indicators(_trend_frame())
        sig = signals.add_signals(ind)
        rx = ind["reflex"]
        expect_up = ((rx > 0) & (rx.shift(1) <= 0)).fillna(False).astype(bool)
        expect_dn = ((rx < 0) & (rx.shift(1) >= 0)).fillna(False).astype(bool)
        pd.testing.assert_series_equal(sig["long_entry"], expect_up,
                                       check_names=False)
        pd.testing.assert_series_equal(sig["short_entry"], expect_dn,
                                       check_names=False)

    def test_exits_are_opposite_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        pd.testing.assert_series_equal(sig["long_exit"], sig["short_entry"],
                                       check_names=False)
        pd.testing.assert_series_equal(sig["short_exit"], sig["long_entry"],
                                       check_names=False)

    def test_crosses_fire_on_trend_flip(self):
        sig = signals.add_signals(indicators.add_indicators(_trend_frame()))
        # Flip frame: rally -> selloff should produce a short cross.
        self.assertGreater(sig["short_entry"].sum(), 0)
        # Mirror frame: selloff -> rally should produce a long cross.
        sig2 = signals.add_signals(
            indicators.add_indicators(_trend_frame(down_first=True)))
        self.assertGreater(sig2["long_entry"].sum(), 0)

    def test_entries_only_on_actual_cross(self):
        # No cross while Reflex sits on one side of zero: count of
        # entries must equal the count of zero crosses.
        ind = indicators.add_indicators(_trend_frame())
        sig = signals.add_signals(ind)
        rx = ind["reflex"]
        n_up = ((rx > 0) & (rx.shift(1) <= 0)).fillna(False).sum()
        self.assertEqual(int(sig["long_entry"].sum()), int(n_up))

    def test_no_lookahead(self):
        df = _trend_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 250
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.WARMUP, 100)

    def test_registration(self):
        import strategies.ehlers_reflex as mod
        from strategies.registry import REGISTRY

        self.assertIn("ehlers_reflex", REGISTRY)
        self.assertIs(REGISTRY["ehlers_reflex"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "ehlers_reflex")
        self.assertEqual(mod.SPEC.name, "Reflex Zero-Lag")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
