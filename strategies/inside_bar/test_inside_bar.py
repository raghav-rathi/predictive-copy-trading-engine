"""Inside-bar breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.inside_bar import indicators, risk, signals


def _frame(n, c):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _uptrend_with_setup(n=300):
    """Uptrend, then a crafted mother/inside/breakout sequence at the tail."""
    c = 60.0 + 0.15 * np.arange(n)  # trend lands near ~104 at the tail
    df = _frame(n, c)
    j = n - 4  # mother bar
    df.loc[j, ["h", "l", "o", "c"]] = [112.0, 104.0, 106.0, 108.0]
    df.loc[j + 1, ["h", "l", "o", "c"]] = [110.0, 106.0, 107.0, 109.0]  # inside
    df.loc[j + 2, ["h", "l", "o", "c"]] = [113.0, 107.0, 108.0, 112.0]  # breakout
    return df, j


class TestInsideBar(unittest.TestCase):
    def test_inside_bar_detected(self):
        df, j = _uptrend_with_setup()
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["inside"].iloc[j + 1])
        self.assertFalse(ind["inside"].iloc[j])
        self.assertFalse(ind["inside"].iloc[j + 2])

    def test_mother_extremes_are_prior_bar(self):
        df, j = _uptrend_with_setup()
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["mother_high"].iloc[j + 1], 112.0)
        self.assertAlmostEqual(ind["mother_low"].iloc[j + 1], 104.0)

    def test_uptrend_bias_is_long(self):
        n = 300
        c = 110.0 + 0.15 * np.arange(n)
        ind = indicators.add_indicators(_frame(n, c))
        tail = ind.iloc[-50:]
        self.assertTrue(tail["long_bias"].all())
        self.assertFalse(tail["short_bias"].any())

    def test_long_entry_fires_on_mother_high_break(self):
        df, j = _uptrend_with_setup()
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].iloc[j + 2])
        # no entry on the inside bar itself or before the setup
        self.assertFalse(sig["long_entry"].iloc[j + 1])
        self.assertFalse(sig["long_entry"].iloc[: j - 1].any())

    def test_no_entry_without_break(self):
        df, j = _uptrend_with_setup()
        df.loc[j + 2, ["h", "l", "o", "c"]] = [109.0, 106.5, 107.0, 108.0]  # stalls
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(sig["long_entry"].iloc[j + 1: j + 4].any())

    def test_setup_expires_after_two_bars(self):
        df, j = _uptrend_with_setup()
        # stalling bar j+2 must NOT itself be an inside bar (h above prior high)
        df.loc[j + 2, ["h", "l", "o", "c"]] = [110.5, 106.5, 107.0, 108.0]
        # breakout attempt on bar j+4 (3 bars after the watch window) -> expired
        df.loc[j + 3, ["h", "l", "o", "c"]] = [113.0, 107.0, 108.0, 110.0]
        df.loc[j + 4, ["h", "l", "o", "c"]] = [114.0, 107.0, 108.0, 112.0]
        sig = signals.add_signals(indicators.add_indicators(df), expiry=2)
        self.assertFalse(sig["long_entry"].iloc[j + 4])
        self.assertTrue(sig["long_entry"].iloc[j + 3])  # j+3 is inside the watch

    def test_short_entry_mirror(self):
        n = 300
        c = 150.0 - 0.15 * np.arange(n)  # downtrend lands near ~106 at the tail
        df = _frame(n, c)
        j = n - 4
        df.loc[j, ["h", "l", "o", "c"]] = [110.0, 102.0, 108.0, 104.0]  # mother
        df.loc[j + 1, ["h", "l", "o", "c"]] = [108.0, 104.0, 107.0, 105.0]  # inside
        df.loc[j + 2, ["h", "l", "o", "c"]] = [107.0, 100.0, 106.0, 102.0]  # breakdown
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["short_entry"].iloc[j + 2])
        self.assertFalse(sig["long_entry"].iloc[j + 2])

    def test_signal_columns_bool_no_nan(self):
        n = 250
        rng = np.random.default_rng(7)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_no_lookahead(self):
        n = 300
        rng = np.random.default_rng(11)
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
        from strategies import inside_bar
        from strategies.registry import REGISTRY
        self.assertEqual(inside_bar.SPEC.slug, "inside_bar")
        self.assertIn("inside_bar", REGISTRY)
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
