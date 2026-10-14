"""KST tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kst import indicators, risk, signals

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


def _reversal(seed=5):
    """Downtrend then a strong uptrend: KST must cross its signal up."""
    rng = np.random.default_rng(seed)
    n1, n2 = 180, 260
    c1 = 140.0 - 0.5 * np.arange(n1) + rng.normal(0, 0.2, n1).cumsum() * 0.1
    c2 = c1[-1] + 0.6 * np.arange(n2) + rng.normal(0, 0.2, n2).cumsum() * 0.1
    return _frame(np.concatenate([c1, c2]))


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestKst(unittest.TestCase):
    def test_kst_formula_independent_loop(self):
        # Independent loop recomputation of weighted smoothed ROCs.
        c = np.concatenate([np.full(80, 100.0), 100.0 + 0.4 * np.arange(80)])
        df = indicators.add_indicators(_frame(c))
        cc = c
        kst = np.zeros(len(cc))
        for n, m, w in zip(
            indicators.ROC_PERIODS, indicators.RCMA_PERIODS, indicators.WEIGHTS
        ):
            roc = np.full(len(cc), np.nan)
            roc[n:] = 100.0 * (cc[n:] - cc[:-n]) / cc[:-n]
            rcma = np.full(len(cc), np.nan)
            for i in range(m - 1, len(cc)):
                window = roc[i - m + 1 : i + 1]
                if not np.isnan(window).any():
                    rcma[i] = window.mean()
            kst = kst + w * np.nan_to_num(rcma)
        last = len(cc) - 1
        self.assertAlmostEqual(df["kst"].iloc[last], kst[last], places=4)
        self.assertGreater(df["kst"].iloc[last], 0)  # rising -> positive

    def test_signal_line_is_sma_of_kst(self):
        c = 100.0 + 0.3 * np.arange(200)
        df = indicators.add_indicators(_frame(c))
        expect = df["kst"].rolling(9, min_periods=9).mean()
        pd.testing.assert_series_equal(
            df["kst_signal"], expect, check_names=False
        )

    def test_long_entry_on_reversal(self):
        df = _run(_reversal())
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertLessEqual(df["kst"].iloc[i - 1], df["kst_signal"].iloc[i - 1])
        self.assertGreater(df["kst"].iloc[i], df["kst_signal"].iloc[i])

    def test_short_entry_on_cross_below(self):
        # Accelerating up leg keeps KST above its signal; a genuine cross
        # below must register as a short entry with the right conditions.
        rng = np.random.default_rng(9)
        n1, n2 = 200, 240
        c1 = 60.0 + 0.004 * np.arange(n1) ** 2 + rng.normal(0, 0.3, n1).cumsum() * 0.1
        c2 = c1[-1] - 0.8 * np.arange(n2) + rng.normal(0, 0.3, n2).cumsum() * 0.1
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        j = int(df.index[df["short_entry"]][0])
        self.assertGreaterEqual(
            df["kst"].iloc[j - 1], df["kst_signal"].iloc[j - 1]
        )
        self.assertLess(df["kst"].iloc[j], df["kst_signal"].iloc[j])

    def test_no_entries_on_flat(self):
        df = _run(_frame(np.full(300, 100.0)))
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _reversal()
        ind_full = indicators.add_indicators(full)
        for i in (250, 400):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("kst", "kst_signal"):
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
        self.assertEqual(indicators.SIGNAL, 9)
        self.assertEqual(indicators.ROC_PERIODS, (10, 15, 20, 30))
        self.assertEqual(indicators.WEIGHTS, (1, 2, 3, 4))


if __name__ == "__main__":
    unittest.main()
