"""Elder Force Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elder_force_index import indicators, risk, signals


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


def _df_from_c(c, v=100.0):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _ema_loop(x, n):
    alpha = 2.0 / (n + 1)
    y = np.full(len(x), np.nan)
    acc = x[0]
    for i in range(len(x)):
        acc = x[i] if i == 0 else alpha * x[i] + (1 - alpha) * acc
        if i >= n - 1:
            y[i] = acc
    return y


def _pullback_frame():
    """Strong uptrend (fi13 > 0), then a sharp multi-bar dip so fi2
    crosses below zero while fi13 stays positive."""
    n = 120
    c = np.empty(n)
    c[:80] = 100 + np.arange(80) * 0.5          # steady grind up
    c[80:90] = c[79] - np.arange(1, 11) * 2.0   # sharp 10-bar dip
    c[90:] = c[89] + np.arange(1, n - 90 + 1) * 0.5  # resume
    rng = np.random.default_rng(5)
    v = rng.uniform(80, 120, n)
    return _df_from_c(c, v)


class TestElderForceIndex(unittest.TestCase):
    def test_force_index_hand_computed(self):
        df = _frame(60, seed=3)
        ind = indicators.add_indicators(df)
        dc = df["c"].diff().fillna(0.0).to_numpy()
        exp = dc * df["v"].to_numpy()
        np.testing.assert_allclose(ind["force_index"].to_numpy(), exp, rtol=1e-12)
        self.assertFalse(ind["force_index"].isna().any())
        # first bar: no prior close -> FI = 0
        self.assertEqual(ind["force_index"].iloc[0], 0.0)

    def test_fi_emas_hand_computed(self):
        n = 90
        rng = np.random.default_rng(9)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        ind = indicators.add_indicators(_df_from_c(c))
        fi = np.concatenate([[0.0], np.diff(c)]) * 100.0
        for col, span in (("fi2", 2), ("fi13", 13)):
            exp = _ema_loop(fi, span)
            got = ind[col].to_numpy()
            mask = ~np.isnan(exp)
            np.testing.assert_allclose(got[mask], exp[mask], rtol=1e-10)

    def test_long_entry_on_pullback(self):
        df = _pullback_frame()
        sig = signals.add_signals(indicators.add_indicators(df))
        le = sig["long_entry"].to_numpy()
        self.assertGreater(int(le.sum()), 0)
        # the entry fires during the dip, not before it starts
        first = int(np.flatnonzero(le)[0])
        self.assertGreaterEqual(first, 80)
        # fi13 is positive at the entry (bulls in charge) and fi2 < 0
        ind = indicators.add_indicators(df)
        self.assertGreater(ind["fi13"].iloc[first], 0)
        self.assertLess(ind["fi2"].iloc[first], 0)

    def test_no_signal_before_warmup(self):
        df = _pullback_frame()
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].iloc[:20].any())

    def test_signal_columns_on_random_walk(self):
        df = _frame(400, seed=21)
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool)
        total = sum(int(sig[c].sum()) for c in
                    ("long_entry", "short_entry", "long_exit", "short_exit"))
        self.assertGreater(total, 0)  # pullback timing fires often on 1h-like noise

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

    def test_registration_imports_cleanly(self):
        import strategies.elder_force_index as mod

        self.assertEqual(mod.SPEC.slug, "elder_force_index")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
