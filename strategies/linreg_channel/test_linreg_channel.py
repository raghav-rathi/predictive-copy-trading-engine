"""Regression-channel tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.linreg_channel import indicators, risk, signals

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


def _frame_ohlc(o, h, l, c):
    n = len(c)
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": np.asarray(o, dtype=float),
            "h": np.asarray(h, dtype=float),
            "l": np.asarray(l, dtype=float),
            "c": np.asarray(c, dtype=float),
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestLinregChannel(unittest.TestCase):
    def test_lsma_on_straight_line(self):
        # on a perfect line the LSMA end-point equals the last close and
        # the band width collapses to ~0
        c = 100 + 0.5 * np.arange(200)
        df = indicators.add_indicators(_frame(c, spread=0.001))
        np.testing.assert_allclose(df["lr_lsma"].iloc[-1], c[-1], rtol=1e-6)
        self.assertLess(df["lr_upper"].iloc[-1] - df["lr_lower"].iloc[-1], 0.5)

    def test_lsma_matches_numpy_polyfit(self):
        rng = np.random.default_rng(91)
        c = 100 + np.cumsum(rng.normal(0, 0.6, 200))
        df = indicators.add_indicators(_frame(c))
        i = 150
        w = c[i - 49 : i + 1]
        a, b = np.polyfit(np.arange(50), w, 1)
        np.testing.assert_allclose(df["lr_lsma"].iloc[i], a * 49 + b, rtol=1e-9)

    def test_lower_tag_detected(self):
        # force a dip that tags the lower band and closes back inside
        rng = np.random.default_rng(92)
        c = 100 + rng.normal(0, 0.2, 120).cumsum() * 0.3
        df0 = indicators.add_indicators(_frame(c))
        lower = float(df0["lr_lower"].iloc[119])
        close = float(df0["c"].iloc[119])
        self.assertLess(lower, close)  # sanity: band sits below price here
        c2 = c.copy()
        c2 = np.append(c2, [close - 0.5])  # dip below the band...
        df1 = indicators.add_indicators(_frame(c2))
        # ...then rebuild the frame with the dip low but close back inside
        o = np.append(np.concatenate([[c[0]], c[:-1]]), [close - 0.4])
        h = np.append(np.maximum(c, np.concatenate([[c[0]], c[:-1]])) + 0.2, [close + 0.1])
        l = np.append(np.minimum(c, np.concatenate([[c[0]], c[:-1]])) - 0.2, [lower - 0.3])
        cc = np.append(c, [close + 0.05])
        df2 = _run(_frame_ohlc(o, h, l, cc))
        self.assertTrue(bool(df2["tag_low"].iloc[-1]))
        self.assertTrue(bool(df2["long_entry"].iloc[-1]))

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(93)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 300))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        trunc = _run(_frame(c[:200]))
        np.testing.assert_allclose(
            df["lr_lsma"].iloc[199], trunc["lr_lsma"].iloc[199], rtol=1e-12
        )


if __name__ == "__main__":
    unittest.main()
