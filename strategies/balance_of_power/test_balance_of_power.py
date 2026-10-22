"""Balance of Power tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.balance_of_power import indicators, risk, signals
from strategies import base as B


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


def _flip_frame(n=600, seed=21, cycle=100):
    """Alternate buyer-dominated / seller-dominated regimes so the
    smoothed BOP crosses zero repeatedly in both directions."""
    rng = np.random.default_rng(seed)
    phase = (np.arange(n) // cycle) % 2  # 0 = buyers, 1 = sellers
    body = np.where(phase == 0, 1.0, -1.0)
    c = 100 * np.exp(np.cumsum(body * 0.004))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _raw_check_frame():
    """Hand-computable bars: a perfect buyer bar, a perfect seller bar,
    a midpoint bar, and a degenerate flat bar (h == l)."""
    return pd.DataFrame({
        "t": np.arange(4) * 3_600_000,
        "o": [10.0, 20.0, 15.0, 12.0],
        "h": [15.0, 20.0, 20.0, 12.0],
        "l": [10.0, 15.0, 10.0, 12.0],
        "c": [15.0, 15.0, 15.0, 12.0],
        "v": [1.0, 1.0, 1.0, 1.0],
    })


class TestRawFormula(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("raw_bop", "bop", "atr"):
            self.assertIn(col, ind.columns)

    def test_raw_formula_vs_hand_computation(self):
        df = _raw_check_frame()
        raw = indicators.raw_bop(df["o"], df["h"], df["l"], df["c"])
        # bar0: (15-10)/(15-10) = +1 ; bar1: (15-20)/(20-15) = -1
        # bar2: (15-15)/(20-10) = 0 ; bar3: degenerate, h==l -> 0.0
        self.assertTrue(np.allclose(raw.tolist(), [1.0, -1.0, 0.0, 0.0]))

    def test_degenerate_bar_guard_is_zero(self):
        df = _raw_check_frame()
        raw = indicators.raw_bop(df["o"], df["h"], df["l"], df["c"])
        self.assertEqual(raw.iloc[3], 0.0)
        self.assertFalse(raw.isna().any())

    def test_plus_one_on_buyer_bar(self):
        # open at low, close at high -> raw_bop == +1
        o = pd.Series([10.0, 10.0, 10.0])
        h = pd.Series([15.0, 15.0, 15.0])
        l = pd.Series([10.0, 10.0, 10.0])
        c = pd.Series([15.0, 15.0, 15.0])
        raw = indicators.raw_bop(o, h, l, c)
        self.assertTrue((raw == 1.0).all())

    def test_bounded_in_minus_one_plus_one(self):
        raw = indicators.add_indicators(_frame())["raw_bop"]
        self.assertTrue((raw >= -1.0 - 1e-12).all())
        self.assertTrue((raw <= 1.0 + 1e-12).all())

    def test_bop_is_sma_of_raw(self):
        df = _frame()
        expect = B.sma(indicators.raw_bop(df["o"], df["h"], df["l"],
                                          df["c"]), 14)
        got = indicators.add_indicators(df)["bop"]
        pd.testing.assert_series_equal(got, expect, check_names=False)

    def test_bop_also_bounded(self):
        bop = indicators.add_indicators(_frame())["bop"].dropna()
        self.assertTrue((bop >= -1.0 - 1e-12).all())
        self.assertTrue((bop <= 1.0 + 1e-12).all())

    def test_smoothing_reduces_chop(self):
        df = _frame()
        ind = indicators.add_indicators(df)
        raw = ind["raw_bop"].dropna().to_numpy()
        bop = ind["bop"].dropna().to_numpy()
        raw_flips = int(np.sum(np.diff(np.sign(raw)) != 0))
        bop_flips = int(np.sum(np.diff(np.sign(bop)) != 0))
        self.assertLess(bop_flips, raw_flips)

    def test_warmup_nans(self):
        ind = indicators.add_indicators(_frame())
        # SMA(14) with min_periods=14: first valid value at index 13.
        self.assertTrue(ind["bop"].iloc[:13].isna().all())
        self.assertFalse(ind["bop"].iloc[13:].isna().any())

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_flip_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_zero_cross_detection(self):
        ind = indicators.add_indicators(_flip_frame())
        sig = signals.add_signals(ind)
        zero = pd.Series(np.zeros(len(ind)), index=ind.index)
        pd.testing.assert_series_equal(
            sig["long_entry"],
            B.crossed_above(ind["bop"], zero).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_entry"],
            B.crossed_below(ind["bop"], zero).fillna(False).astype(bool),
            check_names=False)

    def test_entries_fire_on_control_flips(self):
        sig = signals.add_signals(indicators.add_indicators(_flip_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_flip_frame())
        sig = signals.add_signals(ind)
        zero = pd.Series(np.zeros(len(ind)), index=ind.index)
        pd.testing.assert_series_equal(
            sig["long_exit"],
            B.crossed_below(ind["bop"], zero).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"],
            B.crossed_above(ind["bop"], zero).fillna(False).astype(bool),
            check_names=False)

    def test_entries_agree_with_bop_sign_change(self):
        df = _flip_frame()
        sig = signals.add_signals(indicators.add_indicators(df))
        # every long_entry must be a move from <=0 to >0 on the bop line
        ind = indicators.add_indicators(df)
        for j in np.flatnonzero(sig["long_entry"].to_numpy()):
            self.assertLessEqual(ind["bop"].iloc[j - 1], 0.0)
            self.assertGreater(ind["bop"].iloc[j], 0.0)

    def test_no_lookahead(self):
        df = _flip_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 300
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)

    def test_registration(self):
        import strategies.balance_of_power as mod
        from strategies.registry import REGISTRY

        self.assertIn("balance_of_power", REGISTRY)
        self.assertIs(REGISTRY["balance_of_power"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "balance_of_power")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertIn("Livshin", mod.SPEC.source_name)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
