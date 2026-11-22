"""Multi-Timeframe EMA Agreement tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.multi_timeframe_ema_agreement import indicators, risk, signals

T0 = 1_700_006_400_000  # 2023-11-15 00:00:00 UTC (4h-aligned)


def _frame_from_close(c, seed=7, t0=T0):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _signal_frame(n=12, fast1=None, slow1=None, fast4=None, slow4=None):
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    f1 = np.full(n, 100.0) if fast1 is None else np.asarray(fast1, dtype=float)
    s1 = np.full(n, 100.0) if slow1 is None else np.asarray(slow1, dtype=float)
    f4 = np.full(n, 100.0) if fast4 is None else np.asarray(fast4, dtype=float)
    s4 = np.full(n, 100.0) if slow4 is None else np.asarray(slow4, dtype=float)
    return pd.DataFrame({
        "t": t, "o": np.full(n, 100.0), "h": np.full(n, 100.1),
        "l": np.full(n, 99.9), "c": np.full(n, 100.0),
        "v": np.full(n, 100.0), "ema_fast_1h": f1, "ema_slow_1h": s1,
        "ema_fast_4h": f4, "ema_slow_4h": s4,
    })


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("ema_fast_1h", "ema_slow_1h", "ema_fast_4h",
                    "ema_slow_4h", "atr"):
            self.assertIn(col, ind.columns)

    def test_4h_ema_uses_only_completed_bars(self):
        # Flat 100s: the 4h EMA(9) needs 9 completed 4h bars and
        # first becomes visible at the 1h bar after the 9th 4h bar
        # closes (bar 36), not before.
        ind = indicators.add_indicators(_frame_from_close(np.full(200, 100.0)))
        self.assertTrue(ind["ema_fast_4h"].iloc[:36].isna().all())
        self.assertTrue(np.allclose(ind["ema_fast_4h"].iloc[36:], 100.0))
        # EMA(21) needs 21 completed 4h bars -> visible at bar 84.
        self.assertTrue(ind["ema_slow_4h"].iloc[:84].isna().all())
        self.assertTrue(np.allclose(ind["ema_slow_4h"].iloc[84:], 100.0))

    def test_4h_ema_reflects_step_change_only_after_close(self):
        # Close 100 for 40 bars (10 completed 4h bars, so the 4h
        # EMA is valid), then 110. The 4h bar covering bars 40-43
        # closes at bar 43, so the 4h EMA at bar 43 still reflects
        # only 100s; bar 44 is the first to see the 110s.
        c = np.concatenate([np.full(40, 100.0), np.full(200, 110.0)])
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertAlmostEqual(ind["ema_fast_4h"].iloc[43], 100.0, places=6)
        self.assertGreater(ind["ema_fast_4h"].iloc[44], 100.0)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        full = indicators.add_indicators(df)
        part = indicators.add_indicators(short)
        for col in ("ema_fast_1h", "ema_slow_1h", "ema_fast_4h", "ema_slow_4h"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                part[col].reset_index(drop=True), check_names=False)


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_cross_up_with_4h_agreement_enters_long(self):
        fast1 = [100.0] * 5 + [101.0] * 7
        slow1 = [100.0] * 12
        f = _signal_frame(fast1=fast1, slow1=slow1,
                          fast4=[102.0] * 12, slow4=[101.0] * 12)
        sig = signals.add_signals(f)
        self.assertTrue(sig["long_entry"].iloc[5])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_cross_up_blocked_when_4h_disagrees(self):
        fast1 = [100.0] * 5 + [101.0] * 7
        slow1 = [100.0] * 12
        f = _signal_frame(fast1=fast1, slow1=slow1,
                          fast4=[99.0] * 12, slow4=[101.0] * 12)
        sig = signals.add_signals(f)
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_cross_down_with_4h_agreement_enters_short(self):
        fast1 = [100.0] * 5 + [99.0] * 7
        slow1 = [100.0] * 12
        f = _signal_frame(fast1=fast1, slow1=slow1,
                          fast4=[98.0] * 12, slow4=[99.0] * 12)
        sig = signals.add_signals(f)
        self.assertTrue(sig["short_entry"].iloc[5])

    def test_exit_on_opposite_cross(self):
        fast1 = [100.0] * 5 + [101.0] * 3 + [99.0] * 4
        slow1 = [100.0] * 12
        f = _signal_frame(fast1=fast1, slow1=slow1,
                          fast4=[102.0] * 12, slow4=[101.0] * 12)
        sig = signals.add_signals(f)
        self.assertTrue(sig["long_entry"].iloc[5])
        self.assertTrue(sig["long_exit"].iloc[8])
        # The cross-down at bar 8 does not also open a short: the
        # 4h pair still points long, so the filter blocks it.
        self.assertFalse(sig["short_entry"].iloc[8])

    def test_no_lookahead_signals(self):
        df = _random_walk_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        part = signals.add_signals(
            indicators.add_indicators(df.iloc[:200]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                part[col].reset_index(drop=True), check_names=False)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 3.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 120)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 120)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        self.assertGreaterEqual(res.metrics()["trades"], 0)


if __name__ == "__main__":
    unittest.main()
