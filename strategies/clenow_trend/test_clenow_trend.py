"""Clenow trend-following tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.clenow_trend import indicators, risk, signals
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


def _flat_frame(n=2600, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(c, bullish, donch_high, donch_low, bearish=None):
    n = len(c)
    if bearish is None:
        bearish = [not b for b in bullish]
    return pd.DataFrame({
        "c": np.array(c, dtype=float),
        "bullish": np.array(bullish, dtype=bool),
        "bearish": np.array(bearish, dtype=bool),
        "donchian_high_1200": np.array(donch_high, dtype=float),
        "donchian_low_1200": np.array(donch_low, dtype=float),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=3000, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _hand_ema(closes, span):
    """Independent EMA recurrence: alpha=2/(span+1), seeded at closes[0]."""
    alpha = 2.0 / (span + 1)
    out = np.empty(len(closes))
    e = float(closes[0])
    for i, x in enumerate(closes):
        e = float(x) if i == 0 else alpha * float(x) + (1 - alpha) * e
        out[i] = e
    return out


class TestClenowTrend(unittest.TestCase):
    def test_registered(self):
        self.assertIn("clenow_trend", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        # Constant 100 close: both EMAs converge exactly to 100.
        self.assertTrue(np.allclose(tail["ema_fast_1200"], 100.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["ema_slow_2400"], 100.0, atol=1e-9))
        # Constant 101 high / 99 low: Donchian extremes are the constants.
        self.assertTrue(np.allclose(tail["donchian_high_1200"], 101.0))
        self.assertTrue(np.allclose(tail["donchian_low_1200"], 99.0))
        # Equal EMAs -> neither bullish nor bearish (strict > / <).
        self.assertFalse(tail["bullish"].any())
        self.assertFalse(tail["bearish"].any())
        # First 1199 bars have no Donchian value; first 2399 no slow EMA.
        self.assertTrue(df["donchian_high_1200"].iloc[:1199].isna().all())
        self.assertTrue(df["ema_slow_2400"].iloc[:2399].isna().all())
        self.assertTrue(np.isfinite(tail["ema_fast_1200"]).all())

    def test_indicator_ema_hand_computed(self):
        # Hand-computed EMA recurrence vs pandas ewm on a rising series.
        closes = 100 * (1.001 ** np.arange(2600))
        df = indicators.add_indicators(_frame(closes))
        for span, col in ((1200, "ema_fast_1200"), (2400, "ema_slow_2400")):
            expected = _hand_ema(closes, span)
            # min_periods=span: first valid index is span-1.
            self.assertAlmostEqual(df[col].iloc[span - 1], expected[span - 1], places=6)
            self.assertAlmostEqual(df[col].iloc[2500], expected[2500], places=6)
            self.assertTrue(np.allclose(
                df[col].iloc[span - 1:].to_numpy(), expected[span - 1:], atol=1e-6))

    def test_indicator_donchian_hand_computed(self):
        # Highs rise 0.01/bar from 100: rolling 1200-bar max at bar i is
        # simply the current high (monotone rising); with a peak then a
        # fall, the max stays pinned at the peak for the next 1199 bars.
        n = 2600
        highs = np.concatenate([100 + 0.01 * np.arange(1300), np.full(1300, 90.0)])
        closes = highs - 0.5
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=highs - 1.0))
        self.assertAlmostEqual(df["donchian_high_1200"].iloc[1199], 100 + 0.01 * 1199, places=9)
        self.assertAlmostEqual(df["donchian_high_1200"].iloc[1299], 100 + 0.01 * 1299, places=9)
        # Peak high 112.99 stays the rolling max until it leaves the window.
        self.assertAlmostEqual(df["donchian_high_1200"].iloc[2000], 112.99, places=9)
        self.assertAlmostEqual(df["donchian_low_1200"].iloc[1199], 100 + 0.01 * 0 - 1.0, places=9)

    def test_indicator_values_uptrend(self):
        # Steady 0.1% per-bar rally: fast EMA above slow EMA once warmed.
        closes = 100 * (1.001 ** np.arange(3000))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue((tail["ema_fast_1200"] > tail["ema_slow_2400"]).all())
        self.assertTrue(tail["bullish"].all())
        self.assertTrue(np.isfinite(tail["ema_fast_1200"]).all())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 720)
        self.assertEqual(risk.RISK.stop_atr_mult, 3.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 2400)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertIn("net_pnl_usd", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_new_high_bullish(self):
        # Close breaks above the prior 1200-bar high while bullish -> long entry.
        df = signals.add_signals(_signal_frame(
            [100, 101, 102], [True, True, True],
            [100, 101, 102], [90, 90, 90]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])
        self.assertTrue(df["short_exit"].iloc[2])

    def test_long_entry_requires_both_conditions(self):
        # New high but bearish -> no long entry (and no short exit).
        df = signals.add_signals(_signal_frame(
            [102], [False], [102], [90]))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])
        # Bullish but close below the 1200-bar high -> no long entry.
        df = signals.add_signals(_signal_frame(
            [101], [True], [102], [90]))
        self.assertFalse(df["long_entry"].iloc[0])

    def test_short_entry_new_low_bearish(self):
        df = signals.add_signals(_signal_frame(
            [100, 99, 98], [False, False, False],
            [110, 110, 110], [100, 99, 98]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[2])

    def test_short_entry_requires_both_conditions(self):
        # New low but bullish -> no short entry.
        df = signals.add_signals(_signal_frame(
            [98], [True], [110], [98]))
        self.assertFalse(df["short_entry"].iloc[0])
        # Bearish but close above the 1200-bar low -> no short entry.
        df = signals.add_signals(_signal_frame(
            [99], [False], [110], [98]))
        self.assertFalse(df["short_entry"].iloc[0])

    def test_exits_opposite_breakout(self):
        # Long exits on a new low while bearish; short exits on a new
        # high while bullish. Entries and exits fire on the same bar
        # by construction (the opposite breakout is the other side's entry).
        # The breakout is measured against the PRIOR bar's extreme, so
        # the crafted frames need at least two bars.
        df = signals.add_signals(_signal_frame(
            [100, 98], [False, False], [110, 110], [100, 98]))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[0])
        df = signals.add_signals(_signal_frame(
            [100, 102], [True, True], [100, 102], [90, 90]))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_full_pipeline_long_entry_on_rising_close_at_high(self):
        # Rising closes with close == high every bar: after the 1200-bar
        # window fills, every bar is a new high and the trend is bullish.
        closes = 100 * (1.001 ** np.arange(2600))
        df = _run(_frame(closes, highs=closes, lows=closes - 0.5))
        self.assertFalse(df["long_entry"].iloc[:1199].any())
        self.assertTrue(df["long_entry"].iloc[2400:].any())
        self.assertFalse(df["short_entry"].iloc[2400:].any())

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 2600))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("ema_fast_1200", "ema_slow_2400", "donchian_high_1200",
                    "donchian_low_1200", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:2600].reset_index(drop=True),
                df2[col].iloc[:2600].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the breakout window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): EMAs converge to the price and
        # are equal, so the market is neither bullish nor bearish and no
        # entry fires even though the close sits on both Donchian edges.
        df = _run(_frame([100.0] * 2600, highs=[100.0] * 2600,
                         lows=[100.0] * 2600))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["ema_fast_1200"], 100.0, atol=1e-9))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
