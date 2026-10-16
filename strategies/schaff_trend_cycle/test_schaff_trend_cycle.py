"""Schaff Trend Cycle tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.schaff_trend_cycle import indicators, risk, signals


def _oscillating(n=2000, drift=0.0001, seed=7):
    # STC is an oscillator: on pure monotonic trends it pins high/low and
    # never crosses. An oscillating series (sine wave + drift) exercises
    # both the up-through-25 and down-through-75 turns.
    rng = np.random.default_rng(seed)
    c = (
        100
        * np.exp(np.cumsum(rng.normal(drift, 0.004, n)))
        * (1 + 0.03 * np.sin(2 * np.pi * np.arange(n) / 150))
    )
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestSchaffTrendCycle(unittest.TestCase):
    def test_long_entries_fire_on_oversold_turns(self):
        df = signals.add_signals(indicators.add_indicators(_oscillating()))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_short_entries_fire_on_overbought_turns(self):
        df = signals.add_signals(indicators.add_indicators(_oscillating()))
        self.assertGreater(int(df["short_entry"].sum()), 0)

    def test_stc_bounded_zero_to_hundred(self):
        df = indicators.add_indicators(_oscillating())
        post = df["stc"].iloc[risk.WARMUP:].dropna()
        self.assertTrue(len(post) > 0)
        self.assertGreaterEqual(post.min(), 0)
        self.assertLessEqual(post.max(), 100)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_oscillating()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_no_lookahead(self):
        df_full = signals.add_signals(indicators.add_indicators(_oscillating()))
        idx = df_full.index[df_full["long_entry"]]
        self.assertTrue(len(idx) > 0)
        for i in idx[:5]:
            recomputed = signals.add_signals(
                indicators.add_indicators(df_full.iloc[: i + 1])
            )
            # entry at bar i must be reproducible from data through bar i
            self.assertTrue(bool(recomputed["long_entry"].iloc[-1]))
            # and it is a genuine cross: stc_s formed without the bar ahead
            self.assertLess(df_full["stc_s"].iloc[i - 1], 25 + 1e-9)
            self.assertGreaterEqual(df_full["stc_s"].iloc[i], 25 - 1e-9)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.WARMUP, 200)
        # lookback chain: macd 26 + stoch 50 + ema23 + ema50 + ema10 ≈ 159
        self.assertGreater(risk.WARMUP, 109)


if __name__ == "__main__":
    unittest.main()
