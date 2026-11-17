"""Donchian MACD tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian_macd import indicators, risk, signals
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


def _breakout_frame():
    """20 quiet bars (high 110, low 90, close 100), then a bar with
    close 111 / high 112: close breaks above the previous-20 high
    of 110."""
    closes = [100.0] * 20 + [111.0]
    highs = [110.0] * 20 + [112.0]
    lows = [90.0] * 20 + [90.0]
    return _frame(closes, highs=highs, lows=lows)


def _breakdown_frame():
    closes = [100.0] * 20 + [89.0]
    highs = [110.0] * 20 + [110.0]
    lows = [90.0] * 20 + [88.0]
    return _frame(closes, highs=highs, lows=lows)


class TestDonchianMacd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("donchian_macd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_donchian_previous_20_high(self):
        df = indicators.add_indicators(_breakout_frame())
        last = df.iloc[-1]
        # Previous-20 high is 110 (the current bar's 112 excluded).
        self.assertAlmostEqual(last["donchian_high_20"], 110.0)
        self.assertAlmostEqual(last["donchian_low_20"], 90.0)
        self.assertGreater(last["c"], last["donchian_high_20"])

    def test_donchian_previous_20_low(self):
        df = indicators.add_indicators(_breakdown_frame())
        last = df.iloc[-1]
        self.assertAlmostEqual(last["donchian_low_20"], 90.0)
        self.assertLess(last["c"], last["donchian_low_20"])

    def test_donchian_not_yet_seeded(self):
        df = indicators.add_indicators(_frame([100.0] * 10))
        self.assertTrue(df["donchian_high_20"].isna().all())

    def test_macd_hist_positive_on_rise(self):
        closes = [100.0 + i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertGreater(df["macd_hist"].iloc[-1], 0)

    def test_macd_hist_negative_on_fall(self):
        closes = [200.0 - i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertLess(df["macd_hist"].iloc[-1], 0)

    def test_macd_hist_zero_on_flat(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["macd_hist"].iloc[-1], 0.0)

    def test_signal_logic_crafted_rows(self):
        # Breakout + positive histogram -> long entry only.
        rows = pd.DataFrame([dict(c=111.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=0.5)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        # Breakdown + negative histogram -> short entry only.
        rows = pd.DataFrame([dict(c=89.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=-0.5)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])

    def test_no_entry_without_macd_agreement(self):
        # Breakout but histogram negative -> no long entry.
        rows = pd.DataFrame([dict(c=111.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=-0.5)])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])

    def test_no_entry_without_breakout(self):
        # Positive histogram but close inside the channel -> no entry.
        rows = pd.DataFrame([dict(c=105.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=0.5)])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])

    def test_exit_long_on_breakdown(self):
        rows = pd.DataFrame([dict(c=89.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=-0.5)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_hist_flip(self):
        # Inside the channel, but histogram flipped negative -> long exit.
        rows = pd.DataFrame([dict(c=105.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=-0.1)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(c=111.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=0.5)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        rows = pd.DataFrame([dict(c=105.0, donchian_high_20=110.0,
                                  donchian_low_20=90.0, macd_hist=0.1)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

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
        # Flat closes: no breakout (close inside channel), hist 0.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("donchian_high_20", "macd_hist", "long_entry", "long_exit"):
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
