"""TTM Squeeze tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ttm_squeeze import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _squeeze_breakout(n=500, seed=11):
    """Flat low-vol phase (squeeze forms) then a strong expanding uptrend."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:200] = 100 + 0.05 * np.sin(np.arange(200) / 5) + rng.normal(0, 0.03, 200)
    c[200:] = c[199] + 0.25 * np.arange(1, n - 200 + 1) + rng.normal(0, 0.08, n - 200)
    o = np.concatenate([[c[0]], c[:-1]])
    spread = np.where(np.arange(n) < 200, 0.06, 0.35)
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.02, n)) + spread
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.02, n)) - spread
    return _ohlcv(o, h, l, c)


def _fade_series(n=500, seed=5):
    """Uptrend then a sharp reversal so the momentum histogram fades."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:300] = 100 + 0.20 * np.arange(300) + rng.normal(0, 0.1, 300)
    c[300:] = c[299] - 0.35 * np.arange(1, n - 300 + 1) + rng.normal(0, 0.1, n - 300)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.2
    return _ohlcv(o, h, l, c)


class TestTTMSqueeze(unittest.TestCase):
    def test_release_fires_long_in_breakout(self):
        df = signals.add_signals(indicators.add_indicators(_squeeze_breakout()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_fire_requires_prior_squeeze(self):
        df = signals.add_signals(indicators.add_indicators(_squeeze_breakout()))
        idx = df.index[df["long_entry"] | df["short_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx:
            self.assertTrue(df["squeeze"].iloc[i - 1])
            self.assertFalse(df["squeeze"].iloc[i])
            self.assertGreaterEqual(df["squeeze_count"].iloc[i - 1], 5)

    def test_momentum_fade_exits_fire(self):
        df = signals.add_signals(indicators.add_indicators(_fade_series()))
        self.assertGreater(int(df["long_exit"].sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _squeeze_breakout()
        ind_full = indicators.add_indicators(full)
        for i in (250, 400):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("bb_upper", "bb_lower", "kc_upper", "kc_lower", "mom_hist", "squeeze_count"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_squeeze_breakout()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertGreater(risk.WARMUP, 20)


if __name__ == "__main__":
    unittest.main()
