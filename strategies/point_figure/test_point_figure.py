"""Point & Figure tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.point_figure import indicators, risk, signals


def _frame(n, c, v=100.0):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, v)})


def _staircase():
    # box = 1.0: rise 100->109 (X column), dip to 106 (O reversal),
    # rise to 111 (new X column breaking the prior X top by >= 1 box)
    up = [100 + i for i in range(10)]
    dn = [108.5, 108.0, 106.5, 106.0]
    up2 = [109.5, 110.0, 111.0]
    return np.array(up + dn + up2, dtype=float)


class TestPointFigure(unittest.TestCase):
    def test_builder_column_alternation_and_reversal_count(self):
        c = _staircase()
        box = np.full(len(c), 1.0)
        pf = indicators._build_pf(c, box)
        d = pf["dir"]
        # one X column, one O column (starts bar 13), one X column (bar 14)
        self.assertTrue((d[:13] == 1).all())
        self.assertEqual(d[13], -1)
        self.assertTrue((d[14:] == 1).all())
        # exactly two reversals
        self.assertEqual(int((np.diff(d) != 0).sum()), 2)

    def test_builder_records_column_extremes(self):
        c = _staircase()
        box = np.full(len(c), 1.0)
        pf = indicators._build_pf(c, box)
        self.assertEqual(pf["top"][9], 109.0)     # X column top
        self.assertEqual(pf["prev_x_top"][14], 109.0)  # completed X top
        self.assertEqual(pf["prev_o_bottom"][15], 106.0)  # completed O bottom

    def test_builder_double_bottom_short(self):
        c = np.array([100 - i for i in range(16)] + [86, 87, 88, 89]
                     + [88, 87, 86, 85, 84, 83], dtype=float)
        box = np.full(len(c), 1.0)
        pf = indicators._build_pf(c, box)
        d = pf["dir"]
        # falls: X->O reversal, rises back, then O again -> short breakdown
        self.assertIn(-1, d)
        # after the second O column starts, prev_o_bottom is recorded
        self.assertFalse(np.isnan(pf["prev_o_bottom"][-1]))
        # second O column bottom (83) breaks first O bottom by >= 1 box
        self.assertLessEqual(pf["bottom"][-1], pf["prev_o_bottom"][-1] - 1.0)

    def test_pipeline_double_top_fires_long(self):
        # V-shaped synthetic series through the real ATR-based pipeline
        n = 240
        i = np.arange(n)
        c = np.where(i < 80, 100.0 + 0.375 * i,
                     np.where(i < 140, 130.0 - 0.25 * (i - 80),
                              115.0 + 0.25 * (i - 140)))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        self.assertTrue(sig["long_entry"].any())

    def test_pipeline_columns_sane(self):
        n = 300
        rng = np.random.default_rng(3)
        c = 100 + np.cumsum(rng.normal(0, 0.6, n))
        df = indicators.add_indicators(_frame(n, c))
        self.assertTrue(set(df["pf_col"].unique()) <= {1, -1})
        self.assertTrue((df["pf_top"] >= df["pf_bottom"]).all())
        for col in ("pf_col", "pf_top", "pf_bottom"):
            self.assertFalse(df[col].isna().any())
        # pf_box is NaN only during the ATR(14) warmup
        self.assertFalse(df["pf_box"].iloc[14:].isna().any())

    def test_signal_columns_bool_no_nan(self):
        n = 300
        rng = np.random.default_rng(5)
        c = 100 + np.cumsum(rng.normal(0, 0.6, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_no_lookahead(self):
        n = 400
        rng = np.random.default_rng(13)
        c = 100 + np.cumsum(rng.normal(0, 0.7, n))
        full = indicators.add_indicators(_frame(n, c))
        for k in (200, 399):
            trunc = indicators.add_indicators(_frame(n, c)[:k + 1])
            self.assertEqual(full["pf_col"].iloc[k], trunc["pf_col"].iloc[k])
            self.assertEqual(full["pf_top"].iloc[k], trunc["pf_top"].iloc[k])
            self.assertEqual(full["pf_bottom"].iloc[k], trunc["pf_bottom"].iloc[k])

    def test_registration_and_risk(self):
        import strategies.point_figure as P
        self.assertEqual(P.SPEC.slug, "point_figure")
        self.assertEqual(risk.WARMUP, 120)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)


if __name__ == "__main__":
    unittest.main()
