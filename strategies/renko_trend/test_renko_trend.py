"""Renko trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.renko_trend import indicators, risk, signals
from strategies.renko_trend.indicators import _renko_direction


def _frame(n, c, spread=0.2):
    c = np.asarray(c, float)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestRenko(unittest.TestCase):
    def test_brick_construction_hand_computed(self):
        closes = np.array([100.0, 101.0, 102.5, 102.6, 100.5, 99.0])
        brick = np.full(6, 1.0)
        d = _renko_direction(closes, brick)
        # level=100; +1 brick at 101 (level 101); +1 at 102.5 (level 102);
        # 102.6 no new brick; 100.5 -> -1 brick (level 101, dir -1);
        # 99.0 -> -1 bricks down to 99 (dir -1)
        self.assertEqual(d[0], 0)
        self.assertEqual(d[1], 1)
        self.assertEqual(d[2], 1)
        self.assertEqual(d[3], 1)
        self.assertEqual(d[4], -1)
        self.assertEqual(d[5], -1)

    def test_flat_price_never_forms_bricks(self):
        n = 60
        df = indicators.add_indicators(_frame(n, np.full(n, 100.0), spread=0.01))
        self.assertTrue((df["renko_dir"] == 0).all())

    def test_sustained_trend_holds_direction(self):
        n = 150
        c = 100.0 + 0.5 * np.arange(n)
        df = indicators.add_indicators(_frame(n, c))
        self.assertEqual(df["renko_dir"].iloc[-1], 1)

    def test_reversal_fires_both_entries(self):
        # up -> down -> up: both brick-direction flips must occur
        n = 450
        i = np.arange(n)
        c = 100.0 + np.where(i < 150, 0.4 * i,
                             np.where(i < 300, 60.0 - 0.4 * (i - 150),
                                      0.4 * (i - 300)))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        self.assertTrue(sig["long_entry"].any())
        self.assertTrue(sig["short_entry"].any())

    def test_brick_size_is_half_atr(self):
        n = 100
        rng = np.random.default_rng(2)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        df = indicators.add_indicators(_frame(n, c))
        from strategies import base as B
        exp = B.atr(df["h"], df["l"], df["c"], 14) * 0.5
        pd.testing.assert_series_equal(df["brick"], exp, check_names=False)

    def test_signal_columns_bool_no_nan(self):
        n = 150
        rng = np.random.default_rng(5)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 40)
        self.assertEqual(risk.RISK.max_hold_bars, 200)


if __name__ == "__main__":
    unittest.main()
