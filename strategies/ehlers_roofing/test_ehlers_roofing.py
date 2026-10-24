"""Ehlers Roofing Filter tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_roofing import indicators, risk, signals
from strategies.ehlers_roofing.indicators import (
    CYCLE,
    SS_PERIOD,
    high_pass,
    roofing_coefs,
    roofing_filter,
    supersmoother_coefs,
)


def _frame_from_parts(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _flat_frame(n=200, close=100.0, vol=100.0):
    c = np.full(n, close)
    h = c * 1.001
    l = c * 0.999
    return _frame_from_parts(c, h, l, c, np.full(n, vol))


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
        for col in ("roofing_hp", "roofing", "atr"):
            self.assertIn(col, ind.columns)

    def test_high_pass_hand_computation(self):
        # x = [100, 101, 103, 106]; y[0] = y[1] = 0 (seeded).
        # y[2] = a*(103 - 2*101 + 100) = a*1.
        # y[3] = a*(106 - 2*103 + 101) + b*y[2] = a*1 + b*a.
        k = roofing_coefs(CYCLE)
        a, b = k["a"], k["b"]
        x = pd.Series([100.0, 101.0, 103.0, 106.0])
        hp = high_pass(x, CYCLE)
        self.assertAlmostEqual(float(hp.iloc[0]), 0.0, places=12)
        self.assertAlmostEqual(float(hp.iloc[1]), 0.0, places=12)
        self.assertAlmostEqual(float(hp.iloc[2]), a * 1.0, places=12)
        self.assertAlmostEqual(float(hp.iloc[3]), a * 1.0 + b * a, places=12)

    def test_flat_data_output_zero_and_finite(self):
        # A constant series has zero second difference, so the
        # high-pass stays 0 and the smoother stays 0: no blowup, no NaN.
        ind = indicators.add_indicators(_flat_frame(300))
        self.assertTrue(np.isfinite(ind["roofing"]).all())
        self.assertTrue(np.isfinite(ind["roofing_hp"]).all())
        self.assertTrue((ind["roofing"] == 0.0).all())

    def test_sine_wave_passes_with_limited_attenuation(self):
        # Pure 48-bar sine, amplitude 10, around 100. In steady state
        # (last two cycles) the roofing line must keep a substantial
        # fraction of the input amplitude: the filter is tuned to this
        # cycle, so it must not crush it (ratio in (0.2, 1.0)).
        n = 480
        sine = 100.0 + 10.0 * np.sin(2 * np.pi * np.arange(n) / 48.0)
        roof = roofing_filter(pd.Series(sine), CYCLE, SS_PERIOD).to_numpy()
        tail = roof[-96:]
        amp = (tail.max() - tail.min()) / 2.0
        self.assertGreater(amp / 10.0, 0.2)
        self.assertLess(amp / 10.0, 1.0)

    def test_sine_wave_tracks_cycle_phase(self):
        # Steady-state roofing output must track the tuned cycle: any
        # causal filter imposes a fixed phase shift, so the test
        # takes the best correlation over all 48 lags (0.999 in
        # practice) and checks the zero-crossing rhythm — 8 crossings
        # over the last 192 bars = one full cycle per 48 bars.
        n = 480
        sine = 100.0 + 10.0 * np.sin(2 * np.pi * np.arange(n) / 48.0)
        roof = roofing_filter(pd.Series(sine), CYCLE, SS_PERIOD).to_numpy()
        tail_s, tail_r = sine[-192:], roof[-192:]
        best = max(np.corrcoef(np.roll(tail_s, lag), tail_r)[0, 1]
                   for lag in range(48))
        self.assertGreater(best, 0.9)
        crossings = int((np.diff(np.sign(tail_r)) != 0).sum())
        self.assertEqual(crossings, 8)

    def test_supersmoother_unity_dc_gain(self):
        # c1 / (1 - c2 - c3) must be exactly 1: the smoother passes
        # the level unchanged, so it cannot rescale the roofing line.
        s = supersmoother_coefs(SS_PERIOD)
        self.assertAlmostEqual(s["c1"] / (1 - s["c2"] - s["c3"]), 1.0, places=12)

    def test_no_lookahead(self):
        # roofing at bar j must not change when later bars are appended.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["roofing"].iloc[:200].reset_index(drop=True),
            ind_short["roofing"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _direct_frame(self, roofing):
        n = len(roofing)
        df = _flat_frame(n)
        df["roofing"] = np.asarray(roofing, dtype=float)
        return df

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_cross_above_zero(self):
        # roofing: -1, -1, +1 -> cross above at bar 2, exactly once.
        sig = signals.add_signals(self._direct_frame([-1.0, -1.0, 1.0, 1.0]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertFalse(sig["short_entry"].any())

    def test_short_entry_on_cross_below_zero(self):
        sig = signals.add_signals(self._direct_frame([1.0, 1.0, -1.0, -1.0]))
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_exit_is_opposite_zero_cross(self):
        # Up-cross at 2 (long entry), down-cross at 4 (long exit).
        sig = signals.add_signals(
            self._direct_frame([-1.0, -1.0, 1.0, 1.0, -1.0]))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[4])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["short_entry"].iloc[4])

    def test_sine_wave_produces_both_sides(self):
        n = 480
        sine = 100.0 + 10.0 * np.sin(2 * np.pi * np.arange(n) / 48.0)
        sig = signals.add_signals(indicators.add_indicators(_frame_from_close(sine)))
        self.assertGreater(int(sig["long_entry"].sum()), 0)
        self.assertGreater(int(sig["short_entry"].sum()), 0)


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
        self.assertEqual(risk.WARMUP, 80)

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
