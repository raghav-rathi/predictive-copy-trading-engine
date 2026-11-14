"""Kase DevStop tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kase_devstop import indicators, risk, signals
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


def _swing_frame(n=700, seed=21, cycles=3):
    """Slow sine swings: DevStop flips repeatedly in both directions."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, cycles * 2 * np.pi, n)
    c = 100 + 25 * np.sin(x) + rng.normal(0, 0.4, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _trend_frame(n=300, seed=3, slope=0.3, noise=0.1):
    """Clean uptrend then clean downtrend: exactly one flip each way."""
    rng = np.random.default_rng(seed)
    up = 100 + slope * np.arange(n // 2) + rng.normal(0, noise, n // 2)
    dn = up[-1] - slope * np.arange(1, n - n // 2 + 1) + rng.normal(0, noise, n - n // 2)
    c = np.concatenate([up, dn])
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
        for col in ("dtr", "devstop_band", "devstop_long",
                    "devstop_short", "devstop_dir"):
            self.assertIn(col, self.ind.columns)

    def test_dtr_formula(self):
        expect = (pd.concat([self.df["h"], self.df["h"].shift(1)], axis=1).max(axis=1)
                  - pd.concat([self.df["l"], self.df["l"].shift(1)], axis=1).min(axis=1))
        pd.testing.assert_series_equal(
            self.ind["dtr"], expect, check_names=False)

    def test_band_formula_sample_std(self):
        dtr = self.ind["dtr"]
        expect = (dtr.rolling(30, min_periods=30).mean()
                  + dtr.rolling(30, min_periods=30).std(ddof=1))
        got = self.ind["devstop_band"].dropna()
        self.assertEqual(len(got), len(expect.dropna()))
        self.assertTrue(np.allclose(got, expect.dropna(), atol=1e-9))

    def test_band_positive(self):
        self.assertTrue((self.ind["devstop_band"].dropna() > 0).all())

    def test_direction_only_pm1_after_warmup(self):
        d = self.ind["devstop_dir"]
        # DTR[0] is valid (pandas max skips the NaN shift), so the
        # 30-bar band is first valid at index 29.
        self.assertTrue((d.iloc[:29] == 0).all())
        self.assertTrue(set(d.iloc[29:].unique()) <= {1.0, -1.0})

    def test_long_stop_ratchets_up(self):
        # While long, the stop never moves down.
        ind = self.ind
        d = ind["devstop_dir"]
        ls = ind["devstop_long"]
        long_runs = (d == 1) & (d.shift(1) == 1)
        prev = ls.shift(1)
        self.assertTrue((ls[long_runs] >= prev[long_runs] - 1e-9).all())

    def test_short_stop_ratchets_down(self):
        ind = self.ind
        d = ind["devstop_dir"]
        ss = ind["devstop_short"]
        short_runs = (d == -1) & (d.shift(1) == -1)
        prev = ss.shift(1)
        self.assertTrue((ss[short_runs] <= prev[short_runs] + 1e-9).all())

    def test_stop_below_price_when_long(self):
        ind = self.ind.dropna(subset=["devstop_long"])
        long_bars = ind[ind["devstop_dir"] == 1]
        # On every long bar the stop sits below the close (else it
        # would have flipped); same mirrored for shorts.
        self.assertTrue((long_bars["devstop_long"] <= long_bars["c"] + 1e-9).all())
        short_bars = ind.dropna(subset=["devstop_short"])
        short_bars = short_bars[short_bars["devstop_dir"] == -1]
        self.assertTrue((short_bars["devstop_short"] >= short_bars["c"] - 1e-9).all())

    def test_flip_after_clean_reversal(self):
        ind = indicators.add_indicators(_trend_frame())
        d = ind["devstop_dir"]
        # Starts long, flips short somewhere in the down leg, stays short.
        self.assertEqual(d.iloc[30], 1.0)
        self.assertEqual(d.iloc[-1], -1.0)
        flips = ((d == -1) & (d.shift(1) == 1)).sum()
        self.assertEqual(flips, 1)

    def test_warmup_nans(self):
        # Band first valid at index 29 (see DTR note above).
        self.assertTrue(self.ind["devstop_band"].iloc[:29].isna().all())
        self.assertFalse(self.ind["devstop_band"].iloc[30:].isna().any())

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

    def test_entries_are_direction_flips(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        d = ind["devstop_dir"]
        prev = d.shift(1)
        pd.testing.assert_series_equal(
            sig["long_entry"], ((d == 1) & (prev == -1)).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_entry"], ((d == -1) & (prev == 1)).fillna(False).astype(bool),
            check_names=False)

    def test_exits_are_opposite_flips(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        pd.testing.assert_series_equal(
            sig["long_exit"], sig["short_entry"], check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], sig["long_entry"], check_names=False)

    def test_flips_fire_both_ways_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_initial_entry_signal(self):
        # The initial tracking state (long at first valid band bar)
        # must not emit an entry -- only genuine flips trade.
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        first_valid = 29
        self.assertFalse(sig["long_entry"].iloc[: first_valid + 1].any())

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 6.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 300)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.kase_devstop as mod
        from strategies.registry import REGISTRY

        self.assertIn("kase_devstop", REGISTRY)
        self.assertIs(REGISTRY["kase_devstop"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "kase_devstop")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
