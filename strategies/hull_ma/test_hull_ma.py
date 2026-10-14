"""Hull MA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.hull_ma import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.2):
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
            "v": np.full(n, 100.0),
        }
    )


def _reversal(n1=150, n2=250, seed=5):
    """Downtrend then a clean uptrend: HMA must slope down, flip, and a
    long entry must fire on the cross of the rising HMA."""
    rng = np.random.default_rng(seed)
    c1 = 120.0 - 0.35 * np.arange(n1) + rng.normal(0, 0.2, n1).cumsum() * 0.1
    c2 = c1[-1] + 0.45 * np.arange(n2) + rng.normal(0, 0.2, n2).cumsum() * 0.1
    return _frame(np.concatenate([c1, c2]))


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestHullMa(unittest.TestCase):
    def test_hma_formula_independent_loop(self):
        # Independent pure-Python HMA(16): WMA weights 1..n, half=8, sqrt=4.
        c = np.concatenate([np.full(40, 100.0), 100.0 + 0.5 * np.arange(40)])
        df = indicators.add_indicators(_frame(c))

        def wma(vals):
            n = len(vals)
            w = np.arange(1, n + 1, dtype=float)
            return float(np.dot(vals, w)) / w.sum()

        cc = c
        raw = np.full(len(cc), np.nan)
        for i in range(len(cc)):
            if i >= 15:  # needs WMA(16)
                raw[i] = 2 * wma(cc[i - 7 : i + 1]) - wma(cc[i - 15 : i + 1])
        expect = np.nan
        i = len(cc) - 1
        if i >= 15 + 3:
            expect = wma(raw[i - 3 : i + 1])
        self.assertAlmostEqual(df["hma"].iloc[-1], expect, places=6)
        # HMA hugs a clean trend: slope positive at the end of the ramp
        self.assertGreater(df["hma_slope"].iloc[-1], 0)

    def test_long_entry_on_reversal(self):
        df = _run(_reversal())
        self.assertLess(df["hma_slope"].iloc[100], 0)  # sloping down early
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertGreater(df["hma_slope"].iloc[i], 0)
        self.assertLessEqual(df["hma_slope"].iloc[i - 1], 0)
        self.assertGreater(df["c"].iloc[i], df["hma"].iloc[i])

    def test_short_entry_on_down_reversal(self):
        rng = np.random.default_rng(9)
        n1, n2 = 150, 250
        c1 = 80.0 + 0.35 * np.arange(n1) + rng.normal(0, 0.2, n1).cumsum() * 0.1
        c2 = c1[-1] - 0.45 * np.arange(n2) + rng.normal(0, 0.2, n2).cumsum() * 0.1
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        j = int(df.index[df["short_entry"]][0])
        self.assertLess(df["hma_slope"].iloc[j], 0)
        self.assertLess(df["c"].iloc[j], df["hma"].iloc[j])

    def test_no_entries_on_flat(self):
        df = _run(_frame(np.full(300, 100.0)))
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_slope_flip_exits_long(self):
        # Down, then up (long entry on the slope turn), then a slow bleed:
        # the slope flip must exit the long after the entry.
        c = np.concatenate(
            [
                150.0 - 0.4 * np.arange(100),
                110.0 + 0.5 * np.arange(150),
                185.0 - 0.15 * np.arange(80),
            ]
        )
        df = _run(_frame(c))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        exits = df.index[df["long_exit"]]
        self.assertTrue((exits > i).any())
        j = int(exits[exits > i][0])
        self.assertTrue(
            df["hma_slope"].iloc[j] < 0
            or df["c"].iloc[j] < df["hma"].iloc[j]
        )

    def test_no_lookahead_truncation(self):
        full = _reversal(n2=300)
        ind_full = indicators.add_indicators(full)
        for i in (250, 400):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("hma", "hma_slope"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = _run(_reversal())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 90)
        self.assertEqual(indicators.N, 16)


if __name__ == "__main__":
    unittest.main()
