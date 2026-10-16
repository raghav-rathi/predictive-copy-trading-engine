"""Raschke Tail tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.raschke_tail import indicators, risk, signals


def _frame(n, c):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _with_bullish_tail(n=80, j=50):
    """Decline into a textbook bullish tail bar at j."""
    c = 110.0 - 0.2 * np.arange(n)
    df = _frame(n, c)
    # tail: small body, long lower wick, fresh 20-bar low
    df.loc[j, ["o", "h", "l", "c"]] = [100.0, 100.5, 96.0, 100.2]
    return df, j


def _with_bearish_tail(n=80, j=50):
    """Rally into a textbook bearish tail bar at j."""
    c = 90.0 + 0.2 * np.arange(n)
    df = _frame(n, c)
    df.loc[j, ["o", "h", "l", "c"]] = [100.0, 104.0, 99.5, 99.8]
    return df, j


class TestRaschkeTail(unittest.TestCase):
    def test_bullish_tail_detected(self):
        df, j = _with_bullish_tail()
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["bullish_tail"].iloc[j])
        self.assertFalse(ind["bearish_tail"].iloc[j])
        self.assertFalse(ind["bullish_tail"].iloc[:j].any())

    def test_bearish_tail_detected(self):
        df, j = _with_bearish_tail()
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["bearish_tail"].iloc[j])
        self.assertFalse(ind["bullish_tail"].iloc[j])

    def test_dogi_noise_rejected(self):
        # tiny bar with tail geometry but range below 0.75x ATR -> no tail
        n = 80
        c = 100.0 + np.zeros(n)
        df = _frame(n, c)
        j = 50
        df.loc[j, ["o", "h", "l", "c"]] = [99.96, 99.99, 99.93, 99.97]
        ind = indicators.add_indicators(df)
        self.assertFalse(ind["bullish_tail"].iloc[j])

    def test_long_entry_on_tail_high_break(self):
        df, j = _with_bullish_tail()
        df.loc[j + 1, ["h", "l", "o", "c"]] = [101.0, 99.5, 100.0, 100.8]
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].iloc[j + 1])
        # tail bar itself never triggers
        self.assertFalse(sig["long_entry"].iloc[j])

    def test_entry_window_expires(self):
        df, j = _with_bullish_tail()
        for k in (1, 2, 3):
            df.loc[j + k, ["h", "l", "o", "c"]] = [100.0, 99.0, 99.5, 99.8]
        df.loc[j + 4, ["h", "l", "o", "c"]] = [102.0, 99.0, 99.5, 101.0]
        sig = signals.add_signals(indicators.add_indicators(df), window=3)
        self.assertFalse(sig["long_entry"].iloc[j + 4])
        self.assertFalse(sig["long_entry"].iloc[j + 1: j + 4].any())

    def test_short_entry_mirror(self):
        df, j = _with_bearish_tail()
        df.loc[j + 2, ["h", "l", "o", "c"]] = [100.5, 98.5, 100.0, 99.0]
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["short_entry"].iloc[j + 2])
        self.assertFalse(sig["long_entry"].iloc[j + 2])

    def test_signal_columns_bool_no_nan(self):
        n = 200
        rng = np.random.default_rng(21)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_no_lookahead(self):
        n = 200
        rng = np.random.default_rng(23)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        full = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        cut = signals.add_signals(indicators.add_indicators(_frame(n, c).iloc[:-1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:-1].reset_index(drop=True),
                cut[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        from strategies import raschke_tail
        from strategies.registry import REGISTRY
        self.assertEqual(raschke_tail.SPEC.slug, "raschke_tail")
        self.assertIn("raschke_tail", REGISTRY)
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
