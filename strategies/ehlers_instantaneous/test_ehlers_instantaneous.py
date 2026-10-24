"""Ehlers Instantaneous Trendline tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_instantaneous import indicators, risk, signals
from strategies.ehlers_instantaneous.indicators import (
    ALPHA,
    instantaneous_trendline,
)


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
        for col in ("it", "atr"):
            self.assertIn(col, ind.columns)

    def test_seeded_with_price(self):
        # IT[0] = P[0], IT[1] = P[1] by construction.
        p = pd.Series([100.0, 101.0, 102.0, 103.0])
        it = instantaneous_trendline(p)
        self.assertAlmostEqual(float(it.iloc[0]), 100.0, places=9)
        self.assertAlmostEqual(float(it.iloc[1]), 101.0, places=9)

    def test_hand_computation_bar2(self):
        # alpha=0.07: c0=0.068775, c1=0.00245, c2=-0.066325,
        # d1=1.86, d2=-0.8649. P=[100,101,102], IT=[100,101]:
        # IT[2] = 0.068775*102 + 0.00245*101 - 0.066325*100
        #       + 1.86*101 - 0.8649*100 = 102.0 exactly.
        p = pd.Series([100.0, 101.0, 102.0])
        it = instantaneous_trendline(p)
        a = ALPHA
        c0 = a - a * a / 4.0
        c1 = 0.5 * a * a
        c2 = -(a - 0.75 * a * a)
        d1 = 2.0 * (1.0 - a)
        d2 = -(1.0 - a) ** 2
        expected = (c0 * 102.0 + c1 * 101.0 + c2 * 100.0
                    + d1 * 101.0 + d2 * 100.0)
        self.assertAlmostEqual(float(it.iloc[2]), float(expected), places=9)
        self.assertAlmostEqual(float(it.iloc[2]), 102.0, places=9)

    def test_flat_price_reproduces_exactly(self):
        # Coefficients sum to 1, so a flat series is a fixed point.
        p = pd.Series(np.full(200, 123.45))
        it = instantaneous_trendline(p)
        np.testing.assert_allclose(it.to_numpy(), 123.45, rtol=0, atol=1e-9)

    def test_it_tracks_steady_ramp(self):
        # On a slow linear ramp the low-lag filter converges close to
        # price (within 5% at the end) and is itself rising.
        c = np.linspace(100.0, 200.0, 300)
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertLess(abs(float(ind["it"].iloc[-1]) - 200.0), 0.05 * 200.0)
        self.assertGreater(float(ind["it"].iloc[-1]),
                           float(ind["it"].iloc[-50]))

    def test_coefficients_sum_to_one(self):
        # Price-term coefficients sum to alpha^2, recursion terms to
        # 1 - alpha^2: total DC gain exactly 1.
        a = ALPHA
        price_sum = (a - a * a / 4.0) + 0.5 * a * a - (a - 0.75 * a * a)
        recur_sum = 2.0 * (1.0 - a) - (1.0 - a) ** 2
        self.assertAlmostEqual(price_sum + recur_sum, 1.0, places=12)

    def test_no_lookahead(self):
        # IT[i] reads only P[..i] and IT[..i-1]: appending later bars
        # must not change the prefix.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["it"].iloc[:200].reset_index(drop=True),
            ind_short["it"].reset_index(drop=True),
            check_names=False,
        )

    def test_no_nan_on_random_walk(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(ind["it"].isna().any())


class TestSignals(unittest.TestCase):
    def _signal_frame(self):
        return signals.add_signals(indicators.add_indicators(_random_walk_frame()))

    def test_signal_columns_boolean_no_nan(self):
        sig = self._signal_frame()
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def _direct_frame(self, cross_bar=50, direction=1):
        """Deterministic frame: IT flat at 100, close steps across it.

        direction=1: close 99 before cross_bar, 101 from cross_bar.
        direction=-1: close 101 before, 99 from cross_bar.
        """
        n = 100
        close = np.full(n, 99.0 if direction == 1 else 101.0)
        close[cross_bar:] = 101.0 if direction == 1 else 99.0
        df = _frame_from_close(close, seed=9)
        df["it"] = np.full(n, 100.0)
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
        # Close rides above IT the whole time -> no cross, no entry.
        n = 100
        df = _frame_from_close(np.full(n, 101.0), seed=9)
        df["it"] = np.full(n, 100.0)
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_exit_on_opposite_cross(self):
        # After the long entry at bar 50, close drops back below IT
        # at bar 70 -> long_exit fires exactly there.
        df = self._direct_frame(direction=1)
        close = df["c"].to_numpy().copy()
        close[70:] = 99.0
        df["c"] = close
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
        self.assertEqual(risk.WARMUP, 60)

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
