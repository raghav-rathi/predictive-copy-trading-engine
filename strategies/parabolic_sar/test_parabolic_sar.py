"""Parabolic SAR tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.parabolic_sar import indicators, risk, signals
from strategies.parabolic_sar.indicators import AF_START, AF_MAX


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _uptrend(n=400, seed=3):
    """Straight-line uptrend with small noise: SAR must trail below lows."""
    rng = np.random.default_rng(seed)
    c = 100 + 0.5 * np.arange(n) + rng.normal(0, 0.15, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.25
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.25
    return _ohlcv(o, h, l, c)


def _reversal(n=400, seed=7):
    """Long uptrend then a sharp crash: a flip must occur at the crash."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:250] = 100 + 0.4 * np.arange(250) + rng.normal(0, 0.1, 250)
    c[250:] = c[249] - 1.2 * np.arange(1, n - 250 + 1) + rng.normal(0, 0.1, n - 250)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.2
    return _ohlcv(o, h, l, c)


def _vshape(n=600, seed=9):
    """Up, crash, recover: produces flips in both directions."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:200] = 100 + 0.4 * np.arange(200) + rng.normal(0, 0.1, 200)
    c[200:400] = c[199] - 1.2 * np.arange(1, 201) + rng.normal(0, 0.1, 200)
    c[400:] = c[399] + 1.2 * np.arange(1, n - 400 + 1) + rng.normal(0, 0.1, n - 400)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.2
    return _ohlcv(o, h, l, c)


class TestParabolicSAR(unittest.TestCase):
    def test_uptrend_sar_stays_below_lows(self):
        df = indicators.add_indicators(_uptrend())
        d = df["sar_dir"].to_numpy()
        sar = df["sar"].to_numpy()
        l = df["l"].to_numpy()
        mask = d == 1
        self.assertGreater(mask.sum(), 300)
        # while long, clamped SAR must never pierce the bar's low
        self.assertTrue(np.all(sar[mask] <= l[mask] + 1e-9))

    def test_af_ramps_to_max_in_sustained_trend(self):
        df = indicators.add_indicators(_uptrend())
        d = df["sar_dir"].to_numpy()
        af = df["sar_af"].to_numpy()
        long_run = d[-60:] == 1
        self.assertTrue(long_run.all())
        self.assertAlmostEqual(float(af[-1]), AF_MAX, places=9)

    def test_flip_fires_when_low_pierces_sar(self):
        df = indicators.add_indicators(_reversal())
        d = df["sar_dir"].to_numpy()
        # starts long, ends short after the crash
        self.assertEqual(d[10], 1)
        self.assertEqual(d[-1], -1)
        # the flip bar itself is the first -1
        flip = np.where(np.diff(d) != 0)[0][0] + 1
        # flip must happen during the crash, not the uptrend
        self.assertGreaterEqual(flip, 250)
        self.assertEqual(int(df["sar_dir"].iloc[flip - 1]), 1)
        self.assertLess(flip, 400)

    def test_af_resets_to_start_after_flip(self):
        df = indicators.add_indicators(_reversal())
        d = df["sar_dir"].to_numpy()
        flip = np.where(np.diff(d) != 0)[0][0] + 1
        self.assertAlmostEqual(float(df["sar_af"].iloc[flip]), AF_START, places=9)

    def test_short_sar_never_below_price(self):
        """Clamp: while short, SAR may not go below the prior two highs."""
        df = indicators.add_indicators(_reversal())
        d = df["sar_dir"].to_numpy()
        sar = df["sar"].to_numpy()
        h = df["h"].to_numpy()
        mask = (d == -1) & (np.arange(len(d)) > 10)
        self.assertGreater(mask.sum(), 20)
        for i in np.where(mask)[0]:
            self.assertTrue(sar[i] >= max(h[i - 1], h[i - 2]) - 1e-9)

    def test_reverse_system_exact_opposites(self):
        df = signals.add_signals(indicators.add_indicators(_vshape()))
        self.assertTrue((df["long_exit"] == df["short_entry"]).all())
        self.assertTrue((df["short_exit"] == df["long_entry"]).all())
        # never enter both sides on the same bar
        self.assertFalse((df["long_entry"] & df["short_entry"]).any())
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertGreater(int(df["short_entry"].sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _reversal()
        ind_full = indicators.add_indicators(full)
        for i in (100, 250, 380):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            self.assertEqual(int(ind_full["sar_dir"].iloc[i]),
                             int(ind_tr["sar_dir"].iloc[i]))
            self.assertAlmostEqual(float(ind_full["sar"].iloc[i]),
                                   float(ind_tr["sar"].iloc[i]), places=9)
            self.assertAlmostEqual(float(ind_full["sar_af"].iloc[i]),
                                   float(ind_tr["sar_af"].iloc[i]), places=9)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_reversal()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
