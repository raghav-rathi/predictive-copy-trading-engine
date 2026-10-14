"""Supertrend tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.supertrend import indicators, risk, signals


def _vshape(n=250, seed=11, first_drift=-0.006, second_drift=0.006):
    """Down then up: forces a Supertrend flip to +1 mid-series."""
    rng = np.random.default_rng(seed)
    half = n // 2
    drifts = np.concatenate([
        np.full(half, first_drift), np.full(n - half, second_drift)
    ])
    c = 100 * np.exp(np.cumsum(rng.normal(drifts, 0.008, n)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.003
    l = np.minimum(o, c) * 0.997
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


def _series(n=500, drift=0.003, seed=11):
    return _vshape(n, seed, -abs(drift), abs(drift))


class TestSupertrend(unittest.TestCase):
    def test_uptrend_longs(self):
        df = signals.add_signals(indicators.add_indicators(_vshape(first_drift=-0.006, second_drift=0.006)))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_downtrend_shorts(self):
        df = signals.add_signals(indicators.add_indicators(_vshape(first_drift=0.006, second_drift=-0.006)))
        self.assertGreater(int(df["short_entry"].sum()), 0)

    def test_flips_are_exits(self):
        # every long exit coincides with a flip to down
        df = signals.add_signals(indicators.add_indicators(_series()))
        exits = df.index[df["long_exit"]]
        for i in exits[:10]:
            self.assertEqual(df["st_dir"].iloc[i], -1)

    def test_entries_need_adx_regime(self):
        df = indicators.add_indicators(_series())
        df = signals.add_signals(df)
        entered = df[df["long_entry"] | df["short_entry"]]
        self.assertTrue(((entered["adx"] > 20.0) | entered["adx"].isna()).all())

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_series()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertTrue(risk.RISK.allow_shorts)


if __name__ == "__main__":
    unittest.main()
