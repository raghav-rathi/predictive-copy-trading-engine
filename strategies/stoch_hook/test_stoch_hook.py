"""Stochastic-hook tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stoch_hook import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _uptrend_with_pullback(n=600, seed=21):
    """Sustained uptrend (bias up), a sharp 12-bar pullback, then a strong
    recovery -- the recovery should print a slowK hook cross with rising
    rawK while still above EMA50."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:400] = 100 + 0.12 * np.arange(400) + rng.normal(0, 0.25, 400)
    c[400:412] = c[399] - 0.9 * np.arange(1, 13) + rng.normal(0, 0.15, 12)
    c[412:] = c[411] + 1.4 * np.arange(1, n - 411) + rng.normal(0, 0.2, n - 412)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.25
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.25
    return _ohlcv(o, h, l, c)


def _downtrend_with_bounce(n=600, seed=23):
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:400] = 200 - 0.12 * np.arange(400) + rng.normal(0, 0.25, 400)
    c[400:412] = c[399] + 0.9 * np.arange(1, 13) + rng.normal(0, 0.15, 12)
    c[412:] = c[411] - 1.4 * np.arange(1, n - 411) + rng.normal(0, 0.2, n - 412)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.25
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.25
    return _ohlcv(o, h, l, c)


class TestStochHook(unittest.TestCase):
    def test_pullback_hook_generates_long_only(self):
        df = signals.add_signals(indicators.add_indicators(_uptrend_with_pullback()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_bounce_hook_generates_short_only(self):
        df = signals.add_signals(indicators.add_indicators(_downtrend_with_bounce()))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_entries_respect_bias(self):
        ind = indicators.add_indicators(_uptrend_with_pullback())
        df = signals.add_signals(ind)
        for i in df.index[df["long_entry"]]:
            self.assertTrue(ind["bias_up"].iloc[i])

    def test_cross_against_exits_fire(self):
        df = signals.add_signals(indicators.add_indicators(_uptrend_with_pullback()))
        self.assertGreater(int(df["long_exit"].sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _uptrend_with_pullback()
        ind_full = indicators.add_indicators(full)
        for i in (420, 500):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("rawK", "slowK", "trig", "bias_up"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                if isinstance(a, (bool, np.bool_)):
                    self.assertEqual(bool(a), bool(b))
                else:
                    self.assertTrue((pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_uptrend_with_pullback()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertGreaterEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
