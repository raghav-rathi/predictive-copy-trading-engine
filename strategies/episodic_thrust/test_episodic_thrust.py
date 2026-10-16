"""Episodic-pivot tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.episodic_thrust import indicators, risk, signals


def _coil_frame(n=160, j=120):
    """Tight low-volume coil (bars j-30..j-1) after normal volume, then a
    textbook thrust bar at j. Crafted OHLCV is written explicitly."""
    c = np.full(n, 100.0)
    df = pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": c, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.where(np.arange(n) < j - 30, 200.0, 80.0),
    })
    # tighten the coil: range 0.8
    for i in range(j - 30, j):
        df.loc[i, ["o", "h", "l", "c"]] = [100.1, 100.8, 100.0, 100.2]
    # thrust bar: 4-point range, 2x volume, close near high, above base
    df.loc[j, ["o", "h", "l", "c", "v"]] = [100.2, 104.0, 100.0, 103.5, 300.0]
    return df, j


class TestEpisodicThrust(unittest.TestCase):
    def test_thrust_detected(self):
        df, j = _coil_frame()
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["thrust"].iloc[j])
        self.assertFalse(ind["thrust"].iloc[:j].any())

    def test_no_thrust_when_volume_weak(self):
        df, j = _coil_frame()
        df.loc[j, "v"] = 100.0
        ind = indicators.add_indicators(df)
        self.assertFalse(ind["thrust"].iloc[j])

    def test_no_thrust_when_base_not_tight(self):
        df, j = _coil_frame()
        for i in range(j - 30, j):  # wide, non-neglect base
            df.loc[i, ["o", "h", "l", "c"]] = [100.0, 104.0, 96.0, 100.0]
        ind = indicators.add_indicators(df)
        self.assertFalse(ind["thrust"].iloc[j])

    def test_no_thrust_when_close_mid_range(self):
        df, j = _coil_frame()
        df.loc[j, ["o", "h", "l", "c"]] = [100.2, 104.0, 100.0, 101.0]
        ind = indicators.add_indicators(df)
        self.assertFalse(ind["thrust"].iloc[j])

    def test_long_exit_first_down_bar_after_three_ups(self):
        df, j = _coil_frame()
        df.loc[j + 1, ["o", "h", "l", "c"]] = [103.0, 104.0, 102.0, 104.0]
        df.loc[j + 2, ["o", "h", "l", "c"]] = [104.0, 105.0, 103.0, 104.5]
        df.loc[j + 3, ["o", "h", "l", "c"]] = [104.5, 106.0, 104.0, 105.0]
        df.loc[j + 4, ["o", "h", "l", "c"]] = [105.0, 105.5, 103.0, 104.0]
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].iloc[j])
        self.assertTrue(sig["long_exit"].iloc[j + 4])
        self.assertFalse(sig["long_exit"].iloc[j + 1: j + 4].any())

    def test_no_exit_after_only_two_ups(self):
        # the thrust bar itself is an up bar, so one more up bar then a
        # down bar is only a 2-bar streak -> no exit
        df, j = _coil_frame()
        df.loc[j + 1, ["o", "h", "l", "c"]] = [103.0, 104.0, 102.0, 104.0]
        df.loc[j + 2, ["o", "h", "l", "c"]] = [104.0, 105.0, 103.0, 103.5]
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(sig["long_exit"].iloc[j + 2])

    def test_shorts_disabled(self):
        df, j = _coil_frame()
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(sig["short_entry"].any())
        self.assertFalse(risk.RISK.allow_shorts)

    def test_signal_columns_bool_no_nan(self):
        n = 200
        rng = np.random.default_rng(31)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        o = np.concatenate([[c[0]], c[:-1]])
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": np.maximum(o, c) + 0.05, "l": np.minimum(o, c) - 0.05,
            "c": c, "v": rng.uniform(50, 150, n),
        })
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_no_lookahead(self):
        n = 200
        rng = np.random.default_rng(37)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        o = np.concatenate([[c[0]], c[:-1]])
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": o, "h": np.maximum(o, c) + 0.05, "l": np.minimum(o, c) - 0.05,
            "c": c, "v": rng.uniform(50, 150, n),
        })
        full = signals.add_signals(indicators.add_indicators(df))
        cut = signals.add_signals(indicators.add_indicators(df.iloc[:-1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:-1].reset_index(drop=True),
                cut[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        from strategies import episodic_thrust
        from strategies.registry import REGISTRY
        self.assertEqual(episodic_thrust.SPEC.slug, "episodic_thrust")
        self.assertIn("episodic_thrust", REGISTRY)
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
