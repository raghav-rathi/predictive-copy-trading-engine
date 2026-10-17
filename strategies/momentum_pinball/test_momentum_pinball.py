"""Momentum Pinball tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.momentum_pinball import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, v=None, spread=0.2):
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
            "v": np.full(n, 100.0) if v is None else np.asarray(v, dtype=float),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestPinball(unittest.TestCase):
    def test_pinball_matches_wilder_rsi_of_roc(self):
        # independent loop recomputation of 3-period Wilder RSI of diff(1)
        c = 100.0 + np.cumsum(np.random.default_rng(3).normal(0, 1.0, 220))
        df = indicators.add_indicators(_frame(c))
        ms = pd.Series(c)
        mom = ms.diff()  # the 1-period ROC series, NaN at index 0
        n = 3
        # Wilder RSI of the momentum series: RSI itself diffs its input
        d = mom.diff()  # NaN at 0 and 1
        gain = d.clip(lower=0).to_numpy()
        loss = (-d.clip(upper=0)).to_numpy()
        ag = np.full_like(gain, np.nan)
        al = np.full_like(loss, np.nan)
        # pandas ewm(adjust=False, ignore_na=True): seed = first valid obs
        k = int(np.argmax(~np.isnan(gain)))
        ag[k] = gain[k]
        al[k] = loss[k]
        for i in range(k + 1, len(mom)):
            ag[i] = (ag[i - 1] * (n - 1) + gain[i]) / n
            al[i] = (al[i - 1] * (n - 1) + loss[i]) / n
        rs = ag / np.where(al == 0, np.nan, al)
        exp = 100 - 100 / (1 + rs)
        exp = np.where(np.isnan(exp), 100.0 * (ag > 0), exp)
        # min_periods=n: ewm is valid once n non-NaN observations seen
        exp[: k + n - 1] = np.nan
        got = df["pinball"].to_numpy()
        nanmask = np.isnan(df["pinball"].where(
            pd.Series(np.arange(len(df))) >= k + n - 1
        ).to_numpy())
        valid = ~nanmask
        np.testing.assert_allclose(got[valid], exp[valid], rtol=1e-6)
        self.assertEqual(int(valid.sum()), len(got) - (k + n - 1))

    def test_buy_day_flip_after_crash(self):
        # sharp crash then first bounce: pinball < 30 then hooks up -> long_entry
        c = np.concatenate([np.full(60, 100.0), np.linspace(100, 80, 10), np.linspace(80, 84, 6)])
        df = _run(_frame(c))
        self.assertTrue(bool(df["long_entry"].any()))

    def test_sell_day_flip_after_spike(self):
        c = np.concatenate([np.full(60, 100.0), np.linspace(100, 120, 10), np.linspace(120, 116, 6)])
        df = _run(_frame(c))
        self.assertTrue(bool(df["short_entry"].any()))

    def test_flat_market_no_entries(self):
        df = _run(_frame(np.full(200, 100.0)))
        self.assertFalse(bool(df["long_entry"].any()))
        self.assertFalse(bool(df["short_entry"].any()))

    def test_signal_columns_boolean(self):
        rng = np.random.default_rng(9)
        df = _run(_frame(100 + np.cumsum(rng.normal(0, 0.5, 300))))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)

    def test_no_lookahead_truncation(self):
        rng = np.random.default_rng(11)
        c = 100 + np.cumsum(rng.normal(0, 0.5, 400))
        full = indicators.add_indicators(_frame(c))["pinball"].iloc[-1]
        trunc = indicators.add_indicators(_frame(c[:200]))["pinball"].iloc[-1]
        full200 = indicators.add_indicators(_frame(c))["pinball"].iloc[199]
        self.assertAlmostEqual(trunc, full200, places=10)


if __name__ == "__main__":
    unittest.main()
