"""PVT tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pvt_trend import indicators, risk, signals


def _ohlcv(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.asarray(v, float)}
    )


def _df_from_c(c, v=100.0):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    return _ohlcv(o, h, l, c, np.full(n, v))


class TestPVT(unittest.TestCase):
    def test_pvt_formula_hand_computed(self):
        c = np.array([100.0, 102.0, 101.0, 105.0, 105.0])
        v = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        df = indicators.add_indicators(_df_from_c(c, v))
        exp = 0.0
        for i in range(1, len(c)):
            exp += v[i] * (c[i] - c[i - 1]) / c[i - 1]
        self.assertAlmostEqual(df["pvt"].iloc[-1], exp, places=9)

    def test_pvt_flat_price_adds_nothing(self):
        n = 30
        df = indicators.add_indicators(_df_from_c(np.full(n, 100.0)))
        self.assertTrue((df["pvt"].iloc[1:] == 0.0).all())

    def test_pvt_ma_is_sma20(self):
        n = 60
        c = 100.0 + np.cumsum(np.random.default_rng(0).normal(0, 0.5, n))
        df = indicators.add_indicators(_df_from_c(c))
        exp = df["pvt"].iloc[-20:].mean()
        self.assertAlmostEqual(df["pvt_ma"].iloc[-1], exp, places=9)

    def test_cross_up_fires_long(self):
        # falling then rising price => PVT dips then climbs through its MA
        n = 120
        i = np.arange(n)
        c = 100.0 - 0.15 * i + np.where(i > 60, 0.5 * (i - 60), 0.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(sig["long_entry"].any())

    def test_cross_down_fires_short(self):
        n = 120
        i = np.arange(n)
        c = 100.0 + 0.15 * i - np.where(i > 60, 0.5 * (i - 60), 0.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(sig["short_entry"].any())

    def test_no_lookahead_first_signal_after_warmup(self):
        n = 200
        c = 100.0 + np.cumsum(np.random.default_rng(3).normal(0, 0.3, n))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        # no signal can fire before the 20-bar MA exists
        early = sig.iloc[:19]
        self.assertFalse(early["long_entry"].any())
        self.assertFalse(early["short_entry"].any())

    def test_signal_columns_bool_no_nan(self):
        n = 100
        c = 100.0 + np.cumsum(np.random.default_rng(5).normal(0, 0.3, n))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertGreater(risk.WARMUP, 20)


if __name__ == "__main__":
    unittest.main()
