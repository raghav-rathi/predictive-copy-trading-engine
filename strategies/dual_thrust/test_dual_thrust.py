"""Dual Thrust tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dual_thrust import indicators, risk, signals

DAY_MS = 86_400_000
HOUR_MS = 3_600_000
DAY0 = 20_000 * DAY_MS  # an exact UTC-midnight boundary


def _days(day_specs):
    """day_specs: list of (open0, highs[24], lows[24], closes[24])."""
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


def _quiet_day(open0=100.0, spread=0.5):
    """Tight-range day: h/l/c constants give a narrow dual-thrust range."""
    return (open0, np.full(24, open0 + spread), np.full(24, open0 - spread),
            np.full(24, open0))


def _trend_day(open0, step, spread=0.4):
    """Monotonic ramp: close rises by `step` each bar."""
    closes = open0 + step * np.arange(1, 25)
    prev = np.concatenate([[open0], closes[:-1]])
    highs = np.maximum(closes, prev) + spread
    lows = np.minimum(closes, prev) - spread
    return (open0, highs, lows, closes)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestDualThrust(unittest.TestCase):
    def test_indicator_values_hand_built(self):
        # 5 lookback days with known extremes, then a current day.
        specs = []
        for d in range(5):
            hi, lo, ch, cl = 110 + d, 88 - d, 105 + d, 92 - d
            closes = np.array([ch if b % 2 == 0 else cl for b in range(24)])
            specs.append((100.0, np.full(24, hi), np.full(24, lo), closes))
        specs.append(_quiet_day(open0=100.0))
        df = indicators.add_indicators(_days(specs))
        hh, lc, hc, ll = 114.0, 88.0, 109.0, 84.0
        rng = max(hh - lc, hc - ll)
        self.assertAlmostEqual(rng, 26.0)
        bar = df.iloc[5 * 24 + 3]  # inside the current (6th) day
        self.assertAlmostEqual(bar["day_open"], 100.0)
        self.assertAlmostEqual(bar["dt_range"], 26.0)
        self.assertAlmostEqual(bar["buy_line"], 100.0 + 0.7 * 26.0)
        self.assertAlmostEqual(bar["sell_line"], 100.0 - 0.7 * 26.0)

    def test_no_range_before_five_complete_sessions(self):
        specs = [_quiet_day() for _ in range(5)]
        df = indicators.add_indicators(_days(specs))
        self.assertTrue(df["buy_line"].isna().all())
        self.assertTrue(df["dt_range"].isna().all())

    def test_long_entry_fires_on_breakout_day(self):
        specs = [_quiet_day(open0=100.0 + 0.1 * d, spread=0.4) for d in range(6)]
        specs.append(_trend_day(open0=100.6, step=1.2))
        df = _run(_days(specs))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertLessEqual(df["c"].iloc[i - 1], df["buy_line"].iloc[i - 1])
        self.assertGreater(df["c"].iloc[i], df["buy_line"].iloc[i])

    def test_short_entry_fires_on_breakdown_day(self):
        specs = [_quiet_day(open0=100.0 + 0.1 * d, spread=0.4) for d in range(6)]
        specs.append(_trend_day(open0=100.6, step=-1.2))
        df = _run(_days(specs))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        i = int(df.index[df["short_entry"]][0])
        self.assertGreaterEqual(df["c"].iloc[i - 1], df["sell_line"].iloc[i - 1])
        self.assertLess(df["c"].iloc[i], df["sell_line"].iloc[i])

    def test_no_lookahead_truncation(self):
        rng = np.random.default_rng(7)
        specs = []
        px = 100.0
        for _ in range(14):
            walk = rng.normal(0, 0.6, 24).cumsum()
            closes = px + walk
            o0 = px
            highs = closes + np.abs(rng.normal(0, 0.15, 24)) + 0.2
            lows = closes - np.abs(rng.normal(0, 0.15, 24)) - 0.2
            specs.append((o0, highs, lows, closes))
            px = closes[-1]
        full = _days(specs)
        ind_full = indicators.add_indicators(full)
        for i in (160, 300):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("day_open", "dt_range", "buy_line", "sell_line"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        specs = [_quiet_day(open0=100.0, spread=0.4) for _ in range(6)]
        specs.append(_trend_day(open0=100.0, step=1.2))
        df = _run(_days(specs))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_reversing_exits_consistent(self):
        specs = [_quiet_day(open0=100.0, spread=0.4) for _ in range(6)]
        specs.append(_trend_day(open0=100.0, step=1.2))
        specs.append(_trend_day(open0=128.8, step=-1.4))
        df = _run(_days(specs))
        pd.testing.assert_series_equal(
            df["long_exit"], df["short_entry"], check_names=False
        )
        pd.testing.assert_series_equal(
            df["short_exit"], df["long_entry"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 150)


if __name__ == "__main__":
    unittest.main()
