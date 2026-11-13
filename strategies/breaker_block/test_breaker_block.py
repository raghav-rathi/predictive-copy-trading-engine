"""Breaker Block tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.breaker_block import indicators, risk, signals
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


def _bearish_breaker_frame():
    """Flat 100 (bars 0-29), down bar 30, breakout bar 31 (bull OB
    [98.5, 100.5]), break bar 32 (close 98), retest bar 33 (close
    99.5), entry bar 34 (close 98)."""
    n = 35
    closes = [100.0] * 30 + [99.0, 103.0, 98.0, 99.5, 98.0]
    opens = [100.0] * 30 + [100.0, 100.0, 100.0, 98.0, 99.5]
    highs = [101.0] * 30 + [100.5, 103.5, 100.0, 100.0, 99.0]
    lows = [99.0] * 30 + [98.5, 100.0, 97.0, 99.0, 97.0]
    return _frame(closes, highs=highs, lows=lows, opens=opens)


def _bullish_breaker_frame():
    """Mirror image: flat 100, up bar 30, breakdown bar 31 (bear OB
    [99.5, 101.5]), break bar 32 (close 102), retest bar 33 (close
    100.5), entry bar 34 (close 102)."""
    closes = [100.0] * 30 + [101.0, 97.0, 102.0, 100.5, 102.0]
    opens = [100.0] * 30 + [100.0, 100.0, 100.0, 102.0, 100.5]
    highs = [101.0] * 30 + [101.5, 100.0, 103.0, 101.0, 103.0]
    lows = [99.0] * 30 + [99.5, 96.5, 100.0, 100.0, 101.0]
    return _frame(closes, highs=highs, lows=lows, opens=opens)


class TestBreakerBlock(unittest.TestCase):
    def test_registered(self):
        self.assertIn("breaker_block", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_prev20_high_exact(self):
        # Prior 20-bar high at bar 31 is the max high of bars 11-30.
        df = indicators.add_indicators(_bearish_breaker_frame())
        self.assertAlmostEqual(df["prev20_high"].iloc[31], 101.0)
        self.assertAlmostEqual(df["prev20_low"].iloc[31], 98.5)

    def test_bullish_ob_detected(self):
        # Bar 31 closes 103 above the prior 20-bar high 101; the last
        # down-closed bar before it is bar 30 -> OB zone [98.5, 100.5].
        df = indicators.add_indicators(_bearish_breaker_frame())
        self.assertAlmostEqual(df["ob_bull_high"].iloc[31], 100.5)
        self.assertAlmostEqual(df["ob_bull_low"].iloc[31], 98.5)
        self.assertEqual(df["ob_bull_bar"].iloc[31], 30)
        # Bar 32 closes 98 < 98.5: the OB is cleared (breaker forms).
        self.assertTrue(np.isnan(df["ob_bull_high"].iloc[32]))

    def test_bearish_breaker_short_entry(self):
        df = _run(_bearish_breaker_frame())
        self.assertFalse(df["short_entry"].iloc[:34].any())
        self.assertTrue(df["short_entry"].iloc[34])
        self.assertTrue(df["long_exit"].iloc[34])
        self.assertFalse(df["long_entry"].any())
        # Exactly one short entry: the breaker is consumed on trade.
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_bullish_breaker_long_entry(self):
        df = _run(_bullish_breaker_frame())
        # Bear OB at bar 31 is [99.5, 101.5]; bar 32 breaks it up.
        ind = indicators.add_indicators(_bullish_breaker_frame())
        self.assertAlmostEqual(ind["ob_bear_high"].iloc[31], 101.5)
        self.assertAlmostEqual(ind["ob_bear_low"].iloc[31], 99.5)
        self.assertFalse(df["long_entry"].iloc[:34].any())
        self.assertTrue(df["long_entry"].iloc[34])
        self.assertTrue(df["short_exit"].iloc[34])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_no_entry_without_retest(self):
        # Break bar 32, then price keeps falling and never closes back
        # into the zone: no retest, no entry.
        df = _bearish_breaker_frame()
        df.loc[33:, "c"] = [97.0, 96.0]
        df.loc[33:, "o"] = [98.0, 97.0]
        df.loc[33:, "h"] = [98.0, 97.0]
        df.loc[33:, "l"] = [96.0, 95.0]
        df = _run(df)
        self.assertFalse(df["short_entry"].any())

    def test_breaker_expires_after_200_bars(self):
        # Break at bar 32; retest only arrives at bar 233 (>200 bars
        # later) with entry at 234: the breaker has expired, no trade.
        # (Bars 33-34 of the base frame are neutralised first so the
        # original breaker does not trade there.)
        base = _bearish_breaker_frame()
        base.loc[33:, "c"] = [97.0, 96.0]
        base.loc[33:, "o"] = [98.0, 97.0]
        base.loc[33:, "h"] = [98.0, 97.0]
        base.loc[33:, "l"] = [96.0, 95.0]
        n_extra = 200
        t0 = int(base["t"].iloc[-1]) + 3_600_000
        extra = pd.DataFrame({
            "t": (t0 + np.arange(n_extra) * 3_600_000).astype("int64"),
            "o": [97.0] * n_extra, "h": [98.0] * n_extra,
            "l": [96.0] * n_extra, "c": [97.0] * n_extra,
            "v": [100.0] * n_extra,
        })
        # Retest bar (233) closes 99, entry bar (234) closes 98.
        extra.loc[198, ["o", "h", "l", "c"]] = [97.0, 100.0, 98.0, 99.0]
        extra.loc[199, ["o", "h", "l", "c"]] = [99.0, 99.5, 97.0, 98.0]
        df = _run(pd.concat([base, extra], ignore_index=True))
        self.assertFalse(df["short_entry"].any())

    def test_signal_logic_crafted_rows(self):
        # Breaker state machine on explicit OB columns: OB present
        # rows 0-2, cleared row 3 with close below the low (break),
        # row 4 closes back into the zone (retest), row 5 closes
        # back below the low -> short entry.
        rows = pd.DataFrame({
            "c": [100.0, 100.0, 100.0, 98.0, 99.5, 98.0],
            "ob_bull_high": [100.5, 100.5, 100.5, np.nan, np.nan, np.nan],
            "ob_bull_low": [98.5, 98.5, 98.5, np.nan, np.nan, np.nan],
            "ob_bear_high": [np.nan] * 6,
            "ob_bear_low": [np.nan] * 6,
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[5])
        self.assertFalse(df["short_entry"].iloc[:5].any())
        self.assertTrue(df["long_exit"].iloc[5])

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
        self.assertEqual(risk.WARMUP, 100)

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
        for col in ("ob_bull_high", "long_entry", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["ob_bull_high"].isna().all())
        self.assertTrue(df["ob_bear_high"].isna().all())


if __name__ == "__main__":
    unittest.main()
