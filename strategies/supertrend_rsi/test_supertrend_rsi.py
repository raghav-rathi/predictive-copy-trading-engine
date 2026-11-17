"""Supertrend RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.supertrend_rsi import indicators, risk, signals
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


def _trend_frame(up=True, n=200):
    if up:
        c = 100 * (1.005 ** np.arange(n))
    else:
        c = 100 * (0.995 ** np.arange(n))
    return _frame(c)


class TestSupertrendRsi(unittest.TestCase):
    def test_registered(self):
        self.assertIn("supertrend_rsi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_rsi_all_up_is_100(self):
        df = indicators.add_indicators(_trend_frame(up=True))
        self.assertAlmostEqual(df["rsi"].iloc[-1], 100.0)

    def test_rsi_all_down_is_0(self):
        df = indicators.add_indicators(_trend_frame(up=False))
        self.assertAlmostEqual(df["rsi"].iloc[-1], 0.0)

    def test_supertrend_dir_up_on_rising_series(self):
        df = indicators.add_indicators(_trend_frame(up=True))
        self.assertEqual(df["supertrend_dir"].iloc[-1], 1.0)
        # In an uptrend the line sits below the close.
        self.assertLess(df["supertrend"].iloc[-1], df["c"].iloc[-1])

    def test_supertrend_dir_down_on_falling_series(self):
        df = indicators.add_indicators(_trend_frame(up=False))
        self.assertEqual(df["supertrend_dir"].iloc[-1], -1.0)
        self.assertGreater(df["supertrend"].iloc[-1], df["c"].iloc[-1])

    def test_supertrend_nan_before_first_atr(self):
        df = indicators.add_indicators(_trend_frame(up=True))
        self.assertTrue(df["supertrend"].iloc[:9].isna().all())
        self.assertTrue(df["supertrend_dir"].iloc[:9].isna().all())
        self.assertFalse(np.isnan(df["supertrend"].iloc[-1]))

    def test_signal_logic_crafted_rows(self):
        # Close above the line + RSI crosses 50 upward -> long.
        rows = [dict(c=100.0, supertrend=90.0, supertrend_dir=1.0, rsi=49.0),
                dict(c=101.0, supertrend=90.0, supertrend_dir=1.0, rsi=51.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Close below the line + RSI crosses 50 downward -> short.
        rows = [dict(c=80.0, supertrend=90.0, supertrend_dir=-1.0, rsi=51.0),
                dict(c=79.0, supertrend=90.0, supertrend_dir=-1.0, rsi=49.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_entry_blocked_when_price_on_wrong_side(self):
        # RSI crosses above 50 but the close is BELOW the line:
        # no long entry.
        rows = [dict(c=85.0, supertrend=90.0, supertrend_dir=-1.0, rsi=49.0),
                dict(c=86.0, supertrend=90.0, supertrend_dir=-1.0, rsi=51.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # RSI crosses below 50 but the close is ABOVE the line:
        # no short entry.
        rows = [dict(c=95.0, supertrend=90.0, supertrend_dir=1.0, rsi=51.0),
                dict(c=94.0, supertrend=90.0, supertrend_dir=1.0, rsi=49.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertFalse(df["short_entry"].iloc[1])

    def test_no_entry_without_rsi_cross(self):
        # RSI already above 50 on both bars (no cross): no entry.
        rows = [dict(c=100.0, supertrend=90.0, supertrend_dir=1.0, rsi=60.0),
                dict(c=101.0, supertrend=90.0, supertrend_dir=1.0, rsi=62.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertFalse(df["long_entry"].iloc[1])

    def test_exit_on_direction_flip(self):
        rows = [dict(c=100.0, supertrend=90.0, supertrend_dir=1.0, rsi=60.0),
                dict(c=85.0, supertrend=92.0, supertrend_dir=-1.0, rsi=40.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        rows = [dict(c=80.0, supertrend=90.0, supertrend_dir=-1.0, rsi=40.0),
                dict(c=95.0, supertrend=88.0, supertrend_dir=1.0, rsi=60.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # No flip, no exit.
        rows = [dict(c=100.0, supertrend=90.0, supertrend_dir=1.0, rsi=60.0),
                dict(c=101.0, supertrend=90.0, supertrend_dir=1.0, rsi=62.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertFalse(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

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
        # Flat closes: RSI is 0 (no gains ever), so no cross above
        # 50 and no entry on either side.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("supertrend", "supertrend_dir", "rsi",
                    "long_entry", "long_exit"):
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
