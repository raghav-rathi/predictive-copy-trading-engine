"""Ehlers Instantaneous Trendline tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_instantaneous_trend import indicators, risk, signals


def _frame(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _random_walk_frame(n=1500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _it_frame(c, it):
    """Signals-only frame: signals.py reads just c and it."""
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "c": np.asarray(c, dtype=float),
                         "it": np.asarray(it, dtype=float)})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("it", "atr"):
            self.assertIn(col, ind.columns)

    def test_no_nan(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(ind["it"].isna().any())
        self.assertTrue(np.isfinite(ind["it"]).all())

    def test_seeding(self):
        # IT[0] = C[0], IT[1] = C[1] per spec.
        c = pd.Series([100.0, 101.0, 102.0, 103.0, 104.0])
        it = indicators.instantaneous_trendline(c)
        self.assertEqual(it.iloc[0], 100.0)
        self.assertEqual(it.iloc[1], 101.0)

    def test_hand_computed_third_bar(self):
        # alpha=0.07: a1=0.068775, a2=0.00245, a3=0.066325,
        # b1=1.86, b2=0.8649.
        # IT[2] = 0.068775*102 + 0.00245*101 - 0.066325*100
        #       + 1.86*101 - 0.8649*100 = 102.0 exactly.
        c = pd.Series([100.0, 101.0, 102.0])
        it = indicators.instantaneous_trendline(c)
        self.assertAlmostEqual(it.iloc[2], 102.0, places=9)

    def test_linear_ramp_tracked_exactly(self):
        # The filter's coefficients sum to 1, so a linear ramp is
        # tracked with zero lag: IT[i] == C[i] for every bar.
        c = pd.Series([100.0 + float(i) for i in range(50)])
        it = indicators.instantaneous_trendline(c)
        pd.testing.assert_series_equal(
            it, c.rename("it"), check_names=False, atol=1e-9)

    def test_constant_price_stays_constant(self):
        c = pd.Series([100.0] * 50)
        it = indicators.instantaneous_trendline(c)
        self.assertTrue(np.allclose(it, 100.0))

    def test_coefficients_sum_to_one(self):
        # a1 + a2 - a3 + b1 - b2 == 1 (filter preserves DC level).
        a = 0.07
        total = (a - a * a / 4.0) + 0.5 * a * a - (a - 0.75 * a * a) \
            + 2.0 * (1.0 - a) - (1.0 - a) ** 2
        self.assertAlmostEqual(total, 1.0, places=12)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:800]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["it"].iloc[:800].reset_index(drop=True),
            ind_short["it"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_transition(self):
        sig = signals.add_signals(_it_frame(
            [100, 101, 102, 103, 104], [100, 100, 101, 102, 103]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_no_reentry_while_condition_persists(self):
        # Condition true bars 2..5, already long: one entry only.
        sig = signals.add_signals(_it_frame(
            [100, 101, 102, 103, 104, 105],
            [100, 100, 101, 102, 103, 104]))
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_exit_long_on_close_through_trendline(self):
        sig = signals.add_signals(_it_frame(
            [100, 101, 102, 103, 98, 97],
            [100, 100, 101, 102, 103, 102]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[4])
        self.assertFalse(sig["short_entry"].iloc[4])

    def test_exit_long_on_trendline_turning_against(self):
        # Price still above the line, but the line turns down.
        sig = signals.add_signals(_it_frame(
            [100, 101, 102, 103, 104, 105],
            [100, 100, 101, 102, 103, 102]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertFalse(sig["long_exit"].iloc[4])
        self.assertTrue(sig["long_exit"].iloc[5])

    def test_flip_long_to_short_on_opposite_transition(self):
        sig = signals.add_signals(_it_frame(
            [100, 101, 102, 103, 98],
            [100, 100, 101, 102, 101]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[4])
        self.assertTrue(sig["short_entry"].iloc[4])

    def test_short_entry_on_transition(self):
        sig = signals.add_signals(_it_frame(
            [100, 99, 98, 97], [100, 100, 99, 98]))
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_exit_short_on_close_through_trendline(self):
        sig = signals.add_signals(_it_frame(
            [100, 99, 98, 97, 99], [100, 100, 99, 98, 98]))
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertTrue(sig["short_exit"].iloc[4])

    def test_reentry_after_fresh_transition(self):
        # Long at bar 2, exit at bar 5 (line turns), fresh long
        # transition at bar 6 -> second entry.
        sig = signals.add_signals(_it_frame(
            [100, 101, 102, 103, 104, 103, 104, 105],
            [100, 100, 101, 102, 103, 102, 103, 104]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[5])
        self.assertTrue(sig["long_entry"].iloc[6])
        self.assertEqual(int(sig["long_entry"].sum()), 2)

    def test_no_signal_when_price_equals_trendline(self):
        sig = signals.add_signals(_it_frame(
            [100, 101, 102, 103], [100, 101, 102, 103]))
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)


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
        self.assertEqual(risk.WARMUP, 30)

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
