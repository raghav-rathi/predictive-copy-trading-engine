"""Connors RSI(2) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi2_connors import indicators, risk, signals
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


def _rise_then_crash():
    """150 bars rising +0.1%/bar (CRSI ~66.7), then 8 bars of -3%."""
    c = [100.0]
    for _ in range(149):
        c.append(c[-1] * 1.001)
    for _ in range(8):
        c.append(c[-1] * 0.97)
    return _frame(c)


def _fall_then_surge():
    """150 bars falling -0.1%/bar (CRSI ~0), then accelerating rises
    (+1%, +2%, ..., +10%) so ROC is the largest in its window."""
    c = [100.0]
    for _ in range(149):
        c.append(c[-1] * 0.999)
    for k in range(1, 11):
        c.append(c[-1] * (1 + 0.01 * k))
    return _frame(c)


class TestRsi2Connors(unittest.TestCase):
    def test_registered(self):
        self.assertIn("rsi2_connors", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_streak_series(self):
        df = indicators.add_indicators(
            _frame([100, 101, 100, 100, 99, 98]))
        # Streak is NaN-free; first bars are pre-CRSI but streak is
        # defined from bar 0. Use a longer frame for the tail check.
        df2 = indicators.add_indicators(
            _frame([100, 101, 100, 100, 99, 98] + [98] * 150))
        self.assertEqual(list(df2["streak"].iloc[:6]),
                         [0.0, 1.0, 0.0, 0.0, -1.0, -2.0])

    def test_crsi_rising_hand_computed(self):
        # Steady +1/bar rise for 110 bars: RSI(3) of close = 100,
        # RSI(3) of the streak = 100, ROC strictly decreasing so
        # today's ROC is the smallest of the trailing 100 -> rank 0.
        closes = [100.0 + i for i in range(110)]
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["rsi_price"].iloc[105], 100.0, places=6)
        self.assertAlmostEqual(df["rsi_streak"].iloc[105], 100.0, places=6)
        self.assertAlmostEqual(df["pct_rank"].iloc[105], 0.0, places=6)
        self.assertAlmostEqual(df["crsi"].iloc[105], 200.0 / 3.0, places=6)

    def test_pct_rank_middle(self):
        # ROC values: 50 bars of +2%, then 49 bars of +0.5%, then one
        # bar of +1% -- today's ROC beats the 49 small ones only.
        closes = [100.0]
        for _ in range(50):
            closes.append(closes[-1] * 1.02)
        for _ in range(49):
            closes.append(closes[-1] * 1.005)
        closes.append(closes[-1] * 1.01)
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["pct_rank"].iloc[100], 49.0, places=6)

    def test_crsi_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["crsi"].iloc[:100].isna().all())
        self.assertFalse(np.isnan(df["crsi"].iloc[100]))
        self.assertTrue((df["crsi"].iloc[100:] >= 0).all())
        self.assertTrue((df["crsi"].iloc[100:] <= 100).all())

    def test_long_entry_on_crash(self):
        df = _run(_rise_then_crash())
        self.assertTrue(df["long_entry"].any())
        i = int(np.where(df["long_entry"].to_numpy())[0][0])
        self.assertLess(df["crsi"].iloc[i], 10.0)
        self.assertGreaterEqual(df["crsi"].iloc[i - 1], 10.0)
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_short_entry_on_surge(self):
        df = _run(_fall_then_surge())
        self.assertTrue(df["short_entry"].any())
        i = int(np.where(df["short_entry"].to_numpy())[0][0])
        self.assertGreater(df["crsi"].iloc[i], 90.0)
        self.assertLessEqual(df["crsi"].iloc[i - 1], 90.0)

    def test_no_entry_while_crsi_stays_extreme(self):
        # After the crash CRSI stays < 10 for a while; no re-entry.
        df = _run(_rise_then_crash())
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_exit_crosses(self):
        df = pd.DataFrame({"crsi": [5.0, 20.0, 40.0, 55.0, 60.0, 45.0, 30.0]})
        out = signals.add_signals(df)
        self.assertTrue(out["long_exit"].iloc[3])   # cross above 50
        self.assertFalse(out["long_exit"].iloc[4])
        self.assertTrue(out["short_exit"].iloc[5])  # cross below 50
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].any())

    def test_entry_transitions_only(self):
        df = pd.DataFrame({"crsi": [20.0, 5.0, 4.0, 3.0, 95.0, 96.0, 50.0]})
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertFalse(out["long_entry"].iloc[2])
        self.assertFalse(out["long_entry"].iloc[3])
        self.assertTrue(out["short_entry"].iloc[4])
        self.assertFalse(out["short_entry"].iloc[5])

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
        self.assertEqual(risk.WARMUP, 120)

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
        for col in ("crsi", "pct_rank", "rsi_price", "rsi_streak",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["crsi"].isna().all())

    def test_atr_defined(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(np.isnan(df["atr"].iloc[100]))


if __name__ == "__main__":
    unittest.main()
