"""Ease of Movement tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ease_of_movement import indicators, risk, signals


def _ohlcv(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.asarray(v, float)}
    )


class TestEMV(unittest.TestCase):
    def test_emv_formula_hand_computed(self):
        # hand-computed 1-bar EMV at the last bar
        h = np.array([10.0, 12.0, 11.0, 13.0])
        l = np.array([9.0, 10.0, 10.0, 11.0])
        c = np.array([9.5, 11.5, 10.5, 12.5])
        v = np.array([100.0, 200.0, 150.0, 300.0])
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(_ohlcv(o, h, l, c, v))
        mid = (h + l) / 2.0
        dist = mid[-1] - mid[-2]
        box = v[-1] / (h[-1] - l[-1])
        self.assertAlmostEqual(df["emv_raw"].iloc[-1], dist / box, places=9)

    def test_emv_smooth_is_sma14(self):
        n = 40
        rng = np.random.default_rng(1)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.1
        l = np.minimum(o, c) - 0.1
        df = indicators.add_indicators(_ohlcv(o, h, l, c, np.full(n, 100.0)))
        self.assertAlmostEqual(
            df["emv"].iloc[-1], df["emv_raw"].iloc[-14:].mean(), places=9
        )

    def test_degenerate_bar_contributes_zero(self):
        n = 20
        c = np.full(n, 100.0)
        o, h, l = c.copy(), c.copy(), c.copy()  # H == L everywhere
        df = indicators.add_indicators(_ohlcv(o, h, l, c, np.full(n, 50.0)))
        self.assertTrue((df["emv_raw"] == 0.0).all())

    def test_sustained_rise_pushes_emv_positive(self):
        n = 120
        i = np.arange(n)
        c = 100.0 + 0.4 * i
        o = np.concatenate([[c[0]], c[:-1]])
        h = c + 0.1
        l = o - 0.1
        df = indicators.add_indicators(_ohlcv(o, h, l, c, np.full(n, 100.0)))
        self.assertGreater(df["emv"].iloc[-1], 0)

    def test_zero_cross_fires_both_directions(self):
        n = 240
        i = np.arange(n)
        # down -> up -> down so EMV crosses zero in both directions
        c = 100.0 + np.where(i < 80, -0.4 * i,
                             np.where(i < 160, -32.0 + 0.5 * (i - 80),
                                      8.0 - 0.4 * (i - 160)))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.05
        l = np.minimum(o, c) - 0.05
        sig = signals.add_signals(indicators.add_indicators(
            _ohlcv(o, h, l, c, np.full(n, 100.0))))
        self.assertTrue(sig["long_entry"].any())
        self.assertTrue(sig["short_entry"].any())

    def test_signal_columns_bool_no_nan(self):
        n = 100
        rng = np.random.default_rng(4)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.1
        l = np.minimum(o, c) - 0.1
        sig = signals.add_signals(indicators.add_indicators(
            _ohlcv(o, h, l, c, np.full(n, 100.0))))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
