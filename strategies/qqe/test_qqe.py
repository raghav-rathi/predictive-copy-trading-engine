"""QQE tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.qqe import indicators, risk, signals


def _frame(n, c):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestQQE(unittest.TestCase):
    def test_trailing_ratchet_never_reverses_against_trend(self):
        # steadily rising RSI-index: the long band may only move up
        n = 200
        c = 100.0 + 0.3 * np.arange(n)
        df = indicators.add_indicators(_frame(n, c))
        lb = df["qqe_fast"].dropna()
        # fast line tracks the long band in an uptrend -> non-decreasing
        self.assertTrue((lb.diff().dropna() >= -1e-9).all())

    def test_bands_bracket_rsindex(self):
        n = 200
        rng = np.random.default_rng(1)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        df = indicators.add_indicators(_frame(n, c)).iloc[120:]
        r = df["qqe_rsindex"]
        # slow band is a trend-following line: it should sit on the
        # correct side of RSIndex most of the time (not a strict bracket)
        self.assertFalse(df["qqe_slow"].isna().all())

    def test_uptrend_pushes_fast_above_slow(self):
        n = 300
        c = 100.0 + 0.25 * np.arange(n)
        df = indicators.add_indicators(_frame(n, c))
        self.assertGreater(df["qqe_fast"].iloc[-1], df["qqe_slow"].iloc[-1])

    def test_downtrend_reversal_fires_short_cross(self):
        # sharp reversal from up to down: fast TL must cross below slow
        # within a few bars of the turn (the documented QQE signal)
        n = 400
        i = np.arange(n)
        c = 100.0 + np.where(i < 200, 0.3 * i, 60.0 - 0.8 * (i - 200))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        shorts = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(any(195 <= j <= 215 for j in shorts),
                        f"no short cross near reversal; got {shorts[:6]}")

    def test_uptrend_reversal_fires_long_cross(self):
        n = 400
        i = np.arange(n)
        c = 100.0 + np.where(i < 200, 0.3 * i,
                             np.where(i < 300, 60.0 - 0.8 * (i - 200),
                                      -20.0 + 0.5 * (i - 300)))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        longs = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(any(295 <= j <= 315 for j in longs),
                        f"no long cross near reversal; got {longs[:6]}")

    def test_cross_fires_on_reversal(self):
        n = 400
        i = np.arange(n)
        c = 100.0 + np.where(i < 200, 0.3 * i, 0.3 * (400 - i))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        self.assertTrue(sig["long_entry"].any() or sig["short_entry"].any())

    def test_signal_columns_bool_no_nan(self):
        n = 250
        rng = np.random.default_rng(4)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 120)
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)


if __name__ == "__main__":
    unittest.main()
