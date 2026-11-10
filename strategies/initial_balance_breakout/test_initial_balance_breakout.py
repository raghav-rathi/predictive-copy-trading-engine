"""Initial Balance breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.initial_balance_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

# 2024-01-01 00:00 UTC, Monday, hour-aligned.
T0 = 1_704_067_200_000
HOUR = 3_600_000


def _frame(closes, highs=None, lows=None, opens=None, start=T0):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (start + np.arange(n) * HOUR).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes,
                         "v": np.full(n, 100.0)})


def _two_day_frame():
    """48 bars: day 1 IB bar h=102 l=98 c=101; day 2 IB bar h=110 l=104 c=107."""
    closes = [101.0] + [100.0] * 23 + [107.0] + [107.0] * 23
    highs = [102.0] + [101.0] * 23 + [110.0] + [108.0] * 23
    lows = [98.0] + [99.0] * 23 + [104.0] + [106.0] * 23
    return _frame(closes, highs=highs, lows=lows)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (T0 + np.arange(n) * HOUR).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestInitialBalanceBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("initial_balance_breakout", registry.REGISTRY)

    def test_indicator_values_hand_computed(self):
        df = indicators.add_indicators(_two_day_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        # Day 1: IB 102/98, range 4, targets 106/94.
        d1 = df.iloc[:24]
        self.assertTrue((d1["ib_high"] == 102.0).all())
        self.assertTrue((d1["ib_low"] == 98.0).all())
        self.assertTrue((d1["ib_range"] == 4.0).all())
        self.assertTrue((d1["ib_target_long"] == 106.0).all())
        self.assertTrue((d1["ib_target_short"] == 94.0).all())
        # Day 2: IB 110/104, range 6, targets 116/98.
        d2 = df.iloc[24:]
        self.assertTrue((d2["ib_high"] == 110.0).all())
        self.assertTrue((d2["ib_low"] == 104.0).all())
        self.assertTrue((d2["ib_range"] == 6.0).all())
        self.assertTrue((d2["ib_target_long"] == 116.0).all())
        self.assertTrue((d2["ib_target_short"] == 98.0).all())
        # Only the 00:00 bars are IB bars.
        self.assertTrue(df["is_ib_bar"].iloc[0])
        self.assertTrue(df["is_ib_bar"].iloc[24])
        self.assertEqual(int(df["is_ib_bar"].sum()), 2)
        # IB levels are fixed within the day (no drift).
        self.assertEqual(df["ib_high"].iloc[5], df["ib_high"].iloc[23])

    def test_indicator_ib_bar_uses_own_bar(self):
        # IB bar's own high/low define the day's IB.
        df = indicators.add_indicators(_frame(
            [101.0, 100.0, 100.0],
            highs=[105.0, 101.0, 101.0], lows=[95.0, 99.0, 99.0]))
        self.assertEqual(df["ib_high"].iloc[0], 105.0)
        self.assertEqual(df["ib_low"].iloc[0], 95.0)
        self.assertEqual(df["ib_range"].iloc[0], 10.0)

    def test_long_entry_first_break(self):
        # Day 1 IB 102/98. Bar 1 flat, bar 2 closes 103 > 102 -> long.
        # Bar 3 closes 104 -> no second entry (one trade per day).
        closes = [101.0, 100.0, 103.0, 104.0] + [104.0] * 20
        highs = [102.0] + [101.0] * 23
        lows = [98.0] + [99.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["long_entry"].iloc[0])  # IB bar never enters
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertEqual(int(df["long_entry"].iloc[:24].sum()), 1)
        self.assertFalse(df["short_entry"].iloc[:24].any())

    def test_short_entry_first_break(self):
        closes = [101.0, 100.0, 97.0, 96.0] + [96.0] * 20
        highs = [102.0] + [101.0] * 23
        lows = [98.0] + [99.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertEqual(int(df["short_entry"].iloc[:24].sum()), 1)
        self.assertFalse(df["long_entry"].iloc[:24].any())

    def test_first_side_wins(self):
        # Short break first; a later long break the same day is ignored.
        closes = [101.0, 97.0, 103.0, 103.0] + [103.0] * 20
        highs = [102.0] + [104.0] * 23
        lows = [98.0] + [96.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[:24].any())

    def test_no_entry_outside_window(self):
        # Breakout on the 14:00 bar (hour 14) -> no entry that day.
        closes = [101.0] + [100.0] * 13 + [103.0] + [103.0] * 9
        highs = [102.0] + [101.0] * 23
        lows = [98.0] + [99.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["long_entry"].iloc[:24].any())
        self.assertFalse(df["short_entry"].iloc[:24].any())
        # Same setup with the break on the 13:00 bar (hour 13) -> entry.
        closes = [101.0] + [100.0] * 12 + [103.0] + [103.0] * 10
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["long_entry"].iloc[13])

    def test_long_exit_reclaim_and_target(self):
        # Long at bar 2 (close 103 > 102). Bar 3 close 101 < 102 -> reclaim exit.
        closes = [101.0, 100.0, 103.0, 101.0] + [101.0] * 20
        highs = [102.0] + [104.0] * 23
        lows = [98.0] + [99.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[3])
        # Target exit: bar 3 close 106 >= 106.
        closes = [101.0, 100.0, 103.0, 106.0] + [106.0] * 20
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["long_exit"].iloc[3])

    def test_short_exit_reclaim_and_target(self):
        # Short at bar 2 (close 97 < 98). Bar 3 close 99 > 98 -> reclaim exit.
        closes = [101.0, 100.0, 97.0, 99.0] + [99.0] * 20
        highs = [102.0] + [101.0] * 23
        lows = [98.0] + [96.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertTrue(df["short_exit"].iloc[3])
        # Target exit: bar 3 close 94 <= 94.
        closes = [101.0, 100.0, 97.0, 94.0] + [94.0] * 20
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["short_exit"].iloc[3])

    def test_no_reentry_after_exit_same_day(self):
        # Long at bar 2, reclaim exit at bar 3, another break at bar 4
        # must NOT re-enter the same day.
        closes = [101.0, 100.0, 103.0, 101.0, 104.0] + [104.0] * 19
        highs = [102.0] + [105.0] * 23
        lows = [98.0] + [99.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertEqual(int(df["long_entry"].iloc[:24].sum()), 1)
        self.assertEqual(int(df["short_entry"].iloc[:24].sum()), 0)

    def test_new_day_new_trade(self):
        # Long day 1, then a fresh short break on day 2 is allowed.
        closes = [101.0, 100.0, 103.0] + [103.0] * 21 + [107.0, 103.0] + [103.0] * 22
        highs = [102.0] + [104.0] * 23 + [110.0] + [108.0] * 23
        lows = [98.0] + [99.0] * 23 + [104.0] + [102.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertTrue(df["short_entry"].iloc[25])

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 23)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        df1 = _run(_random_walk_frame())
        df2 = _run(_random_walk_frame(n=450))
        for col in ("ib_high", "ib_low", "ib_range", "long_entry",
                    "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:400].reset_index(drop=True),
                df2[col].iloc[:400].reset_index(drop=True),
                check_names=False)

    def test_no_lookahead_flat(self):
        df = _run(_frame([100.0] * 72, highs=[101.0] * 72, lows=[99.0] * 72))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than warmup: no crash, no entries.
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range IB (h == l == c on the IB bar): no crash; a close
        # above the level still breaks out.
        closes = [100.0, 100.0, 101.0, 101.0] + [101.0] * 20
        highs = [100.0] + [102.0] * 23
        lows = [100.0] + [99.0] * 23
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue((df["ib_range"].iloc[:24] == 0.0).all())
        self.assertTrue(df["long_entry"].iloc[2])

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("net_pnl_usd", m)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
