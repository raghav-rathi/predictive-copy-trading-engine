"""Swing High Low Breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.swing_high_low_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


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


def _base_arrays(n=30):
    closes = [100.0] * n
    highs = [101.0] * n
    lows = [99.0] * n
    return closes, highs, lows


def _long_entry_frame():
    """Swing high 110 (center 4, confirmed 6); swing lows 90
    (center 10, confirmed 12) then 95 (center 16, confirmed 18);
    bar 20 closes 112, above the last swing high, with ascending
    lows -> long entry."""
    closes, highs, lows = _base_arrays()
    highs[4] = 110.0
    lows[10] = 90.0
    lows[16] = 95.0
    closes[20] = 112.0
    highs[20] = 113.0
    lows[20] = 100.0
    return _frame(closes, highs=highs, lows=lows)


def _short_entry_frame():
    """Swing low 90 (center 4, confirmed 6); swing highs 110
    (center 10, confirmed 12) then 105 (center 16, confirmed 18);
    bar 20 closes 88, below the last swing low, with descending
    highs -> short entry."""
    closes, highs, lows = _base_arrays()
    lows[4] = 90.0
    highs[10] = 110.0
    highs[16] = 105.0
    closes[20] = 88.0
    highs[20] = 100.0
    lows[20] = 87.0
    return _frame(closes, highs=highs, lows=lows)


class TestSwingHighLowBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("swing_high_low_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_pivot_confirmed_at_center_plus_two(self):
        df = indicators.add_indicators(_long_entry_frame())
        # Swing high centered at 4: not known at bar 4, confirmed at 6.
        self.assertFalse(df["is_swing_high"].iloc[4])
        self.assertFalse(df["is_swing_high"].iloc[5])
        self.assertTrue(df["is_swing_high"].iloc[6])
        self.assertAlmostEqual(df["swing_high"].iloc[6], 110.0)
        self.assertTrue(pd.isna(df["last_swing_high"].iloc[5]))
        self.assertAlmostEqual(df["last_swing_high"].iloc[6], 110.0)
        # Swing low centered at 10: confirmed at 12.
        self.assertFalse(df["is_swing_low"].iloc[10])
        self.assertTrue(df["is_swing_low"].iloc[12])
        self.assertAlmostEqual(df["swing_low"].iloc[12], 90.0)

    def test_long_entry_exact(self):
        df = _run(_long_entry_frame())
        self.assertAlmostEqual(df["last_swing_high"].iloc[20], 110.0)
        self.assertAlmostEqual(df["last_swing_low"].iloc[20], 95.0)
        self.assertAlmostEqual(df["prev_swing_low"].iloc[20], 90.0)
        self.assertTrue(df["lows_ascending"].iloc[20])
        self.assertTrue(df["long_breakout"].iloc[20])
        self.assertTrue(df["long_entry"].iloc[20])
        self.assertFalse(df["short_entry"].iloc[20])
        self.assertFalse(df["long_entry"].iloc[:20].any())

    def test_short_entry_exact(self):
        df = _run(_short_entry_frame())
        self.assertAlmostEqual(df["last_swing_low"].iloc[20], 90.0)
        self.assertAlmostEqual(df["last_swing_high"].iloc[20], 105.0)
        self.assertAlmostEqual(df["prev_swing_high"].iloc[20], 110.0)
        self.assertTrue(df["highs_descending"].iloc[20])
        self.assertTrue(df["short_breakout"].iloc[20])
        self.assertTrue(df["short_entry"].iloc[20])
        self.assertFalse(df["long_entry"].iloc[20])
        self.assertFalse(df["short_entry"].iloc[:20].any())

    def test_no_long_entry_without_ascending_lows(self):
        # Same breakout close, but the second swing low (85) is
        # LOWER than the first (90): no higher low, no entry.
        closes, highs, lows = _base_arrays()
        highs[4] = 110.0
        lows[10] = 90.0
        lows[16] = 85.0
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 100.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["lows_ascending"].iloc[20])
        self.assertTrue(df["long_breakout"].iloc[20])
        self.assertFalse(df["long_entry"].iloc[20])

    def test_no_entry_with_only_one_swing_low(self):
        # One swing low only: lows_ascending needs two pivots.
        closes, highs, lows = _base_arrays()
        highs[4] = 110.0
        lows[10] = 90.0
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 100.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["lows_ascending"].iloc[20])
        self.assertFalse(df["long_entry"].iloc[20])

    def test_no_entry_without_breakout(self):
        # Ascending lows present, but close 108 stays below the
        # last swing high 110: no entry.
        closes, highs, lows = _base_arrays()
        highs[4] = 110.0
        lows[10] = 90.0
        lows[16] = 95.0
        closes[20] = 108.0
        highs[20] = 109.0
        lows[20] = 100.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["lows_ascending"].iloc[20])
        self.assertFalse(df["long_breakout"].iloc[20])
        self.assertFalse(df["long_entry"].iloc[20])

    def test_long_exit_exact(self):
        # Same structure as the long-entry frame, but bar 20 closes
        # at 89, below the last swing low (95): long exit.
        closes, highs, lows = _base_arrays()
        highs[4] = 110.0
        lows[10] = 90.0
        lows[16] = 95.0
        closes[20] = 89.0
        highs[20] = 100.0
        lows[20] = 88.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["short_breakout"].iloc[20])
        self.assertTrue(df["long_exit"].iloc[20])
        self.assertFalse(df["long_entry"].iloc[20])

    def test_short_exit_exact(self):
        # Same structure as the short-entry frame, but bar 20 closes
        # at 112, above the last swing high (105): short exit.
        closes, highs, lows = _base_arrays()
        lows[4] = 90.0
        highs[10] = 110.0
        highs[16] = 105.0
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 100.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["long_breakout"].iloc[20])
        self.assertTrue(df["short_exit"].iloc[20])
        self.assertFalse(df["short_entry"].iloc[20])

    def test_equal_high_is_not_a_pivot(self):
        # A high equal to a neighbour is not strictly greater, so
        # no swing high is confirmed (flat-top pattern).
        closes, highs, lows = _base_arrays()
        highs[4] = 110.0
        highs[5] = 110.0
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["is_swing_high"].any())

    def test_signal_logic_crafted_rows(self):
        rows = [dict(long_breakout=True, lows_ascending=True,
                     short_breakout=False, highs_descending=False)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])
        rows = [dict(long_breakout=False, lows_ascending=False,
                     short_breakout=True, highs_descending=True)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])

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
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("is_swing_high", "is_swing_low", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["last_swing_high"].isna().all())
        self.assertTrue(df["last_swing_low"].isna().all())


if __name__ == "__main__":
    unittest.main()
