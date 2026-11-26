"""Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.heikin_ashi_adx import indicators, risk, signals


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

def _up_series():
    # flat, then a steady 1.5/bar rise (ADX builds past 25), then flat.
    # First long entry lands at bar 54.
    return np.concatenate(
        [np.full(40, 100.0), 100 + 1.5 * np.arange(40), np.full(30, 160.0)]
    )


def _down_series():
    # flat, then a steady 1.5/bar fall, then flat. First short at 54.
    return np.concatenate(
        [np.full(40, 160.0), 160 - 1.5 * np.arange(40), np.full(30, 100.0)]
    )


def _up_then_down_series():
    # uptrend (long entry 54) then a reversal; first exit after entry is 72.
    return np.concatenate(
        [np.full(40, 100.0), 100 + 1.5 * np.arange(30),
         145 - 1.5 * np.arange(30), np.full(20, 100.0)]
    )


class TestHeikinAshiAdx(unittest.TestCase):
    def test_ha_close_is_ohlc_average(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect = (df["o"] + df["h"] + df["l"] + df["c"]) / 4.0
        self.assertTrue(bool(np.allclose(df["ha_close"], expect)))

    def test_ha_open_recursion_and_seed(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertEqual(float(df["ha_open"].iloc[0]), float(df["o"].iloc[0]))
        expect = (df["ha_open"].shift(1) + df["ha_close"].shift(1)) / 2.0
        self.assertTrue(bool(np.allclose(df["ha_open"].iloc[1:], expect.iloc[1:])))

    def test_ha_high_low_envelope(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect_high = np.maximum(np.maximum(df["h"], df["ha_open"]), df["ha_close"])
        expect_low = np.minimum(np.minimum(df["l"], df["ha_open"]), df["ha_close"])
        self.assertTrue(bool(np.allclose(df["ha_high"], expect_high)))
        self.assertTrue(bool(np.allclose(df["ha_low"], expect_low)))

    def test_adx_columns_match_base(self):
        from strategies import base as B

        df = indicators.add_indicators(_rand_df(800, seed=5))
        a = B.adx(df["h"], df["l"], df["c"], 14)
        valid = a["adx"].notna()
        for col in ("adx", "plus_di", "minus_di"):
            self.assertTrue(bool(np.allclose(df.loc[valid, col], a.loc[valid, col])))

    def test_long_fires_on_green_ha_with_strong_adx(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_up_series())))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertEqual(entries[0], 54)
        i = entries[0]
        self.assertGreater(float(sig["ha_close"].iloc[i]), float(sig["ha_open"].iloc[i]))
        self.assertGreater(float(sig["adx"].iloc[i]), 25.0)
        self.assertGreater(float(sig["plus_di"].iloc[i]), float(sig["minus_di"].iloc[i]))

    def test_short_fires_on_red_ha_with_strong_adx(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_down_series())))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertEqual(entries[0], 54)
        i = entries[0]
        self.assertLess(float(sig["ha_close"].iloc[i]), float(sig["ha_open"].iloc[i]))
        self.assertGreater(float(sig["adx"].iloc[i]), 25.0)
        self.assertGreater(float(sig["minus_di"].iloc[i]), float(sig["plus_di"].iloc[i]))

    def test_adx_filter_blocks_weak_trend(self):
        ind = indicators.add_indicators(_df_from_c(_up_series()))
        ind["adx"] = 15.0  # chop: the same green HA bars must not fire
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_di_filter_blocks_wrong_direction(self):
        ind = indicators.add_indicators(_df_from_c(_up_series()))
        ind["plus_di"], ind["minus_di"] = ind["minus_di"], ind["plus_di"]
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exit_on_ha_flip_after_long(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_up_then_down_series())))
        entries = sig.index[sig["long_entry"]].tolist()
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        after = [e for e in exits if e > entries[0]]
        self.assertEqual(after[0], 72)
        # the exit bar is a red HA bar
        self.assertLess(float(sig["ha_close"].iloc[after[0]]),
                        float(sig["ha_open"].iloc[after[0]]))

    def test_exit_on_adx_collapse(self):
        ind = indicators.add_indicators(_df_from_c(_up_series()))
        ind["adx"] = 10.0  # trend dead: every bar must signal long_exit
        sig = signals.add_signals(ind)
        self.assertTrue(bool(sig["long_exit"].all()))
        self.assertTrue(bool(sig["short_exit"].all()))

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("ha_open", "ha_high", "ha_low", "ha_close",
                    "adx", "plus_di", "minus_di", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("ha_open", "ha_high", "ha_low", "ha_close",
                        "adx", "plus_di", "minus_di", "atr14"):
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
        import strategies.heikin_ashi_adx as mod

        self.assertEqual(mod.SPEC.slug, "heikin_ashi_adx")
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
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
