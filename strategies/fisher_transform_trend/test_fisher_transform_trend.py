"""Ehlers Fisher Transform trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fisher_transform_trend import indicators, risk, signals


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


def _top_of_range_frame(n=12):
    """Every bar h=110, l=90, c=110 (close pinned to the top of its
    10-bar range): raw = 1, x = 0.999, fisher_raw = 0.5*ln(1999)."""
    return _frame([110.0] * n, [110.0] * n, [90.0] * n, [110.0] * n,
                  [100.0] * n)


def _fisher_frame(values):
    """Signals-only frame: signals.py reads just the fisher column."""
    n = len(values)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "fisher": np.asarray(values, dtype=float)})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("x_norm", "fisher_raw", "fisher", "atr"):
            self.assertIn(col, ind.columns)

    def test_no_nan_anywhere(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("x_norm", "fisher_raw", "fisher"):
            self.assertFalse(ind[col].isna().any(), col)
            self.assertTrue(np.isfinite(ind[col]).all(), col)

    def test_hand_computed_top_of_range(self):
        # fisher_raw = 0.5*ln((1+0.999)/(1-0.999)) = 0.5*ln(1999)
        #   = 3.8002012. Smoothing seeded at 0: fisher[9] is the
        # first bar with a complete 10-bar window.
        ind = indicators.add_indicators(_top_of_range_frame())
        self.assertAlmostEqual(ind["fisher_raw"].iloc[9], 3.8002012, places=5)
        self.assertAlmostEqual(ind["fisher"].iloc[9], 1.9001006, places=5)
        self.assertAlmostEqual(ind["fisher"].iloc[10], 2.8501509, places=5)
        self.assertAlmostEqual(ind["fisher"].iloc[11], 3.3251760, places=5)
        self.assertAlmostEqual(ind["x_norm"].iloc[9], 0.999, places=6)

    def test_flat_price_gives_zero_fisher(self):
        # Zero 10-bar range -> raw = 0.5 -> x = 0 -> fisher = 0.
        df = _frame([100.0] * 50, [100.0] * 50, [100.0] * 50,
                    [100.0] * 50, [100.0] * 50)
        ind = indicators.add_indicators(df)
        self.assertTrue((ind["fisher"] == 0.0).all())
        self.assertTrue((ind["x_norm"] == 0.0).all())

    def test_mid_range_close_gives_zero_x(self):
        # Close exactly mid-range every bar: raw = 0.5 -> x = 0.
        df = _frame([100.0] * 50, [110.0] * 50, [90.0] * 50,
                    [100.0] * 50, [100.0] * 50)
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["x_norm"].iloc[9:], 0.0))
        self.assertTrue(np.allclose(ind["fisher"].iloc[9:], 0.0))

    def test_x_norm_bounded(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertTrue((ind["x_norm"].abs() <= 0.999 + 1e-12).all())

    def test_smoothing_is_half_weight(self):
        # fisher[i] = 0.5*fisher_raw[i] + 0.5*fisher[i-1], checked
        # on real (non-degenerate) data.
        ind = indicators.add_indicators(_random_walk_frame())
        fr = ind["fisher_raw"].to_numpy()
        f = ind["fisher"].to_numpy()
        for i in (50, 200, 1000):
            self.assertAlmostEqual(f[i], 0.5 * fr[i] + 0.5 * f[i - 1],
                                   places=10)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:800]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("x_norm", "fisher_raw", "fisher"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:800].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_cross_above_zero_enters_long(self):
        sig = signals.add_signals(_fisher_frame([-0.5, -0.2, 0.1, 0.3, 0.4]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_cross_below_zero_enters_short(self):
        sig = signals.add_signals(_fisher_frame([0.5, 0.2, -0.1, -0.3]))
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_no_reentry_while_holding(self):
        # Fisher stays positive and rising: exactly one long entry.
        sig = signals.add_signals(
            _fisher_frame([-0.5, 0.3, 0.4, 0.5, 0.6, 0.7]))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_two_down_bars_exit_long_without_flip(self):
        sig = signals.add_signals(
            _fisher_frame([-0.5, -0.2, 0.1, 0.3, 0.2, 0.1, 0.0]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertFalse(sig["long_exit"].iloc[4])
        self.assertTrue(sig["long_exit"].iloc[5])
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_cross_back_below_zero_flips_to_short(self):
        sig = signals.add_signals(_fisher_frame([-0.5, 0.2, 0.1, -0.1, -0.3]))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_two_up_bars_exit_short(self):
        sig = signals.add_signals(
            _fisher_frame([0.5, -0.2, -0.3, -0.2, -0.1, 0.0]))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertFalse(sig["short_exit"].iloc[3])
        self.assertTrue(sig["short_exit"].iloc[4])

    def test_cross_back_above_zero_flips_to_long(self):
        sig = signals.add_signals(_fisher_frame([0.5, -0.2, -0.1, 0.1, 0.3]))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertTrue(sig["short_exit"].iloc[3])
        self.assertTrue(sig["long_entry"].iloc[3])

    def test_no_signal_when_fisher_never_crosses(self):
        sig = signals.add_signals(_fisher_frame([0.1, 0.2, 0.3, 0.2, 0.1]))
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)


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
