"""Stochastic + Bollinger %b tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stochastic_bollinger import indicators, risk, signals


def _frame(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _flat_frame(n=60, price=100.0, vol=100.0):
    c = np.full(n, price)
    return _frame(c, c * 1.01, c * 0.99, c, np.full(n, vol))


def _random_walk_frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("bb_mid", "bb_upper", "bb_lower", "bb_width", "pct_b",
                    "stoch_k", "stoch_d", "atr"):
            self.assertIn(col, ind.columns)

    def test_pct_b_golden_value_on_rising_series(self):
        # c = 100..119 over 20 bars. At bar 19: mid = 109.5,
        # sample SD = 5.9161, upper = 121.332, lower = 97.668,
        # %b = (119 - 97.668) / (121.332 - 97.668) = 0.9016.
        c = np.arange(100.0, 120.0)
        ind = indicators.add_indicators(_frame(c, c + 1, c - 1, c, np.full(20, 100.0)))
        self.assertAlmostEqual(ind["pct_b"].iloc[19], 0.9016, places=3)
        self.assertAlmostEqual(ind["bb_mid"].iloc[19], 109.5, places=6)

    def test_pct_b_neutral_seed_on_flat_series(self):
        # Flat market: band width is zero, %b is seeded to 0.5.
        ind = indicators.add_indicators(_flat_frame())
        self.assertTrue((ind["pct_b"] == 0.5).all())
        # Band width is zero once the 20-bar window fills (first
        # 19 bars are NaN: no full window yet, not a zero width).
        self.assertTrue((ind["bb_width"].iloc[19:] == 0.0).all())

    def test_stochastic_golden_values(self):
        # Bars 0..13: h=110, l=90, c=100 -> raw %K = 50, so
        # %K = 50 and %D = 50 at bar 13. Bar 14: c=105 ->
        # raw %K = 75, %K = (50+50+75)/3 = 58.3333,
        # %D = (50+50+58.3333)/3 = 52.7778.
        n = 15
        c = np.full(n, 100.0)
        c[14] = 105.0
        ind = indicators.add_indicators(
            _frame(c, np.full(n, 110.0), np.full(n, 90.0), c, np.full(n, 100.0)))
        self.assertAlmostEqual(ind["stoch_k"].iloc[13], 50.0, places=6)
        self.assertAlmostEqual(ind["stoch_d"].iloc[13], 50.0, places=6)
        self.assertAlmostEqual(ind["stoch_k"].iloc[14], 58.333333, places=4)
        self.assertAlmostEqual(ind["stoch_d"].iloc[14], 52.777778, places=4)

    def test_stochastic_neutral_seed_on_zero_range(self):
        # h == l == c everywhere: 14-bar range is zero, %K/%D
        # seed to 50.0 instead of NaN/inf.
        n = 60
        c = np.full(n, 100.0)
        ind = indicators.add_indicators(_frame(c, c, c, c, np.full(n, 100.0)))
        self.assertTrue((ind["stoch_k"] == 50.0).all())
        self.assertTrue((ind["stoch_d"] == 50.0).all())

    def test_no_nan_in_indicator_columns(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("pct_b", "stoch_k", "stoch_d"):
            self.assertFalse(ind[col].isna().any(), col)
            self.assertTrue(np.isfinite(ind[col]).all(), col)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("pct_b", "stoch_k", "stoch_d", "bb_upper"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:300].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, pct_b, k, d):
        n = len(k)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": np.full(n, 100.0), "h": np.full(n, 101.0),
            "l": np.full(n, 99.0), "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
            "pct_b": np.asarray(pct_b, dtype=float),
            "stoch_k": np.asarray(k, dtype=float),
            "stoch_d": np.asarray(d, dtype=float),
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_cross_with_double_oversold_gate(self):
        # %K crosses above %D at bar 3 (24 -> 28 vs D 24),
        # %b = 0.1 < 0.2 and %K = 28 < 30.
        sig = signals.add_signals(self._signal_frame(
            pct_b=[0.1] * 6,
            k=[20.0, 22.0, 24.0, 28.0, 29.0, 29.0],
            d=[25.0, 25.0, 25.0, 24.0, 24.0, 24.0],
        ))
        self.assertTrue(sig["long_entry"].iloc[3])
        # No re-entry while held: bar 4 still oversold, no new cross.
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_long_entry_blocked_when_pct_b_not_oversold(self):
        sig = signals.add_signals(self._signal_frame(
            pct_b=[0.5] * 6,
            k=[20.0, 22.0, 24.0, 28.0, 29.0, 29.0],
            d=[25.0, 25.0, 25.0, 24.0, 24.0, 24.0],
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_long_entry_blocked_when_k_not_oversold(self):
        # Same cross, but %K = 35 at the cross bar (>= 30).
        sig = signals.add_signals(self._signal_frame(
            pct_b=[0.1] * 6,
            k=[20.0, 22.0, 24.0, 35.0, 36.0, 36.0],
            d=[25.0, 25.0, 25.0, 24.0, 24.0, 24.0],
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_long_exit_on_pct_b_above_0_8(self):
        sig = signals.add_signals(self._signal_frame(
            pct_b=[0.1, 0.1, 0.1, 0.1, 0.1, 0.9],
            k=[20.0, 22.0, 24.0, 28.0, 29.0, 29.0],
            d=[25.0, 25.0, 25.0, 24.0, 24.0, 24.0],
        ))
        self.assertTrue(sig["long_entry"].iloc[3])
        self.assertTrue(sig["long_exit"].iloc[5])

    def test_long_exit_on_k_cross_below_d(self):
        # Long at bar 3; %K crosses back below %D at bar 4
        # (28 -> 20 vs D 24) while %b stays low.
        sig = signals.add_signals(self._signal_frame(
            pct_b=[0.1] * 5,
            k=[20.0, 22.0, 24.0, 28.0, 20.0],
            d=[25.0, 25.0, 25.0, 24.0, 24.0],
        ))
        self.assertTrue(sig["long_entry"].iloc[3])
        self.assertTrue(sig["long_exit"].iloc[4])

    def test_short_mirror_entry_and_exit(self):
        # %K crosses below %D at bar 3 (76 -> 72 vs D 76),
        # %b = 0.9 > 0.8 and %K = 72 > 70. Exit at bar 4
        # when %b falls to 0.1.
        sig = signals.add_signals(self._signal_frame(
            pct_b=[0.9, 0.9, 0.9, 0.9, 0.1],
            k=[80.0, 78.0, 76.0, 72.0, 72.0],
            d=[75.0, 75.0, 75.0, 76.0, 76.0],
        ))
        self.assertTrue(sig["short_entry"].iloc[3])
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertTrue(sig["short_exit"].iloc[4])

    def test_opposite_setup_flips_position(self):
        # Long at bar 3; at bar 5 a full short setup fires
        # (%K crosses below %D, %b 0.9, %K 72) -> exit + flip.
        sig = signals.add_signals(self._signal_frame(
            pct_b=[0.1, 0.1, 0.1, 0.1, 0.1, 0.9],
            k=[20.0, 22.0, 24.0, 28.0, 80.0, 72.0],
            d=[25.0, 25.0, 25.0, 24.0, 24.0, 76.0],
        ))
        self.assertTrue(sig["long_entry"].iloc[3])
        self.assertTrue(sig["long_exit"].iloc[5])
        self.assertTrue(sig["short_entry"].iloc[5])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 120)
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
