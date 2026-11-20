"""Prior-week range breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.weekly_pivot_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

MONDAY = int(pd.Timestamp("2026-03-16 00:00", tz="UTC").timestamp() * 1000)
SATURDAY = int(pd.Timestamp("2026-03-14 22:00", tz="UTC").timestamp() * 1000)


def _frame(closes, highs=None, lows=None, start_ms=MONDAY):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (start_ms + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.concatenate([[closes[0]], closes[:-1]])
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes,
                         "v": np.full(n, 100.0)})


def _flat_frame(n=700, close=100.0, hi=101.0, lo=99.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (MONDAY + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _breakout_frame():
    """Week 1 (168 bars): flat 100 (h 100.5, l 99.5). Week 2: flat
    100, then a close of 105 at bar 180, 104 for 4 bars, back to
    100 at bar 185. Week 3+: flat 100."""
    closes = ([100.0] * 168 + [100.0] * 12 + [105.0] + [104.0] * 4
              + [100.0] * 10 + [100.0] * 150)
    return _frame(closes)


def _breakdown_frame():
    """Mirror of _breakout_frame: close of 95 at bar 180."""
    closes = ([100.0] * 168 + [100.0] * 12 + [95.0] + [96.0] * 4
              + [100.0] * 10 + [100.0] * 150)
    return _frame(closes)


class TestWeeklyPivotBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("weekly_pivot_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_levels_nan_in_first_week(self):
        df = indicators.add_indicators(_breakout_frame())
        self.assertTrue(df["prior_week_high"].iloc[:168].isna().all())
        self.assertTrue(df["prior_week_low"].iloc[:168].isna().all())

    def test_levels_are_prior_week_range(self):
        # Week 1 flat 100 with h=100.5, l=99.5 -> levels from bar 168.
        df = indicators.add_indicators(_breakout_frame())
        self.assertAlmostEqual(df["prior_week_high"].iloc[168], 100.5)
        self.assertAlmostEqual(df["prior_week_low"].iloc[168], 99.5)
        self.assertAlmostEqual(df["prior_week_high"].iloc[335], 100.5)

    def test_levels_constant_within_a_week(self):
        df = indicators.add_indicators(_breakout_frame())
        self.assertEqual(df["prior_week_high"].iloc[168:336].nunique(), 1)
        self.assertEqual(df["prior_week_low"].iloc[168:336].nunique(), 1)

    def test_levels_update_at_monday_boundary(self):
        # Week 2's range includes the 105 close (h 105.5), so week 3
        # (from bar 336) carries prior high 105.5 / low 99.5.
        df = indicators.add_indicators(_breakout_frame())
        self.assertAlmostEqual(df["prior_week_high"].iloc[336], 105.5)
        self.assertAlmostEqual(df["prior_week_low"].iloc[336], 99.5)
        # The intraweek spike does NOT move the in-force level.
        self.assertAlmostEqual(df["prior_week_high"].iloc[200], 100.5)

    def test_long_entry_on_close_above_prior_high(self):
        df = _run(_breakout_frame())
        self.assertFalse(df["long_entry"].iloc[:180].any())
        self.assertTrue(df["long_entry"].iloc[180])
        self.assertFalse(df["short_entry"].iloc[180])

    def test_short_entry_on_close_below_prior_low(self):
        df = _run(_breakdown_frame())
        self.assertFalse(df["short_entry"].iloc[:180].any())
        self.assertTrue(df["short_entry"].iloc[180])
        self.assertFalse(df["long_entry"].iloc[180])

    def test_long_exit_on_close_back_inside(self):
        df = _run(_breakout_frame())
        self.assertTrue(df["long_exit"].iloc[185])
        self.assertFalse(df["long_exit"].iloc[180])

    def test_short_exit_on_close_back_inside(self):
        df = _run(_breakdown_frame())
        self.assertTrue(df["short_exit"].iloc[185])
        self.assertFalse(df["short_exit"].iloc[180])

    def test_opposite_breakout_is_an_exit(self):
        # A close below the prior-week low is also below the
        # prior-week high, so it exits a long (and vice versa).
        rows = pd.DataFrame([dict(c=94.0, prior_week_high=101.0, prior_week_low=99.0),
                             dict(c=106.0, prior_week_high=101.0, prior_week_low=99.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertTrue(df["long_entry"].iloc[1])

    def test_no_signal_before_first_completed_week(self):
        # Data starts Saturday 2026-03-14 22:00 UTC: the Mar 9 week
        # is partial (only ~26 bars), so no levels -- and no signals
        # -- until the first full week (Mar 16-22) completes at bar 194.
        df = _run(_frame([100.0] * 400, highs=[101.0] * 400,
                         lows=[99.0] * 400, start_ms=SATURDAY))
        self.assertTrue(df["prior_week_high"].iloc[:194].isna().all())
        self.assertAlmostEqual(df["prior_week_high"].iloc[194], 101.0)
        self.assertFalse(df["long_entry"].iloc[:194].any())
        self.assertFalse(df["short_entry"].iloc[:194].any())

    def test_no_entry_on_flat_frame(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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
        self.assertEqual(risk.WARMUP, 200)

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

    def test_no_lookahead_future_week(self):
        # Appending a whole extra week must not change any earlier
        # level or signal (levels come only from completed weeks).
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 336))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + list(
            100 * np.exp(np.cumsum(
                np.random.default_rng(5).normal(0.0005, 0.01, 168))))))
        for col in ("prior_week_high", "prior_week_low",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:336].reset_index(drop=True),
                df2[col].iloc[:336].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
