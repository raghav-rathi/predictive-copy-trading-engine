"""Change of Character (ChoCh) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.choch import indicators, risk, signals
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


def _choch_bear_frame():
    """Uptrend: swing low 90 (c22), swing high 110 (c27), swing low
    95 (c32, higher low), swing high 115 (c37, higher high).
    Protected low = 95. Bar 40 breaks below 95 (close 85) on a
    displacement body -> bearish ChoCh."""
    closes = ([100.0] * 20
              + [100, 100, 99, 100, 100]
              + [100, 100, 101, 100, 100]
              + [100, 100, 99, 100, 100]
              + [100, 100, 101, 100, 100]
              + [85.0])
    highs = ([101.0] * 20
             + [101] * 5
             + [101, 105, 110, 105, 101]
             + [101] * 5
             + [101, 108, 115, 108, 101]
             + [110.0])
    lows = ([99.0] * 20
            + [99, 98, 90, 98, 99]
            + [99] * 5
            + [99, 97, 95, 97, 99]
            + [99] * 5
            + [84.0])
    return _frame(closes, highs=highs, lows=lows)


def _choch_bull_frame():
    """Downtrend: swing high 110 (c22), swing low 90 (c27), swing
    high 95 (c32, lower high), swing low 85 (c37, lower low).
    Protected high = 95. Bar 40 breaks above 95 (close 110) on a
    displacement body -> bullish ChoCh."""
    closes = ([100.0] * 20
              + [100, 100, 101, 100, 100]
              + [100, 100, 99, 100, 100]
              + [92, 94, 93, 94, 92]
              + [93, 95, 90, 95, 97]
              + [110.0])
    highs = ([101.0] * 20
             + [101, 102, 110, 102, 101]
             + [101] * 5
             + [93, 94, 95, 94, 93]
             + [94, 96, 98, 99, 100]
             + [111.0])
    lows = ([99.0] * 20
            + [99] * 5
            + [99, 95, 90, 95, 99]
            + [91, 92, 92, 92, 91]
            + [92, 93, 85, 93, 95]
            + [97.0])
    return _frame(closes, highs=highs, lows=lows)


class TestChoch(unittest.TestCase):
    def test_registered(self):
        self.assertIn("choch", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_uptrend_and_protected_low(self):
        df = indicators.add_indicators(_choch_bear_frame())
        self.assertEqual(df["trend"].iloc[39], 1)
        self.assertAlmostEqual(df["protected_low"].iloc[39], 95.0)
        self.assertAlmostEqual(df["swing_high"].iloc[39], 115.0)
        self.assertAlmostEqual(df["swing_low"].iloc[39], 95.0)

    def test_downtrend_and_protected_high(self):
        df = indicators.add_indicators(_choch_bull_frame())
        self.assertEqual(df["trend"].iloc[39], -1)
        self.assertAlmostEqual(df["protected_high"].iloc[39], 95.0)
        self.assertAlmostEqual(df["swing_low"].iloc[39], 85.0)
        self.assertAlmostEqual(df["swing_high"].iloc[39], 95.0)

    def test_trend_zero_before_structure_forms(self):
        df = indicators.add_indicators(_choch_bear_frame())
        self.assertEqual(df["trend"].iloc[24], 0)
        self.assertEqual(df["trend"].iloc[29], 0)

    def test_bearish_choch_short_entry(self):
        df = _run(_choch_bear_frame())
        self.assertGreater(df["body_atr"].iloc[40], 1.5)
        self.assertTrue(df["short_entry"].iloc[40])
        self.assertFalse(df["long_entry"].iloc[40])
        self.assertFalse(df["short_entry"].iloc[39])

    def test_bullish_choch_long_entry(self):
        df = _run(_choch_bull_frame())
        self.assertGreater(df["body_atr"].iloc[40], 1.5)
        self.assertTrue(df["long_entry"].iloc[40])
        self.assertFalse(df["short_entry"].iloc[40])
        self.assertFalse(df["long_entry"].iloc[39])

    def test_no_choch_without_displacement(self):
        # Same break below 95, but a small body (close 94, open 100).
        df = _choch_bear_frame()
        df.loc[40, "c"] = 94.0
        df.loc[40, "l"] = 93.0
        df.loc[40, "h"] = 101.0
        df.loc[40, "o"] = 96.0  # small body despite the break
        out = _run(df)
        self.assertLess(out["body_atr"].iloc[40], 1.5)
        self.assertFalse(out["short_entry"].iloc[40])

    def test_no_choch_without_break(self):
        # Displacement body but the close stays above the protected low.
        df = _choch_bear_frame()
        df.loc[40, "c"] = 96.0
        df.loc[40, "l"] = 95.5
        df.loc[40, "h"] = 110.0
        out = _run(df)
        self.assertFalse(out["short_entry"].iloc[40])

    def test_no_choch_without_trend(self):
        # Break + displacement but no trend (flat frame + crafted rows
        # with trend 0) -> no entry.
        rows = pd.DataFrame([
            dict(c=100.0, o=100.0, trend=0.0, protected_low=95.0,
                 protected_high=105.0, body_atr=3.0,
                 swing_high=115.0, swing_low=95.0),
            dict(c=90.0, o=100.0, trend=0.0, protected_low=95.0,
                 protected_high=105.0, body_atr=3.0,
                 swing_high=115.0, swing_low=95.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_signal_logic_crafted_rows(self):
        # Bearish ChoCh: uptrend, close below protected low, displacement.
        rows = pd.DataFrame([
            dict(c=100.0, o=100.0, trend=1.0, protected_low=95.0,
                 protected_high=115.0, body_atr=0.5,
                 swing_high=115.0, swing_low=95.0),
            dict(c=90.0, o=100.0, trend=1.0, protected_low=95.0,
                 protected_high=115.0, body_atr=3.0,
                 swing_high=115.0, swing_low=95.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        # Bullish ChoCh mirror.
        rows = pd.DataFrame([
            dict(c=100.0, o=100.0, trend=-1.0, protected_low=85.0,
                 protected_high=95.0, body_atr=0.5,
                 swing_high=95.0, swing_low=85.0),
            dict(c=110.0, o=100.0, trend=-1.0, protected_low=85.0,
                 protected_high=95.0, body_atr=3.0,
                 swing_high=95.0, swing_low=85.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_exit_long_on_bearish_choch(self):
        rows = pd.DataFrame([
            dict(c=100.0, o=100.0, trend=1.0, protected_low=95.0,
                 protected_high=115.0, body_atr=0.5,
                 swing_high=115.0, swing_low=95.0),
            dict(c=90.0, o=100.0, trend=1.0, protected_low=95.0,
                 protected_high=115.0, body_atr=3.0,
                 swing_high=115.0, swing_low=95.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])

    def test_exit_long_on_close_above_swing_high(self):
        rows = pd.DataFrame([
            dict(c=100.0, o=100.0, trend=1.0, protected_low=95.0,
                 protected_high=115.0, body_atr=0.5,
                 swing_high=115.0, swing_low=95.0),
            dict(c=116.0, o=115.0, trend=1.0, protected_low=95.0,
                 protected_high=115.0, body_atr=0.5,
                 swing_high=115.0, swing_low=95.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([
            dict(c=100.0, o=100.0, trend=-1.0, protected_low=85.0,
                 protected_high=95.0, body_atr=0.5,
                 swing_high=95.0, swing_low=85.0),
            dict(c=84.0, o=85.0, trend=-1.0, protected_low=85.0,
                 protected_high=95.0, body_atr=0.5,
                 swing_high=95.0, swing_low=85.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])

    def test_body_atr_value(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["body_atr"].iloc[-1], 0.0)

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
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("swing_high", "swing_low", "protected_low",
                    "protected_high", "trend", "long_entry",
                    "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue((df["trend"] == 0).all())


if __name__ == "__main__":
    unittest.main()
