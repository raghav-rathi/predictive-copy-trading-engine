"""Ehlers Center of Gravity tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.center_of_gravity import indicators, risk, signals
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


def _trend_frame(direction=+1):
    """20 flat bars at 100, then a 20-bar steady trend, then 20 flat.
    direction=+1 rises 101 -> 120, -1 falls 99 -> 80."""
    base = [100.0] * 20
    trend = list(np.linspace(101, 120, 20)) if direction > 0 else \
        list(np.linspace(99, 80, 20))
    tail = [trend[-1]] * 20
    return _frame(base + trend + tail)


class TestCenterOfGravity(unittest.TestCase):
    def test_registered(self):
        self.assertIn("center_of_gravity", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_cg_hand_computed(self):
        # Closes 100..109 over the first 10 bars (p[0]=100 oldest).
        # sum p = 1045; weighted = 1*100 + 2*101 + ... + 10*109 = 5830.
        # CG = -5830/1045.
        closes = list(range(100, 110)) + [109.0] * 5
        df = indicators.add_indicators(_frame(closes))
        expected = -5830.0 / 1045.0
        self.assertAlmostEqual(df["cg"].iloc[9], expected, places=9)

    def test_cg_flat_series(self):
        # Flat 100: weighted = (1+...+10)*100 = 5500, total = 1000.
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["cg"].iloc[100], -5.5, places=9)
        self.assertAlmostEqual(df["cg_trigger"].iloc[100], -5.5, places=9)

    def test_trigger_is_sma3_of_cg(self):
        df = indicators.add_indicators(_random_walk_frame())
        i = 100
        expected = df["cg"].iloc[i - 2:i + 1].mean()
        self.assertAlmostEqual(df["cg_trigger"].iloc[i], expected, places=9)

    def test_cross_up_is_long_entry(self):
        df = pd.DataFrame({
            "cg": [-5.6, -5.5, -5.4, -5.3, -5.4],
            "cg_trigger": [-5.5, -5.5, -5.5, -5.5, -5.5],
        })
        out = signals.add_signals(df)
        # CG crosses up through trigger at index 2 (-5.5 -> -5.4).
        self.assertTrue(out["long_entry"].iloc[2])
        self.assertEqual(int(out["long_entry"].sum()), 1)
        self.assertFalse(out["short_entry"].any())
        # The cross-up bar is also a short exit.
        self.assertTrue(out["short_exit"].iloc[2])

    def test_cross_down_is_short_entry(self):
        df = pd.DataFrame({
            "cg": [-5.4, -5.5, -5.6, -5.7, -5.6],
            "cg_trigger": [-5.5, -5.5, -5.5, -5.5, -5.5],
        })
        out = signals.add_signals(df)
        # CG crosses down through trigger at index 2 (-5.5 -> -5.6).
        self.assertTrue(out["short_entry"].iloc[2])
        self.assertEqual(int(out["short_entry"].sum()), 1)
        self.assertFalse(out["long_entry"].any())
        self.assertTrue(out["long_exit"].iloc[2])

    def test_no_cross_no_entry(self):
        df = pd.DataFrame({
            "cg": [-5.4, -5.4, -5.4, -5.4],
            "cg_trigger": [-5.5, -5.5, -5.5, -5.5],
        })
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].any())

    def test_exit_is_opposite_cross(self):
        df = pd.DataFrame({
            "cg": [-5.6, -5.4, -5.6],
            "cg_trigger": [-5.5, -5.5, -5.5],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["long_exit"].iloc[2])
        self.assertTrue(out["short_entry"].iloc[2])

    def test_declining_trend_gives_long_entry(self):
        # With the brief's weighting (newest price weight 10), CG rises
        # when prices fall, so a downtrend crosses CG up through trigger.
        df = _run(_trend_frame(-1))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_rising_trend_gives_short_entry(self):
        df = _run(_trend_frame(+1))
        self.assertGreater(int(df["short_entry"].sum()), 0)

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["cg"].iloc[:9].isna().all())
        self.assertFalse(np.isnan(df["cg"].iloc[9]))
        self.assertTrue(df["cg_trigger"].iloc[:11].isna().all())
        self.assertFalse(np.isnan(df["cg_trigger"].iloc[11]))

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
        self.assertEqual(risk.WARMUP, 40)

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
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("cg", "cg_trigger", "long_entry", "short_entry",
                    "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["cg"].iloc[:9].isna().all())
        self.assertAlmostEqual(df["cg"].iloc[9], -5.5, places=9)


if __name__ == "__main__":
    unittest.main()
