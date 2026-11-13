"""ICT Power of Three tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ict_power_of_three import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

DAY0_MS = int(pd.Timestamp("2026-01-05", tz="UTC").value // 1_000_000)


def _pot_frame(sweep="low", sweep_depth=4.0):
    """3 UTC days of 1h bars starting 2026-01-05 00:00 UTC.

    Day 1: flat 100 (range 99-101). Day 2: first 8h range 99-101;
    bar 36 (12:00) sweeps the range low to 95 (sweep='low') or the
    range high to 105 (sweep='high'); bars 40-41 close below/above
    the range so no reclaim fires early; bar 42 (18:00) reclaims
    (close 100.5 for a low sweep, 99.5 for a high sweep). Day 3:
    flat 100, no sweep.
    """
    n = 72
    t = (DAY0_MS + np.arange(n) * 3_600_000).astype("int64")
    o = np.full(n, 100.0)
    h = np.full(n, 101.0)
    l = np.full(n, 99.0)
    c = np.full(n, 100.0)
    v = np.full(n, 100.0)
    if sweep == "low":
        h[36], l[36], c[36] = 100.0, 99.0 - sweep_depth, 99.5
        h[40], l[40], c[40] = 99.0, 97.0, 98.5
        h[41], l[41], c[41] = 99.0, 97.0, 98.5
        h[42], l[42], c[42] = 101.0, 99.5, 100.5
    elif sweep == "high":
        h[36], l[36], c[36] = 101.0 + sweep_depth, 100.0, 100.5
        h[40], l[40], c[40] = 103.0, 101.0, 101.5
        h[41], l[41], c[41] = 103.0, 101.0, 101.5
        h[42], l[42], c[42] = 100.5, 99.0, 99.5
    elif sweep == "none":
        pass
    else:
        raise ValueError(sweep)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    t0 = DAY0_MS
    return pd.DataFrame({
        "t": (t0 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestIctPowerOfThree(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ict_power_of_three", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_accumulation_range_exact(self):
        # Day 2 accumulation (bars 24-31) is 99-101; the frozen range
        # is carried into the distribution window (bar 40).
        df = indicators.add_indicators(_pot_frame("low"))
        self.assertAlmostEqual(df["pot_acc_high"].iloc[40], 101.0)
        self.assertAlmostEqual(df["pot_acc_low"].iloc[40], 99.0)
        self.assertAlmostEqual(df["pot_acc_high"].iloc[36], 101.0)
        self.assertAlmostEqual(df["pot_acc_low"].iloc[36], 99.0)
        # Expanding range during accumulation: bar 28 sees the range
        # of bars 24-28 only.
        self.assertAlmostEqual(df["pot_acc_high"].iloc[28], 101.0)
        self.assertAlmostEqual(df["pot_acc_low"].iloc[28], 99.0)

    def test_sweep_flag_exact(self):
        # ATR is 2.0 on constant true range 2, so the 0.25x threshold
        # is 0.5; the day-2 sweep (depth 4) trips it at bar 36 and the
        # flag carries to the end of day 2, then resets.
        df = indicators.add_indicators(_pot_frame("low"))
        self.assertFalse(df["pot_swept_low"].iloc[35])
        self.assertTrue(df["pot_swept_low"].iloc[36])
        self.assertTrue(df["pot_swept_low"].iloc[47])
        self.assertFalse(df["pot_swept_low"].iloc[48])
        self.assertFalse(df["pot_swept_high"].iloc[36])

    def test_sweep_below_threshold_no_flag(self):
        # Sweep depth 0.4 < 0.25 x ATR (0.5): no sweep, no trade.
        df = _run(_pot_frame("low", sweep_depth=0.4))
        self.assertFalse(df["pot_swept_low"].any())
        self.assertFalse(df["long_entry"].any())

    def test_low_sweep_reclaim_long_entry(self):
        df = _run(_pot_frame("low"))
        # Exactly one long entry, on the reclaim bar 42 (18:00 UTC).
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[42])
        self.assertFalse(df["short_entry"].any())
        # Bars 40-41 close below the range low: no early reclaim.
        self.assertFalse(df["long_entry"].iloc[40])
        self.assertFalse(df["long_entry"].iloc[41])
        # One trade per day: later distribution bars do not re-fire.
        self.assertFalse(df["long_entry"].iloc[43:48].any())

    def test_high_sweep_reclaim_short_entry(self):
        df = _run(_pot_frame("high"))
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertTrue(df["short_entry"].iloc[42])
        self.assertFalse(df["long_entry"].any())

    def test_no_sweep_no_trade(self):
        df = _run(_pot_frame("none"))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_day_end_exits(self):
        # Exit fires on every 23:00 UTC bar (bars 23, 47, 71) and
        # nowhere else; entries never fire on the 23:00 bar.
        df = _run(_pot_frame("low"))
        exit_idx = np.where(df["long_exit"])[0]
        self.assertListEqual(list(exit_idx), [23, 47, 71])
        self.assertListEqual(list(np.where(df["short_exit"])[0]), [23, 47, 71])
        self.assertFalse(df["long_entry"].iloc[47])
        self.assertFalse(df["short_entry"].iloc[47])

    def test_signal_logic_crafted_rows(self):
        # Direct signal logic on explicit per-bar dicts.
        rows = pd.DataFrame({
            "pot_hour": [16, 17, 18, 23],
            "pot_day_start": [0, 0, 0, 0],
            "c": [98.0, 98.0, 100.5, 100.0],
            "pot_acc_high": [101.0] * 4,
            "pot_acc_low": [99.0] * 4,
            "pot_swept_low": [True, True, True, True],
            "pot_swept_high": [False] * 4,
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertTrue(df["long_exit"].iloc[3])
        # No reclaim (close stays below the range low): no entry.
        rows2 = rows.copy()
        rows2["c"] = [98.0, 98.5, 98.8, 98.0]
        df2 = signals.add_signals(rows2)
        self.assertFalse(df2["long_entry"].any())

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
        self.assertEqual(risk.WARMUP, 1200)

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

    def test_no_lookahead_future_jump(self):
        # A future jump must not change any indicator or signal value
        # on the bars before it (per-day ranges are causal).
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_random_walk_frame(n=1300))
        df2 = _run(_random_walk_frame(n=1350))
        for col in ("pot_acc_high", "pot_swept_low", "long_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_pot_frame("low").iloc[:10])
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
