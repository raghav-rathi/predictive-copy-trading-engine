"""Heikin Ashi + Stochastic tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.heikin_ashi_stochastic import indicators, risk, signals


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _signal_frame(n=70, **overrides):
    """Minimal frame with hand-set indicator columns for signals.py."""
    df = pd.DataFrame(
        {
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0),
            "h": np.full(n, 100.0),
            "l": np.full(n, 100.0),
            "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
            "ha_open": np.full(n, 100.0),
            "ha_close": np.full(n, 100.0),
            "ha_ema50": np.full(n, 99.0),
            "stoch_k": np.full(n, 50.0),
            "stoch_d": np.full(n, 50.0),
        }
    )
    for col, vals in overrides.items():
        for i, v in vals.items():
            df.loc[i, col] = v
    return df


class TestHeikinAshiStochasticIndicators(unittest.TestCase):
    def test_ha_close_is_ohlc_average(self):
        df = indicators.add_indicators(_rand_df())
        expect = (df["o"] + df["h"] + df["l"] + df["c"]) / 4.0
        self.assertTrue(bool(np.allclose(df["ha_close"], expect)))

    def test_ha_open_recursion_hand_computed(self):
        # bar0: o=100,h=102,l=99,c=101 -> ha_close=100.5, ha_open=o[0]=100
        # bar1: o=101,h=103,l=100,c=102 -> ha_close=101.5,
        #       ha_open=(100+100.5)/2=100.25
        # bar2: o=102,h=104,l=101,c=103 -> ha_close=102.5,
        #       ha_open=(100.25+101.5)/2=100.875
        df = pd.DataFrame(
            {
                "t": [1_700_000_000_000 + i * 3_600_000 for i in range(3)],
                "o": [100.0, 101.0, 102.0],
                "h": [102.0, 103.0, 104.0],
                "l": [99.0, 100.0, 101.0],
                "c": [101.0, 102.0, 103.0],
                "v": [100.0, 100.0, 100.0],
            }
        )
        out = indicators.add_indicators(df)
        self.assertTrue(np.allclose(out["ha_close"], [100.5, 101.5, 102.5]))
        self.assertTrue(np.allclose(out["ha_open"], [100.0, 100.25, 100.875]))

    def test_ha_open_seeded_to_first_open(self):
        df = indicators.add_indicators(_rand_df())
        self.assertEqual(df["ha_open"].iloc[0], df["o"].iloc[0])

    def test_ha_high_low_envelope(self):
        df = indicators.add_indicators(_rand_df())
        self.assertTrue(bool((df["ha_high"] >= df["h"]).all()))
        self.assertTrue(bool((df["ha_high"] >= df["ha_close"]).all()))
        self.assertTrue(bool((df["ha_low"] <= df["l"]).all()))
        self.assertTrue(bool((df["ha_low"] <= df["ha_close"]).all()))

    def test_stoch_k_d_bounded_0_100(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((df["stoch_k"] >= 0) & (df["stoch_k"] <= 100)).all()))
        self.assertTrue(bool(((df["stoch_d"] >= 0) & (df["stoch_d"] <= 100)).all()))

    def test_stoch_k_100_at_range_high_0_at_range_low(self):
        n = 20
        base = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.full(n, 105.0),
                "h": np.full(n, 110.0),
                "l": np.full(n, 100.0),
                "c": np.full(n, 110.0),
                "v": np.full(n, 100.0),
            }
        )
        out = indicators.add_indicators(base)
        self.assertTrue(bool((out["stoch_k"].iloc[16:] == 100.0).all()))
        base["c"] = 100.0
        out2 = indicators.add_indicators(base)
        self.assertTrue(bool((out2["stoch_k"].iloc[16:] == 0.0).all()))

    def test_stoch_flat_series_neutral_50(self):
        df = indicators.add_indicators(_df_from_c(np.full(100, 100.0)))
        self.assertTrue(bool((df["stoch_k"] == 50.0).all()))
        self.assertTrue(bool((df["stoch_d"] == 50.0).all()))

    def test_stoch_d_is_sma3_of_k(self):
        df = indicators.add_indicators(_rand_df(300, seed=7))
        expect = df["stoch_k"].rolling(3, min_periods=3).mean()
        valid = expect.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "stoch_d"], expect[valid])))

    def test_ha_ema50_no_nan_and_filled_before_bar_50(self):
        df = indicators.add_indicators(_rand_df(200, seed=3))
        self.assertFalse(df["ha_ema50"].isna().any())
        # Before the EMA exists (min_periods=50) it is filled with
        # ha_close, so the trend comparison is False, never NaN.
        self.assertTrue(
            bool(np.allclose(df["ha_ema50"].iloc[:49], df["ha_close"].iloc[:49]))
        )

    def test_no_nan_indicator_columns(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        for col in ("ha_open", "ha_high", "ha_low", "ha_close",
                    "ha_ema50", "stoch_k", "stoch_d"):
            self.assertFalse(df[col].isna().any(), col)


class TestHeikinAshiStochasticSignals(unittest.TestCase):
    def test_long_entry_fires_on_handcrafted_conditions(self):
        # %K crosses above %D at bar 60 (20->25 vs 22->21) with %K=25<30,
        # HA bullish (ha_close 101 > ha_open 100), above EMA(50)=99.
        df = _signal_frame(
            stoch_k={59: 20.0, 60: 25.0, 61: 28.0, 62: 20.0},
            stoch_d={59: 22.0, 60: 21.0, 61: 23.0, 62: 24.0},
            ha_close={60: 101.0, 61: 101.0, 62: 99.0},
        )
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_entry"].iloc[60]))
        self.assertFalse(bool(sig["long_entry"].iloc[61]))  # transition-only
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_entry_fires_on_handcrafted_conditions(self):
        # %K crosses below %D at bar 60 (80->75 vs 78->79) with %K=75>70,
        # HA bearish (ha_close 99 < ha_open 100), below EMA(50)=101.
        df = _signal_frame(
            ha_ema50={i: 101.0 for i in range(70)},
            stoch_k={59: 80.0, 60: 75.0, 61: 72.0, 62: 80.0},
            stoch_d={59: 78.0, 60: 79.0, 61: 77.0, 62: 76.0},
            ha_close={60: 99.0, 61: 99.0, 62: 101.0},
        )
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["short_entry"].iloc[60]))
        self.assertFalse(bool(sig["short_entry"].iloc[61]))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_long_blocked_when_k_not_oversold(self):
        # Same cross as the long test but %K=35 at the cross bar.
        df = _signal_frame(
            stoch_k={59: 20.0, 60: 35.0},
            stoch_d={59: 22.0, 60: 21.0},
            ha_close={60: 101.0},
        )
        sig = signals.add_signals(df)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_long_blocked_when_ha_bearish(self):
        # Cross + oversold + above EMA, but HA bearish.
        df = _signal_frame(
            stoch_k={59: 20.0, 60: 25.0},
            stoch_d={59: 22.0, 60: 21.0},
            ha_close={60: 99.0},
        )
        sig = signals.add_signals(df)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_long_blocked_below_ema(self):
        # Cross + oversold + HA bullish, but ha_close below the EMA.
        df = _signal_frame(
            ha_ema50={i: 102.0 for i in range(70)},
            stoch_k={59: 20.0, 60: 25.0},
            stoch_d={59: 22.0, 60: 21.0},
            ha_close={60: 101.0},
        )
        sig = signals.add_signals(df)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exit_on_opposite_cross(self):
        # Long at 60, %K crosses below %D at 62 -> long_exit, no flip
        # (short needs %K>70, here %K=20).
        df = _signal_frame(
            stoch_k={59: 20.0, 60: 25.0, 61: 28.0, 62: 20.0},
            stoch_d={59: 22.0, 60: 21.0, 61: 23.0, 62: 24.0},
            ha_close={60: 101.0, 61: 101.0, 62: 99.0},
        )
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_exit"].iloc[62]))
        self.assertFalse(bool(sig["short_entry"].iloc[62]))

    def test_flip_on_opposite_entry_conditions(self):
        # Long at 60; at 62 %K crosses below %D (long exit) AND the
        # short conditions hold (HA bearish, below EMA, %K>70) ->
        # exit + short entry on the same bar.
        df = _signal_frame(
            ha_ema50={i: 101.0 for i in range(70)},
            stoch_k={59: 20.0, 60: 25.0, 61: 28.0, 62: 75.0},
            stoch_d={59: 22.0, 60: 21.0, 61: 23.0, 62: 76.0},
            ha_close={60: 101.0, 61: 101.0, 62: 99.0},
            ha_open={62: 100.0},
        )
        # ha_ema50=101 everywhere makes the bar-60 long fail the
        # above-EMA test, so set the EMA low before bar 62.
        df.loc[60, "ha_ema50"] = 99.0
        df.loc[61, "ha_ema50"] = 99.0
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_entry"].iloc[60]))
        self.assertTrue(bool(sig["long_exit"].iloc[62]))
        self.assertTrue(bool(sig["short_entry"].iloc[62]))

    def test_no_simultaneous_long_and_short(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))
        self.assertFalse(bool((sig["long_exit"] & sig["short_exit"]).any()))

    def test_no_nan_boolean_signal_columns(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_long_entry_fires_on_spike_pullback_bounce(self):
        # End-to-end long path through indicators+signals on OHLC:
        # flat 100, spike to 115 (widens the 14-bar range), pull back
        # to 103 (still above the EMA(50), %K back under 30), then a
        # steady bounce — %K crosses above %D out of oversold while
        # HA is bullish and ha_close is above its EMA(50).
        c = np.concatenate([
            np.full(60, 100.0),
            np.linspace(100, 115, 5)[1:],
            np.linspace(115, 103, 12)[1:],
            103.0 + 1.0 * np.arange(1, 41),
            np.full(20, 143.0),
        ])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))
        i = int(np.where(sig["long_entry"].to_numpy())[0][0])
        self.assertTrue(sig["ha_close"].iloc[i] > sig["ha_open"].iloc[i])
        self.assertTrue(sig["ha_close"].iloc[i] > sig["ha_ema50"].iloc[i])
        self.assertTrue(sig["stoch_k"].iloc[i] < 30)
        self.assertTrue(sig["stoch_k"].iloc[i] > sig["stoch_d"].iloc[i])

    def test_short_entries_fire_on_random_data(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_warmup_no_entries_before_bar_49(self):
        # Before bar 49 the EMA(50) does not exist yet, so the trend
        # gate is False (ha_ema50 filled with ha_close) and no entry
        # can fire. Bar 49 is the first bar with a real EMA(50).
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool(sig["long_entry"].iloc[:49].any()))
        self.assertFalse(bool(sig["short_entry"].iloc[:49].any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("ha_open", "ha_close", "ha_ema50", "stoch_k", "stoch_d"):
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

    def test_registration_imports_cleanly(self):
        import strategies.heikin_ashi_stochastic as mod

        self.assertEqual(mod.SPEC.slug, "heikin_ashi_stochastic")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )
        self.assertTrue(mod.SPEC.source_url.startswith("https://"))

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
