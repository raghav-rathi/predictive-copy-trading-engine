"""Pretty Good Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pretty_good_osc import indicators, risk, signals


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


def _gap_frame():
    # 60 flat bars, then a sharp gap up (breakout), then a grind back down
    # through the mean (exit territory)
    up = np.full(20, 120.0)
    down = np.linspace(120.0, 98.0, 80)
    c = np.concatenate([np.full(60, 100.0), up, down])
    return _df_from_c(c)


class TestPgoIndicators(unittest.TestCase):
    def test_pgo_formula_matches_definition(self):
        df = indicators.add_indicators(_frame(200))
        from strategies.base import atr as _atr, sma as _sma

        raw = _frame(200)
        atr14 = _atr(raw["h"], raw["l"], raw["c"], 14)
        expect = ((raw["c"] - _sma(raw["c"], 14)) / _sma(atr14, 14)).to_numpy()
        got = df["pgo"].to_numpy()
        # warmup bars: reference is NaN, implementation pins 0.0 — compare
        # only where the reference formula is defined
        mask = np.isfinite(expect)
        self.assertGreater(mask.sum(), 150)
        np.testing.assert_allclose(got[mask], expect[mask], rtol=1e-10,
                                   err_msg="PGO must equal (c-SMA14)/SMA(ATR14,14)")

    def test_flat_series_pgo_zero(self):
        df = indicators.add_indicators(_df_from_c(np.full(120, 100.0)))
        self.assertTrue((np.abs(df["pgo"]) < 1e-8).all())

    def test_gap_up_pushes_pgo_above_trigger(self):
        df = indicators.add_indicators(_gap_frame())
        self.assertGreater(float(df["pgo"].iloc[70]), 3.0)
        # grind back to the mean: pgo must fall back through 0
        self.assertLess(float(df["pgo"].iloc[-1]), 0.0)

    def test_degenerate_flat_bars_no_inf(self):
        n = 100
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({"t": t, "o": np.full(n, 100.0), "h": np.full(n, 100.0),
                           "l": np.full(n, 100.0), "c": np.full(n, 100.0),
                           "v": np.full(n, 50.0)})
        ind = indicators.add_indicators(df)
        self.assertTrue(np.isfinite(ind["pgo"].to_numpy()).all())

    def test_trigger_column_and_param(self):
        df = indicators.add_indicators(_frame(100), trigger=2.5)
        self.assertTrue((df["pgo_trigger"] == 2.5).all())
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].isna().any())

    def test_columns_shape(self):
        df = indicators.add_indicators(_frame(200))
        for col in ("atr14", "atr14_sma", "pgo", "pgo_trigger"):
            self.assertIn(col, df.columns, col)
        self.assertEqual(len(df), 200)


class TestPgoSignals(unittest.TestCase):
    def test_breakout_fires_long_then_exit(self):
        sig = signals.add_signals(indicators.add_indicators(_gap_frame()))
        self.assertTrue(bool(sig["long_entry"].any()), "gap up never crossed +3")
        self.assertTrue(bool(sig["long_exit"].any()), "mean reversion never crossed 0 down")

    def test_flat_series_fires_nothing(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(np.full(200, 100.0))))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(bool(sig[col].any()), col)

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_frame(600)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_exit_meaning_on_crafted_series(self):
        # after the gap up, pgo falls back: long_exit must fire only on
        # cross-down-through-zero bars
        sig = signals.add_signals(indicators.add_indicators(_gap_frame()))
        pgo = sig["pgo"]
        expect = ((pgo < 0.0) & (pgo.shift(1) >= 0.0)).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_exit"] == expect).all()))

    def test_no_lookahead_truncation(self):
        full = _frame(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("pgo", "atr14", "atr14_sma"):
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


class TestPgoRegistration(unittest.TestCase):
    def test_registration_imports_cleanly(self):
        import strategies.pretty_good_osc as mod

        self.assertEqual(mod.SPEC.slug, "pretty_good_osc")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 100)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
