"""McGinley Dynamic tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mcginley_dynamic import indicators, risk, signals


def _frame(n, c):
    c = np.asarray(c, float)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestMcGinley(unittest.TestCase):
    def test_formula_hand_computed_two_bars(self):
        c = np.array([100.0, 110.0, 105.0])
        df = indicators.add_indicators(_frame(3, c))
        md1 = 100.0
        md2 = md1 + (110.0 - md1) / (10 * (110.0 / md1) ** 4)
        self.assertAlmostEqual(df["md_fast"].iloc[1], md2, places=9)
        md3 = md2 + (105.0 - md2) / (10 * (105.0 / md2) ** 4)
        self.assertAlmostEqual(df["md_fast"].iloc[2], md3, places=9)

    def test_tracks_price_closely(self):
        n = 200
        c = 100.0 + np.cumsum(np.random.default_rng(0).normal(0, 0.3, n))
        df = indicators.add_indicators(_frame(n, c))
        # MD stays within a few percent of price on random walk
        dev = (df["md_fast"] - df["c"]).abs() / df["c"]
        self.assertLess(dev.iloc[50:].max(), 0.05)

    def test_fast_reacts_quicker_than_slow(self):
        n = 120
        i = np.arange(n)
        c = 100.0 + np.where(i < 60, 0.0, 0.6 * (i - 60))
        df = indicators.add_indicators(_frame(n, c))
        # after the regime break the fast line is nearer to price
        self.assertLess(abs(df["md_fast"].iloc[-1] - c[-1]),
                        abs(df["md_slow"].iloc[-1] - c[-1]))

    def test_cross_fires_both_directions(self):
        n = 240
        i = np.arange(n)
        c = 100.0 + 10.0 * np.sin(i / 15.0)
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        self.assertTrue(sig["long_entry"].any())
        self.assertTrue(sig["short_entry"].any())

    def test_no_nan_outputs(self):
        n = 100
        c = 100.0 + np.cumsum(np.random.default_rng(9).normal(0, 0.3, n))
        df = indicators.add_indicators(_frame(n, c))
        self.assertFalse(df[["md_fast", "md_slow"]].isna().any().any())
        sig = signals.add_signals(df)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 60)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)


if __name__ == "__main__":
    unittest.main()
