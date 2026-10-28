"""Pennant pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pennant_pattern import indicators, risk, signals
from strategies.registry import REGISTRY


def _pennant_frame(breakout_volume=500.0, rising_highs=False):
    """Lead flat bars, 5-bar pole, stall bar, converging range, breakout.

    Bars: 0-29 flat at 100; 30-34 pole 102..110; 35 stall at 110;
    36-40 consolidation (highs falling, lows rising unless
    rising_highs); 41 breakout close 111; 42-44 flat tail at 111.
    """
    closes, highs, lows, vols = [], [], [], []
    for _ in range(30):
        closes.append(100.0); highs.append(100.1); lows.append(99.9); vols.append(100.0)
    for cval in (102.0, 104.0, 106.0, 108.0, 110.0):
        closes.append(cval); highs.append(cval + 0.1); lows.append(cval - 0.1); vols.append(100.0)
    closes.append(110.0); highs.append(110.1); lows.append(109.9); vols.append(100.0)
    if rising_highs:
        cons = [(109.0, 110.0, 108.0), (109.5, 110.5, 108.5),
                (110.0, 111.0, 109.0), (110.5, 111.5, 109.5),
                (111.0, 112.0, 110.0)]
    else:
        cons = [(109.0, 110.0, 108.0), (108.8, 109.6, 108.4),
                (109.2, 109.4, 108.8), (109.0, 109.2, 109.0),
                (109.1, 109.1, 109.0)]
    for cval, hval, lval in cons:
        closes.append(cval); highs.append(hval); lows.append(lval); vols.append(100.0)
    closes.append(111.0); highs.append(111.1); lows.append(110.9); vols.append(breakout_volume)
    for _ in range(3):
        closes.append(111.0); highs.append(111.1); lows.append(110.9); vols.append(100.0)
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": np.asarray(highs), "l": np.asarray(lows),
                         "c": c, "v": np.asarray(vols)})


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("pennant_dir", "pennant_level", "vol_avg20", "atr"):
            self.assertIn(col, ind.columns)

    def test_armed_at_consolidation_end(self):
        ind = indicators.add_indicators(_pennant_frame())
        # Pole ends (stalls) at bar 35; consolidation bars 36-40 arm it.
        self.assertEqual(int(ind["pennant_dir"].iloc[40]), 1)
        self.assertAlmostEqual(float(ind["pennant_level"].iloc[40]), 110.1,
                               places=6)

    def test_no_arm_when_highs_rising(self):
        # Slice before the flat tail: the tail itself would flatten
        # the range and legitimately satisfy convergence later.
        df = _pennant_frame(rising_highs=True).iloc[:41]
        ind = indicators.add_indicators(df)
        self.assertFalse((ind["pennant_dir"] != 0).any())

    def test_vol_avg_excludes_current_bar(self):
        ind = indicators.add_indicators(_pennant_frame())
        # vol_avg20[41] = mean of v[21..40] = 100 (breakout bar excluded).
        self.assertAlmostEqual(float(ind["vol_avg20"].iloc[41]), 100.0)

    def test_no_lookahead_indicators(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("pennant_dir", "pennant_level"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:200].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, direction, level, c, v, avg):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": v,
            "pennant_dir": direction, "pennant_level": level,
            "vol_avg20": avg,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_flat_data_no_entries(self):
        n = 200
        flat = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0), "h": np.full(n, 100.0),
            "l": np.full(n, 100.0), "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
        })
        sig = signals.add_signals(indicators.add_indicators(flat))
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_breakout_enters_long_once(self):
        ind = indicators.add_indicators(_pennant_frame())
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[41])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_breakout_without_volume_no_entry(self):
        ind = indicators.add_indicators(_pennant_frame(breakout_volume=100.0))
        sig = signals.add_signals(ind)
        self.assertFalse(sig["long_entry"].any())

    def test_exit_on_opposite_breakout(self):
        # Bull breakout at bar 1, bear breakout at bar 3 -> flip.
        direction = np.array([0, 1, 0, -1])
        level = np.array([np.nan, 110.0, np.nan, 108.0])
        c = np.array([100.0, 111.0, 111.0, 107.0])
        v = np.array([100.0, 500.0, 100.0, 500.0])
        avg = np.array([100.0, 100.0, 100.0, 100.0])
        sig = signals.add_signals(self._signal_frame(direction, level, c, v, avg))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_no_lookahead_signals(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        full = signals.add_signals(indicators.add_indicators(df))
        trunc = signals.add_signals(indicators.add_indicators(short))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )


class TestRiskAndRegistry(unittest.TestCase):
    def test_registered(self):
        self.assertIn("pennant_pattern", REGISTRY)
        self.assertEqual(REGISTRY["pennant_pattern"].warmup_bars, risk.WARMUP)

    def test_risk_config_sane(self):
        r = risk.RISK
        self.assertGreater(r.stop_atr_mult, 0)
        self.assertGreater(r.risk_frac, 0)
        self.assertLessEqual(r.max_leverage, 3.0)
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.5)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 168)
        self.assertTrue(r.allow_longs and r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 40)

    def test_backtest_smoke(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)
        self.assertIn("net_pnl_usd", m)


if __name__ == "__main__":
    unittest.main()
