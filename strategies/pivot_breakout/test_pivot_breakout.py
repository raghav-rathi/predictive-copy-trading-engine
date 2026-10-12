"""Pivot breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pivot_breakout import indicators, risk, signals

DAY_MS = 86_400_000
HOUR_MS = 3_600_000
DAY0 = 20_000 * DAY_MS  # an exact UTC-midnight boundary


def _day(open0, hi, lo, closes):
    return (open0, np.full(24, hi), np.full(24, lo), np.asarray(closes, dtype=float))


def _days(day_specs):
    t, o, h, l, c, v = [], [], [], [], [], []
    for d, (open0, highs, lows, closes) in enumerate(day_specs):
        for b in range(24):
            t.append(DAY0 + d * DAY_MS + b * HOUR_MS)
            o.append(open0 if b == 0 else closes[b - 1])
            h.append(highs[b])
            l.append(lows[b])
            c.append(closes[b])
            v.append(100.0)
    return pd.DataFrame(
        {
            "t": np.array(t, dtype="int64"),
            "o": np.array(o),
            "h": np.array(h),
            "l": np.array(l),
            "c": np.array(c),
            "v": np.array(v),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestPivotBreakout(unittest.TestCase):
    def test_pivot_math_hand_built(self):
        # Prior day: H=110, L=90, C=100 -> PP=100, R1=110, S1=90, R2=120, S2=80.
        closes = np.linspace(95, 100, 24)
        specs = [_day(100.0, 110.0, 90.0, closes), _day(100.0, 105.0, 95.0, closes)]
        df = indicators.add_indicators(_days(specs))
        bar = df.iloc[24 + 5]  # inside the second day
        self.assertAlmostEqual(bar["pp"], 100.0)
        self.assertAlmostEqual(bar["r1"], 110.0)
        self.assertAlmostEqual(bar["s1"], 90.0)
        self.assertAlmostEqual(bar["r2"], 120.0)
        self.assertAlmostEqual(bar["s2"], 80.0)

    def test_levels_constant_within_day(self):
        closes = np.linspace(95, 100, 24)
        specs = [
            _day(100.0, 110.0, 90.0, closes),
            _day(100.0, 105.0, 95.0, closes),
            _day(100.0, 104.0, 96.0, closes),
        ]
        df = indicators.add_indicators(_days(specs))
        day2 = df.iloc[48:72]
        self.assertTrue((day2["r1"] == day2["r1"].iloc[0]).all())
        self.assertTrue((day2["s1"] == day2["s1"].iloc[0]).all())
        # Day 3's levels use day 2's H/L/C, not day 1's.
        bar3 = df.iloc[48]
        self.assertAlmostEqual(bar3["pp"], (105.0 + 95.0 + 100.0) / 3.0)

    def test_no_levels_before_one_complete_day(self):
        closes = np.linspace(95, 100, 24)
        df = indicators.add_indicators(_days([_day(100.0, 110.0, 90.0, closes)]))
        self.assertTrue(df["r1"].isna().all())
        self.assertTrue(df["s1"].isna().all())

    def test_long_entry_on_r1_break(self):
        closes = np.linspace(95, 100, 24)
        specs = [
            _day(100.0, 110.0, 90.0, closes),  # R1 for next day = 110
            _day(100.0, 112.0, 98.0, np.linspace(100, 113, 24)),
        ]
        df = _run(_days(specs))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertLessEqual(df["c"].iloc[i - 1], df["r1"].iloc[i - 1])
        self.assertGreater(df["c"].iloc[i], df["r1"].iloc[i])

    def test_short_entry_on_s1_break(self):
        closes = np.linspace(95, 100, 24)
        specs = [
            _day(100.0, 110.0, 90.0, closes),  # S1 for next day = 90
            _day(100.0, 102.0, 88.0, np.linspace(100, 87, 24)),
        ]
        df = _run(_days(specs))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        i = int(df.index[df["short_entry"]][0])
        self.assertGreaterEqual(df["c"].iloc[i - 1], df["s1"].iloc[i - 1])
        self.assertLess(df["c"].iloc[i], df["s1"].iloc[i])

    def test_no_lookahead_truncation(self):
        rng = np.random.default_rng(7)
        specs = []
        px = 100.0
        for _ in range(8):
            walk = rng.normal(0, 0.6, 24).cumsum()
            closes = px + walk
            highs = closes + np.abs(rng.normal(0, 0.15, 24)) + 0.2
            lows = closes - np.abs(rng.normal(0, 0.15, 24)) - 0.2
            specs.append((px, highs, lows, closes))
            px = closes[-1]
        full = _days(specs)
        ind_full = indicators.add_indicators(full)
        for i in (100, 170):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("pp", "r1", "s1", "r2", "s2"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        closes = np.linspace(95, 100, 24)
        specs = [
            _day(100.0, 110.0, 90.0, closes),
            _day(100.0, 112.0, 88.0, np.linspace(100, 113, 24)),
        ]
        df = _run(_days(specs))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 100)


if __name__ == "__main__":
    unittest.main()
