"""Smash Day tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.smash_day import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

DAY_MS = 86_400_000
HOUR_MS = 3_600_000


def _day_start():
    base = 1_700_000_000_000
    return base - (base % DAY_MS)


def _days_frame(day_specs):
    """day_specs: list of (high, low, close) per UTC day, 24 hourly bars each.

    Each day's bars share the day's high/low; closes are the day's close
    except the open of the day which is the prior day's close.
    """
    start = _day_start()
    rows = []
    prev_close = 100.0
    for d, (hi, lo, cl) in enumerate(day_specs):
        for h in range(24):
            t = start + d * DAY_MS + h * HOUR_MS
            o = prev_close if h == 0 else cl
            rows.append({"t": t, "o": o, "h": hi, "l": lo, "c": cl, "v": 100.0})
        prev_close = cl
    return pd.DataFrame(rows)


def _flat_days(n, hi=110.0, lo=90.0, cl=100.0):
    return [(hi, lo, cl)] * n


class TestSmashDay(unittest.TestCase):
    def test_registered(self):
        self.assertIn("smash_day", registry.REGISTRY)

    def test_signal_columns_bool(self):
        specs = _flat_days(30) + [(130.0, 70.0, 100.0), (120.0, 80.0, 100.0),
                                  (125.0, 95.0, 124.0)]
        df = signals.add_signals(indicators.add_indicators(_days_frame(specs)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_setup_fires_on_breakout(self):
        # 25 flat days (range 20) -> wide day (range 60) -> inside day
        # (120/80 inside 130/70) -> next day breaks above the inside high 120.
        specs = (_flat_days(25) + [(130.0, 70.0, 100.0), (120.0, 80.0, 100.0)]
                 + [(125.0, 95.0, 124.0)])
        df = signals.add_signals(indicators.add_indicators(_days_frame(specs)))
        # Day 27 bars start at index 27*24.
        day27 = df.iloc[27 * 24: 28 * 24]
        self.assertTrue(day27["setup_active"].all())
        self.assertEqual(int(day27["long_entry"].sum()), 1)
        self.assertEqual(int(day27["short_entry"].sum()), 0)
        # The entry fires on the first bar whose close breaks 120.
        self.assertTrue(bool(day27["long_entry"].iloc[0]))

    def test_no_setup_without_wide_day(self):
        # Inside day preceded by a normal-range day (20, not > 1.5x mean 20):
        # no setup, no entries even on a break of the inside range.
        specs = (_flat_days(25) + [(110.0, 90.0, 100.0), (105.0, 95.0, 100.0)]
                 + [(125.0, 95.0, 124.0)])
        df = signals.add_signals(indicators.add_indicators(_days_frame(specs)))
        day27 = df.iloc[27 * 24: 28 * 24]
        self.assertFalse(day27["setup_active"].any())
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_short_on_downside_break(self):
        specs = (_flat_days(25) + [(130.0, 70.0, 100.0), (120.0, 80.0, 100.0)]
                 + [(125.0, 75.0, 76.0)])
        df = signals.add_signals(indicators.add_indicators(_days_frame(specs)))
        day27 = df.iloc[27 * 24: 28 * 24]
        self.assertEqual(int(day27["short_entry"].sum()), 1)
        self.assertEqual(int(day27["long_entry"].sum()), 0)

    def test_backtest_runs_on_synthetic(self):
        specs = (_flat_days(25) + [(130.0, 70.0, 100.0), (120.0, 80.0, 100.0)]
                 + [(125.0, 95.0, 124.0)] + _flat_days(5))
        df = signals.add_signals(indicators.add_indicators(_days_frame(specs)))
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=0, use_funding=False)
        self.assertGreaterEqual(len(res.trades), 0)
        self.assertTrue(np.isfinite(res.metrics()["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
