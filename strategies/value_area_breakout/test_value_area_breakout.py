"""Value-area breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.value_area_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

# 2025-01-01 00:00 UTC (a UTC-midnight-aligned base).
MIDNIGHT = 1_735_689_600_000


def _frame(closes, highs=None, lows=None, vols=None, opens=None, t0=MIDNIGHT):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
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
        "t": (MIDNIGHT + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _profile_day_frame(day1_closes):
    """Day 0 (24 bars, h=110/l=90): 22 closes at 100 (vol 100) + 2 at
    105 (vol 10). Profile: POC bin 25 (vol 2200 of 2220), 70% target
    1554 met by the POC bin alone -> VAH=100.4, VAL=100.0, POC=100.2.
    Day 1 closes are the caller's; bars after day 1 stay near 100."""
    closes = [100.0] * 22 + [105.0, 105.0] + list(day1_closes)
    vols = [100.0] * 22 + [10.0, 10.0] + [100.0] * len(day1_closes)
    highs = [110.0] * 24 + [c + 0.5 for c in day1_closes]
    lows = [90.0] * 24 + [c - 0.5 for c in day1_closes]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


class TestValueAreaBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("value_area_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_profile_visible_only_from_next_day(self):
        df = indicators.add_indicators(_profile_day_frame([101.0, 102.0]))
        self.assertTrue(np.isnan(df["vah"].iloc[23]))
        self.assertAlmostEqual(df["vah"].iloc[24], 100.4)
        self.assertAlmostEqual(df["val"].iloc[24], 100.0)
        self.assertAlmostEqual(df["poc"].iloc[24], 100.2)

    def test_long_trigger_on_second_close_above_vah(self):
        df = _run(_profile_day_frame([101.0, 102.0, 103.0]))
        self.assertFalse(df["long_entry"].iloc[:25].any())
        self.assertTrue(df["long_entry"].iloc[25])
        self.assertFalse(df["short_entry"].iloc[25])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertEqual(int(df["above_count"].iloc[24]), 1)
        self.assertEqual(int(df["above_count"].iloc[25]), 2)

    def test_short_trigger_on_second_close_below_val(self):
        df = _run(_profile_day_frame([99.0, 98.0, 97.0]))
        self.assertFalse(df["short_entry"].iloc[:25].any())
        self.assertTrue(df["short_entry"].iloc[25])
        self.assertFalse(df["long_entry"].iloc[25])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_no_entry_on_single_poke(self):
        # One close above VAH, then back inside: a poke, not acceptance.
        df = _run(_profile_day_frame([101.0, 99.5, 100.0, 100.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertEqual(int(df["above_count"].iloc[25]), 0)

    def test_no_entry_on_close_exactly_at_vah(self):
        # Close exactly on VAH is not above it.
        df = _run(_profile_day_frame([100.4, 100.4, 100.0]))
        self.assertFalse(df["long_entry"].any())

    def test_exit_long_on_close_back_inside(self):
        rows = pd.DataFrame([dict(
            c=100.0, long_trigger=False, short_trigger=False,
            vah=100.4, val=100.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        # A close inside the area also reads as a short exit (c >= VAL);
        # the harness only checks the exit of the side actually held.
        self.assertTrue(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(
            c=100.5, long_trigger=False, short_trigger=False,
            vah=100.4, val=100.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_no_exit_while_outside(self):
        rows = pd.DataFrame([dict(
            c=102.0, long_trigger=False, short_trigger=False,
            vah=100.4, val=100.0)])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])  # above VAL: short exits

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
        df1 = _run(_frame(closes, t0=MIDNIGHT))
        df2 = _run(_frame(closes + [300.0] * 50, t0=MIDNIGHT))
        for col in ("vah", "val", "poc", "above_count", "long_entry",
                    "short_entry", "long_exit"):
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
