"""Wyckoff spring/upthrust tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wyckoff_spring import indicators, risk, signals


def _ohlcv(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.asarray(v, float)}
    )


def _range_frame(n=120, poke="spring"):
    """Flat 100-110 range, then a poke below/above support/resistance."""
    c = np.full(n, 105.0)
    o = c.copy()
    h = np.full(n, 107.0)
    l = np.full(n, 103.0)
    v = np.full(n, 100.0)
    j = n - 5  # poke near the end
    if poke == "spring":
        l[j] = 101.0   # below range low 103
        c[j] = 104.0   # closes back inside
        v[j] = 500.0   # volume spike
    else:
        h[j] = 109.0
        c[j] = 106.0
        v[j] = 500.0
    return _ohlcv(o, h, l, c, v)


class TestWyckoffSpring(unittest.TestCase):
    def test_spring_detected(self):
        df = indicators.add_indicators(_range_frame(poke="spring"))
        self.assertTrue(df["spring"].iloc[-5])
        self.assertTrue(df["vol_ok"].iloc[-5])

    def test_upthrust_detected(self):
        df = indicators.add_indicators(_range_frame(poke="upthrust"))
        self.assertTrue(df["upthrust"].iloc[-5])
        self.assertFalse(df["spring"].iloc[-5])

    def test_poke_without_close_back_inside_is_not_spring(self):
        df0 = _range_frame(poke="spring")
        df0.loc[df0.index[-5], "c"] = 101.5  # closes BELOW support: real breakdown
        df = indicators.add_indicators(df0)
        self.assertFalse(df["spring"].iloc[-5])

    def test_range_edges_use_prior_bars_only(self):
        # range_low at bar i must not include bar i's low (no lookahead)
        n = 120
        df = indicators.add_indicators(_range_frame(n, poke="spring"))
        # the engineered low (101) must not leak into the range edge itself
        self.assertAlmostEqual(df["range_low"].iloc[-5], 103.0, places=9)

    def test_long_entry_and_objective_exit(self):
        sig = signals.add_signals(indicators.add_indicators(_range_frame(poke="spring")))
        self.assertTrue(sig["long_entry"].iloc[-5])
        # after the spring, a close at the range top exits the long
        df2 = _range_frame(poke="spring").copy()
        df2.loc[df2.index[-1], "c"] = 107.5
        sig2 = signals.add_signals(indicators.add_indicators(df2))
        self.assertTrue(sig2["long_exit"].iloc[-1])

    def test_quiet_poke_needs_volume(self):
        df0 = _range_frame(poke="spring")
        df0.loc[df0.index[-5], "v"] = 50.0  # below average: no confirmation
        sig = signals.add_signals(indicators.add_indicators(df0))
        self.assertFalse(sig["long_entry"].iloc[-5])

    def test_signal_columns_bool_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_range_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.0)
        self.assertEqual(risk.WARMUP, 70)


if __name__ == "__main__":
    unittest.main()
