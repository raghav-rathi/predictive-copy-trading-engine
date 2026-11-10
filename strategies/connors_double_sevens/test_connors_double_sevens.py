"""Connors Double 7s tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.connors_double_sevens import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

# 2024-01-01 00:00 UTC, a UTC-midnight-aligned 1h grid.
T0 = 1_704_067_200_000


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _daily_frame(daily_closes):
    """One 1h bar per hour; every bar of a UTC day closes at that day's close."""
    closes = np.repeat(np.array(daily_closes, dtype=float), 24)
    return _frame(closes)


def _flat_frame(n_days=210, close=100.0):
    return _daily_frame([close] * n_days)


def _signal_frame(c, low7, high7, sma200, is_day_close):
    return pd.DataFrame({
        "c": np.array(c, dtype=float),
        "low7_daily": np.array(low7, dtype=float),
        "high7_daily": np.array(high7, dtype=float),
        "sma200_daily": np.array(sma200, dtype=float),
        "is_day_close": np.array(is_day_close, dtype=bool),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=5200, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (T0 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


# 200 flat days at 100, then a 7-day pullback 110 -> 104, then a
# 7-day recovery 105 -> 111. Day 206 (0-based) closes at 104, the
# 7-day low, above the 200-day SMA (~100.245) -> long entry.
# Day 209 closes at 107, the 7-day high -> long exit.
PULLBACK_DAYS = [100.0] * 200 + [110, 109, 108, 107, 106, 105, 104,
                                 105, 106, 107, 108, 109, 110, 111]


class TestConnorsDoubleSevens(unittest.TestCase):
    def test_registered(self):
        self.assertIn("connors_double_sevens", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat 100: daily close 100, SMA(200) = 100 once 200 days are
        # in, 7-day low/high both 100.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        # First valid SMA(200) is on day 199's 23:00 bar (bar 4799).
        self.assertTrue(np.isnan(df["sma200_daily"].iloc[4798]))
        self.assertAlmostEqual(df["sma200_daily"].iloc[4799], 100.0)
        self.assertAlmostEqual(df["low7_daily"].iloc[4799], 100.0)
        self.assertAlmostEqual(df["high7_daily"].iloc[4799], 100.0)
        # Forward-filled daily close is visible on the next day's bars.
        self.assertAlmostEqual(df["daily_close"].iloc[4800], 100.0)
        # Exactly one day-close bar per 24 bars, at hour 23.
        self.assertEqual(int(df["is_day_close"].sum()), 210)
        self.assertTrue(df["is_day_close"].iloc[23])
        self.assertFalse(df["is_day_close"].iloc[24])

    def test_indicator_values_pullback(self):
        # Hand-computed: SMA(200) on day 206 = (193*100 + 749) / 200.
        df = indicators.add_indicators(_daily_frame(PULLBACK_DAYS))
        bar_206 = 206 * 24 + 23
        self.assertAlmostEqual(df["sma200_daily"].iloc[bar_206], 20049 / 200)
        self.assertAlmostEqual(df["low7_daily"].iloc[bar_206], 104.0)
        self.assertAlmostEqual(df["high7_daily"].iloc[bar_206], 110.0)
        self.assertAlmostEqual(df["daily_close"].iloc[bar_206], 104.0)

    def test_long_entry_on_seven_day_low(self):
        df = _run(_daily_frame(PULLBACK_DAYS))
        bar_206 = 206 * 24 + 23
        self.assertTrue(df["long_entry"].iloc[bar_206])
        # No other entry in the pullback stretch: days 200-205 are not
        # 7-day lows (day 199's close of 100 is lower).
        self.assertFalse(df["long_entry"].iloc[200 * 24 + 23:206 * 24 + 23].any())
        # Entry only fires on the day-close bar, never intraday.
        self.assertFalse(df["long_entry"].iloc[bar_206 - 23:bar_206].any())

    def test_trend_filter_blocks_entry(self):
        # 7-day low that sits BELOW the 200-day SMA: no entry.
        # 200 days at 200, then a pullback to 100-94.
        days = [200.0] * 200 + [100, 99, 98, 97, 96, 95, 94]
        df = _run(_daily_frame(days))
        self.assertFalse(df["long_entry"].any())

    def test_long_exit_on_seven_day_high(self):
        df = _run(_daily_frame(PULLBACK_DAYS))
        # Day 207 (105) is not a 7-day high (109 in window); day 209
        # (107) is the max of days 203-209.
        self.assertFalse(df["long_exit"].iloc[207 * 24 + 23])
        self.assertTrue(df["long_exit"].iloc[209 * 24 + 23])
        self.assertTrue(df["long_exit"].iloc[213 * 24 + 23])

    def test_flat_is_exit_not_entry(self):
        # Flat 100: every day-close is a 7-day high (exit) but never
        # above the SMA(200) (entry blocked by the trend filter).
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertTrue(df["long_exit"].iloc[4799])

    def test_no_shorts(self):
        df = _run(_daily_frame(PULLBACK_DAYS))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["short_exit"].any())

    def test_crafted_signal_frame(self):
        df = signals.add_signals(_signal_frame(
            c=[100, 95, 110, 120, 130],
            low7=[100, 95, 95, 95, 95],
            high7=[100, 100, 110, 120, 130],
            sma200=[90, 90, 90, 90, 90],
            is_day_close=[False, True, True, False, True]))
        # Row 1: 95 is the 7-day low and above SMA 90 -> entry.
        self.assertTrue(df["long_entry"].iloc[1])
        # Row 2: 110 is the 7-day high -> exit, not entry.
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[2])
        # Row 3 is not a day-close bar: no signal despite new highs.
        self.assertFalse(df["long_exit"].iloc[3])
        # Row 4: 130 is the 7-day high -> exit.
        self.assertTrue(df["long_exit"].iloc[4])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 10.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertEqual(risk.WARMUP, 4800)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_future_days(self):
        # Appending later days with a huge jump must not change any
        # indicator or signal value on the earlier bars.
        df1 = _run(_daily_frame(PULLBACK_DAYS))
        df2 = _run(_daily_frame(PULLBACK_DAYS + [500.0] * 10))
        n = len(df1)
        for col in ("sma200_daily", "low7_daily", "high7_daily",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:n].reset_index(drop=True),
                df2[col].iloc[:n].reset_index(drop=True),
                check_names=False)

    def test_no_lookahead_intraday(self):
        # Changing the close of a later intraday bar within the same
        # day must not change signals on earlier bars of that day
        # (signals only fire on the day-close bar).
        base = _daily_frame([100.0] * 201 + [110, 109, 108, 107, 106, 105, 104])
        df1 = _run(base)
        mod = base.copy()
        mod.loc[206 * 24 + 12, "c"] = 50.0  # midday bar of day 206
        df2 = _run(mod)
        n = 206 * 24 + 12
        for col in ("long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:n].reset_index(drop=True),
                df2[col].iloc[:n].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than one day: no crash, no entries.
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["long_exit"].any())
        # Zero-range bars (h == l == c): indicators still compute.
        df = _run(_frame([100.0] * 5040, highs=[100.0] * 5040,
                         lows=[100.0] * 5040))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
