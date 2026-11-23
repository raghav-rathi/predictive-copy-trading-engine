"""Tillson T3 tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.t3_ma_trend import indicators, risk, signals


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


def _ema_loop(x, n):
    """Independent EMA recursion (seeded at x[0]) for cross-checks."""
    k = 2.0 / (n + 1)
    out = [float(x[0])]
    for v_ in x[1:]:
        out.append(float(v_) * k + out[-1] * (1 - k))
    return out


class TestTillsonT3(unittest.TestCase):
    def test_coefficients_sum_to_one(self):
        v = 0.7
        c1 = -(v ** 3)
        c2 = 3 * v ** 2 + 3 * v ** 3
        c3 = -6 * v ** 2 - 3 * v - 3 * v ** 3
        c4 = 1 + 3 * v + v ** 3 + 3 * v ** 2
        self.assertAlmostEqual(c1 + c2 + c3 + c4, 1.0)
        self.assertAlmostEqual(c1, -0.343)
        self.assertAlmostEqual(c2, 2.499)
        self.assertAlmostEqual(c3, -6.069)
        self.assertAlmostEqual(c4, 4.913)

    def test_t3_constant_series(self):
        c = pd.Series([100.0] * 60)
        out = indicators.tillson_t3(c, 10, 0.7)
        self.assertFalse(out.isna().any())
        np.testing.assert_allclose(out.values, 100.0, atol=1e-9)

    def test_t3_golden_value_ramp(self):
        # Cross-checked against an independent loop-EMA computation:
        # T3(10, 0.7) of closes 1..10 is 4.405000554779874 at bar 9,
        # and of closes 1..50 is 45.95806889426845 at bar 49.
        c10 = pd.Series(np.arange(1.0, 11.0))
        self.assertAlmostEqual(
            indicators.tillson_t3(c10, 10, 0.7).iloc[-1],
            4.405000554779874, places=9)
        c50 = pd.Series(np.arange(1.0, 51.0))
        self.assertAlmostEqual(
            indicators.tillson_t3(c50, 10, 0.7).iloc[-1],
            45.95806889426845, places=9)

    def test_t3_matches_loop_ema_computation(self):
        c = np.arange(1.0, 31.0)
        e1 = _ema_loop(c, 10)
        e2 = _ema_loop(e1, 10)
        e3 = _ema_loop(e2, 10)
        e4 = _ema_loop(e3, 10)
        e5 = _ema_loop(e4, 10)
        e6 = _ema_loop(e5, 10)
        v = 0.7
        c1, c2 = -(v ** 3), 3 * v ** 2 + 3 * v ** 3
        c3 = -6 * v ** 2 - 3 * v - 3 * v ** 3
        c4 = 1 + 3 * v + v ** 3 + 3 * v ** 2
        expected = c1 * e6[-1] + c2 * e5[-1] + c3 * e4[-1] + c4 * e3[-1]
        got = indicators.tillson_t3(pd.Series(c), 10, 0.7).iloc[-1]
        self.assertAlmostEqual(got, expected, places=9)

    def test_t3_faster_than_single_ema_on_step(self):
        # After a step up, T3(10) must sit closer to the new level
        # than a single EMA(10) — the lag-reduction claim. Note the
        # overshoot: T3 ends slightly ABOVE 120 after the step (the
        # negative c1/c3 weights ring past a sharp move). That is a
        # real T3 property, not a bug — see CALIBRATION.md.
        c = pd.Series([100.0] * 100 + [120.0] * 40)
        from strategies import base as B
        t3 = indicators.tillson_t3(c, 10, 0.7).iloc[-1]
        ema = B.ema(c, 10).iloc[-1]
        self.assertGreater(t3, ema)
        self.assertLess(t3, 121.0)  # overshoot stays < 1% of the step

    def test_t3_vfactor_zero_is_triple_ema(self):
        # vfactor 0 collapses the weights to c4 = 1, so T3 == e3.
        c = pd.Series(np.arange(1.0, 51.0))
        t3 = indicators.tillson_t3(c, 10, 0.0)
        e1 = c.ewm(span=10, adjust=False, min_periods=1).mean()
        e2 = e1.ewm(span=10, adjust=False, min_periods=1).mean()
        e3 = e2.ewm(span=10, adjust=False, min_periods=1).mean()
        pd.testing.assert_series_equal(t3, e3, check_names=False)


class TestIndicators(unittest.TestCase):
    def test_columns_present_no_nan(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("t3_fast", "t3_slow", "t3_rising", "t3_falling",
                    "long_setup", "short_setup"):
            self.assertIn(col, ind.columns)
            self.assertFalse(ind[col].isna().any(), col)
        # ATR(14) from base.py is NaN for the first 13 bars only.
        self.assertIn("atr", ind.columns)
        self.assertTrue(ind["atr"].iloc[:13].isna().all())
        self.assertFalse(ind["atr"].iloc[13:].isna().any())

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
        for col in ("long_setup", "short_setup", "t3_fast", "t3_slow"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:400].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, long_setup, short_setup, c, t3, rising, falling):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c * 1.001, "l": c * 0.999, "c": c,
            "v": np.full(n, 100.0), "t3_fast": t3,
            "t3_rising": rising, "t3_falling": falling,
            "long_setup": long_setup, "short_setup": short_setup,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_transition_only_no_reentry(self):
        n = 6
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False] + [True] * 5),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 101.0, 102.0, 103.0, 104.0, 105.0]),
            t3=np.array([100.0, 100.5, 101.5, 102.5, 103.5, 104.5]),
            rising=np.array([False] + [True] * 5),
            falling=np.zeros(n, dtype=bool),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(sig["long_entry"].iloc[1])

    def test_exit_on_close_below_t3(self):
        n = 4
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 102.0, 103.0, 100.0]),
            t3=np.array([100.0, 101.0, 102.0, 102.0]),
            rising=np.array([False, True, True, False]),
            falling=np.array([False, False, False, True]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_exit_on_t3_turning_down(self):
        n = 3
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False]),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 102.0, 103.0]),
            t3=np.array([100.0, 101.0, 100.5]),
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
            t3=np.array([100.0, 101.0, 102.0, 101.0]),
            rising=np.array([False, True, True, False]),
            falling=np.array([False, False, False, True]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_short_exit_on_close_above_t3(self):
        n = 3
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.zeros(n, dtype=bool),
            short_setup=np.array([False, True, False]),
            c=np.array([100.0, 98.0, 101.0]),
            t3=np.array([100.0, 99.0, 99.5]),
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
