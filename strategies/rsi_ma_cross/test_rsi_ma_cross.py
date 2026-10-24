"""RSI vs its SMA signal-line cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_ma_cross import indicators, risk, signals


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
        for col in ("rsi", "rsi_sma", "atr"):
            self.assertIn(col, ind.columns)

    def test_rsi_all_gains_is_100(self):
        # Every bar up: average loss is 0 -> Wilder RSI is 100.
        c = 100.0 + np.arange(100, dtype=float)
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertAlmostEqual(float(ind["rsi"].iloc[-1]), 100.0, places=9)

    def test_rsi_all_losses_is_0(self):
        # Every bar down: average gain is 0 -> Wilder RSI is 0.
        c = 200.0 - np.arange(100, dtype=float)
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertAlmostEqual(float(ind["rsi"].iloc[-1]), 0.0, places=9)

    def test_rsi_bounded_no_nan(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(ind["rsi"].isna().any())
        self.assertTrue((ind["rsi"] >= 0).all())
        self.assertTrue((ind["rsi"] <= 100).all())

    def test_rsi_sma_is_trailing_mean_of_rsi(self):
        ind = indicators.add_indicators(_random_walk_frame())
        expected = ind["rsi"].rolling(14, min_periods=14).mean().iloc[-1]
        self.assertAlmostEqual(float(ind["rsi_sma"].iloc[-1]),
                               float(expected), places=9)

    def test_rsi_sma_lags_rsi_on_sustained_rise(self):
        # On a long steady rise RSI pins at 100; the SMA trails up to
        # it from below, so rsi_sma ends below (or equal to) rsi.
        c = 100.0 + np.arange(300, dtype=float) * 0.5
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertLessEqual(float(ind["rsi_sma"].iloc[-1]),
                             float(ind["rsi"].iloc[-1]))

    def test_no_lookahead(self):
        # rsi/rsi_sma at bar j must not change when later bars are
        # appended (Wilder smoothing and trailing SMA are causal).
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("rsi", "rsi_sma"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:200].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self):
        return signals.add_signals(indicators.add_indicators(_random_walk_frame()))

    def test_signal_columns_boolean_no_nan(self):
        sig = self._signal_frame()
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def _direct_frame(self, cross_bar=50, direction=1):
        """Deterministic frame: rsi_sma flat at 50, rsi steps across it.

        direction=1: rsi 40 before cross_bar, 60 from cross_bar.
        direction=-1: rsi 60 before, 40 from cross_bar.
        """
        n = 100
        rsi = np.full(n, 40.0 if direction == 1 else 60.0)
        rsi[cross_bar:] = 60.0 if direction == 1 else 40.0
        df = _frame_from_close(np.full(n, 100.0), seed=9)
        df["rsi"] = rsi
        df["rsi_sma"] = np.full(n, 50.0)
        return df

    def test_long_entry_on_cross_above(self):
        df = self._direct_frame(direction=1)
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_entry"].iloc[50])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_short_entry_on_cross_below(self):
        df = self._direct_frame(direction=-1)
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_entry"].iloc[50])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_no_entry_without_cross(self):
        # RSI rides above its average the whole time -> no cross,
        # no entry in either direction.
        n = 100
        df = _frame_from_close(np.full(n, 100.0), seed=9)
        df["rsi"] = np.full(n, 60.0)
        df["rsi_sma"] = np.full(n, 50.0)
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_exit_on_opposite_cross(self):
        # After the long entry at bar 50, RSI drops back below its
        # average at bar 70 -> long_exit fires exactly there.
        df = self._direct_frame(direction=1)
        rsi = df["rsi"].to_numpy().copy()
        rsi[70:] = 40.0
        df["rsi"] = rsi
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["long_exit"].iloc[50])

    def test_long_and_short_exits_are_mirrors(self):
        # A cross up is a short_exit as well as a long_entry; a cross
        # down is a long_exit as well as a short_entry.
        df = self._direct_frame(direction=1)
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_exit"].iloc[50])
        df2 = self._direct_frame(direction=-1)
        sig2 = signals.add_signals(df2)
        self.assertTrue(sig2["long_exit"].iloc[50])


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
