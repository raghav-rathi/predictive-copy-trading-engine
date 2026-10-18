"""Bill Williams' Alligator + fractal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.williams_alligator import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _df_from_c(c):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    return _ohlcv(o, h, l, c)


def _smma_loop(x, n):
    """Independent Wilder smoothing loop: y[0]=x[0], y[i]=(x[i]+(n-1)y[i-1])/n."""
    y = np.full(len(x), np.nan)
    acc = x[0]
    for i in range(len(x)):
        acc = x[i] if i == 0 else (x[i] + (n - 1) * acc) / n
        if i >= n - 1:
            y[i] = acc
    return y


def _uptrend_with_fractals(n=120):
    """Steady uptrend with a buy-fractal spike at bar 30 and a sell-fractal
    dip at bar 60."""
    i = np.arange(n)
    c = 100.0 + 0.3 * i
    o = c - 0.05
    h = c + 0.1
    l = c - 0.15
    # buy fractal: strict 5-bar high pivot at bar 30
    h[28], h[29], h[30], h[31], h[32] = 108.5, 108.8, 109.9, 109.4, 109.7
    # sell fractal: strict 5-bar low pivot at bar 60
    l[58], l[59], l[60], l[61], l[62] = 117.2, 117.5, 116.9, 118.1, 118.4
    return _ohlcv(o, h, l, c)


class TestWilliamsAlligator(unittest.TestCase):
    def test_smma_hand_computed_and_shifted(self):
        n = 120
        rng = np.random.default_rng(6)
        df = _df_from_c(100 + np.cumsum(rng.normal(0, 0.4, n)))
        ind = indicators.add_indicators(df)
        median = ((df["h"] + df["l"]) / 2).to_numpy()
        for col, ln, sh in (
            ("alligator_jaw", 13, 8),
            ("alligator_teeth", 8, 5),
            ("alligator_lips", 5, 3),
        ):
            exp = _smma_loop(median, ln)
            exp = np.concatenate([np.full(sh, np.nan), exp[: n - sh]])
            got = ind[col].to_numpy()
            mask = ~np.isnan(exp)
            np.testing.assert_allclose(got[mask], exp[mask], rtol=1e-12, err_msg=col)

    def test_buy_fractal_detected_and_confirmed_two_bars_later(self):
        ind = indicators.add_indicators(_uptrend_with_fractals())
        self.assertTrue(bool(ind["fractal_buy_raw"].iloc[30]))
        # pivot at bar 30 is confirmed at bar 32 (k=2), not before
        self.assertTrue(pd.isna(ind["fractal_buy_level"].iloc[31]))
        self.assertAlmostEqual(ind["fractal_buy_level"].iloc[32], 109.9, places=9)
        # nothing confirmed before the first pivot
        self.assertTrue(ind["fractal_buy_level"].iloc[:32].isna().all())

    def test_sell_fractal_mirror(self):
        ind = indicators.add_indicators(_uptrend_with_fractals())
        self.assertTrue(bool(ind["fractal_sell_raw"].iloc[60]))
        self.assertTrue(pd.isna(ind["fractal_sell_level"].iloc[61]))
        self.assertAlmostEqual(ind["fractal_sell_level"].iloc[62], 116.9, places=9)

    def test_long_entry_wiring(self):
        df = _uptrend_with_fractals()
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        # level 109.9 confirmed at bar 32; close first exceeds it at bar 34
        self.assertEqual(int(sig["long_entry"].iloc[:34].sum()), 0)
        self.assertTrue(bool(sig["long_entry"].iloc[34]))
        j = 34
        self.assertGreater(df["c"].iloc[j], ind["fractal_buy_level"].iloc[j])
        self.assertGreater(ind["fractal_buy_level"].iloc[j], ind["alligator_teeth"].iloc[j])
        self.assertTrue(bool(ind["gator_awake_long"].iloc[j]))

    def test_sleep_exit_wiring(self):
        # sharp reversal: lips must cross below teeth -> long_exit fires
        n = 160
        i = np.arange(n)
        c = np.where(i < 100, 100.0 + 0.5 * i, 150.0 - 1.5 * (i - 100))
        df = _df_from_c(c)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        lips, teeth = ind["alligator_lips"], ind["alligator_teeth"]
        sleep = B.crossed_below(lips, teeth).fillna(False)
        self.assertGreater(int(sleep.sum()), 0)
        buy_break = (
            (ind["c"] > ind["fractal_buy_level"])
            & (ind["fractal_buy_level"] > teeth)
        ).fillna(False)
        sell_break = (
            (ind["c"] < ind["fractal_sell_level"])
            & (ind["fractal_sell_level"] < teeth)
        ).fillna(False)
        self.assertTrue(bool(((sig["long_exit"]) == (sleep | sell_break)).all()))
        # short side mirror: lips crosses above teeth -> short_exit
        sleep_up = B.crossed_above(lips, teeth).fillna(False)
        self.assertTrue(bool(((sig["short_exit"]) == (sleep_up | buy_break)).all()))

    def test_no_lookahead_truncation(self):
        n = 300
        rng = np.random.default_rng(10)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        full = _df_from_c(c)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (150, 250):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            for col in (
                "alligator_jaw",
                "alligator_teeth",
                "alligator_lips",
                "fractal_buy_level",
                "fractal_sell_level",
            ):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                )
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_uptrend_with_fractals()))
        for col in (
            "long_entry",
            "short_entry",
            "long_exit",
            "short_exit",
            "gator_awake_long",
            "gator_awake_short",
            "fractal_buy_raw",
            "fractal_sell_raw",
        ):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        from strategies import williams_alligator
        from strategies.registry import REGISTRY

        self.assertIs(REGISTRY["williams_alligator"], williams_alligator.SPEC)
        self.assertEqual(williams_alligator.SPEC.slug, "williams_alligator")


if __name__ == "__main__":
    unittest.main()
