"""TRIX momentum-turn tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.trix import indicators, risk, signals
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
    """Slow sine swings: TRIX crosses its signal repeatedly in both signs."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, cycles * 2 * np.pi, n)
    c = 100 + 25 * np.sin(x) + rng.normal(0, 0.4, n)
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
        for col in ("trix", "trix_signal", "ema3", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_trix_is_triple_ema_pct_change(self):
        c = self.df["c"]
        ema3 = B.ema(B.ema(B.ema(c, 14), 14), 14)
        expect = (100 * (ema3 - ema3.shift(1)) / ema3.shift(1)).dropna()
        got = self.ind["trix"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_signal_is_ema_of_trix(self):
        expect = B.ema(self.ind["trix"], 9).dropna()
        got = self.ind["trix_signal"].dropna()
        self.assertEqual(len(got), len(expect))
        self.assertTrue(np.allclose(got, expect, atol=1e-9))

    def test_trix_magnitude_sane(self):
        # TRIX is a percent change of a smooth line: small values.
        got = self.ind["trix"].dropna()
        self.assertTrue((got.abs() < 10).all())

    def test_warmup_nans(self):
        # Triple EMA(14) needs ~3*(14-1)+1 = 40 bars for ema3; signal line
        # adds ~8 more, all well inside WARMUP=80.
        self.assertTrue(self.ind["trix"].iloc[:40].isna().all())
        self.assertFalse(self.ind["trix_signal"].iloc[60:].isna().any())

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

    def test_territory_filter(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        ind = indicators.add_indicators(_frame())
        longs = sig["long_entry"]
        self.assertTrue(((~ind.loc[longs, "trix"].isna())
                         & (ind.loc[longs, "trix"] < 0)).all())
        shorts = sig["short_entry"]
        self.assertTrue(((~ind.loc[shorts, "trix"].isna())
                         & (ind.loc[shorts, "trix"] > 0)).all())

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        tx, sg = ind["trix"], ind["trix_signal"]
        pd.testing.assert_series_equal(
            sig["long_exit"], B.crossed_below(tx, sg).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], B.crossed_above(tx, sg).fillna(False).astype(bool),
            check_names=False)

    def test_crosses_fire_on_swing_frame(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_no_lookahead(self):
        df = _swing_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 350
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        import strategies.trix as mod
        from strategies.registry import REGISTRY

        self.assertIn("trix", REGISTRY)
        self.assertIs(REGISTRY["trix"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "trix")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
