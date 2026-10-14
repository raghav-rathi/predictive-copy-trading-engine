"""Aroon tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.aroon import indicators, risk, signals

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
    """Downtrend then a strong uptrend: AroonDown must start at 100, then
    AroonUp takes over and a long entry fires with up >= 70."""
    rng = np.random.default_rng(seed)
    n1, n2 = 120, 220
    c1 = 130.0 - 0.5 * np.arange(n1) + rng.normal(0, 0.2, n1).cumsum() * 0.1
    c2 = c1[-1] + 0.6 * np.arange(n2) + rng.normal(0, 0.2, n2).cumsum() * 0.1
    return _frame(np.concatenate([c1, c2]))


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestAroon(unittest.TestCase):
    def test_aroon_formula_hand_checked(self):
        # Monotonic rise: highest high is always the latest bar -> up=100.
        # Lowest low over 25 bars is 24 bars back -> down=100*(25-24)/25=4.
        c = 100.0 + np.arange(60)
        df = indicators.add_indicators(_frame(c, spread=0.1))
        self.assertAlmostEqual(df["aroon_up"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["aroon_down"].iloc[-1], 100.0 * 1 / 25)

    def test_fresh_low_mirror(self):
        c = 100.0 - np.arange(60)
        df = indicators.add_indicators(_frame(c, spread=0.1))
        self.assertAlmostEqual(df["aroon_down"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["aroon_up"].iloc[-1], 100.0 * 1 / 25)

    def test_osc_bounds(self):
        df = indicators.add_indicators(_reversal())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue((tail["aroon_osc"] >= -100 - 1e-9).all())
        self.assertTrue((tail["aroon_osc"] <= 100 + 1e-9).all())

    def test_long_entry_on_reversal(self):
        df = _run(_reversal())
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertGreaterEqual(df["aroon_up"].iloc[i], indicators.STRONG)
        self.assertLessEqual(
            df["aroon_up"].iloc[i - 1], df["aroon_down"].iloc[i - 1]
        )
        self.assertGreater(df["aroon_up"].iloc[i], df["aroon_down"].iloc[i])

    def test_short_entry_on_down_reversal(self):
        rng = np.random.default_rng(9)
        n1, n2 = 120, 220
        c1 = 70.0 + 0.5 * np.arange(n1) + rng.normal(0, 0.2, n1).cumsum() * 0.1
        c2 = c1[-1] - 0.6 * np.arange(n2) + rng.normal(0, 0.2, n2).cumsum() * 0.1
        df = _run(_frame(np.concatenate([c1, c2])))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        j = int(df.index[df["short_entry"]][0])
        self.assertGreaterEqual(df["aroon_down"].iloc[j], indicators.STRONG)

    def test_no_entry_without_strong_leg(self):
        # Chop: crosses happen but neither leg reaches 70 at the cross.
        i = np.arange(300)
        c = 100.0 + 0.6 * np.sin(2 * np.pi * i / 8.0)
        df = _run(_frame(c, spread=0.25))
        tail = df.iloc[risk.WARMUP:]
        self.assertEqual(int(tail["long_entry"].sum()), 0)
        self.assertEqual(int(tail["short_entry"].sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _reversal()
        ind_full = indicators.add_indicators(full)
        for i in (200, 300):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("aroon_up", "aroon_down", "aroon_osc"):
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
        self.assertEqual(risk.WARMUP, 60)
        self.assertEqual(indicators.N, 25)


if __name__ == "__main__":
    unittest.main()
