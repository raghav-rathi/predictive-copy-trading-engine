"""Connors Cumulative RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.connors_cumulative_rsi import indicators, risk, signals
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


def _flat_frame(n=300, close=100.0):
    return _frame([close] * n)


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


class TestConnorsCumulativeRsi(unittest.TestCase):
    def test_registered(self):
        self.assertIn("connors_cumulative_rsi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_rsi2_and_cum_hand_computed(self):
        # Closes [100, 101, 100, 102, 101, 103]. Wilder RSI(2),
        # alpha = 1/2. The first delta is NaN, and the ewm's
        # min_periods=2 counts that NaN row, so the average gain/loss
        # is still undefined at bar 1 and base.rsi fills 0.0 there.
        # From bar 2 on the hand-computed average gains/losses are:
        #   ag: -, -, 0.5, 1.25, 0.625, 1.3125
        #   al: -, -, 0.5, 0.25, 0.625, 0.3125
        # RSI: bars 0-1 -> 0.0 (fillna), bar 2 -> 50,
        # bar 3 -> 100 - 100/6, bar 4 -> 50, bar 5 -> 100 - 100/5.2.
        # cum_rsi = cumsum(rsi2 - 50).
        closes = [100.0, 101.0, 100.0, 102.0, 101.0, 103.0]
        df = indicators.add_indicators(_frame(closes))
        expected_rsi = [0.0, 0.0, 50.0, 100 - 100 / 6.0, 50.0,
                        100 - 100 / 5.2]
        for i, exp in enumerate(expected_rsi):
            self.assertAlmostEqual(df["rsi2"].iloc[i], exp, places=8)
        expected_cum = np.cumsum(np.array(expected_rsi) - 50.0)
        for i, exp in enumerate(expected_cum):
            self.assertAlmostEqual(df["cum_rsi"].iloc[i], exp, places=8)

    def test_indicator_cum_is_running_sum(self):
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        df = indicators.add_indicators(_frame(closes))
        manual = (df["rsi2"] - 50.0).cumsum()
        pd.testing.assert_series_equal(df["cum_rsi"], manual,
                                       check_names=False)
        # RSI(2) stays in [0, 100]; cum_rsi is unbounded by design.
        self.assertTrue(((df["rsi2"] >= 0) & (df["rsi2"] <= 100)).all())

    def test_long_entry_cross_above_minus_100(self):
        # Crafted cum_rsi: crosses above -100 at index 2 only.
        df = signals.add_signals(pd.DataFrame(
            {"cum_rsi": [-150.0, -120.0, -90.0, -50.0]}))
        self.assertEqual(list(df["long_entry"]), [False, False, True, False])
        self.assertFalse(df["short_entry"].any())
        # Boundary: prev exactly -100, current above -> fires.
        df = signals.add_signals(pd.DataFrame(
            {"cum_rsi": [-100.0, -90.0]}))
        self.assertTrue(df["long_entry"].iloc[1])
        # Flat at -100 -> no cross.
        df = signals.add_signals(pd.DataFrame(
            {"cum_rsi": [-100.0, -100.0]}))
        self.assertFalse(df["long_entry"].any())

    def test_short_entry_cross_below_plus_100(self):
        df = signals.add_signals(pd.DataFrame(
            {"cum_rsi": [150.0, 120.0, 90.0, 50.0]}))
        self.assertEqual(list(df["short_entry"]), [False, False, True, False])
        self.assertFalse(df["long_entry"].any())

    def test_exits_cross_zero(self):
        df = signals.add_signals(pd.DataFrame(
            {"cum_rsi": [-50.0, -10.0, 10.0]}))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].any())
        df = signals.add_signals(pd.DataFrame(
            {"cum_rsi": [50.0, 10.0, -10.0]}))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].any())

    def test_full_pipeline_decline_then_rally(self):
        # 10 bars down 1% each: RSI(2) -> 0, cum_rsi falls ~50/bar.
        # Then 15 bars up 2% each: RSI(2) -> 100, cum_rsi climbs
        # ~50/bar back through -100 (long entry) and then 0 (exit).
        down = 100.0 * (0.99 ** np.arange(10))
        up = down[-1] * (1.02 ** np.arange(1, 16))
        closes = np.concatenate([down, up])
        df = _run(_frame(closes))
        self.assertTrue((df["cum_rsi"].iloc[1:10].diff().dropna() < 0).all())
        self.assertFalse(df["long_entry"].iloc[:10].any())
        self.assertTrue(df["long_entry"].iloc[10:].any())
        # The long exit (cross above 0) comes after the entry.
        entry_idx = int(np.where(df["long_entry"].to_numpy())[0][0])
        self.assertTrue(df["long_exit"].iloc[entry_idx:].any())

    def test_no_signal_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("rsi2", "cum_rsi", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:300].reset_index(drop=True),
                df2[col].iloc[:300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
