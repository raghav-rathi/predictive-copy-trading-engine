"""Hull MA trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.hull_ma_trend import indicators, risk, signals


def _frame(o, h, l, c, v, seed=7):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _flat_frame(n=300, price=100.0, vol=100.0):
    c = np.full(n, price)
    return _frame(c, c * 1.001, c * 0.999, c, np.full(n, vol))


def _ramp_frame(n=300, start=100.0, step=0.5):
    c = start + step * np.arange(n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    return _frame(o, h, l, c, np.full(n, 100.0))


def _random_walk_frame(n=800, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestWma(unittest.TestCase):
    def test_wma_known_values(self):
        # WMA([1,2,3], 3) = (1*1 + 2*2 + 3*3) / 6 = 14/6.
        s = pd.Series([1.0, 2.0, 3.0])
        self.assertAlmostEqual(indicators.wma(s, 3).iloc[-1], 14.0 / 6.0)
        # WMA([1,2,3,4], 4) = (1 + 4 + 9 + 16) / 10 = 3.0.
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        self.assertAlmostEqual(indicators.wma(s, 4).iloc[-1], 3.0)

    def test_wma_weights_recent_most(self):
        # A jump on the last bar moves WMA(3) by 3/6 of the jump.
        s = pd.Series([10.0, 10.0, 20.0])
        self.assertAlmostEqual(indicators.wma(s, 3).iloc[-1], (10 + 20 + 60) / 6.0)

    def test_wma_nan_until_full_window(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0])
        out = indicators.wma(s, 4)
        self.assertTrue(out.iloc[:3].isna().all())
        self.assertFalse(np.isnan(out.iloc[3]))


class TestHullMa(unittest.TestCase):
    def test_hull_golden_value(self):
        # HMA(4) on 1..8: inner WMA(2)/WMA(4) give diff 13/3 at bar 3
        # and 16/3 at bar 4; WMA(2) of those = 5.0 at bar 4.
        c = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        hma = indicators.hull_ma(c, 4)
        self.assertAlmostEqual(hma.iloc[4], 5.0)
        self.assertTrue(hma.iloc[:4].isna().all())

    def test_hull_tracks_linear_series_exactly(self):
        # On a perfectly linear series HMA(4) equals the close once
        # valid (the WMA algebra cancels the lag exactly when
        # sqrt(n) == 2). HMA(16) lags a unit-slope ramp by exactly
        # 2/3 of a bar-step: last + 1/3 - (4-1)/3 = last - 2/3.
        c = pd.Series(np.arange(1.0, 101.0))
        hma4 = indicators.hull_ma(c, 4)
        valid = hma4.dropna()
        np.testing.assert_allclose(valid.values, c.loc[valid.index].values)
        hma16 = indicators.hull_ma(c, 16)
        valid16 = hma16.dropna()
        np.testing.assert_allclose(
            valid16.values, c.loc[valid16.index].values - 2.0 / 3.0
        )

    def test_hull_constant_series(self):
        c = pd.Series([100.0] * 120)
        hma = indicators.hull_ma(c, 16)
        self.assertAlmostEqual(hma.iloc[-1], 100.0)

    def test_hull_faster_than_ema_on_ramp(self):
        # After a step up, HMA(16) must be closer to the new level
        # than EMA(16) — the lag-halving claim, checked directly.
        c = pd.Series([100.0] * 100 + [120.0] * 40)
        from strategies import base as B
        hma = indicators.hull_ma(c, 16).iloc[-1]
        ema = B.ema(c, 16).iloc[-1]
        self.assertGreater(hma, ema)
        self.assertLessEqual(hma, 120.0)


class TestIndicators(unittest.TestCase):
    def test_columns_present_no_nan(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("hma16", "hma64", "hma16_rising", "hma16_falling",
                    "long_setup", "short_setup"):
            self.assertIn(col, ind.columns)
            self.assertFalse(ind[col].isna().any(), col)
        # ATR(14) from base.py is NaN for the first 13 bars only
        # (min_periods=14), like every other strategy in the repo.
        self.assertIn("atr", ind.columns)
        self.assertTrue(ind["atr"].iloc[:13].isna().all())
        self.assertFalse(ind["atr"].iloc[13:].isna().any())

    def test_seeding_equals_close_before_valid(self):
        ind = indicators.add_indicators(_flat_frame(50))
        # HMA(16) first valid at bar 19; bars 0..18 are seeded = close.
        self.assertTrue((ind["hma16"].iloc[:19] == 100.0).all())
        self.assertTrue((ind["hma64"].iloc[:19] == 100.0).all())

    def test_flat_series_no_setup(self):
        ind = indicators.add_indicators(_flat_frame())
        self.assertFalse(ind["long_setup"].any())
        self.assertFalse(ind["short_setup"].any())

    def test_uptrend_ramp_fires_long_setup(self):
        ind = indicators.add_indicators(_ramp_frame())
        self.assertTrue(ind["long_setup"].iloc[-1])
        self.assertFalse(ind["short_setup"].iloc[-1])

    def test_downtrend_ramp_fires_short_setup(self):
        ind = indicators.add_indicators(_ramp_frame(step=-0.5))
        self.assertTrue(ind["short_setup"].iloc[-1])
        self.assertFalse(ind["long_setup"].iloc[-1])

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:400]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("long_setup", "short_setup", "hma16", "hma64"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:400].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, long_setup, short_setup, c, hma16, rising, falling):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c * 1.001, "l": c * 0.999, "c": c,
            "v": np.full(n, 100.0), "hma16": hma16,
            "hma16_rising": rising, "hma16_falling": falling,
            "long_setup": long_setup, "short_setup": short_setup,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_transition_only_no_reentry(self):
        # Long setup true for 5 straight bars: exactly one entry.
        n = 6
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False] + [True] * 5),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0]),
            hma16=np.array([100.0, 100.5, 101.5, 102.5, 103.5, 104.5]),
            rising=np.array([False] + [True] * 5),
            falling=np.zeros(n, dtype=bool),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(sig["long_entry"].iloc[1])

    def test_exit_on_close_below_hma16(self):
        n = 4
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 102.0, 103.0, 100.0]),
            hma16=np.array([100.0, 101.0, 102.0, 102.0]),
            rising=np.array([False, True, True, False]),
            falling=np.array([False, False, False, True]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_exit_on_hma_turning_down(self):
        # Close still above HMA(16) but HMA turns down -> exit.
        n = 3
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False]),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 102.0, 103.0]),
            hma16=np.array([100.0, 101.0, 100.5]),
            rising=np.array([False, True, False]),
            falling=np.array([False, False, True]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[2])

    def test_opposite_setup_flips_position(self):
        n = 4
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.array([False, False, False, True]),
            c=np.array([100.0, 102.0, 103.0, 99.0]),
            hma16=np.array([100.0, 101.0, 102.0, 101.0]),
            rising=np.array([False, True, True, False]),
            falling=np.array([False, False, False, True]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_short_exit_on_close_above_hma16(self):
        n = 3
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.zeros(n, dtype=bool),
            short_setup=np.array([False, True, False]),
            c=np.array([100.0, 98.0, 101.0]),
            hma16=np.array([100.0, 99.0, 99.5]),
            rising=np.array([False, False, True]),
            falling=np.array([False, True, False]),
        ))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertTrue(sig["short_exit"].iloc[2])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 168)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 100)

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
