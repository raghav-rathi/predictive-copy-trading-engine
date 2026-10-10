"""DeMarker exhaustion tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.demarker import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _selloff(n=600, seed=3):
    """Flat chop (DeM ~0.5), then steady selloff (DeM near 0), then a bounce."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:100] = 100 + 0.3 * np.sin(np.arange(100) / 6) + rng.normal(0, 0.1, 100)
    c[100:400] = c[99] - 0.15 * np.arange(300) + rng.normal(0, 0.06, 300)
    c[400:] = c[399] + 0.10 * np.arange(1, n - 400 + 1) + rng.normal(0, 0.06, n - 400)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.03, n)) + 0.15
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.03, n)) - 0.15
    return _ohlcv(o, h, l, c)


def _rally(n=600, seed=7):
    """Flat chop (DeM ~0.5), then steady rally (DeM near 1), then a pullback."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:100] = 100 + 0.3 * np.sin(np.arange(100) / 6) + rng.normal(0, 0.1, 100)
    c[100:400] = c[99] + 0.15 * np.arange(300) + rng.normal(0, 0.06, 300)
    c[400:] = c[399] - 0.10 * np.arange(1, n - 400 + 1) + rng.normal(0, 0.06, n - 400)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.03, n)) + 0.15
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.03, n)) - 0.15
    return _ohlcv(o, h, l, c)


class TestDeMarker(unittest.TestCase):
    def test_dem_formula_rising_highs_near_one(self):
        n = 40
        h = 100.0 + np.arange(n)  # monotonically rising highs
        l = 100.0 + np.arange(n) * 0.5  # lows rising too but slower
        c = (h + l) / 2
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(_ohlcv(o, h, l, c))
        dem = df["dem"].dropna()
        self.assertTrue((dem > 0.9).all(), dem.tail(3).tolist())

    def test_dem_formula_falling_lows_near_zero(self):
        n = 40
        l = 100.0 - np.arange(n)  # monotonically falling lows
        h = 100.0 - np.arange(n) * 0.5
        c = (h + l) / 2
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(_ohlcv(o, h, l, c))
        dem = df["dem"].dropna()
        self.assertTrue((dem < 0.1).all(), dem.tail(3).tolist())

    def test_dem_bounded_zero_one(self):
        rng = np.random.default_rng(42)
        n = 300
        c = 100 + np.cumsum(rng.normal(0, 1, n))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + np.abs(rng.normal(0, 0.2, n))
        l = np.minimum(o, c) - np.abs(rng.normal(0, 0.2, n))
        df = indicators.add_indicators(_ohlcv(o, h, l, c))
        dem = df["dem"].dropna()
        self.assertTrue(((dem >= 0.0) & (dem <= 1.0)).all())

    def test_dem_flat_market_is_half(self):
        n = 40
        c = np.full(n, 100.0)
        df = indicators.add_indicators(_ohlcv(c, c, c, c))
        dem = df["dem"].dropna()
        self.assertTrue((dem == 0.5).all())

    def test_long_entry_fires_on_cross_below_0p3(self):
        df = signals.add_signals(indicators.add_indicators(_selloff()))
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx:
            self.assertGreaterEqual(df["dem"].iloc[i - 1], 0.3)
            self.assertLess(df["dem"].iloc[i], 0.3)

    def test_entry_requires_cross_not_touch(self):
        """Bar that stays below 0.3 without a cross must not fire an entry."""
        n = 60
        l = 100.0 - 0.5 * np.arange(n)  # falling lows -> DeM pinned < 0.3
        h = l + 0.1
        c = (h + l) / 2
        o = np.concatenate([[c[0]], c[:-1]])
        df = signals.add_signals(indicators.add_indicators(_ohlcv(o, h, l, c)))
        tail = df.iloc[20:]  # after DeM is pinned
        self.assertTrue((tail["dem"].dropna() < 0.3).all())
        self.assertEqual(int(tail["long_entry"].sum()), 0)

    def test_short_entry_fires_on_cross_above_0p7(self):
        df = signals.add_signals(indicators.add_indicators(_rally()))
        idx = df.index[df["short_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx:
            self.assertLessEqual(df["dem"].iloc[i - 1], 0.7)
            self.assertGreater(df["dem"].iloc[i], 0.7)

    def test_long_exit_fires_on_cross_above_0p5(self):
        df = signals.add_signals(indicators.add_indicators(_selloff()))
        idx = df.index[df["long_exit"]]
        self.assertGreater(len(idx), 0)
        # at least one exit must be a cross-above-0.5 (not just dem > 0.7)
        crossed = [
            i
            for i in idx
            if df["dem"].iloc[i - 1] <= 0.5 < df["dem"].iloc[i]
        ]
        self.assertGreater(len(crossed), 0)

    def test_no_lookahead_truncation(self):
        full = _selloff()
        ind_full = indicators.add_indicators(full)
        for i in (250, 450):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("demax", "demin", "dem"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-12, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_selloff()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
