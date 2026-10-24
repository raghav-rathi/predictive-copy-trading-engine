"""Golden Cross / Death Cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.golden_cross import indicators, risk, signals


def _frame_from_parts(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _flat_frame(n=300, close=100.0, vol=100.0):
    c = np.full(n, close)
    h = c * 1.001
    l = c * 0.999
    return _frame_from_parts(c, h, l, c, np.full(n, vol))


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
        for col in ("sma50", "sma200", "sma_diff", "atr"):
            self.assertIn(col, ind.columns)

    def test_flat_closes_give_equal_averages(self):
        # Constant closes -> both SMAs equal the close after warmup.
        ind = indicators.add_indicators(_flat_frame(300, close=100.0))
        self.assertAlmostEqual(float(ind["sma50"].iloc[-1]), 100.0, places=9)
        self.assertAlmostEqual(float(ind["sma200"].iloc[-1]), 100.0, places=9)
        self.assertAlmostEqual(float(ind["sma_diff"].iloc[-1]), 0.0, places=9)

    def test_sma50_hand_window_value(self):
        # sma50 at the last bar = mean of the last 50 closes.
        c = np.linspace(100.0, 150.0, 300)
        ind = indicators.add_indicators(_frame_from_close(c, seed=3))
        expected = float(c[-50:].mean())
        self.assertAlmostEqual(float(ind["sma50"].iloc[-1]), expected, places=9)

    def test_sma200_hand_window_value(self):
        # sma200 at the last bar = mean of the last 200 closes.
        c = np.linspace(100.0, 150.0, 300)
        ind = indicators.add_indicators(_frame_from_close(c, seed=3))
        expected = float(c[-200:].mean())
        self.assertAlmostEqual(float(ind["sma200"].iloc[-1]), expected, places=9)

    def test_rising_trend_puts_fast_above_slow(self):
        # Sustained rise: the 50-bar average sits above the 200-bar one.
        c = np.linspace(100.0, 150.0, 300)
        ind = indicators.add_indicators(_frame_from_close(c, seed=3))
        self.assertGreater(float(ind["sma_diff"].iloc[-1]), 0.0)

    def test_no_lookahead(self):
        # sma50 at bar j must not change when later bars are appended.
        df = _random_walk_frame()
        short = df.iloc[:300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["sma50"].iloc[:300].reset_index(drop=True),
            ind_short["sma50"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _direct_frame(self, fast, slow):
        df = _frame_from_close(np.full(len(fast), 100.0), seed=9)
        df["sma50"] = np.asarray(fast, dtype=float)
        df["sma200"] = np.asarray(slow, dtype=float)
        return df

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_golden_cross(self):
        # sma50 flat at 100, jumps to 101+ at bar 50 over a flat
        # sma200 at 100.5 -> Golden Cross fires exactly at bar 50.
        fast = np.full(100, 100.0)
        fast[50:] = 100.0 + (np.arange(50) + 1.0)
        slow = np.full(100, 100.5)
        sig = signals.add_signals(self._direct_frame(fast, slow))
        self.assertTrue(sig["long_entry"].iloc[50])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_no_entry_without_cross(self):
        # sma50 pinned below sma200 the whole frame -> no entry.
        sig = signals.add_signals(self._direct_frame(
            np.full(100, 100.0), np.full(100, 100.5)))
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_short_entry_on_death_cross(self):
        # sma50 flat at 101, drops to 100- at bar 50 under a flat
        # sma200 at 100.5 -> Death Cross fires exactly at bar 50.
        fast = np.full(100, 101.0)
        fast[50:] = 101.0 - (np.arange(50) + 1.0)
        slow = np.full(100, 100.5)
        sig = signals.add_signals(self._direct_frame(fast, slow))
        self.assertTrue(sig["short_entry"].iloc[50])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_long_exit_on_opposite_cross(self):
        # Golden Cross at 50, then sma50 collapses to 99 at bar 70
        # -> Death Cross there is the long exit.
        fast = np.full(100, 100.0)
        fast[50:70] = 100.0 + (np.arange(20) + 1.0)
        fast[70:] = 99.0
        slow = np.full(100, 100.5)
        sig = signals.add_signals(self._direct_frame(fast, slow))
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["long_exit"].iloc[50])

    def test_short_exit_on_opposite_cross(self):
        # Death Cross at 50, then sma50 recovers to 102 at bar 70
        # -> Golden Cross there is the short exit.
        fast = np.full(100, 101.0)
        fast[50:70] = 101.0 - (np.arange(20) + 1.0)
        fast[70:] = 102.0
        slow = np.full(100, 100.5)
        sig = signals.add_signals(self._direct_frame(fast, slow))
        self.assertTrue(sig["short_exit"].iloc[70])
        self.assertFalse(sig["short_exit"].iloc[50])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 3.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 240)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 250)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
