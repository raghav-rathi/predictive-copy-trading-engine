"""Chaikin ADL trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chaikin_adl_trend import indicators, risk, signals
from strategies.chaikin_adl_trend.indicators import (
    accumulation_distribution_line,
    money_flow_multiplier,
)


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
        for col in ("adl", "adl_sma", "sma50", "atr"):
            self.assertIn(col, ind.columns)

    def test_mfm_hand_computation(self):
        # One bar: h=110, l=90, c=105 -> ((105-90)-(110-105))/20 = 0.5.
        # With v=1000 the MFV (and 1-bar ADL) is exactly 500.
        h = pd.Series([110.0])
        l = pd.Series([90.0])
        c = pd.Series([105.0])
        v = pd.Series([1000.0])
        self.assertAlmostEqual(float(money_flow_multiplier(h, l, c).iloc[0]),
                               0.5, places=9)
        self.assertAlmostEqual(
            float(accumulation_distribution_line(h, l, c, v).iloc[0]),
            500.0, places=9)

    def test_mfm_extremes(self):
        # Close on the high -> +1; close on the low -> -1.
        self.assertAlmostEqual(
            float(money_flow_multiplier(pd.Series([110.0]), pd.Series([90.0]),
                                        pd.Series([110.0])).iloc[0]),
            1.0, places=9)
        self.assertAlmostEqual(
            float(money_flow_multiplier(pd.Series([110.0]), pd.Series([90.0]),
                                        pd.Series([90.0])).iloc[0]),
            -1.0, places=9)

    def test_zero_range_bar_guard(self):
        # h == l -> no range, no money-flow signal: MFM 0, ADL flat at 0
        # no matter how large the volume.
        n = 10
        c = np.full(n, 100.0)
        df = _frame_from_parts(c, c, c, c, np.full(n, 1000.0))
        adl = accumulation_distribution_line(df["h"], df["l"],
                                             df["c"], df["v"])
        self.assertTrue((adl == 0.0).all())

    def test_adl_equals_manual_cumsum(self):
        df = _random_walk_frame()
        h, l, c, v = df["h"], df["l"], df["c"], df["v"]
        rng = h - l
        mfm = np.where(rng != 0, ((c - l) - (h - c)) / rng.where(rng != 0, 1.0), 0.0)
        expected = np.cumsum(mfm * v.to_numpy())
        got = accumulation_distribution_line(h, l, c, v).to_numpy()
        np.testing.assert_allclose(got, expected, rtol=1e-9)

    def test_adl_sma_is_trailing_mean_of_adl(self):
        ind = indicators.add_indicators(_random_walk_frame())
        expected = ind["adl"].rolling(10, min_periods=10).mean().iloc[-1]
        self.assertAlmostEqual(float(ind["adl_sma"].iloc[-1]),
                               float(expected), places=9)

    def test_sma50_rises_on_rising_closes(self):
        c = np.concatenate([np.full(100, 100.0), np.linspace(100.0, 130.0, 200)])
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertGreater(float(ind["sma50"].iloc[-1]),
                           float(ind["sma50"].iloc[60]))

    def test_no_lookahead(self):
        # adl/adl_sma/sma50 at bar j must not change when later bars
        # are appended (all windows trailing).
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("adl", "adl_sma", "sma50"):
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

    def _direct_frame(self, cross_bar=50, direction=1, close_vs_sma50=1):
        """Deterministic frame: adl_sma flat at 0, adl steps across it.

        direction=1: adl -1 before cross_bar, +1 from cross_bar (cross up).
        direction=-1: adl +1 before, -1 from cross_bar (cross down).
        close_vs_sma50=+1 puts close above sma50 (passes the long
        filter, fails the short filter); -1 mirrors it.
        """
        n = 100
        adl = np.full(n, -1.0 if direction == 1 else 1.0)
        adl[cross_bar:] = 1.0 if direction == 1 else -1.0
        df = _frame_from_close(np.full(n, 110.0), seed=9)
        df["adl"] = adl
        df["adl_sma"] = np.zeros(n)
        df["sma50"] = np.full(n, 100.0 if close_vs_sma50 == 1 else 120.0)
        return df

    def test_long_entry_requires_cross_and_trend_filter(self):
        df = self._direct_frame(direction=1, close_vs_sma50=1)
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_entry"].iloc[50])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_trend_filter_blocks_long_below_sma50(self):
        # Clean ADL cross above, but close sits below SMA(50) -> the
        # trend filter blocks the long entry.
        df = self._direct_frame(direction=1, close_vs_sma50=-1)
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())

    def test_short_entry_symmetry(self):
        df = self._direct_frame(direction=-1, close_vs_sma50=-1)
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_entry"].iloc[50])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_trend_filter_blocks_short_above_sma50(self):
        df = self._direct_frame(direction=-1, close_vs_sma50=1)
        sig = signals.add_signals(df)
        self.assertFalse(sig["short_entry"].any())

    def test_exit_on_opposite_cross(self):
        # After the long entry at bar 50, ADL drops back below its SMA
        # at bar 70 -> long_exit fires exactly there (no trend filter
        # on exits).
        df = self._direct_frame(direction=1, close_vs_sma50=1)
        adl = df["adl"].to_numpy().copy()
        adl[70:] = -1.0
        df["adl"] = adl
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["long_exit"].iloc[50])


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
        self.assertEqual(risk.WARMUP, 70)

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
