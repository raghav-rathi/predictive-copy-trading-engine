"""True Strength Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd
import pandas.testing as tm

from strategies.true_strength_index import indicators, risk, signals
from strategies import base as B


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


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _signal_frame(tsi_vals, sig_vals):
    n = len(tsi_vals)
    df = _frame_from_close(np.full(n, 100.0))
    df["tsi"] = np.asarray(tsi_vals, dtype=float)
    df["tsi_signal"] = np.asarray(sig_vals, dtype=float)
    return df


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("tsi", "tsi_signal"):
            self.assertIn(col, ind.columns)

    def test_tsi_hand_computation(self):
        # r=s=1 => every EMA is the identity (alpha=1), so double-EMA
        # of momentum is momentum itself:
        # c=[100,102,102,99,101] -> m=[nan,2,0,-3,2]
        # TSI = [nan, 100, 0 (den==0 guard), -100, 100].
        c = pd.Series([100.0, 102.0, 102.0, 99.0, 101.0])
        got = indicators.true_strength_index(c, r=1, s=1)
        self.assertTrue(np.isnan(got.iloc[0]))
        self.assertAlmostEqual(got.iloc[1], 100.0, places=9)
        self.assertAlmostEqual(got.iloc[2], 0.0, places=9)   # zero-division guard
        self.assertAlmostEqual(got.iloc[3], -100.0, places=9)
        self.assertAlmostEqual(got.iloc[4], 100.0, places=9)

    def test_tsi_matches_independent_reference(self):
        df = _frame()
        m = df["c"].diff()
        num = m.ewm(span=25, adjust=False, min_periods=25).mean()
        num = num.ewm(span=13, adjust=False, min_periods=13).mean()
        den = m.abs().ewm(span=25, adjust=False, min_periods=25).mean()
        den = den.ewm(span=13, adjust=False, min_periods=13).mean()
        ref = 100.0 * num / den
        ref = ref.where((den != 0) | den.isna(), 0.0)
        tm.assert_series_equal(indicators.true_strength_index(df["c"]),
                               ref, check_names=False)

    def test_signal_line_is_ema7_of_tsi(self):
        df = indicators.add_indicators(_frame())
        ref = df["tsi"].ewm(span=7, adjust=False, min_periods=7).mean()
        tm.assert_series_equal(df["tsi_signal"], ref, check_names=False)

    def test_flat_market_maps_to_zero(self):
        # All momentum is zero: den == 0 everywhere -> TSI == 0, not NaN/inf.
        df = _frame_from_close(np.full(300, 100.0))
        tsi = indicators.true_strength_index(df["c"])
        valid = tsi.dropna()
        self.assertGreater(len(valid), 0)
        self.assertTrue((valid == 0.0).all())
        self.assertFalse(np.isinf(tsi.fillna(0)).any())

    def test_tsi_bounded(self):
        df = indicators.add_indicators(_frame())
        valid = df["tsi"].dropna()
        self.assertGreater(len(valid), 0)
        self.assertTrue(((valid >= -100.0) & (valid <= 100.0)).all())

    def test_monotonic_trends_converge_to_bounds(self):
        up = _frame_from_close(100.0 + np.arange(500))
        tsi_up = indicators.add_indicators(up)["tsi"].iloc[-1]
        self.assertGreater(tsi_up, 99.0)
        dn = _frame_from_close(600.0 - np.arange(500))
        tsi_dn = indicators.add_indicators(dn)["tsi"].iloc[-1]
        self.assertLess(tsi_dn, -99.0)

    def test_nan_warmup(self):
        df = indicators.add_indicators(_frame())
        self.assertTrue(df["tsi"].iloc[0] != df["tsi"].iloc[0])  # NaN
        self.assertTrue(df["tsi_signal"].iloc[0] != df["tsi_signal"].iloc[0])

    def test_no_lookahead_truncation_invariance(self):
        # adjust=False EMAs are forward-recursive: values at bars <= k
        # must be identical whether computed on 300 bars or on the first
        # 200 bars only.
        full = _frame(n=300)
        trunc = full.iloc[:200].copy()
        tsi_full = indicators.add_indicators(full)["tsi"].iloc[:150]
        tsi_trunc = indicators.add_indicators(trunc)["tsi"].iloc[:150]
        tm.assert_series_equal(tsi_full, tsi_trunc)

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        tm.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_long_entry_on_cross_in_bull_territory(self):
        df = _signal_frame([1, 2, 4, 6, 8], [3, 3, 3, 3, 3])
        out = signals.add_signals(df)
        self.assertEqual(out["long_entry"].tolist(), [False, False, True, False, False])
        self.assertFalse(out["short_entry"].any())
        self.assertFalse(out["long_exit"].any())
        self.assertEqual(out["short_exit"].tolist(), [False, False, True, False, False])

    def test_long_entry_vetoed_in_bear_territory(self):
        # Cross up happens at bar 2 (-4 > -5) but TSI is negative there.
        df = _signal_frame([-8, -6, -4, -2, 0], [-5, -5, -5, -5, -5])
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].any())
        self.assertEqual(out["short_exit"].tolist(), [False, False, True, False, False])

    def test_short_entry_on_cross_in_bear_territory(self):
        # Cross down at bar 2 (-1 < 0, prev 1 >= 0), TSI negative.
        df = _signal_frame([2, 1, -1, -2, -3], [0, 0, 0, 0, 0])
        out = signals.add_signals(df)
        self.assertEqual(out["short_entry"].tolist(), [False, False, True, False, False])
        self.assertFalse(out["long_entry"].any())
        self.assertEqual(out["long_exit"].tolist(), [False, False, True, False, False])

    def test_short_entry_vetoed_in_bull_territory(self):
        # Cross down at bar 2 (4 < 5) but TSI is positive there.
        df = _signal_frame([8, 6, 4, 2, 0], [5, 5, 5, 5, 5])
        out = signals.add_signals(df)
        self.assertFalse(out["short_entry"].any())
        self.assertEqual(out["long_exit"].tolist(), [False, False, True, False, False])

    def test_exit_fires_on_raw_opposite_cross(self):
        # Cross down at bar 2 while TSI stays positive: no short entry,
        # but a long position must still be exited.
        df = _signal_frame([8, 6, 4, 2, 0], [5, 5, 5, 5, 5])
        out = signals.add_signals(df)
        self.assertTrue(out["long_exit"].iloc[2])
        df = _signal_frame([-8, -6, -4, -2, 0], [-5, -5, -5, -5, -5])
        out = signals.add_signals(df)
        self.assertTrue(out["short_exit"].iloc[2])

    def test_boolean_dtype_and_no_nan(self):
        out = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(out[col].dtype), "bool")
            self.assertFalse(out[col].isna().any())

    def test_no_entries_during_warmup(self):
        out = signals.add_signals(indicators.add_indicators(_frame()))
        self.assertFalse(out["long_entry"].iloc[:60].any())
        self.assertFalse(out["short_entry"].iloc[:60].any())

    def test_integration_pipeline(self):
        out = signals.add_signals(indicators.add_indicators(_frame(n=300)))
        self.assertEqual(len(out), 300)
        # entries must be a subset of cross bars
        crosses = B.crossed_above(out["tsi"], out["tsi_signal"]).fillna(False)
        self.assertTrue(((out["long_entry"]) & ~crosses).sum() == 0)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.5)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 120)
        self.assertAlmostEqual(r.risk_frac, 0.01)
        self.assertAlmostEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
