"""Williams %R tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.williams_pct_r import indicators, risk, signals


def _frame(n, c, h=None, l=None):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.Series(np.asarray(h, float)) if h is not None else pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.Series(np.asarray(l, float)) if l is not None else pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _long_scenario():
    """Decline (pct_r pinned at -100), then a gentle rally so the
    -85 cross lands exactly 5 bars after the last -100 extreme."""
    n = 80
    c = np.array([100.0 - i if i <= 30 else 70.0 + 0.4 * (i - 30) for i in range(n)])
    h = c + 2.0
    l = c.copy()  # close at the low -> pct_r == -100 in the decline
    return _frame(n, c, h=h, l=l)


def _short_scenario():
    """Rally (pct_r pinned at 0), then a gentle decline so the -15
    cross lands exactly 5 bars after the last 0 extreme."""
    n = 80
    c = np.array([70.0 + i if i <= 30 else 100.0 - 0.4 * (i - 30) for i in range(n)])
    h = c.copy()  # close at the high -> pct_r == 0 in the rally
    l = c - 2.0
    return _frame(n, c, h=h, l=l)


class TestWilliamsPctR(unittest.TestCase):
    def test_pct_r_range_and_extremes(self):
        ind = indicators.add_indicators(_long_scenario())
        self.assertTrue(((ind["pct_r"] >= -100.0) & (ind["pct_r"] <= 0.0)).all())
        self.assertAlmostEqual(ind["pct_r"].iloc[20], -100.0)
        ind2 = indicators.add_indicators(_short_scenario())
        self.assertAlmostEqual(ind2["pct_r"].iloc[20], 0.0)

    def test_long_entry_fires_after_wait(self):
        sig = signals.add_signals(indicators.add_indicators(_long_scenario()))
        longs = sig.index[sig["long_entry"]].tolist()
        self.assertIn(35, longs)
        # nothing fires during the 5-bar wait after the -100 extreme
        self.assertFalse(sig["long_entry"].iloc[31:35].any())

    def test_short_entry_mirror(self):
        sig = signals.add_signals(indicators.add_indicators(_short_scenario()))
        shorts = sig.index[sig["short_entry"]].tolist()
        self.assertIn(35, shorts)
        self.assertFalse(sig["short_entry"].iloc[31:35].any())

    def test_since_extreme_counter_resets(self):
        ind = indicators.add_indicators(_long_scenario())
        self.assertAlmostEqual(ind["since_low_extreme"].iloc[20], 0.0)
        self.assertAlmostEqual(ind["since_low_extreme"].iloc[25], 0.0)
        self.assertAlmostEqual(ind["since_low_extreme"].iloc[35], 5.0)

    def test_long_exit_in_overbought_zone(self):
        n = 60
        c = 100.0 + np.arange(n)  # steep rally -> pct_r near 0
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c, h=c, l=c - 2.0)))
        self.assertTrue(sig["long_exit"].iloc[-1])
        self.assertFalse(sig["short_exit"].iloc[-1])

    def test_short_exit_in_oversold_zone(self):
        n = 60
        c = 100.0 - np.arange(n)  # steep decline -> pct_r near -100
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c, h=c + 2.0, l=c)))
        self.assertTrue(sig["short_exit"].iloc[-1])
        self.assertFalse(sig["long_exit"].iloc[-1])

    def test_signal_columns_bool_no_nan(self):
        n = 200
        rng = np.random.default_rng(41)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_no_lookahead(self):
        n = 200
        rng = np.random.default_rng(43)
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
        from strategies import williams_pct_r
        from strategies.registry import REGISTRY
        self.assertEqual(williams_pct_r.SPEC.slug, "williams_pct_r")
        self.assertIn("williams_pct_r", REGISTRY)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
