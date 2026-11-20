"""Supertrend + MACD agreement tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.supertrend_macd import indicators, risk, signals


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


def _uptrend_frame(n=80, start=100.0, step=1.0):
    return _frame([start + step * i for i in range(n)])


def _downtrend_frame(n=80, start=180.0, step=1.0):
    return _frame([start - step * i for i in range(n)])


def _reversal_frame():
    closes = [100 + 1.0 * i for i in range(40)] + [140 - 2.0 * i for i in range(40)]
    return _frame(closes)


class TestSupertrendMacd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("supertrend_macd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_supertrend_bullish_on_uptrend(self):
        df = indicators.add_indicators(_uptrend_frame())
        self.assertEqual(df["supertrend_dir"].iloc[-1], 1.0)
        self.assertLess(df["supertrend"].iloc[-1], df["c"].iloc[-1])

    def test_supertrend_bearish_on_downtrend(self):
        df = indicators.add_indicators(_downtrend_frame())
        self.assertEqual(df["supertrend_dir"].iloc[-1], -1.0)
        self.assertGreater(df["supertrend"].iloc[-1], df["c"].iloc[-1])

    def test_supertrend_dir_nan_before_atr_warmup(self):
        df = indicators.add_indicators(_uptrend_frame())
        self.assertTrue(np.isnan(df["supertrend_dir"].iloc[8]))
        self.assertFalse(np.isnan(df["supertrend_dir"].iloc[9]))

    def test_supertrend_flips_on_reversal(self):
        df = indicators.add_indicators(_reversal_frame())
        self.assertEqual(df["supertrend_dir"].iloc[40], 1.0)
        self.assertEqual(df["supertrend_dir"].iloc[43], -1.0)
        self.assertEqual(df["supertrend_dir"].iloc[-1], -1.0)

    def test_macd_hist_positive_on_uptrend(self):
        df = indicators.add_indicators(_uptrend_frame())
        self.assertGreater(df["macd_hist"].iloc[-1], 0)
        self.assertGreater(df["macd"].iloc[-1], df["macd_signal"].iloc[-1])

    def test_macd_hist_negative_on_downtrend(self):
        df = indicators.add_indicators(_downtrend_frame())
        self.assertLess(df["macd_hist"].iloc[-1], 0)

    def test_macd_hist_nan_before_warmup(self):
        df = indicators.add_indicators(_uptrend_frame())
        self.assertTrue(np.isnan(df["macd_hist"].iloc[32]))
        self.assertFalse(np.isnan(df["macd_hist"].iloc[33]))

    def test_long_entry_on_agreement_transition(self):
        df = _run(_uptrend_frame())
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[33])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_agreement_transition(self):
        df = _run(_downtrend_frame())
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertTrue(df["short_entry"].iloc[33])
        self.assertFalse(df["long_entry"].any())

    def test_reversal_enters_short_after_long(self):
        df = _run(_reversal_frame())
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[33])
        self.assertTrue(df["short_entry"].iloc[43])

    def test_no_entry_without_agreement(self):
        # Supertrend bullish but histogram negative -> no long entry.
        rows = pd.DataFrame([
            dict(supertrend_dir=1.0, macd_hist=-0.5),
            dict(supertrend_dir=1.0, macd_hist=-0.4),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Supertrend bearish but histogram positive -> no short entry.
        rows = pd.DataFrame([
            dict(supertrend_dir=-1.0, macd_hist=0.5),
            dict(supertrend_dir=-1.0, macd_hist=0.4),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exit_long_on_hist_flip(self):
        # Histogram turns negative while Supertrend is still bullish:
        # a long exits. short_exit is also True here (dir == +1 would
        # exit a short too) — a position is only ever one side, so
        # only the long_exit assertion is meaningful.
        rows = pd.DataFrame([dict(supertrend_dir=1.0, macd_hist=-0.1)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])

    def test_exit_long_on_supertrend_flip(self):
        rows = pd.DataFrame([dict(supertrend_dir=-1.0, macd_hist=0.3)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])

    def test_exit_short_on_hist_flip(self):
        rows = pd.DataFrame([dict(supertrend_dir=-1.0, macd_hist=0.1)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])

    def test_no_entry_before_macd_warmup(self):
        # MACD(12,26,9) histogram is NaN before bar 33, so no entry
        # can fire earlier. (The harness warmup of 40 bars gates
        # execution separately; the signal layer itself is bounded
        # by the indicator warmup.)
        df = _run(_random_walk_frame())
        self.assertFalse(df["long_entry"].iloc[:33].any())
        self.assertFalse(df["short_entry"].iloc[:33].any())

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

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("supertrend", "supertrend_dir", "macd_hist",
                    "long_entry", "short_entry", "long_exit"):
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
