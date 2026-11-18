"""London session breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.london_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

# 2026-01-01 00:00 UTC in ms.
DAY0 = 1767225600000


def _london_frame(days=3, close=100.0):
    """Each day: hours 0-7 range bars (h 110, l 90, c 100), hours
    8-23 flat at `close` (h/l +/-1). Day 1 hour 8 breaks up
    (c 111), day 2 hour 8 breaks both sides (h 112, l 88, c 111),
    day 3 hour 8 breaks down (c 89)."""
    n = days * 24
    t = (DAY0 + np.arange(n) * 3_600_000).astype("int64")
    c = np.full(n, close)
    h = np.full(n, close + 1.0)
    l = np.full(n, close - 1.0)
    for d in range(days):
        base = d * 24
        for hr in range(8):
            i = base + hr
            c[i] = 100.0
            h[i] = 110.0
            l[i] = 90.0
    if days >= 1:
        c[8] = 111.0
        h[8] = 112.0
        l[8] = 100.0
    if days >= 2:
        c[24 + 8] = 111.0
        h[24 + 8] = 112.0
        l[24 + 8] = 88.0
    if days >= 3:
        c[48 + 8] = 89.0
        h[48 + 8] = 100.0
        l[48 + 8] = 88.0
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestLondonBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("london_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_range_is_overnight_high_low(self):
        df = indicators.add_indicators(_london_frame())
        # Day 1, 08:00 bar: range from hours 0-7 (h 110, l 90).
        self.assertAlmostEqual(df["range_high"].iloc[8], 110.0)
        self.assertAlmostEqual(df["range_low"].iloc[8], 90.0)
        # Same range visible at 15:00.
        self.assertAlmostEqual(df["range_high"].iloc[15], 110.0)

    def test_range_nan_outside_window(self):
        df = indicators.add_indicators(_london_frame())
        self.assertTrue(pd.isna(df["range_high"].iloc[3]))   # 03:00
        self.assertTrue(pd.isna(df["range_high"].iloc[16]))  # 16:00
        self.assertTrue(pd.isna(df["range_high"].iloc[20]))  # 20:00

    def test_hour_column_is_utc_hour(self):
        df = indicators.add_indicators(_london_frame())
        self.assertEqual(df["hour"].iloc[0], 0)
        self.assertEqual(df["hour"].iloc[8], 8)
        self.assertEqual(df["hour"].iloc[16], 16)
        self.assertEqual(df["hour"].iloc[23], 23)

    def test_long_entry_first_break_only(self):
        df = _run(_london_frame())
        self.assertTrue(df["long_entry"].iloc[8])
        # Day 1 hour 9 also closes above the range: no second entry.
        self.assertFalse(df["long_entry"].iloc[9])
        self.assertFalse(df["long_entry"].iloc[11])

    def test_both_sides_break_skips_day(self):
        df = _run(_london_frame())
        # Day 2 hour 8 breaks both sides via wicks: no entry either way.
        self.assertFalse(df["long_entry"].iloc[24 + 8])
        self.assertFalse(df["short_entry"].iloc[24 + 8])

    def test_short_entry_mirror(self):
        df = _run(_london_frame())
        self.assertTrue(df["short_entry"].iloc[48 + 8])
        self.assertFalse(df["long_entry"].iloc[48 + 8])

    def test_no_entry_outside_entry_window(self):
        # A break at 13:00 (outside 08:00-12:00) must not enter.
        df0 = _london_frame(days=1)
        # Undo the built-in 08:00 break so the 13:00 break is the only one.
        df0.loc[8, "c"] = 100.0
        df0.loc[8, "h"] = 101.0
        df0.loc[8, "l"] = 99.0
        df0.loc[13, "c"] = 111.0
        df0.loc[13, "h"] = 112.0
        df = _run(df0)
        self.assertFalse(df["long_entry"].iloc[13])
        self.assertFalse(df["long_entry"].any())

    def test_time_exit_at_16(self):
        df = _run(_london_frame())
        self.assertTrue(df["long_exit"].iloc[16])
        self.assertTrue(df["short_exit"].iloc[16])

    def test_long_exit_on_opposite_break(self):
        rows = pd.DataFrame([dict(c=89.0, h=90.0, l=88.0, hour=10,
                                  london_day="2026-01-01",
                                  range_high=110.0, range_low=90.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_short_exit_on_opposite_break(self):
        rows = pd.DataFrame([dict(c=111.0, h=112.0, l=100.0, hour=10,
                                  london_day="2026-01-01",
                                  range_high=110.0, range_low=90.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_no_exit_inside_range(self):
        rows = pd.DataFrame([dict(c=100.0, h=101.0, l=99.0, hour=10,
                                  london_day="2026-01-01",
                                  range_high=110.0, range_low=90.0)])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("range_high", "range_low", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
