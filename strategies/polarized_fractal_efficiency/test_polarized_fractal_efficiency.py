"""Polarized Fractal Efficiency tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.polarized_fractal_efficiency import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(pfe):
    return pd.DataFrame({"pfe": np.array(pfe, dtype=float)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestPolarizedFractalEfficiency(unittest.TestCase):
    def test_registered(self):
        self.assertIn("polarized_fractal_efficiency", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_linear_uptrend(self):
        # +1 per bar: straight = sqrt(10^2 + 10^2), path = 10*sqrt(2),
        # so raw = +100 exactly on every bar from index 10 on, and the
        # EMA(5) of a constant 100 is 100 (first PFE at index 14).
        closes = 100 + np.arange(60, dtype=float)
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(df["pfe_raw"].iloc[: indicators.N].isna().all())
        self.assertTrue(np.allclose(df["pfe_raw"].iloc[indicators.N:], 100.0))
        self.assertTrue(np.allclose(df["pfe"].iloc[14:], 100.0))
        self.assertTrue(df["pfe"].iloc[:14].isna().all())

    def test_indicator_values_linear_downtrend(self):
        # Mirror image: raw = -100, PFE = -100.
        closes = 200 - np.arange(60, dtype=float)
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(np.allclose(df["pfe_raw"].iloc[indicators.N:], -100.0))
        self.assertTrue(np.allclose(df["pfe"].iloc[14:], -100.0))

    def test_indicator_values_hand_computed_mixed(self):
        # 10 flat bars then a +10 jump at bar 10:
        # straight = sqrt(10^2 + 10^2) = 14.1421356237,
        # path = 9*1 + sqrt(10^2 + 1) = 19.0498756211,
        # raw = 100 * 14.1421356237 / 19.0498756211 = 74.2374171097.
        closes = [100.0] * 10 + [110.0] + [110.0] * 20
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["pfe_straight"].iloc[10], 14.142135623730951, places=9)
        self.assertAlmostEqual(df["pfe_path"].iloc[10], 19.04987562112089, places=9)
        self.assertAlmostEqual(df["pfe_raw"].iloc[10], 74.23741710970201, places=9)
        # After the jump price is flat again, so raw returns to +100
        # (straight 10 / path 10); the EMA then decays toward 100.
        self.assertAlmostEqual(df["pfe_raw"].iloc[20], 100.0, places=9)
        self.assertTrue((df["pfe"].iloc[14:] > 74.0).all())
        self.assertTrue((df["pfe"].iloc[14:] <= 100.0 + 1e-9).all())

    def test_indicator_values_zigzag_chop(self):
        # Alternating +-5: 10-bar net move 0, straight = 10,
        # path = 10*sqrt(26), raw = 100*10/(10*sqrt(26)) = 19.6116...
        # (chop reads well below the +-100 trend extremes).
        closes = [100.0 if i % 2 == 0 else 105.0 for i in range(60)]
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(np.allclose(df["pfe_raw"].iloc[indicators.N:],
                                    19.611613513818405))
        self.assertTrue(np.allclose(df["pfe"].iloc[14:], 19.611613513818405))

    def test_indicator_values_flat(self):
        # Flat price is a spec quirk worth locking in: straight = 10 and
        # path = 10, so raw = +100 (not 0) -- see CALIBRATION.md.
        df = indicators.add_indicators(_flat_frame())
        self.assertTrue(np.allclose(df["pfe_raw"].iloc[indicators.N:], 100.0))
        self.assertTrue(np.allclose(df["pfe"].iloc[14:], 100.0))

    def test_indicator_bounded(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[14:]
        self.assertTrue(np.isfinite(tail["pfe"]).all())
        self.assertTrue(((tail["pfe"] >= -100.0 - 1e-9)
                         & (tail["pfe"] <= 100.0 + 1e-9)).all())
        self.assertTrue(((tail["pfe_raw"] >= -100.0 - 1e-9)
                         & (tail["pfe_raw"] <= 100.0 + 1e-9)).all())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_reversal_from_minimum(self):
        # PFE bottomed at -40, then crosses above 0 at index 22.
        pfe = [-40.0] * 20 + [-20.0, -10.0, 5.0, 20.0, 60.0, 55.0, 40.0, 30.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertTrue(df["long_entry"].iloc[22])
        self.assertFalse(df["long_entry"].iloc[23])
        self.assertFalse(df["short_entry"].iloc[22])

    def test_no_long_entry_without_deep_minimum(self):
        # Cross above 0, but the 20-bar minimum only reached -20.
        pfe = [-20.0] * 20 + [-10.0, -5.0, 5.0, 10.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertFalse(df["long_entry"].any())

    def test_short_entry_on_reversal_from_maximum(self):
        # PFE peaked at +40, then crosses below 0 at index 22.
        pfe = [40.0] * 20 + [20.0, 10.0, -5.0, -20.0, -60.0, -55.0, -40.0, -30.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertTrue(df["short_entry"].iloc[22])
        self.assertFalse(df["short_entry"].iloc[23])
        self.assertFalse(df["long_entry"].iloc[22])

    def test_no_short_entry_without_high_maximum(self):
        pfe = [20.0] * 20 + [10.0, 5.0, -5.0, -10.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertFalse(df["short_entry"].any())

    def test_long_exit_peak_reached(self):
        # Entry at 22, PFE exceeds +50 at 24, crosses back below +50
        # at 26 -> peak-reached exit fires exactly there, not before.
        pfe = [-40.0] * 20 + [-20.0, -10.0, 5.0, 20.0, 60.0, 55.0, 40.0, 30.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertTrue(df["long_exit"].iloc[26])
        self.assertFalse(df["long_exit"].iloc[22:26].any())

    def test_long_exit_zero_cross_without_peak(self):
        # Entry at 22, PFE never reaches +50, crosses below 0 at 26.
        pfe = [-40.0] * 20 + [-20.0, -10.0, 5.0, 20.0, 30.0, 20.0, -5.0, -10.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertTrue(df["long_exit"].iloc[26])
        self.assertFalse(df["long_exit"].iloc[22:26].any())

    def test_long_exit_no_exit_before_peak_cross(self):
        # Entry at 22, PFE exceeds +50 but has not crossed back below
        # it yet -> no exit while it stays above +50.
        pfe = [-40.0] * 20 + [-20.0, -10.0, 5.0, 20.0, 60.0, 55.0, 52.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertFalse(df["long_exit"].any())

    def test_short_exit_peak_reached(self):
        pfe = [40.0] * 20 + [20.0, 10.0, -5.0, -20.0, -60.0, -55.0, -40.0, -30.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertTrue(df["short_exit"].iloc[26])
        self.assertFalse(df["short_exit"].iloc[22:26].any())

    def test_short_exit_zero_cross_without_peak(self):
        pfe = [40.0] * 20 + [20.0, 10.0, -5.0, -20.0, -30.0, -20.0, 5.0, 10.0]
        df = signals.add_signals(_signal_frame(pfe))
        self.assertTrue(df["short_exit"].iloc[26])
        self.assertFalse(df["short_exit"].iloc[22:26].any())

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("pfe", "pfe_raw", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # Fewer bars than the PFE lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["pfe"].isna().all())


if __name__ == "__main__":
    unittest.main()
