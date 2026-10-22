"""Ehlers SuperSmoother tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_supersmoother import indicators, risk, signals
from strategies import base as B

# Hand-computed (independent of the implementation) period=20 coefficients:
#   a1 = exp(-1.414*pi/20), b1 = 2*a1*cos(1.414*180/20 deg),
#   c2 = b1, c3 = -a1^2, c1 = 1 - c2 - c3.
COEFS_20 = {
    "a1": 0.800826788,
    "b1": 1.562308443,
    "c1": 0.079015100,
    "c2": 1.562308443,
    "c3": -0.641323544,
}


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _trend_flip_frame(seed=3):
    """Piecewise linear up/down legs: close crosses the filter both ways."""
    rng = np.random.default_rng(seed)
    legs = [(0.35, 120), (-0.35, 120), (0.35, 120), (-0.35, 120)]
    c = [100.0]
    for slope, n in legs:
        for _ in range(n):
            c.append(c[-1] + slope + rng.normal(0, 0.05))
    c = np.array(c[1:])
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    v = np.full(len(c), 100.0)
    t = (1_700_000_000_000 + np.arange(len(c)) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _swing_frame(n=700, seed=21, cycles=3):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, cycles * 2 * np.pi, n)
    c = 100 + 25 * np.sin(x) + rng.normal(0, 0.4, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestCoefs(unittest.TestCase):
    def test_coefficients_match_hand_values(self):
        k = indicators.supersmoother_coefs(20)
        for name, expect in COEFS_20.items():
            self.assertAlmostEqual(k[name], expect, places=6, msg=name)

    def test_unity_dc_gain(self):
        # c1 / (1 - c2 - c3) == 1: the filter must track the price level.
        k = indicators.supersmoother_coefs(20)
        gain = k["c1"] / (1 - k["c2"] - k["c3"])
        self.assertAlmostEqual(gain, 1.0, places=12)


class TestFilter(unittest.TestCase):
    def setUp(self):
        self.df = _frame()
        self.ind = indicators.add_indicators(self.df)

    def test_columns_present(self):
        for col in ("ss_filt", "ss_rising", "ss_falling", "atr"):
            self.assertIn(col, self.ind.columns)

    def test_step_response_less_lag_than_sma20(self):
        # Unit step at bar 100: filter must reach 50% of the step
        # strictly sooner than SMA(20) (Ehlers' half-lag claim).
        n, k = 400, 100
        c = pd.Series([0.0] * k + [1.0] * (n - k))
        f = indicators.supersmoother(c, 20)
        s = B.sma(c, 20)
        lag_f = int(np.argmax(f.to_numpy() >= 0.5)) - k
        lag_s = int(np.argmax(s.to_numpy() >= 0.5)) - k
        self.assertGreater(lag_f, 0)
        self.assertLess(lag_f, lag_s,
                        f"filter lag {lag_f} not better than sma lag {lag_s}")

    def test_step_response_90pct_less_lag_than_sma20(self):
        n, k = 400, 100
        c = pd.Series([0.0] * k + [1.0] * (n - k))
        f = indicators.supersmoother(c, 20)
        s = B.sma(c, 20)
        lag_f = int(np.argmax(f.to_numpy() >= 0.9)) - k
        lag_s = int(np.argmax(s.to_numpy() >= 0.9)) - k
        self.assertLess(lag_f, lag_s)

    def test_flat_series_no_nan_blowup(self):
        df = _frame()
        df["c"] = 100.0
        df["o"], df["h"], df["l"] = 100.0, 100.0, 100.0
        ind = indicators.add_indicators(df)
        f = ind["ss_filt"]
        self.assertFalse(f.isna().any())
        self.assertTrue(np.isfinite(f).all())
        self.assertTrue(np.allclose(f, 100.0, atol=1e-9))

    def test_converges_to_level_after_step(self):
        # Unity DC gain: after a step the filter must settle at the
        # new level, not drift or oscillate away.
        n, k = 300, 100
        c = pd.Series([50.0] * k + [100.0] * (n - k))
        f = indicators.supersmoother(c, 20)
        self.assertAlmostEqual(float(f.iloc[-1]), 100.0, places=6)

    def test_smooths_noise(self):
        rng = np.random.default_rng(11)
        c = pd.Series(100 + rng.normal(0, 2.0, 500))
        f = indicators.supersmoother(c, 20)
        self.assertLess(float(f.std()), float(c.std()) * 0.5)

    def test_slope_sign_tracks_trend(self):
        n = 200
        c = pd.Series(np.linspace(100.0, 120.0, n))  # steady climb
        ind = indicators.add_indicators(
            pd.DataFrame({"t": np.arange(n), "o": c, "h": c, "l": c, "c": c,
                          "v": np.ones(n)}))
        self.assertTrue(ind["ss_rising"].iloc[60:].all())
        self.assertFalse(ind["ss_falling"].iloc[60:].any())

    def test_does_not_mutate_input(self):
        before = self.df.copy()
        indicators.add_indicators(self.df)
        pd.testing.assert_frame_equal(self.df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_entries_fire_on_trend_flips(self):
        # Sine swings: the filter's slope turns before price crosses it
        # at swing extremes, so the slope gate passes on both sides.
        sig = signals.add_signals(
            indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_entry"].sum(), 0)
        self.assertGreater(sig["short_entry"].sum(), 0)

    def test_long_entries_only_when_filter_rising(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        longs = sig["long_entry"]
        self.assertGreater(longs.sum(), 0)
        self.assertTrue(ind.loc[longs, "ss_rising"].all())
        shorts = sig["short_entry"]
        self.assertGreater(shorts.sum(), 0)
        self.assertTrue(ind.loc[shorts, "ss_falling"].all())

    def test_slope_gate_blocks_countertrend_cross(self):
        # Downtrend + one sharp pop: close crosses above the filter
        # while the filter is still falling -> no long entry.
        n = 300
        c = 100.0 - 0.1 * np.arange(n)
        found = None
        for bump in (0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0):
            cc = c.copy()
            cc[150] += bump
            df = pd.DataFrame({"t": np.arange(n), "o": cc, "h": cc * 1.001,
                               "l": cc * 0.999, "c": cc,
                               "v": np.ones(n)})
            ind = indicators.add_indicators(df)
            up = B.crossed_above(ind["c"], ind["ss_filt"]).fillna(False)
            bar = up[up].index
            if len(bar) and not ind.loc[bar[0], "ss_rising"]:
                found = (ind, bar[0])
                break
        self.assertIsNotNone(found, "no counter-trend cross produced")
        ind, j = found
        sig = signals.add_signals(ind)
        self.assertTrue(bool(B.crossed_above(ind["c"], ind["ss_filt"])
                             .fillna(False).iloc[j]))
        self.assertFalse(ind.loc[j, "ss_rising"])
        self.assertFalse(bool(sig.loc[j, "long_entry"]))

    def test_exits_fire(self):
        sig = signals.add_signals(indicators.add_indicators(_swing_frame()))
        self.assertGreater(sig["long_exit"].sum(), 0)
        self.assertGreater(sig["short_exit"].sum(), 0)

    def test_exits_are_opposite_crosses(self):
        ind = indicators.add_indicators(_swing_frame())
        sig = signals.add_signals(ind)
        c, f = ind["c"], ind["ss_filt"]
        pd.testing.assert_series_equal(
            sig["long_exit"],
            B.crossed_below(c, f).fillna(False).astype(bool),
            check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"],
            B.crossed_above(c, f).fillna(False).astype(bool),
            check_names=False)

    def test_no_lookahead(self):
        df = _trend_flip_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        j = 300
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 150)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration(self):
        import strategies.ehlers_supersmoother as mod
        from strategies.registry import REGISTRY

        self.assertIn("ehlers_supersmoother", REGISTRY)
        self.assertIs(REGISTRY["ehlers_supersmoother"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "ehlers_supersmoother")
        self.assertEqual(mod.SPEC.name, "SuperSmoother Trend")
        self.assertEqual(mod.SPEC.source_name, "SuperSmoother (John Ehlers)")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__),
                         {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
