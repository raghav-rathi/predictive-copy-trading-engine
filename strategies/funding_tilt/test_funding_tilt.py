"""Funding tilt tests. Network-free (synthetic funding series)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.funding_tilt import indicators, risk, signals


def _frame(n=400, seed=29):
    rng = np.random.default_rng(seed)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.005, n)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    df = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})
    # synthetic funding: calm, then extremely positive, then extremely negative
    fr = np.concatenate([
        rng.normal(0.0001, 0.0002, 200),
        np.full(100, 0.005),
        np.full(100, -0.005),
    ])
    funding = pd.Series(fr, index=t)
    return df, funding


class TestFundingTilt(unittest.TestCase):
    def test_zscore_flags_extremes(self):
        df, funding = _frame()
        df = indicators.add_indicators(df, funding=funding)
        self.assertTrue((df.iloc[220:290]["fund_z"] > 2.0).any())
        self.assertTrue((df.iloc[320:390]["fund_z"] < -2.0).any())

    def test_crowded_longs_trigger_shorts(self):
        df, funding = _frame()
        df = signals.add_signals(indicators.add_indicators(df, funding=funding))
        self.assertGreater(int(df.iloc[220:290]["short_entry"].sum()), 0)

    def test_crowded_shorts_trigger_longs(self):
        df, funding = _frame()
        df = signals.add_signals(indicators.add_indicators(df, funding=funding))
        self.assertGreater(int(df.iloc[320:390]["long_entry"].sum()), 0)

    def test_exits_when_crowding_resolves(self):
        df, funding = _frame()
        df = signals.add_signals(indicators.add_indicators(df, funding=funding))
        calm = df.iloc[50:150]
        self.assertTrue((calm["long_exit"] | calm["short_exit"]).any())

    def test_requires_coin_or_funding(self):
        df, _ = _frame()
        with self.assertRaises(ValueError):
            indicators.add_indicators(df)

    def test_clean_booleans(self):
        df, funding = _frame()
        df = signals.add_signals(indicators.add_indicators(df, funding=funding))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.target_atr_mult, 2.0)
        self.assertEqual(risk.RISK.max_hold_bars, 72)


if __name__ == "__main__":
    unittest.main()
