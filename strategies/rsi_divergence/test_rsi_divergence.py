"""RSI divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_divergence import indicators, risk, signals
from strategies.rsi_divergence.signals import (
    _bull_divergence, _bear_divergence, _fractal_pivots)


def _frame(n, c):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _div_frame():
    # hand-built frame: RSI column overridden to force a textbook
    # bullish divergence: price swing lows at 40 (98) and 60 (96),
    # RSI 28 then 32 (higher low, < 35); RSI re-crosses 30 after the
    # divergence is confirmed at bar 65 (pivot 60 + 5)
    n = 120
    c = np.full(n, 100.0)
    c[40], c[60] = 98.0, 96.0
    df = indicators.add_indicators(_frame(n, c))
    rsi = np.full(n, 50.0)
    rsi[40], rsi[60] = 28.0, 32.0
    rsi[61:66] = 25.0
    rsi[66:76] = np.linspace(25.0, 35.0, 10)  # crosses 30 ~bar 70
    df["rsi"] = rsi
    return df


class TestRSIDivergence(unittest.TestCase):
    def test_rsi_wilder_sane(self):
        n = 200
        c = 100.0 + 0.2 * np.arange(n)
        df = indicators.add_indicators(_frame(n, c))
        tail = df["rsi"].iloc[-20:].dropna()
        self.assertTrue(((tail >= 0) & (tail <= 100)).all())
        self.assertGreater(tail.mean(), 90.0)  # strong uptrend -> high RSI

    def test_bull_divergence_detected(self):
        lows = [40, 60]
        closes = np.full(120, 100.0)
        closes[40], closes[60] = 100.0, 96.0
        rsi = np.full(120, 50.0)
        rsi[40], rsi[60] = 28.0, 32.0
        self.assertTrue(_bull_divergence(lows, closes, rsi, 60))

    def test_bull_divergence_rejected_cases(self):
        lows = [40, 60]
        closes = np.full(120, 100.0)
        closes[40], closes[60] = 100.0, 96.0
        # RSI not oversold enough at the second low
        r1 = np.full(120, 50.0); r1[40], r1[60] = 30.0, 36.0
        self.assertFalse(_bull_divergence(lows, closes, r1, 60))
        # RSI makes a lower low (no divergence)
        r2 = np.full(120, 50.0); r2[40], r2[60] = 32.0, 28.0
        self.assertFalse(_bull_divergence(lows, closes, r2, 60))
        # price makes a higher low (no divergence)
        c3 = closes.copy(); c3[60] = 101.0
        r3 = np.full(120, 50.0); r3[40], r3[60] = 28.0, 32.0
        self.assertFalse(_bull_divergence(lows, c3, r3, 60))

    def test_bear_divergence_detected(self):
        highs = [40, 60]
        closes = np.full(120, 100.0)
        closes[40], closes[60] = 100.0, 104.0
        rsi = np.full(120, 50.0)
        rsi[40], rsi[60] = 72.0, 68.0
        self.assertTrue(_bear_divergence(highs, closes, rsi, 60))

    def test_confirmation_entry_fires(self):
        df = _div_frame()
        sig = signals.add_signals(df)
        longs = sig.index[sig["long_entry"]].tolist()
        # divergence confirmed at 65 (pivot 60 + 5); RSI re-crosses 30
        # between 65 and 85
        self.assertTrue(any(65 <= j <= 85 for j in longs),
                        f"no confirmed entry; got {longs[:6]}")

    def test_no_confirmation_no_entry(self):
        # same divergence but RSI never re-crosses 30 -> setup expires
        df = _div_frame()
        df["rsi"] = np.full(len(df), 50.0)
        df.loc[40, "rsi"] = 28.0
        df.loc[60, "rsi"] = 32.0  # divergence exists, no re-cross
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())

    def test_no_lookahead(self):
        n = 200
        rng = np.random.default_rng(23)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        df1 = indicators.add_indicators(_frame(n, c))
        sig1 = signals.add_signals(df1)
        df2 = indicators.add_indicators(_frame(2 * n, np.concatenate([c, c])))
        sig2 = signals.add_signals(df2)
        pd.testing.assert_series_equal(
            sig1["long_entry"], sig2["long_entry"].iloc[:n].reset_index(drop=True),
            check_names=False)

    def test_signal_columns_bool_no_nan(self):
        n = 300
        rng = np.random.default_rng(29)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 120)
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)

    def test_registration(self):
        import strategies.rsi_divergence as m
        from strategies.registry import REGISTRY
        self.assertIn("rsi_divergence", REGISTRY)
        self.assertIs(REGISTRY["rsi_divergence"], m.SPEC)


if __name__ == "__main__":
    unittest.main()
