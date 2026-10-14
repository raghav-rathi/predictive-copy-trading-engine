"""LSMA slope tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.lsma_slope import indicators, risk, signals


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


class TestLsmaSlope(unittest.TestCase):
    def test_lsma_on_linear_series(self):
        # y = 2 + 0.5*x over 30 bars: the trailing 21-bar window's endpoint
        # is the regression value at the last bar of the window,
        # 2 + 0.5*29 = 16.5 (regression on a line is exact).
        n = 30
        c = 2.0 + 0.5 * np.arange(n)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.concatenate([[2.0], c[:-1]]),
                "h": c + 0.1,
                "l": c - 0.1,
                "c": c,
                "v": np.full(n, 100.0),
            }
        )
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["lsma"].iloc[-1], 16.5, places=8)

    def test_lsma_leads_flat_sma_on_trend(self):
        # On a steady uptrend the LSMA endpoint sits above the SMA (leading).
        n = 60
        c = 100.0 + 0.3 * np.arange(n)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.concatenate([[100.0], c[:-1]]),
                "h": c + 0.1,
                "l": c - 0.1,
                "c": c,
                "v": np.full(n, 100.0),
            }
        )
        ind = indicators.add_indicators(df)
        sma21 = df["c"].rolling(21).mean().iloc[-1]
        self.assertGreater(ind["lsma"].iloc[-1], sma21)

    def test_slope_sign_on_trends(self):
        n = 80
        c = 100.0 + 0.3 * np.arange(n)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.concatenate([[100.0], c[:-1]]),
                "h": c + 0.1,
                "l": c - 0.1,
                "c": c,
                "v": np.full(n, 100.0),
            }
        )
        ind = indicators.add_indicators(df)
        self.assertGreater(ind["lsma_slope"].iloc[-1], 0)
        # Slope equals 5 bars * per-bar rise (0.3) on a linear series.
        self.assertAlmostEqual(ind["lsma_slope"].iloc[-1], 1.5, places=6)

    def test_entries_require_alignment(self):
        df = _run(_frame(600, seed=21, drift=0.002, vol=0.01))
        le = df["long_entry"]
        self.assertGreater(int(le.sum()), 0)
        self.assertTrue(((df["c"][le] > df["lsma"][le]) & (df["lsma_slope"][le] > 0)).all())
        se = df["short_entry"]
        self.assertGreater(int(se.sum()), 0)
        self.assertTrue(((df["c"][se] < df["lsma"][se]) & (df["lsma_slope"][se] < 0)).all())

    def test_exits_on_slope_flip(self):
        df = _run(_frame(600, seed=21, drift=0.002, vol=0.01))
        self.assertTrue((df["lsma_slope"][df["long_exit"]] < 0).all())
        self.assertTrue((df["lsma_slope"][df["short_exit"]] > 0).all())

    def test_no_lookahead_truncation(self):
        full = _frame(400, seed=3)
        ind_full = indicators.add_indicators(full)
        for i in (150, 300):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("lsma", "lsma_slope"):
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
        self.assertEqual(risk.RISK.max_hold_bars, 168)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
