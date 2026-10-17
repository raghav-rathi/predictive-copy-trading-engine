"""VIDYA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vidya import indicators, risk, signals

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


class TestVidya(unittest.TestCase):
    def test_vidya_matches_independent_loop(self):
        # independent loop recomputation of the VIDYA recursion
        rng = np.random.default_rng(41)
        c = 100 + np.cumsum(rng.normal(0, 0.5, 300))
        df = indicators.add_indicators(_frame(c))
        d = np.diff(c, prepend=c[0])
        up = pd.Series(np.clip(d, 0, None)).rolling(9, min_periods=9).sum().to_numpy()
        dn = pd.Series(np.clip(-d, 0, None)).rolling(9, min_periods=9).sum().to_numpy()
        denom = np.where(up + dn == 0, np.nan, up + dn)
        cmo = np.where(np.isnan(denom), 0.0, (up - dn) / denom)
        f = 2.0 / 13
        alpha = np.clip(f * np.abs(cmo), 0, 1)
        exp = np.full_like(c, np.nan)
        exp[9] = c[9]
        for i in range(10, len(c)):
            exp[i] = exp[i - 1] + alpha[i] * (c[i] - exp[i - 1])
        np.testing.assert_allclose(df["vidya"].to_numpy()[10:], exp[10:], rtol=1e-9)

    def test_adaptive_speed(self):
        # in a strong trend |CMO| ~ 1: VIDYA hugs price; in chop it lags
        trend = 100 + 0.8 * np.arange(300)
        rng = np.random.default_rng(42)
        chop = 100 + np.cumsum(rng.normal(0, 0.5, 300))
        vt = indicators.add_indicators(_frame(trend))["vidya"].iloc[-1]
        vc = indicators.add_indicators(_frame(chop))["vidya"].iloc[-1]
        # trend VIDYA must sit within 2% of the final close; chop VIDYA is
        # just required to be finite (lag is the point)
        self.assertLess(abs(vt - trend[-1]) / trend[-1], 0.02)
        self.assertTrue(np.isfinite(vc))

    def test_trend_entries_fire(self):
        rng = np.random.default_rng(43)
        c1 = 100 + rng.normal(0, 0.4, 150).cumsum()
        c2 = c1[-1] + 0.7 * np.arange(250)
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertTrue(bool(df["long_entry"].any()))

    def test_chop_fewer_entries_than_plain_ma_cross(self):
        # adaptivity claim: in chop VIDYA slows down and crosses less than a
        # plain EMA(12)/SMA(50) cross on the same data
        rng = np.random.default_rng(44)
        c = 100 + rng.normal(0, 0.05, 400)
        df = _run(_frame(c))
        vidya_entries = int(df["long_entry"].sum() + df["short_entry"].sum())
        cs = pd.Series(c)
        ema = cs.ewm(span=12, adjust=False).mean()
        sma = cs.rolling(50).mean()
        ma_entries = int(
            (
                ((ema > sma) & (ema.shift(1) <= sma.shift(1)))
                | ((ema < sma) & (ema.shift(1) >= sma.shift(1)))
            ).sum()
        )
        self.assertLess(vidya_entries, ma_entries)

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(45)
        c = 100 + np.cumsum(rng.normal(0, 0.6, 400))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        trunc = _run(_frame(c[:250]))
        np.testing.assert_allclose(
            df["vidya"].iloc[249], trunc["vidya"].iloc[249], rtol=1e-12
        )


if __name__ == "__main__":
    unittest.main()
