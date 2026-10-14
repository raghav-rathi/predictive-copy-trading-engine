"""Opening-range breakout tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.opening_range_breakout import indicators, risk, signals


def _frame(days=10, seed=41):
    rng = np.random.default_rng(seed)
    n = days * 24
    t0 = 1_699_920_000_000  # 2023-11-14 00:00:00 UTC (midnight-aligned)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    c = np.empty(n)
    for d in range(days):
        base = 100 + d * 0.5
        # tight first 4h, then a breakout rally
        c[d * 24:d * 24 + 4] = base + rng.normal(0, 0.05, 4)
        c[d * 24 + 4:d * 24 + 24] = base + np.linspace(0.1, 2.0, 20) + rng.normal(0, 0.1, 20)
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) + 0.03
    l = np.minimum(o, c) - 0.03
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestORB(unittest.TestCase):
    def test_or_nan_during_formation(self):
        df = indicators.add_indicators(_frame())
        # NaN exactly on the first 4 bars of each UTC day (OR forming)
        is_or_bar = (np.arange(len(df)) % 24) < 4
        self.assertTrue(df.loc[is_or_bar, "or_high"].isna().all())
        self.assertTrue(df.loc[~is_or_bar, "or_high"].notna().all())

    def test_or_values_correct(self):
        df = indicators.add_indicators(_frame())
        day0 = df.iloc[4:24]
        expect_high = df.iloc[:4]["h"].max()
        self.assertAlmostEqual(day0["or_high"].iloc[0], expect_high)

    def test_breakout_generates_longs(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_no_entries_before_or_complete(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        # entries can only fire once the OR is known
        entered = df[df["long_entry"] | df["short_entry"]]
        self.assertTrue(entered["or_high"].notna().all())

    def test_no_signal_exits(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertEqual(int(df["long_exit"].sum() + df["short_exit"].sum()), 0)

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertEqual(risk.RISK.stop_atr_mult, 1.0)


if __name__ == "__main__":
    unittest.main()
