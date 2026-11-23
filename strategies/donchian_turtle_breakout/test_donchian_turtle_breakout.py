"""Donchian Turtle Breakout (System 1) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian_turtle_breakout import indicators, risk, signals


def _frame(o, h, l, c, v=None, seed=7):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _flat_frame(n=60, price=100.0):
    c = np.full(n, price)
    return _frame(c, c * 1.01, c * 0.99, c)


def _random_walk_frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    return _frame(o, h, l, c, v)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("donchian_high_20", "donchian_low_20",
                    "donchian_high_10", "donchian_low_10", "atr20", "atr",
                    "long_breakout", "short_breakout",
                    "long_exit_cond", "short_exit_cond"):
            self.assertIn(col, ind.columns)

    def test_prior_high_excludes_current_bar(self):
        # 20 bars with high exactly 100; bar 20 has high 110, close 105.
        # Hand-computed: prior-20 high at bar 20 = max(h[0:20]) = 100,
        # so close 105 > 100 is a breakout. If the channel wrongly
        # included bar 20, its high would be 110 and 105 would not break.
        base_h = np.full(20, 100.0)
        base_l = np.full(20, 90.0)
        base_c = np.full(20, 95.0)
        h = np.concatenate([base_h, [110.0]])
        l = np.concatenate([base_l, [95.0]])
        c = np.concatenate([base_c, [105.0]])
        o = c.copy()
        ind = indicators.add_indicators(_frame(o, h, l, c))
        self.assertEqual(ind["donchian_high_20"].iloc[20], 100.0)
        self.assertTrue(bool(ind["long_breakout"].iloc[20]))

    def test_no_breakout_when_close_equals_prior_high(self):
        # Strictly greater: close == prior high is NOT a breakout.
        base_h = np.full(20, 100.0)
        base_l = np.full(20, 90.0)
        base_c = np.full(20, 95.0)
        h = np.concatenate([base_h, [100.0]])
        l = np.concatenate([base_l, [95.0]])
        c = np.concatenate([base_c, [100.0]])
        ind = indicators.add_indicators(_frame(c, h, l, c))
        self.assertFalse(bool(ind["long_breakout"].iloc[20]))
        self.assertFalse(bool(ind["short_breakout"].iloc[20]))

    def test_short_breakout_mirror(self):
        base_h = np.full(20, 100.0)
        base_l = np.full(20, 90.0)
        base_c = np.full(20, 95.0)
        h = np.concatenate([base_h, [96.0]])
        l = np.concatenate([base_l, [85.0]])
        c = np.concatenate([base_c, [89.0]])
        ind = indicators.add_indicators(_frame(c, h, l, c))
        self.assertEqual(ind["donchian_low_20"].iloc[20], 90.0)
        self.assertTrue(bool(ind["short_breakout"].iloc[20]))

    def test_long_exit_level_is_prior_10_low(self):
        # 10 bars with low 90; bar 10 closes 89 < 90 -> exit condition.
        base_h = np.full(10, 100.0)
        base_l = np.full(10, 90.0)
        base_c = np.full(10, 95.0)
        h = np.concatenate([base_h, [96.0]])
        l = np.concatenate([base_l, [88.0]])
        c = np.concatenate([base_c, [89.0]])
        ind = indicators.add_indicators(_frame(c, h, l, c))
        self.assertEqual(ind["donchian_low_10"].iloc[10], 90.0)
        self.assertTrue(bool(ind["long_exit_cond"].iloc[10]))

    def test_boolean_columns_no_nan(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("long_breakout", "short_breakout",
                    "long_exit_cond", "short_exit_cond"):
            self.assertTrue(ind[col].dtype == bool, col)
            self.assertFalse(ind[col].isna().any(), col)

    def test_atr_nan_only_in_warmup(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(ind["atr20"].iloc[:19].isna().all())
        self.assertTrue(np.isfinite(ind["atr20"].iloc[60:]).all())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("long_breakout", "short_breakout", "long_exit_cond"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:300].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, lb, sb, lx_, sx_):
        n = len(lb)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        c = np.full(n, 100.0)
        return pd.DataFrame({
            "t": t, "o": c, "h": c * 1.01, "l": c * 0.99, "c": c,
            "v": np.full(n, 100.0),
            "long_breakout": lb, "short_breakout": sb,
            "long_exit_cond": lx_, "short_exit_cond": sx_,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_breakout(self):
        # Breakout at bar 1, held afterwards.
        sig = signals.add_signals(self._signal_frame(
            lb=np.array([False, True, True, True]),
            sb=np.zeros(4, dtype=bool),
            lx_=np.zeros(4, dtype=bool),
            sx_=np.zeros(4, dtype=bool),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        # No re-entry while held, even though the breakout persists.
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_exit_long_on_10bar_low_break(self):
        sig = signals.add_signals(self._signal_frame(
            lb=np.array([False, True, False, False]),
            sb=np.zeros(4, dtype=bool),
            lx_=np.array([False, False, False, True]),
            sx_=np.zeros(4, dtype=bool),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertFalse(sig["long_exit"].iloc[2])

    def test_exit_short_on_10bar_high_break(self):
        sig = signals.add_signals(self._signal_frame(
            lb=np.zeros(4, dtype=bool),
            sb=np.array([False, True, False, False]),
            lx_=np.zeros(4, dtype=bool),
            sx_=np.array([False, False, False, True]),
        ))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertTrue(sig["short_exit"].iloc[3])

    def test_flip_on_simultaneous_exit_and_opposite_breakout(self):
        # Long at bar 1; bar 3 breaks the 10-bar low (exit) AND the
        # 20-bar low (short breakout) -> exit long + enter short.
        sig = signals.add_signals(self._signal_frame(
            lb=np.array([False, True, False, False]),
            sb=np.array([False, False, False, True]),
            lx_=np.array([False, False, False, True]),
            sx_=np.zeros(4, dtype=bool),
        ))
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_end_to_end_breakout_enters(self):
        # 20 flat bars (high 100) then a close at 105 -> long entry.
        base_h = np.full(20, 100.0)
        base_l = np.full(20, 90.0)
        base_c = np.full(20, 95.0)
        h = np.concatenate([base_h, [110.0]])
        l = np.concatenate([base_l, [95.0]])
        c = np.concatenate([base_c, [105.0]])
        sig = signals.add_signals(
            indicators.add_indicators(_frame(c, h, l, c)))
        self.assertTrue(sig["long_entry"].iloc[20])
        self.assertEqual(int(sig["long_entry"].sum()), 1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 20)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 336)
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
