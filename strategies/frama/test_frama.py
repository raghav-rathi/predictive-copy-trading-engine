"""FRAMA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.frama import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.2):
    c = np.asarray(c, dtype=float)
    n = len(c)
    prev = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": prev,
            "h": np.maximum(c, prev) + spread,
            "l": np.minimum(c, prev) - spread,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestFrama(unittest.TestCase):
    def test_alpha_bounds(self):
        # alpha must always sit in [0.01, 1]; dimen in [1, 2]
        rng = np.random.default_rng(51)
        df = indicators.add_indicators(_frame(100 + np.cumsum(rng.normal(0, 1.0, 400))))
        d = df["frama_dimen"].dropna()
        self.assertTrue(bool(((d >= 1.0) & (d <= 2.0)).all()))

    def test_straight_trend_tracks_fast(self):
        # perfectly straight line => D -> 1 => alpha -> 1 => FRAMA == price
        c = 100 + 2.0 * np.arange(200)
        df = indicators.add_indicators(_frame(c, spread=0.01))
        tail = df["frama"].iloc[-20:].to_numpy()
        np.testing.assert_allclose(tail, c[-20:], rtol=0.02)

    def test_chop_flattens_frama(self):
        # jagged chop => D -> 2 => alpha ~ 0.01: FRAMA barely moves
        rng = np.random.default_rng(52)
        c = 100 + np.cumsum(rng.normal(0, 2.0, 300))
        df = indicators.add_indicators(_frame(c))
        f = df["frama"].dropna().to_numpy()
        self.assertLess(np.abs(np.diff(f[-30:])).mean(), np.abs(np.diff(c[-30:])).mean())

    def test_entries_fire_in_trend(self):
        rng = np.random.default_rng(53)
        c = np.concatenate([100 + rng.normal(0, 0.5, 150).cumsum(),
                            105 + 0.6 * np.arange(250)])
        df = _run(_frame(c))
        self.assertTrue(bool(df["long_entry"].any()))

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(54)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 400))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        trunc = _run(_frame(c[:250]))
        np.testing.assert_allclose(
            df["frama"].iloc[249], trunc["frama"].iloc[249], rtol=1e-12
        )


if __name__ == "__main__":
    unittest.main()
