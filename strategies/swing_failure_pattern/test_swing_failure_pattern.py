"""Swing Failure Pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.swing_failure_pattern import indicators, risk, signals
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


def _base_frame(n=60, close=100.0, hi=101.0, lo=99.0):
    """Flat base: swing high 101, swing low 99 once warmed up."""
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n)


class TestSwingFailurePattern(unittest.TestCase):
    def test_registered(self):
        self.assertIn("swing_failure_pattern", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_swing_levels_hand_computed(self):
        # Flat 101/99 base: swing high = 101, swing low = 99 after the
        # 20-bar lookback (shifted, so bar 20 is the first defined).
        df = indicators.add_indicators(_base_frame(n=60))
        self.assertTrue(np.isnan(df["swing_high"].iloc[19]))
        self.assertTrue(np.allclose(df["swing_high"].iloc[20:], 101.0))
        self.assertTrue(np.allclose(df["swing_low"].iloc[20:], 99.0))
        # A higher bar enters the swing window only after it ages in:
        # bar 30 spikes to 110, so from bar 31 the swing high is 110.
        closes = [100.0] * 60
        highs = [101.0] * 60
        highs[30] = 110.0
        df = indicators.add_indicators(_frame(closes, highs=highs))
        self.assertEqual(df["swing_high"].iloc[30], 101.0)
        self.assertEqual(df["swing_high"].iloc[31], 110.0)
        self.assertEqual(df["swing_high"].iloc[50], 110.0)

    def test_bearish_failure_same_bar(self):
        # Bar 30 pokes to 105 (new 20-bar high vs swing 101) and closes
        # at 100.5, back below the swing high: short entry on bar 30,
        # and it is also the long exit.
        closes = [100.0] * 60
        highs = [101.0] * 60
        highs[30] = 105.0
        closes[30] = 100.5
        df = _run(_frame(closes, highs=highs))
        self.assertTrue(df["short_entry"].iloc[30])
        self.assertTrue(df["long_exit"].iloc[30])
        self.assertFalse(df["short_entry"].iloc[:30].any())
        self.assertFalse(df["long_entry"].iloc[30])

    def test_bullish_failure_same_bar(self):
        # Mirror: bar 30 dips to 95 (new 20-bar low vs swing 99) and
        # closes at 99.5, back above the swing low.
        closes = [100.0] * 60
        lows = [99.0] * 60
        lows[30] = 95.0
        closes[30] = 99.5
        df = _run(_frame(closes, lows=lows))
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertTrue(df["short_exit"].iloc[30])
        self.assertFalse(df["long_entry"].iloc[:30].any())
        self.assertFalse(df["short_entry"].iloc[30])

    def test_failure_within_3_bars(self):
        # Breakout bar closes ABOVE the swing high (no failure yet),
        # then bar 32 closes back below it: short entry on bar 32.
        closes = [100.0] * 60
        highs = [101.0] * 60
        highs[30] = 105.0
        closes[30] = 103.0   # breakout, holds above 101
        closes[31] = 102.0   # still above
        closes[32] = 100.5   # fails back below 101
        df = _run(_frame(closes, highs=highs))
        self.assertFalse(df["short_entry"].iloc[30])
        self.assertFalse(df["short_entry"].iloc[31])
        self.assertTrue(df["short_entry"].iloc[32])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_failure_expires_after_3_bars(self):
        # Breakout holds above the swing high for bars 30-33; the
        # close back below on bar 34 is outside the 3-bar window.
        closes = [100.0] * 60
        highs = [101.0] * 60
        highs[30] = 105.0
        closes[30] = 103.0
        closes[31] = 102.0
        closes[32] = 102.0
        closes[33] = 102.0
        closes[34] = 100.5
        df = _run(_frame(closes, highs=highs))
        self.assertFalse(df["short_entry"].any())

    def test_no_failure_when_breakout_holds(self):
        # Breakout bar closes above the swing high and stays above:
        # no failure, no entry.
        closes = [100.0] * 60
        highs = [101.0] * 60
        highs[30] = 105.0
        closes[30] = 103.0
        closes[31:] = [103.0] * 29
        df = _run(_frame(closes, highs=highs))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_touching_level_is_not_a_breakout(self):
        # High exactly equal to the swing high is not a new high.
        closes = [100.0] * 60
        highs = [101.0] * 60
        highs[30] = 101.0
        closes[30] = 100.5
        df = _run(_frame(closes, highs=highs))
        self.assertFalse(df["short_entry"].any())

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
        self.assertEqual(risk.WARMUP, 30)

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
        # Flat bars never make a new 20-bar high/low.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("swing_high", "swing_low", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # Fewer bars than the 20-bar lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
