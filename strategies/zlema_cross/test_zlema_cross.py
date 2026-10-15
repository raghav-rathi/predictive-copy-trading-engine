"""ZLEMA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.zlema_cross import indicators, risk, signals


def _frame(n, c):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestZLEMA(unittest.TestCase):
    def test_delag_formula_hand_computed(self):
        # fast uses FAST_N: lag=(FAST_N-1)//2; d[i] = c[i]+(c[i]-c[i-lag])
        n = 30
        rng = np.random.default_rng(0)
        c = pd.Series(100 + np.cumsum(rng.normal(0, 0.4, n)))
        df = indicators.add_indicators(_frame(n, c.to_numpy()))
        lag = (indicators.FAST_N - 1) // 2
        d = c + (c - c.shift(lag).fillna(c))
        exp = B.ema(d, indicators.FAST_N)
        pd.testing.assert_series_equal(df["zlema_fast"].rename(None),
                                       exp.rename(None), check_names=False)

    def test_constant_series_returns_constant(self):
        n = 80
        df = indicators.add_indicators(_frame(n, np.full(n, 100.0)))
        self.assertAlmostEqual(df["zlema_fast"].iloc[-1], 100.0, places=6)

    def test_leads_plain_ema_on_trend_start(self):
        # on a fresh uptrend the de-lagged line sits closer to price
        n = 100
        i = np.arange(n)
        c = 100.0 + np.where(i < 50, 0.0, 0.5 * (i - 50))
        df = indicators.add_indicators(_frame(n, c))
        plain = B.ema(df["c"], 10).iloc[-1]
        self.assertLess(abs(df["zlema_fast"].iloc[-1] - c[-1]),
                        abs(plain - c[-1]))

    def test_cross_fires_both_directions(self):
        n = 240
        i = np.arange(n)
        c = 100.0 + 10.0 * np.sin(i / 15.0)
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        self.assertTrue(sig["long_entry"].any())
        self.assertTrue(sig["short_entry"].any())

    def test_no_nan_after_warmup(self):
        n = 150
        c = 100.0 + np.cumsum(np.random.default_rng(3).normal(0, 0.3, n))
        df = indicators.add_indicators(_frame(n, c))
        self.assertFalse(df[["zlema_fast", "zlema_slow"]].iloc[60:].isna().any().any())
        sig = signals.add_signals(df)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 60)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)


if __name__ == "__main__":
    unittest.main()
