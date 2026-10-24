"""Slow Stochastic tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.slow_stochastic import indicators, risk, signals
from strategies.slow_stochastic.indicators import K_N, D_N, OVERSOLD, OVERBOUGHT


def _frame_from_parts(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


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
        for col in ("stoch_k", "stoch_d", "atr"):
            self.assertIn(col, ind.columns)

    def test_k_bounded_0_to_100(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertTrue((ind["stoch_k"] >= 0).all())
        self.assertTrue((ind["stoch_k"] <= 100).all())

    def test_k_hand_computation(self):
        # 14 bars, h=110, l=90 throughout, close=105 on the last
        # bar -> %K = 100*(105-90)/(110-90) = 75.
        n = 14
        df = _frame_from_parts(
            np.full(n, 100.0), np.full(n, 110.0), np.full(n, 90.0),
            np.full(n, 100.0), np.ones(n))
        df.loc[df.index[-1], "c"] = 105.0
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["stoch_k"].iloc[-1]), 75.0, places=9)

    def test_k_at_extremes(self):
        # Close at the 14-bar low -> %K = 0; at the high -> 100.
        n = 14
        df_low = _frame_from_parts(
            np.full(n, 100.0), np.full(n, 110.0), np.full(n, 90.0),
            np.full(n, 90.0), np.ones(n))
        df_high = _frame_from_parts(
            np.full(n, 100.0), np.full(n, 110.0), np.full(n, 90.0),
            np.full(n, 110.0), np.ones(n))
        self.assertAlmostEqual(
            float(indicators.add_indicators(df_low)["stoch_k"].iloc[-1]),
            0.0, places=9)
        self.assertAlmostEqual(
            float(indicators.add_indicators(df_high)["stoch_k"].iloc[-1]),
            100.0, places=9)

    def test_zero_range_maps_to_neutral_50(self):
        # Dead-flat window (h == l == c): no range to divide by ->
        # %K = 50, not NaN or inf.
        n = 20
        df = _frame_from_parts(
            np.full(n, 100.0), np.full(n, 100.0), np.full(n, 100.0),
            np.full(n, 100.0), np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["stoch_k"].iloc[-1]), 50.0, places=9)
        self.assertFalse(ind["stoch_k"].isna().any())

    def test_d_is_sma3_of_k(self):
        # %K sequence [.., 10, 20, 30] on the last three bars ->
        # %D = 20 at the last bar.
        n = 16
        h = np.full(n, 110.0)
        l = np.full(n, 90.0)
        c = np.full(n, 100.0)
        c[-3:] = [92.0, 94.0, 96.0]  # %K = 10, 20, 30
        df = _frame_from_parts(c, h, l, c, np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["stoch_k"].iloc[-3]), 10.0, places=9)
        self.assertAlmostEqual(float(ind["stoch_k"].iloc[-1]), 30.0, places=9)
        self.assertAlmostEqual(float(ind["stoch_d"].iloc[-1]), 20.0, places=9)

    def test_no_lookahead(self):
        # %K at bar j must not change when later bars are appended.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["stoch_k"].iloc[:200].reset_index(drop=True),
            ind_short["stoch_k"].reset_index(drop=True),
            check_names=False,
        )

    def test_d_lags_k_on_sharp_move(self):
        # After a jump in %K, %D (a 3-bar average) must trail %K.
        n = 20
        h = np.full(n, 110.0)
        l = np.full(n, 90.0)
        c = np.full(n, 90.0)
        c[-1] = 110.0  # %K jumps 0 -> 100 on the last bar
        df = _frame_from_parts(c, h, l, c, np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertEqual(float(ind["stoch_k"].iloc[-1]), 100.0)
        self.assertLess(float(ind["stoch_d"].iloc[-1]), 100.0)


class TestSignals(unittest.TestCase):
    def _direct_frame(self, k_path, d_path):
        """Deterministic frame with hand-set %K/%D paths."""
        n = len(k_path)
        df = _frame_from_close(np.full(n, 100.0), seed=9)
        df["stoch_k"] = np.asarray(k_path, dtype=float)
        df["stoch_d"] = np.asarray(d_path, dtype=float)
        return df

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_cross_up_while_oversold(self):
        # %K crosses above %D at bar 10 while %K = 15 (< 20) ->
        # fires exactly there.
        k = [10.0] * 10 + [15.0, 18.0, 22.0]
        d = [12.0] * 10 + [14.0, 16.0, 18.0]
        # bar 9: k=10 <= d=12; bar 10: k=15 > d=14 -> cross above
        sig = signals.add_signals(self._direct_frame(k, d))
        self.assertTrue(sig["long_entry"].iloc[10])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_mid_range_cross_blocked(self):
        # Same cross shape but %K = 50 at the cross -> blocked by
        # the oversold filter.
        k = [40.0] * 10 + [50.0, 55.0, 60.0]
        d = [45.0] * 10 + [48.0, 52.0, 56.0]
        sig = signals.add_signals(self._direct_frame(k, d))
        self.assertFalse(sig["long_entry"].any())

    def test_short_entry_cross_down_while_overbought(self):
        # %K crosses below %D at bar 10 while %K = 85 (> 80) ->
        # fires exactly there.
        k = [90.0] * 10 + [85.0, 82.0, 78.0]
        d = [88.0] * 10 + [86.0, 84.0, 82.0]
        sig = signals.add_signals(self._direct_frame(k, d))
        self.assertTrue(sig["short_entry"].iloc[10])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_mid_range_cross_down_blocked(self):
        k = [60.0] * 10 + [50.0, 45.0, 40.0]
        d = [55.0] * 10 + [52.0, 48.0, 44.0]
        sig = signals.add_signals(self._direct_frame(k, d))
        self.assertFalse(sig["short_entry"].any())

    def test_exit_on_opposite_cross(self):
        # Long entry at bar 10, then %K crosses back below %D at
        # bar 11 -> long_exit fires exactly there (no zone filter
        # on exits).
        k = [10.0] * 10 + [15.0, 12.0, 10.0]
        d = [12.0] * 10 + [14.0, 13.0, 12.0]
        sig = signals.add_signals(self._direct_frame(k, d))
        self.assertTrue(sig["long_entry"].iloc[10])
        self.assertTrue(sig["long_exit"].iloc[11])
        self.assertFalse(sig["long_exit"].iloc[10])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.5)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 40)

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
