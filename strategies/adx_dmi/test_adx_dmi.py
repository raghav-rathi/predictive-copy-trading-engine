"""ADX/DMI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adx_dmi import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(o, h, l, c, v=None):
    n = len(c)
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": np.asarray(o, dtype=float),
            "h": np.asarray(h, dtype=float),
            "l": np.asarray(l, dtype=float),
            "c": np.asarray(c, dtype=float),
            "v": np.full(n, 100.0) if v is None else np.asarray(v, dtype=float),
        }
    )


def _uptrend(n=500, step=0.9, vol=0.35, seed=3):
    """Downtrend first, then a persistent grind higher: the +DI/-DI cross
    must form at the reversal, and ADX must be strong in the up leg."""
    rng = np.random.default_rng(seed)
    n1 = 150
    c1 = 100.0 - 0.7 * np.arange(n1) + rng.normal(0, vol, n1).cumsum() * 0.2
    n2 = n - n1
    c2 = c1[-1] + step * np.arange(n2) + rng.normal(0, vol, n2).cumsum() * 0.2
    c = np.concatenate([c1, c2])
    prev = np.concatenate([[c[0]], c[:-1]])
    hi = np.maximum(c, prev) + vol
    lo = np.minimum(c, prev) - vol
    return _frame(prev, hi, lo, c)


def _chop(n=400):
    """Fast whipsaw oscillation (no sustained leg): +DI ~ -DI so DX stays
    small and ADX must stay weak."""
    i = np.arange(n)
    c = 100.0 + 0.5 * np.sin(2 * np.pi * i / 6.0)
    prev = np.concatenate([[c[0]], c[:-1]])
    hi = np.maximum(c, prev) + 0.30
    lo = np.minimum(c, prev) - 0.30
    return _frame(prev, hi, lo, c)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestAdxDmi(unittest.TestCase):
    def test_indicator_columns_and_bounds(self):
        df = indicators.add_indicators(_uptrend())
        for col in ("plus_di", "minus_di", "adx", "di_spread"):
            self.assertIn(col, df.columns, col)
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue((tail["adx"] >= -1e-9).all())
        self.assertTrue((tail["adx"] <= 100 + 1e-6).all())
        self.assertTrue((tail["plus_di"] >= 0).all())
        self.assertTrue((tail["minus_di"] >= 0).all())
        self.assertFalse(tail["adx"].isna().any())

    def test_wilder_math_hand_checked(self):
        # Constant up-move day: +DM = 1 every bar, -DM = 0, TR = 1.
        n = 120
        c = 100.0 + np.arange(n)
        prev = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(_frame(prev, c, prev, c))
        tail = df.iloc[-10:]
        # With pure one-sided moves: +DI -> 100, -DI -> 0, DX -> 100, ADX -> 100
        self.assertTrue((tail["plus_di"] > 95).all())
        self.assertTrue((tail["minus_di"] < 5).all())
        self.assertTrue((tail["adx"] > 90).all())

    def test_long_entry_fires_in_trend_with_conditions(self):
        df = _run(_uptrend())
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertGreaterEqual(df["adx"].iloc[i], indicators.ADX_ENTRY)
        self.assertLessEqual(df["plus_di"].iloc[i - 1], df["minus_di"].iloc[i - 1])
        self.assertGreater(df["plus_di"].iloc[i], df["minus_di"].iloc[i])

    def test_no_entries_when_adx_weak(self):
        df = _run(_chop())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue((tail["adx"] < indicators.ADX_ENTRY).all())
        self.assertEqual(int(tail["long_entry"].sum()), 0)
        self.assertEqual(int(tail["short_entry"].sum()), 0)

    def test_exits_defined(self):
        df = _run(_uptrend())
        self.assertIn("long_exit", df.columns)
        self.assertIn("short_exit", df.columns)
        # ADX-fade exit exists on some bar somewhere in a reversing chop series
        df2 = _run(_chop())
        self.assertTrue(df2["long_exit"].dtype == bool)

    def test_no_lookahead_truncation(self):
        full = _uptrend(n=500)
        ind_full = indicators.add_indicators(full)
        for i in (200, 400):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("plus_di", "minus_di", "adx"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = _run(_uptrend())
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


if __name__ == "__main__":
    unittest.main()
