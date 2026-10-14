"""TRIX tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.trix import indicators, risk, signals

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
    """Downtrend then a strong uptrend: TRIX must be negative early, cross
    its signal upward below zero -> long entry."""
    rng = np.random.default_rng(seed)
    n1, n2 = 160, 240
    c1 = 140.0 - 0.5 * np.arange(n1) + rng.normal(0, 0.2, n1).cumsum() * 0.1
    c2 = c1[-1] + 0.6 * np.arange(n2) + rng.normal(0, 0.2, n2).cumsum() * 0.1
    return _frame(np.concatenate([c1, c2]))


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestTrix(unittest.TestCase):
    def test_trix_formula_independent_loop(self):
        # Independent loop: EMA with alpha=2/(n+1), triple-smoothed.
        c = np.concatenate([np.full(60, 100.0), 100.0 + 0.4 * np.arange(60)])
        df = indicators.add_indicators(_frame(c))
        n = 15
        alpha = 2.0 / (n + 1)

        def ema_loop(vals):
            out = np.full(len(vals), np.nan)
            e = vals[0]
            for i, v in enumerate(vals):
                e = alpha * v + (1 - alpha) * e if i else v
                out[i] = e
            return out

        cc = c
        e3 = ema_loop(ema_loop(ema_loop(cc)))
        last = len(cc) - 1
        expect = 100.0 * (e3[last] - e3[last - 1]) / e3[last - 1]
        self.assertAlmostEqual(df["trix"].iloc[last], expect, places=4)
        # rising triple-smoothed series -> TRIX positive
        self.assertGreater(df["trix"].iloc[last], 0)

    def test_long_entry_on_reversal(self):
        df = _run(_reversal())
        self.assertLess(df["trix"].iloc[120], 0)  # negative in the down leg
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertLess(df["trix"].iloc[i], 0)
        self.assertLessEqual(
            df["trix"].iloc[i - 1], df["trix_signal"].iloc[i - 1]
        )
        self.assertGreater(df["trix"].iloc[i], df["trix_signal"].iloc[i])

    def test_short_entry_on_down_reversal(self):
        rng = np.random.default_rng(9)
        n1, n2 = 160, 240
        c1 = 60.0 + 0.5 * np.arange(n1) + rng.normal(0, 0.2, n1).cumsum() * 0.1
        c2 = c1[-1] - 0.6 * np.arange(n2) + rng.normal(0, 0.2, n2).cumsum() * 0.1
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        j = int(df.index[df["short_entry"]][0])
        self.assertGreater(df["trix"].iloc[j], 0)

    def test_no_entries_on_flat(self):
        df = _run(_frame(np.full(300, 100.0)))
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_no_long_entry_when_trix_above_zero(self):
        # Strong uptrend from the start: any signal cross happens with
        # TRIX > 0, so no LONG entries may fire (shorts allowed).
        c = 100.0 + 0.5 * np.arange(300)
        df = _run(_frame(c))
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _reversal()
        ind_full = indicators.add_indicators(full)
        for i in (250, 350):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("trix", "trix_signal"):
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
        self.assertEqual(risk.WARMUP, 120)
        self.assertEqual(indicators.N, 15)
        self.assertEqual(indicators.SIGNAL, 9)


if __name__ == "__main__":
    unittest.main()
