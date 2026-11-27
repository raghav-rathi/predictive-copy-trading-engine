"""Alligator + Awesome Oscillator tests. Network-free, synthetic data only.

The crafted trend series use explicit OHLC arrays (not the
o=prev-c helper) because fractal highs/lows must be set
independently of the closes.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.alligator_awesome_combo import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC


def _df_from_ohlc(o, h, l, c):
    n = len(c)
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {
            "t": t,
            "o": np.asarray(o, float),
            "h": np.asarray(h, float),
            "l": np.asarray(l, float),
            "c": np.asarray(c, float),
            "v": np.full(n, 100.0),
        }
    )


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df_from_ohlc(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _long_series():
    # 80 bars. Bars 0-39: steady rise c = 100 + 0.5*i.
    # Bar 39 is a local peak (h=120.5, strict max of
    # h[37..41]) confirmed as an up-fractal at bar 41;
    # pullback to 117.5, then the close crosses above the
    # fractal high 120.5 at bar 44. Long fires at bar 44.
    # The breakout bar is strong (c=126, l held at the open)
    # so the AO turns green on the entry bar: the median's
    # SMA(5) slope must beat its SMA(34) slope, which a
    # weak breakout bar fails after a pullback.
    n = 80
    c = np.empty(n)
    o = np.empty(n)
    h = np.empty(n)
    l = np.empty(n)
    for i in range(40):
        c[i] = 100 + 0.5 * i
        o[i] = c[i - 1] if i else c[i]
        h[i] = c[i] + 0.5
        l[i] = c[i] - 0.5
    h[39] = 120.5
    for i, cc in {40: 118.0, 41: 117.5, 42: 118.0, 43: 119.0, 44: 126.0}.items():
        c[i] = cc
        o[i] = c[i - 1]
        h[i] = max(o[i], c[i]) + 0.5
        l[i] = min(o[i], c[i]) - 0.5
    l[44] = 119.0  # breakout bar holds its low at the open
    for i in range(45, n):
        c[i] = 122.5
        o[i] = c[i - 1]
        h[i] = c[i] + 0.5
        l[i] = c[i] - 0.5
    return _df_from_ohlc(o, h, l, c)


def _short_series():
    # Mirror of _long_series: steady fall c = 120 - 0.5*i,
    # bar 39 a local trough (l=99.5, strict min of l[37..41])
    # confirmed as a down-fractal at bar 41, bounce, then
    # the close crosses below 99.5 at bar 44. Short fires
    # at bar 44. The breakdown bar is strong (c=93) so the
    # AO turns red on the entry bar (mirror of the long
    # series' AO-turn reasoning).
    n = 80
    c = np.empty(n)
    o = np.empty(n)
    h = np.empty(n)
    l = np.empty(n)
    for i in range(40):
        c[i] = 120 - 0.5 * i
        o[i] = c[i - 1] if i else c[i]
        h[i] = c[i] + 0.5
        l[i] = c[i] - 0.5
    l[39] = 99.5
    for i, cc in {40: 102.0, 41: 102.5, 42: 102.0, 43: 101.0, 44: 93.0}.items():
        c[i] = cc
        o[i] = c[i - 1]
        h[i] = max(o[i], c[i]) + 0.5
        l[i] = min(o[i], c[i]) - 0.5
    for i in range(45, n):
        c[i] = 97.5
        o[i] = c[i - 1]
        h[i] = c[i] + 0.5
        l[i] = c[i] - 0.5
    return _df_from_ohlc(o, h, l, c)


class TestAlligatorAwesomeCombo(unittest.TestCase):
    def test_smma_hand_computed(self):
        # prices [10,11,12,13,14,15], n=3: seed SMA(3)=11 at
        # idx 2, then (11*2+13)/3=11.6667, (11.6667*2+14)/3=
        # 12.4444, (12.4444*2+15)/3=13.2963.
        s = pd.Series([10.0, 11, 12, 13, 14, 15])
        out = indicators.smma(s, 3)
        self.assertTrue(np.isnan(out.iloc[0]) and np.isnan(out.iloc[1]))
        self.assertAlmostEqual(float(out.iloc[2]), 11.0, places=6)
        self.assertAlmostEqual(float(out.iloc[3]), 35 / 3, places=6)
        self.assertAlmostEqual(float(out.iloc[4]), 112 / 9, places=6)
        self.assertAlmostEqual(float(out.iloc[5]), 359 / 27, places=6)

    def test_ao_hand_computed(self):
        # _df_from_c sets o[i]=c[i-1], so with spread 0 the
        # median is (c[i]+c[i-1])/2: [10, 10.5, 11.5, 12.5,
        # 13.5, 14.5]. AO = SMA(2)-SMA(3): at idx 2,
        # 11 - 32/3 = 1/3; idx 3, 12 - 11.5 = 0.5; idx 4,
        # 13 - 12.5 = 0.5.
        c = np.array([10.0, 11, 12, 13, 14, 15])
        df = _df_from_c(c, spread=0.0)
        ind = indicators.add_indicators(
            df, jaw_n=3, teeth_n=3, lips_n=3, ao_fast=2, ao_slow=3
        )
        self.assertAlmostEqual(float(ind["ao"].iloc[2]), 1 / 3, places=6)
        self.assertAlmostEqual(float(ind["ao"].iloc[3]), 0.5, places=6)
        self.assertAlmostEqual(float(ind["ao"].iloc[4]), 0.5, places=6)
        self.assertTrue(bool(ind["ao_green"].iloc[3]))   # AO rose 1/3 -> 0.5
        self.assertFalse(bool(ind["ao_green"].iloc[4]))  # AO flat 0.5 -> 0.5

    def test_fractal_confirmed_with_two_bar_lag(self):
        ind = indicators.add_indicators(_long_series())
        # Bar 39 peak h=120.5 is the strict max of h[37..41];
        # confirmed at bar 41, not before.
        self.assertFalse(bool(ind["frac_up"].iloc[40]))
        self.assertTrue(bool(ind["frac_up"].iloc[41]))
        self.assertAlmostEqual(float(ind["frac_up_level"].iloc[41]), 120.5, places=6)
        self.assertAlmostEqual(float(ind["frac_up_level_ff"].iloc[44]), 120.5, places=6)
        # Down-fractal mirror on the short series.
        ind_s = indicators.add_indicators(_short_series())
        self.assertTrue(bool(ind_s["frac_down"].iloc[41]))
        self.assertAlmostEqual(float(ind_s["frac_down_level"].iloc[41]), 99.5, places=6)

    def test_no_fractal_on_equal_highs(self):
        # Flat-top highs: h=105 on bars 5,6,7 -- no strict max,
        # so no fractal is confirmed at bar 7/8/9.
        c = np.full(20, 100.0)
        df = _df_from_c(c)
        df.loc[5:7, "h"] = 105.0
        ind = indicators.add_indicators(df)
        self.assertFalse(bool(ind["frac_up"].any()))

    def test_long_fires_on_fractal_breakout(self):
        sig = signals.add_signals(indicators.add_indicators(_long_series()))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [44])
        self.assertFalse(bool(sig["short_entry"].any()))
        row = sig.iloc[44]
        self.assertTrue(float(row["lips"]) > float(row["teeth"]) > float(row["jaw"]))
        self.assertTrue(float(row["ao"]) > 0 and bool(row["ao_green"]))

    def test_short_fires_on_fractal_breakdown(self):
        sig = signals.add_signals(indicators.add_indicators(_short_series()))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [44])
        self.assertFalse(bool(sig["long_entry"].any()))
        row = sig.iloc[44]
        self.assertTrue(float(row["lips"]) < float(row["teeth"]) < float(row["jaw"]))
        self.assertTrue(float(row["ao"]) < 0 and bool(row["ao_red"]))

    def test_no_entry_when_mouth_closed(self):
        # Minimal frame: the close crosses above a stable
        # fractal high with AO > 0 and rising, but the
        # Alligator lines are stacked equal (mouth closed) --
        # no entry. Positive control with lips > teeth > jaw
        # fires at the same bar.
        n = 6
        base = {
            "t": (T0 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0),
            "h": np.full(n, 101.0),
            "l": np.full(n, 99.0),
            "c": [99.0, 99, 99, 101, 101, 101],
            "v": np.full(n, 100.0),
            "ao": [1.0, 2, 3, 4, 5, 6],
            "ao_green": [False, True, True, True, True, True],
            "ao_red": [False, False, False, False, False, False],
            "frac_up_level_ff": np.full(n, 100.0),
            "frac_down_level_ff": np.full(n, np.nan),
        }
        closed = pd.DataFrame(
            {**base, "lips": np.full(n, 95.0),
             "teeth": np.full(n, 95.0), "jaw": np.full(n, 95.0)}
        )
        sig = signals.add_signals(closed)
        self.assertFalse(bool(sig["long_entry"].any()))
        open_mouth = pd.DataFrame(
            {**base, "lips": np.full(n, 97.0),
             "teeth": np.full(n, 96.0), "jaw": np.full(n, 95.0)}
        )
        sig2 = signals.add_signals(open_mouth)
        self.assertEqual(sig2.index[sig2["long_entry"]].tolist(), [3])

    def test_no_entry_without_cross(self):
        # Close sits above the fractal high for bars 44-46
        # without ever crossing it from below on a fresh bar:
        # gap the close above the level at bar 42 (before the
        # fractal confirms at 41... actually the level only
        # exists from bar 41; put the close above it from bar
        # 41 onward so no crossed_above ever fires).
        df = _long_series()
        df.loc[41:44, "c"] = 122.0
        df.loc[41:44, "h"] = 122.5
        df.loc[41:44, "l"] = 121.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exit_on_close_below_lips(self):
        # Long fires at 44, then a close below the lips at 46 exits.
        df = _long_series()
        df.loc[46, "c"] = 110.0
        df.loc[46, "h"] = 110.5
        df.loc[46, "l"] = 109.5
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [44])
        # The lips exit is a level condition, so it also flags
        # during the pre-entry pullback (the harness only acts
        # on it with a position open); the first exit at or
        # after the entry bar is 46.
        exits = [i for i in sig.index[sig["long_exit"]] if i >= 44]
        self.assertEqual(exits[0], 46)

    def test_ao_red_two_bars_exits(self):
        # Minimal frame: AO falling two bars in a row, close
        # exactly at the lips (so neither the lips exit nor
        # the short-side lips exit can fire -- only the AO rule).
        n = 6
        df = pd.DataFrame(
            {
                "t": (T0 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.full(n, 100.0),
                "h": np.full(n, 101.0),
                "l": np.full(n, 99.0),
                "c": np.full(n, 100.0),
                "v": np.full(n, 100.0),
                "lips": np.full(n, 100.0),
                "teeth": np.full(n, 99.0),
                "jaw": np.full(n, 98.0),
                "ao": [5.0, 5.0, 4.0, 3.0, 2.0, 1.0],
                "ao_green": [False, False, False, False, False, False],
                "ao_red": [False, False, True, True, True, True],
                "frac_up_level_ff": np.full(n, np.nan),
                "frac_down_level_ff": np.full(n, np.nan),
            }
        )
        sig = signals.add_signals(df)
        # AO red at bars 2,3,4,5 -> two-in-a-row first true at bar 3.
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [3, 4, 5])
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("jaw", "teeth", "lips", "ao", "median"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("frac_up", "frac_down", "ao_green", "ao_red",
                    "long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("jaw", "teeth", "lips", "ao", "ao_green",
                        "ao_red", "frac_up", "frac_down",
                        "frac_up_level_ff", "frac_down_level_ff"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_frac_n_param_changes_confirmation_lag(self):
        ind1 = indicators.add_indicators(_long_series(), frac_n=1)
        ind2 = indicators.add_indicators(_long_series(), frac_n=2)
        # frac_n=1: bar 39 peak is the max of h[38..40], confirmed at 40.
        self.assertTrue(bool(ind1["frac_up"].iloc[40]))
        self.assertFalse(bool(ind2["frac_up"].iloc[40]))
        self.assertTrue(bool(ind2["frac_up"].iloc[41]))

    def test_registration_imports_cleanly(self):
        import strategies.alligator_awesome_combo as mod

        self.assertEqual(mod.SPEC.slug, "alligator_awesome_combo")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
