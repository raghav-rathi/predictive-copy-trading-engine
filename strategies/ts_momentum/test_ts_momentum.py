"""Time-series momentum tests. Network-free.

Synthetic design note: the vol-scaled ratios have inherent noise sd ~sqrt(168)
under iid returns, so smooth drift transitions almost never make the 1-week
and 4-week ratios cross +/-0.5 on the *same* bar (the entry condition). The
tests therefore use a controlled regime: a mild pre-trend (both ratios pinned
far from the thresholds), one large single-bar jump (flips both ratios across
the threshold on the same bar), then a strong post-trend. Deterministic across
seeds 11/12/13 (verified).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ts_momentum import indicators, risk, signals

JUMP_IDX = 800


def _regime(pre_drift, post_drift, jump, seed=11, pre_n=800, post_n=1800,
            noise=0.003, phases=None):
    """Mild pre-trend -> single-bar jump -> strong post-trend (or extra phases)."""
    rng = np.random.default_rng(seed)
    if phases is None:
        phases = [(pre_drift, pre_n), (post_drift, post_n)]
    rets = np.concatenate([rng.normal(d, noise, n) for d, n in phases])
    n = len(rets)
    c = np.empty(n)
    c[0] = 100.0
    for k in range(1, n):
        c[k] = c[k - 1] * np.exp(rets[k])
    c[JUMP_IDX] = c[JUMP_IDX - 1] * (1 + jump)
    for k in range(JUMP_IDX + 1, n):
        c[k] = c[k - 1] * np.exp(rets[k])
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)})


def _up():
    return _regime(-0.001, 0.002, 1.5)


def _down():
    return _regime(0.001, -0.002, -0.6)


class TestTsMomentum(unittest.TestCase):
    def test_uptrend_generates_long_entries(self):
        df = signals.add_signals(indicators.add_indicators(_up()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_downtrend_generates_short_entries(self):
        df = signals.add_signals(indicators.add_indicators(_down()))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_long_exit_fires_after_trend_reversal(self):
        # strong uptrend, then a persistent downtrend: hysteresis exit
        # (both ratios below +0.3) must fire while the reversal drags them down
        df = _regime(-0.001, 0.002, 1.5, phases=[(-0.001, 800), (0.002, 1000), (-0.002, 800)])
        df = signals.add_signals(indicators.add_indicators(df))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertGreater(int(df["long_exit"].sum()), 0)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_up()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_no_lookahead(self):
        df = signals.add_signals(indicators.add_indicators(_up()))
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx[:3]:
            sub = signals.add_signals(indicators.add_indicators(df.iloc[: i + 1]))
            self.assertTrue(sub["long_entry"].iloc[-1])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 3.0)
        self.assertEqual(risk.RISK.max_hold_bars, 672)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.WARMUP, 750)


if __name__ == "__main__":
    unittest.main()
