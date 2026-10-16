"""Fisher Transform reversal tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fisher_transform import indicators, risk, signals


def _oscillate(n=1200, drift=0.00005, seed=7):
    """Oscillating series: fisher crosses its lagged trigger repeatedly."""
    rng = np.random.default_rng(seed)
    base = 100 * np.exp(np.cumsum(rng.normal(drift, 0.002, n)))
    c = base * (1 + 0.03 * np.sin(2 * np.pi * np.arange(n) / 60))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


def _spike(n=500, seed=11):
    """Flat, then a sharp sustained ramp: pushes fisher past +2.5."""
    rng = np.random.default_rng(seed)
    c = np.full(n, 100.0)
    for i in range(200, 210):
        c[i] = c[i - 1] * 1.03
    c[210:] = c[209]
    c = c * np.exp(np.cumsum(rng.normal(0, 0.0005, n)))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


class TestFisherTransform(unittest.TestCase):
    def test_oscillating_series_fires_both_sides(self):
        df = signals.add_signals(indicators.add_indicators(_oscillate()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertGreater(int(df["short_entry"].sum()), 0)

    def test_exits_fire(self):
        df = signals.add_signals(indicators.add_indicators(_oscillate()))
        self.assertGreater(int(df["long_exit"].sum()) + int(df["short_exit"].sum()), 0)

    def test_fisher_finite_after_warmup(self):
        df = indicators.add_indicators(_oscillate())
        post = df["fisher"].iloc[risk.WARMUP:]
        self.assertFalse(post.isna().any())
        self.assertTrue(np.isfinite(post.to_numpy()).all())

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_oscillate()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_no_lookahead(self):
        raw = _oscillate()
        df = signals.add_signals(indicators.add_indicators(raw))
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx[:5]:
            sub = signals.add_signals(indicators.add_indicators(raw.iloc[: i + 1]))
            self.assertTrue(bool(sub["long_entry"].iloc[-1]))

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.WARMUP, 80)

    def test_overbought_exit_fires_on_spike(self):
        df = signals.add_signals(indicators.add_indicators(_spike()))
        self.assertGreater(float(df["fisher"].max()), 2.5)
        self.assertGreater(int(df["long_exit"].sum()), 0)


if __name__ == "__main__":
    unittest.main()
