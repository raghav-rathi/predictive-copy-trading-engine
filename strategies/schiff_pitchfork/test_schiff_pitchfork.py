"""Schiff pitchfork tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.schiff_pitchfork import indicators, risk, signals
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


def _schiff_frame(touch_close=105.5, post_close=None):
    """Bullish Schiff set.

    Pivots (10-bar window [j-7, j+2], confirmed at centre+2):
      A swing low 90 at centre 12 (confirmed bar 14),
      B swing high 110 at centre 22 (confirmed bar 24),
      C swing low 95 at centre 32 (confirmed bar 34).
    Schiff anchor: (bar 12, (90+110)/2 = 100); B-C midpoint:
    (bar 27, (110+95)/2 = 102.5); slope = 2.5/15 = 1/6.
    Median line at bar 40 = 100 + (1/6)*28 = 104.67.
    Bar 39 low 102.0 stays clear of the line; bar 40 low 104.0
    touches it (|104 - 104.67| < 0.5 ATR ~ 1.2) and closes back
    above it (default close 105.5) -> long entry at bar 40.
    Bars 41-45 rise away from the line, so no second trigger.
    """
    lows = [99, 98, 97, 96, 95, 94, 93, 92, 91.5, 91.2, 91.0, 90.6, 90.0,
            91, 93, 95, 97, 99, 101, 103, 105, 107, 109,
            107, 105, 103, 101, 99, 98, 97, 96, 95.5, 95.0,
            96, 98, 100, 101, 102, 103, 102.0, 104.0,
            107, 109, 111, 113, 115]
    highs = [lv + 2 for lv in lows]
    highs[12] = 91.5
    highs[22] = 110.0
    highs[32] = 96.5
    highs[40] = 106.0
    closes = [(h + lv) / 2 for h, lv in zip(highs, lows)]
    closes[40] = touch_close
    if post_close is not None:
        for k, val in enumerate(post_close):
            closes[41 + k] = val
    return _frame(closes, highs=highs, lows=lows)


def _no_touch_frame():
    """Same A-B-C set, but after C price jumps far above the median
    line and never comes within 0.5 ATR of it."""
    df = _schiff_frame()
    lows = list(df["l"])
    highs = list(df["h"])
    closes = list(df["c"])
    for i in range(33, 46):
        lows[i] = 108.0 + 2.0 * (i - 33)
        highs[i] = lows[i] + 2.0
        closes[i] = lows[i] + 1.0
    return _frame(closes, highs=highs, lows=lows)


def _mirror_frame(df):
    """Reflect prices about 100: bullish set becomes bearish."""
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


class TestSchiffPitchfork(unittest.TestCase):
    def test_registered(self):
        self.assertIn("schiff_pitchfork", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_set_forms_at_c_confirmation(self):
        df = indicators.add_indicators(_schiff_frame())
        # No median line before C confirms at bar 34.
        self.assertTrue(np.isnan(df["pf_bull_median"].iloc[33]))
        self.assertEqual(df["schiff_state"].iloc[33], 0)
        self.assertEqual(df["schiff_state"].iloc[34], 1)
        # Schiff anchor (12, 100), slope 1/6: median(34) = 103.67.
        self.assertAlmostEqual(df["pf_bull_median"].iloc[34], 103.6667, places=3)
        # Parallels through B (110) and C (95) at bar 34.
        self.assertAlmostEqual(df["pf_bull_upper"].iloc[34], 112.0, places=3)
        self.assertAlmostEqual(df["pf_bull_lower"].iloc[34], 95.3333, places=3)

    def test_schiff_anchor_differs_from_andrews(self):
        # A standard Andrews fork would anchor the median line at
        # A itself (90 at bar 12); the Schiff line starts at
        # (A+B)/2 = 100. Median(40) must be 104.67, not ~94.67.
        df = indicators.add_indicators(_schiff_frame())
        self.assertAlmostEqual(df["pf_bull_median"].iloc[40], 104.6667, places=3)

    def test_long_trigger_on_median_touch_and_reclaim(self):
        df = _run(_schiff_frame())
        self.assertFalse(df["long_entry"].iloc[:40].any())
        self.assertTrue(df["long_entry"].iloc[40])
        self.assertFalse(df["short_entry"].iloc[40])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_bear_short_trigger_on_mirrored_frame(self):
        df = _run(_mirror_frame(_schiff_frame()))
        self.assertFalse(df["short_entry"].iloc[:40].any())
        self.assertTrue(df["short_entry"].iloc[40])
        self.assertFalse(df["long_entry"].iloc[40])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_no_entry_without_touch(self):
        df = _run(_no_touch_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_when_touch_does_not_reclaim(self):
        # Bar 40 touches the line but closes 104.0, below the
        # median 104.67; price then falls away without ever closing
        # back above the line.
        df0 = _schiff_frame(touch_close=104.0)
        closes = list(df0["c"])
        highs = list(df0["h"])
        lows = list(df0["l"])
        for k, val in enumerate([103.0, 102.0, 101.0]):
            closes[41 + k] = val
            lows[41 + k] = val - 1.0
            highs[41 + k] = val + 1.0
        df = _run(_frame(closes[:44], highs=highs[:44], lows=lows[:44]))
        self.assertFalse(df["long_entry"].any())

    def test_exit_long_below_lower_parallel(self):
        rows = pd.DataFrame([dict(
            c=94.0, long_trigger=False, short_trigger=False,
            pf_bull_lower=95.0, pf_bear_upper=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=100.0, long_trigger=False, short_trigger=True,
            pf_bull_lower=95.0, pf_bear_upper=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(
            c=121.0, long_trigger=False, short_trigger=False,
            pf_bull_lower=95.0, pf_bear_upper=120.0)])
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
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("pf_bull_median", "pf_bull_lower", "schiff_state",
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
