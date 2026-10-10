"""KAMA trend tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.kama_trend import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _from_close(c):
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    return _ohlcv(o, h, l, c)


def _straight(n=300):
    """Perfect straight-line uptrend: ER must be exactly 1."""
    return _from_close(100.0 + 1.0 * np.arange(n))


def _oscillate(n=300):
    """Alternating 100/101: net displacement 0 over the 10-bar window."""
    return _from_close(100.0 + (np.arange(n) % 2).astype(float))


def _trend_cross(n=500, seed=7):
    """V-bottom: slow decline (KAMA settles above price) then a strong
    uptrend -> clean cross-up entry with high efficiency."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:150] = 100 - 0.15 * np.arange(150)
    c[150:] = c[149] + 0.45 * np.arange(1, n - 150 + 1) + rng.normal(0, 0.08, n - 150)
    return _from_close(c)


def _chop(n=600, seed=3):
    """High-frequency sine chop: KAMA is crossed often but the 10-bar
    efficiency ratio stays low, so entries must be suppressed."""
    rng = np.random.default_rng(seed)
    c = 100 + 1.5 * np.sin(np.arange(n) / 2.0) + rng.normal(0, 0.2, n)
    return _from_close(c)


class TestKamaTrend(unittest.TestCase):
    def test_er_is_one_on_straight_trend(self):
        df = indicators.add_indicators(_straight())
        er = df["er"].iloc[indicators.N :]
        self.assertTrue(((er - 1.0).abs() < 1e-9).all(), er.max())

    def test_er_near_zero_on_oscillation(self):
        df = indicators.add_indicators(_oscillate())
        er = df["er"].iloc[indicators.N :]
        self.assertLess(float(er.max()), 1e-9)

    def test_er_bounded_in_unit_interval(self):
        df = indicators.add_indicators(_trend_cross())
        er = df["er"].dropna()
        self.assertGreater(len(er), 100)
        self.assertTrue(((er >= 0.0) & (er <= 1.0)).all())

    def test_sc_formula_on_known_er(self):
        df = indicators.add_indicators(_straight())
        i = 120
        er = df["er"].iloc[i]
        self.assertAlmostEqual(er, 1.0, places=9)
        expected = (er * (indicators.FAST_SC - indicators.SLOW_SC) + indicators.SLOW_SC) ** 2
        self.assertAlmostEqual(df["sc"].iloc[i], expected, places=12)
        self.assertAlmostEqual(df["sc"].iloc[i], indicators.FAST_SC**2, places=9)
        df2 = indicators.add_indicators(_oscillate())
        self.assertAlmostEqual(df2["sc"].iloc[120], indicators.SLOW_SC**2, places=12)

    def test_kama_tracks_trend_and_smooths_chop(self):
        df = indicators.add_indicators(_straight())
        lag = (df["c"] - df["kama"]).abs().iloc[-50:]
        # steady-state lag of a linear trend under constant smoothing stays small
        self.assertLess(float(lag.max()), 3.0)
        chop = indicators.add_indicators(_chop())
        kama_move = chop["kama"].diff().abs().mean()
        price_move = chop["c"].diff().abs().mean()
        self.assertLess(kama_move, price_move)

    def test_entry_fires_on_trending_cross_only(self):
        df = signals.add_signals(indicators.add_indicators(_trend_cross()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)
        # every entry bar must satisfy the efficiency filter
        fired = df[df["long_entry"] | df["short_entry"]]
        self.assertTrue((fired["er"] > indicators.ER_MIN).all())

    def test_no_entry_on_low_er_cross(self):
        df = indicators.add_indicators(_chop())
        df = signals.add_signals(df)
        up = B.crossed_above(df["c"], df["kama"]).fillna(False)
        dn = B.crossed_below(df["c"], df["kama"]).fillna(False)
        raw_cross = (up | dn).fillna(False)
        low_er_cross = raw_cross & (df["er"] <= indicators.ER_MIN).fillna(False)
        self.assertGreater(int(low_er_cross.sum()), 0, "chop must contain low-ER crosses")
        suppressed = low_er_cross & (df["long_entry"] | df["short_entry"])
        self.assertEqual(int(suppressed.sum()), 0)

    def test_exits_mirror_entries(self):
        df = signals.add_signals(indicators.add_indicators(_trend_cross()))
        up = B.crossed_above(df["c"], df["kama"]).fillna(False)
        dn = B.crossed_below(df["c"], df["kama"]).fillna(False)
        pd.testing.assert_series_equal(
            df["long_exit"], dn.fillna(False), check_names=False
        )
        pd.testing.assert_series_equal(
            df["short_exit"], up.fillna(False), check_names=False
        )

    def test_no_lookahead_truncation(self):
        full = _trend_cross()
        ind_full = indicators.add_indicators(full)
        for i in (250, 400):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("er", "sc", "kama"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_trend_cross()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
