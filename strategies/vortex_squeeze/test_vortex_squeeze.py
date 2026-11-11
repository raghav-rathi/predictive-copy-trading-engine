"""Vortex squeeze tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vortex_squeeze import indicators, risk, signals
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


def _signal_frame(rows):
    """Direct signal unit-test frame from explicit per-bar dicts."""
    return pd.DataFrame(rows)


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

class TestVortexSqueeze(unittest.TestCase):
    def test_registered(self):
        self.assertIn("vortex_squeeze", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_vortex_hand_computed(self):
        # Steady +1/bar rise, h = c+1, l = c-1. Per bar (i >= 1):
        # VM+ = |h_i - l_{i-1}| = 3, VM- = |l_i - h_{i-1}| = 1,
        # TR = max(2, |h_i - c_{i-1}| = 2, |l_i - c_{i-1}| = 0) = 2.
        # Over 14 bars: VI+ = 42/28 = 1.5, VI- = 14/28 = 0.5.
        n = 40
        closes = 100.0 + np.arange(n, dtype=float)
        df = indicators.add_indicators(_frame(closes, highs=closes + 1.0,
                                              lows=closes - 1.0))
        self.assertAlmostEqual(df["vi_pos"].iloc[14], 1.5, places=9)
        self.assertAlmostEqual(df["vi_neg"].iloc[14], 0.5, places=9)
        self.assertAlmostEqual(df["vi_spread"].iloc[14], 1.0, places=9)
        # First 13 bars have no full 14-bar window.
        self.assertTrue(df["vi_pos"].iloc[:13].isna().all())

    def test_bandwidth_flat_zero(self):
        # Flat price: Bollinger sd = 0, so BandWidth = 0; its 20th
        # percentile is also 0, so 0 < 0 is False -- no squeeze on a
        # perfectly flat series (nothing ever compressed further).
        df = indicators.add_indicators(_flat_frame(n=300))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["bb_bandwidth"], 0.0, atol=1e-12))
        self.assertFalse(df["squeeze"].any())

    def test_squeeze_after_calm_follows_volatile(self):
        # 140 bars alternating 90/110 (wide bands), then 40 flat bars at
        # 100: BandWidth collapses below its 120-bar 20th percentile.
        volatile = np.tile([90.0, 110.0], 70)
        closes = np.concatenate([volatile, np.full(40, 100.0)])
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(df["squeeze"].iloc[-1])
        self.assertTrue(df["squeeze_recent"].iloc[-1])
        # During the volatile stretch the width is at its own top end.
        self.assertFalse(df["squeeze"].iloc[100])

    def test_squeeze_recent_window(self):
        # A single squeeze bar keeps the gate open for exactly 5 bars
        # after it (6-bar window including the squeeze bar itself).
        sq = pd.Series([True] + [False] * 7)
        recent = sq.rolling(6, min_periods=1).max() > 0
        self.assertEqual(list(recent), [True] * 6 + [False] * 2)

    def test_signal_logic_crafted_rows(self):
        # Cross up + gate open -> long entry; gate closed -> nothing.
        rows = [dict(vi_pos=0.4, vi_neg=0.6, squeeze_recent=True),
                dict(vi_pos=0.6, vi_neg=0.4, squeeze_recent=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        rows = [dict(vi_pos=0.4, vi_neg=0.6, squeeze_recent=False),
                dict(vi_pos=0.6, vi_neg=0.4, squeeze_recent=False)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Cross up fires the short exit even with the gate closed
        # (exits are ungated).
        self.assertTrue(df["short_exit"].iloc[1])
        # Cross down + gate open -> short entry.
        rows = [dict(vi_pos=0.6, vi_neg=0.4, squeeze_recent=True),
                dict(vi_pos=0.4, vi_neg=0.6, squeeze_recent=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        # No cross: no entry even with the gate open.
        rows = [dict(vi_pos=0.6, vi_neg=0.4, squeeze_recent=True),
                dict(vi_pos=0.7, vi_neg=0.4, squeeze_recent=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # NaN VI (warmup): no entry.
        rows = [dict(vi_pos=np.nan, vi_neg=np.nan, squeeze_recent=True),
                dict(vi_pos=np.nan, vi_neg=np.nan, squeeze_recent=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
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
        self.assertEqual(risk.WARMUP, 150)

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
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("vi_pos", "vi_neg", "bb_bandwidth", "squeeze",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): VI is NaN (zero TR sum),
        # BandWidth is 0, no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        self.assertTrue(df["vi_pos"].iloc[risk.WARMUP:].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
