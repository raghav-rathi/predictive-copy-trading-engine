"""Turtle Soup tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.turtle_soup import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _false_breakdown(n=300, seed=7):
    """Drift down, 8-bar flat bottom (ages the prior low), one new-low
    signal bar, then close back above the violated low -> long trap fade."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:180] = 120 - 0.15 * np.arange(180) + rng.normal(0, 0.15, 180)
    bot = c[179]
    c[180:188] = bot + rng.normal(0, 0.05, 8)
    c[188] = c[187] - 1.2  # signal bar: new 20-bar low
    c[189:] = c[188] + 0.35 * np.arange(1, n - 188) + rng.normal(0, 0.1, n - 189)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.15
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.15
    l[188] = c[188] - 0.1  # guarantee the undercut
    return _ohlcv(o, h, l, c)


def _false_breakout(n=300, seed=9):
    """Mirror image: drift up, flat top, new-high signal bar, fade back
    below -> short."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:180] = 80 + 0.15 * np.arange(180) + rng.normal(0, 0.15, 180)
    top = c[179]
    c[180:188] = top + rng.normal(0, 0.05, 8)
    c[188] = c[187] + 1.2  # signal bar: new 20-bar high
    c[189:] = c[188] - 0.35 * np.arange(1, n - 188) + rng.normal(0, 0.1, n - 189)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.15
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.15
    h[188] = c[188] + 0.1
    return _ohlcv(o, h, l, c)


class TestTurtleSoup(unittest.TestCase):
    def test_false_breakdown_generates_long_only(self):
        df = signals.add_signals(indicators.add_indicators(_false_breakdown()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_false_breakout_generates_short_only(self):
        df = signals.add_signals(indicators.add_indicators(_false_breakout()))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_entry_within_3_bars_and_above_level(self):
        raw = indicators.add_indicators(_false_breakdown())
        df = signals.add_signals(raw)
        sig_idx = raw.index[raw["sig_low_bar"]]
        self.assertGreater(len(sig_idx), 0)
        lvl = raw["prev_low20"]
        for i in df.index[df["long_entry"]]:
            recent = sig_idx[(sig_idx < i) & (sig_idx >= i - 3)]
            self.assertGreater(len(recent), 0)
            s = recent[-1]
            self.assertGreater(df["c"].iloc[i], lvl.iloc[s])

    def test_no_lookahead_truncation(self):
        full = _false_breakdown()
        ind_full = indicators.add_indicators(full)
        for i in (150, 220):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("prev_low20", "prev_high20", "sig_low_bar", "sig_high_bar"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                if isinstance(a, (bool, np.bool_)):
                    self.assertEqual(bool(a), bool(b))
                else:
                    self.assertTrue((pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_false_breakdown()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertEqual(risk.RISK.target_atr_mult, 2.5)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertGreater(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
