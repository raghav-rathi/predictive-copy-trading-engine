"""Ehlers RVI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rvi_ehlers import indicators, risk, signals


def _frame(n, c, o=None):
    c = pd.Series(np.asarray(c, float))
    if o is None:
        o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    else:
        o = pd.Series(np.asarray(o, float))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestRVIEhlers(unittest.TestCase):
    def test_rvi_converges_in_uptrend(self):
        # every bar closes 1.0 above its open; h-l = 1.1 so raw = 1/1.1
        n = 120
        c = 100.0 + np.arange(n)
        o = c - 1.0
        df = indicators.add_indicators(_frame(n, c, o))
        tail = df["rvi"].iloc[-20:].dropna()
        self.assertTrue(((tail - 1.0 / 1.1).abs() < 1e-9).all())

    def test_signal_line_formula_matches(self):
        n = 120
        rng = np.random.default_rng(3)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        df = indicators.add_indicators(_frame(n, c))
        rvi = df["rvi"]
        manual = (rvi + 2 * rvi.shift(1) + 2 * rvi.shift(2) + rvi.shift(3)) / 6
        pd.testing.assert_series_equal(df["rvi_signal"], manual,
                                       check_names=False)

    def test_divide_by_zero_guard(self):
        # flat bars: h == l -> raw forced to 0, no NaN/inf
        n = 60
        c = np.full(n, 100.0)
        df = indicators.add_indicators(_frame(n, c))
        self.assertFalse(df["rvi_raw"].isna().any())
        self.assertTrue(np.isfinite(df["rvi_raw"]).all())
        self.assertTrue((df["rvi_raw"] == 0.0).all())

    def test_reversal_fires_cross(self):
        n = 300
        i = np.arange(n)
        rng = np.random.default_rng(21)
        c = (100.0 + np.where(i < 150, 0.4 * i, 60.0 - 0.5 * (i - 150))
             + rng.normal(0, 0.02, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        shorts = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(any(145 <= j <= 165 for j in shorts),
                        f"no short cross near reversal; got {shorts[:6]}")

    def test_min_sep_filter_is_monotone(self):
        n = 300
        rng = np.random.default_rng(9)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        base = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        filt = signals.add_signals(
            indicators.add_indicators(_frame(n, c)), min_sep=0.02)
        self.assertLessEqual(int(filt["long_entry"].sum()),
                             int(base["long_entry"].sum()))
        self.assertLessEqual(int(filt["short_entry"].sum()),
                             int(base["short_entry"].sum()))

    def test_no_lookahead(self):
        # RVI at bar i may not change when future bars are appended
        n = 200
        rng = np.random.default_rng(11)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        df1 = indicators.add_indicators(_frame(n, c))
        df2 = indicators.add_indicators(
            _frame(2 * n, np.concatenate([c, c])))
        pd.testing.assert_series_equal(
            df1["rvi"], df2["rvi"].iloc[:n].reset_index(drop=True),
            check_names=False)

    def test_signal_columns_bool_no_nan(self):
        n = 200
        rng = np.random.default_rng(5)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 60)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)

    def test_registration(self):
        import strategies.rvi_ehlers as m
        from strategies.registry import REGISTRY
        self.assertIn("rvi_ehlers", REGISTRY)
        self.assertIs(REGISTRY["rvi_ehlers"], m.SPEC)


if __name__ == "__main__":
    unittest.main()
