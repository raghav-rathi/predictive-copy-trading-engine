"""Minervini Trend Template tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.minervini_trend import indicators, risk, signals


def _frame(n, c, v=100.0):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, v)})


class TestMinervini(unittest.TestCase):
    def test_template_true_in_steady_uptrend(self):
        # steadily rising series: every template term should hold late
        n = 5150
        c = 100.0 + 0.06 * np.arange(n)
        df = indicators.add_indicators(_frame(n, c))
        self.assertTrue(df["mt_template"].iloc[-1])

    def test_template_false_in_downtrend(self):
        n = 5150
        c = 500.0 - 0.06 * np.arange(n)
        df = indicators.add_indicators(_frame(n, c))
        self.assertFalse(df["mt_template"].any())

    def test_template_false_when_too_close_to_year_low(self):
        # flat series: price never >= 30% above the window low
        n = 5150
        c = np.full(n, 100.0)
        df = indicators.add_indicators(_frame(n, c))
        self.assertFalse(df["mt_template"].iloc[-1])

    def test_template_false_when_far_below_year_high(self):
        # crashed and flat: fails the within-25%-of-high term
        n = 5150
        c = np.concatenate([np.full(1000, 1000.0), np.full(n - 1000, 400.0)])
        df = indicators.add_indicators(_frame(n, c))
        self.assertFalse(df["mt_template"].iloc[-1])

    def test_long_entry_fires_only_on_false_to_true_flip(self):
        # decline then strong rally: template must flip at some bar and
        # long_entry must equal the flip exactly
        n = 5150
        i = np.arange(n)
        c = np.where(i < 4000, 500.0 - 0.0125 * i, 450.0 + 0.5 * (i - 4000))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        t = sig["mt_template"].fillna(False).astype(bool)
        expected = t & ~t.shift(1).fillna(False).astype(bool)
        pd.testing.assert_series_equal(sig["long_entry"], expected,
                                       check_names=False)
        self.assertTrue(sig["long_entry"].any())

    def test_long_exit_on_template_breakdown(self):
        n = 5150
        i = np.arange(n)
        c = np.where(i < 4000, 100.0 + 0.06 * i, 340.0 - 0.5 * (i - 4000))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        # late in the crash, price must be below the 50d SMA -> exit true
        self.assertTrue(sig["long_exit"].iloc[-1])

    def test_no_shorts_ever(self):
        n = 3000
        rng = np.random.default_rng(7)
        c = 100 + np.cumsum(rng.normal(0, 1.0, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        self.assertFalse(sig["short_entry"].any())
        self.assertFalse(sig["short_exit"].any())

    def test_signal_columns_bool_no_nan(self):
        n = 3000
        rng = np.random.default_rng(9)
        c = 100 + np.cumsum(rng.normal(0, 0.8, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)
        self.assertTrue(sig["mt_template"].dtype == bool)

    def test_no_lookahead(self):
        # template at bar k must be identical when computed on data
        # truncated at k
        n = 3000
        rng = np.random.default_rng(11)
        c = 100 + np.cumsum(rng.normal(0, 1.0, n))
        full = indicators.add_indicators(_frame(n, c))
        for k in (1500, 2999):
            trunc = indicators.add_indicators(_frame(n, c)[:k + 1])
            self.assertEqual(full["mt_template"].iloc[k],
                             trunc["mt_template"].iloc[k])

    def test_registration_and_risk(self):
        import strategies.minervini_trend as M
        self.assertEqual(M.SPEC.slug, "minervini_trend")
        self.assertEqual(risk.WARMUP, 4900)
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertTrue(risk.RISK.allow_longs)


if __name__ == "__main__":
    unittest.main()
