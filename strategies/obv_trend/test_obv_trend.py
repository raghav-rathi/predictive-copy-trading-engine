"""OBV trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.obv_trend import indicators, risk, signals


def _frame(n=400, seed=7, drift=0.0, vol=0.008):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestObvTrend(unittest.TestCase):
    def test_obv_accumulates_signed_volume(self):
        n = 20
        c = 100.0 + np.arange(n)  # all up closes
        v = np.linspace(10.0, 200.0, n)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.concatenate([[100.0], c[:-1]]),
                "h": c + 0.2,
                "l": c - 0.2,
                "c": c,
                "v": v,
            }
        )
        ind = indicators.add_indicators(df)
        # First bar diff is NaN -> sign 0; bars 1..n-1 add their volume.
        self.assertAlmostEqual(ind["obv"].iloc[-1], v[1:].sum(), places=6)

    def test_obv_down_move(self):
        n = 20
        c = 100.0 - np.arange(n)
        v = np.full(n, 50.0)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.concatenate([[100.0], c[:-1]]),
                "h": c + 0.2,
                "l": c - 0.2,
                "c": c,
                "v": v,
            }
        )
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["obv"].iloc[-1], -50.0 * (n - 1), places=6)

    def test_entry_fires_on_fresh_alignment(self):
        # Long flat drift, then a volume-backed uptrend: entries must fire
        # and each entry must be a fresh alignment (edge-triggered).
        df = _run(_frame(600, seed=21, drift=0.002, vol=0.01))
        le = df["long_entry"]
        self.assertGreater(int(le.sum()), 0)
        above = df["c"] > df["ema50"]
        obv_up = (df["obv"] > df["obv_ema20"]) & (df["obv_slope"] > 0)
        self.assertTrue((above[le] & obv_up[le]).all())
        # No two consecutive-bar entries without a fresh edge: the bar after
        # an entry must not itself be an entry.
        idx = df.index[le]
        for i in idx:
            self.assertFalse(df["long_entry"].iloc[i + 1] if i + 1 < len(df) else False)

    def test_no_lookahead_truncation(self):
        full = _frame(400, seed=3)
        ind_full = indicators.add_indicators(full)
        for i in (150, 300):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("obv", "ema50", "obv_ema20", "obv_slope"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-6, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = _run(_frame(300))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 240)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
