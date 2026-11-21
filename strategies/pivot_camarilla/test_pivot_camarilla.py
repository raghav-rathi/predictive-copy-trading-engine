"""Camarilla Pivot Breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pivot_camarilla import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

T0 = 1_767_225_600_000  # 2026-01-01 00:00 UTC, a UTC-midnight boundary
HOUR = 3_600_000


def _day_bars(day_index, closes, highs=None, lows=None, vols=None):
    """24 hourly bars for one UTC day starting at day_index days after T0."""
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (T0 + day_index * 24 * HOUR + np.arange(n) * HOUR).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _two_day_frame(day2_closes):
    """Day 1: flat 100, H=110, L=90 -> R3=121.1, S3=78.9 for day 2."""
    d1 = _day_bars(0, [100.0] * 24, highs=[110.0] * 24, lows=[90.0] * 24)
    d2 = _day_bars(1, day2_closes)
    return pd.concat([d1, d2], ignore_index=True)


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (T0 + np.arange(n) * HOUR).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestPivotCamarilla(unittest.TestCase):
    def test_registered(self):
        self.assertIn("pivot_camarilla", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_levels_nan_before_first_completed_day(self):
        df = indicators.add_indicators(_day_bars(0, [100.0] * 24,
                                                  highs=[110.0] * 24,
                                                  lows=[90.0] * 24))
        self.assertTrue(df["r3"].isna().all())
        self.assertTrue(df["s3"].isna().all())

    def test_levels_hand_computed(self):
        # Prior day H=110, L=90, C=100, range=20:
        # R3 = 100 + 20*1.055 = 121.1 ; S3 = 100 - 20*1.055 = 78.9.
        df = indicators.add_indicators(
            _two_day_frame([100.0] * 24))
        self.assertAlmostEqual(df["r3"].iloc[24], 121.1)
        self.assertAlmostEqual(df["s3"].iloc[24], 78.9)
        self.assertAlmostEqual(df["r3"].iloc[47], 121.1)
        self.assertAlmostEqual(df["s3"].iloc[47], 78.9)
        self.assertAlmostEqual(df["prev_day_h"].iloc[30], 110.0)
        self.assertAlmostEqual(df["prev_day_l"].iloc[30], 90.0)
        self.assertAlmostEqual(df["prev_day_c"].iloc[30], 100.0)

    def test_levels_constant_within_day_change_at_boundary(self):
        # Day 2 closes rise 100 -> 130: H=130.5, L=99.5, C=130.
        # Day 3 R3 = 130 + 31*1.055 = 162.705.
        d2_closes = list(np.linspace(100, 130, 24))
        df0 = _two_day_frame(d2_closes)
        d3 = _day_bars(2, [130.0] * 24)
        df = indicators.add_indicators(pd.concat([df0, d3], ignore_index=True))
        self.assertTrue(np.allclose(df["r3"].iloc[24:48], 121.1))
        self.assertTrue(np.allclose(df["r3"].iloc[48:72], 162.705))
        self.assertAlmostEqual(df["s3"].iloc[48], 130 - 31 * 1.055)

    def test_long_entry_cross_above_r3(self):
        d2 = list(np.linspace(100, 130, 24))  # crosses 121.1 mid-day
        df = _run(_two_day_frame(d2))
        cross = [i for i in range(25, 48)
                 if d2[i - 24] > 121.1 and d2[i - 24 - 1] <= 121.1]
        self.assertEqual(len(cross), 1)
        self.assertTrue(df["long_entry"].iloc[cross[0]])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_short_entry_cross_below_s3(self):
        d2 = list(np.linspace(100, 70, 24))  # crosses 78.9 mid-day
        df = _run(_two_day_frame(d2))
        cross = [i for i in range(25, 48)
                 if d2[i - 24] < 78.9 and d2[i - 24 - 1] >= 78.9]
        self.assertEqual(len(cross), 1)
        self.assertTrue(df["short_entry"].iloc[cross[0]])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_long_exit_cross_back_below_r3(self):
        # Rise through R3, then fall back below it.
        d2 = list(np.linspace(100, 130, 12)) + list(np.linspace(130, 100, 12))
        df = _run(_two_day_frame(d2))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())
        entry_idx = int(np.where(df["long_entry"].to_numpy())[0][0])
        exit_idx = int(np.where(df["long_exit"].to_numpy())[0][0])
        self.assertGreater(exit_idx, entry_idx)

    def test_short_exit_cross_back_above_s3(self):
        d2 = list(np.linspace(100, 70, 12)) + list(np.linspace(70, 100, 12))
        df = _run(_two_day_frame(d2))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue(df["short_exit"].any())
        entry_idx = int(np.where(df["short_entry"].to_numpy())[0][0])
        exit_idx = int(np.where(df["short_exit"].to_numpy())[0][0])
        self.assertGreater(exit_idx, entry_idx)

    def test_no_entry_while_inside_range(self):
        # Day 2 stays between S3=78.9 and R3=121.1 the whole day.
        d2 = list(np.linspace(100, 115, 24))
        df = _run(_two_day_frame(d2))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_signal_from_level_jump_alone(self):
        # Day 2 closes flat at 100 (no price cross), day 3 levels jump
        # to R3=100.55/S3=99.45 on a zero-range day-2... use a day-2
        # with range so levels move, but price never crosses them.
        d2 = list(np.linspace(100, 105, 24))
        df0 = _two_day_frame(d2)
        d3 = _day_bars(2, [105.0] * 24)
        df = _run(pd.concat([df0, d3], ignore_index=True))
        # Day 3 R3 = 105 + 6.0*1.055 = 111.33 > 105, S3 = 98.67 < 105.
        self.assertFalse(df["long_entry"].iloc[48:].any())
        self.assertFalse(df["short_entry"].iloc[48:].any())

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

    def test_no_lookahead_future_day(self):
        df1 = _run(_two_day_frame(list(np.linspace(100, 130, 24))))
        d3 = _day_bars(2, [130.0] * 24)
        df2 = _run(pd.concat(
            [_two_day_frame(list(np.linspace(100, 130, 24))), d3],
            ignore_index=True))
        for col in ("r3", "s3", "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:48].reset_index(drop=True),
                df2[col].iloc[:48].reset_index(drop=True),
                check_names=False)

    def test_edge_single_day_frame(self):
        df = _run(_day_bars(0, [100.0] * 24, highs=[110.0] * 24,
                            lows=[90.0] * 24))
        self.assertTrue(df["r3"].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
