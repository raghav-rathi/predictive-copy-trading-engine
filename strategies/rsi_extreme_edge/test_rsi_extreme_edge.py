"""RSI extreme-edge unit tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_extreme_edge import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.full(n, float(v))}
    )


def _squeeze_up(n=60, seed=9):
    """Relentless rally: RSI pinned above 90, then a pullback."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:40] = 100.0 + 1.2 * np.arange(40)
    c[40:] = c[39] - 0.8 * np.arange(1, n - 40 + 1) + rng.normal(0, 0.05, n - 40)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.2
    l = np.minimum(o, c) - 0.2
    return _ohlcv(o, h, l, c)


def _squeeze_dn(n=60, seed=9):
    """Relentless selloff: RSI pinned below 10, then a bounce."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:40] = 100.0 - 1.2 * np.arange(40)
    c[40:] = c[39] + 0.8 * np.arange(1, n - 40 + 1) + rng.normal(0, 0.05, n - 40)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.2
    l = np.minimum(o, c) - 0.2
    return _ohlcv(o, h, l, c)


class TestRsiExtremeEdge(unittest.TestCase):
    def test_rsi_pinned_above_90_in_squeeze(self):
        df = indicators.add_indicators(_squeeze_up())
        rsi = df["rsi"].iloc[20:39].dropna()
        self.assertTrue((rsi > 90).all(), rsi.min())

    def test_short_entry_on_cross_back_below_90(self):
        df = signals.add_signals(indicators.add_indicators(_squeeze_up()))
        entries = df.index[df["short_entry"]]
        self.assertTrue(len(entries) > 0)
        for i in entries:
            self.assertGreater(df["rsi"].iloc[i - 1], 90)
            self.assertLess(df["rsi"].iloc[i], 90)
        # after the warmup rally: no longs in a pure short setup
        self.assertFalse(df["long_entry"].iloc[20:].any())

    def test_long_entry_on_cross_back_above_10(self):
        df = signals.add_signals(indicators.add_indicators(_squeeze_dn()))
        entries = df.index[df["long_entry"]]
        self.assertTrue(len(entries) > 0)
        for i in entries:
            self.assertLess(df["rsi"].iloc[i - 1], 10)
            self.assertGreaterEqual(df["rsi"].iloc[i], 10)
        # after the warmup selloff: no shorts in a pure long setup
        self.assertFalse(df["short_entry"].iloc[20:].any())

    def test_no_signal_while_pinned(self):
        # RSI above 90 with no cross-back yet: must not fire mid-excursion
        n = 50
        c = 100.0 + 1.2 * np.arange(n)
        o = np.concatenate([[c[0]], c[:-1]])
        df = signals.add_signals(
            indicators.add_indicators(_ohlcv(o, c + 0.2, c - 0.2, c)))
        pinned = df["rsi"].iloc[15:] > 90
        if pinned.all():
            self.assertFalse(df["short_entry"].iloc[15:].any())

    def test_coin_filter(self):
        df = signals.add_signals(indicators.add_indicators(_squeeze_up()),
                                 coin="BTC")
        self.assertTrue(df["short_entry"].any())  # default: both allowed
        orig = dict(signals.COIN_FILTER)
        try:
            signals.COIN_FILTER["BTC"] = ("long",)
            df2 = signals.add_signals(indicators.add_indicators(_squeeze_up()),
                                      coin="BTC")
            self.assertFalse(df2["short_entry"].any())
        finally:
            signals.COIN_FILTER.update(orig)

    def test_no_lookahead(self):
        raw = _squeeze_up()
        df_full = signals.add_signals(indicators.add_indicators(raw))
        df_tr = signals.add_signals(indicators.add_indicators(raw.iloc[:-1]))
        for col in ("rsi", "atr", "long_entry", "short_entry"):
            a = df_full[col].iloc[:-1].fillna(-999.0).to_numpy()
            b = df_tr[col].fillna(-999.0).to_numpy()
            self.assertTrue(np.allclose(a, b, equal_nan=True),
                            f"lookahead leak in {col}")

    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertAlmostEqual(risk.RISK.target_atr_mult, 2.25)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertGreaterEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
