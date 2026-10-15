"""Chaikin Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.chaikin_osc import indicators, risk, signals


def _ohlcv(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.asarray(v, float)}
    )


def _frame(n, c, v, spread=0.1):
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _ohlcv(o, h, l, c, v)


class TestChaikinOsc(unittest.TestCase):
    def test_clv_bounds(self):
        # close at high -> CLV +1; close at low -> CLV -1
        n = 30
        c = np.full(n, 105.0)
        o = np.full(n, 100.0)
        h = np.full(n, 105.0)
        l = np.full(n, 95.0)
        df = indicators.add_indicators(_ohlcv(o, h, l, c, np.full(n, 10.0)))
        # MFV = +1 * 10 each bar => ADL = 10,20,...,300
        self.assertAlmostEqual(df["adl"].iloc[-1], 300.0, places=9)
        c2 = np.full(n, 95.0)
        df2 = indicators.add_indicators(_ohlcv(o, h, l, c2, np.full(n, 10.0)))
        self.assertAlmostEqual(df2["adl"].iloc[-1], -300.0, places=9)

    def test_osc_is_ema3_minus_ema10_of_adl(self):
        n = 60
        rng = np.random.default_rng(0)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        df = indicators.add_indicators(_frame(n, c, np.full(n, 100.0)))
        exp = B.ema(df["adl"], 3) - B.ema(df["adl"], 10)
        pd.testing.assert_series_equal(df["chaikin_osc"], exp, check_names=False)

    def test_accumulation_pushes_osc_positive(self):
        # closes pinned at the high with rising volume => strong accumulation
        n = 120
        c = 100.0 + 0.2 * np.arange(n)
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(
            _ohlcv(o, c + 0.05, o - 0.5, c, 100.0 + np.arange(n)))
        self.assertGreater(df["chaikin_osc"].iloc[-1], 0)

    def test_zero_cross_fires_both_directions(self):
        n = 200
        i = np.arange(n)
        c = 100.0 + 8.0 * np.sin(i / 12.0)
        sig = signals.add_signals(indicators.add_indicators(
            _frame(n, c, np.full(n, 100.0))))
        self.assertTrue(sig["long_entry"].any())
        self.assertTrue(sig["short_entry"].any())

    def test_degenerate_bars_do_not_move_adl(self):
        n = 20
        c = np.full(n, 100.0)
        df = indicators.add_indicators(_ohlcv(c, c, c, c, np.full(n, 50.0)))
        self.assertTrue((df["adl"] == 0.0).all())

    def test_signal_columns_bool_no_nan(self):
        n = 100
        rng = np.random.default_rng(7)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(
            _frame(n, c, np.full(n, 100.0))))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
