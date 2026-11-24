"""UT Bot Alerts tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ut_bot import indicators, risk, signals


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


class TestUtBot(unittest.TestCase):
    def test_nloss_is_key_value_times_xatr(self):
        df = indicators.add_indicators(_rand_df())
        valid = df["xatr"].notna()
        self.assertTrue(
            bool(np.allclose(df.loc[valid, "nloss"], 1.0 * df.loc[valid, "xatr"]))
        )
        df2 = indicators.add_indicators(_rand_df(), key_value=2.0)
        self.assertTrue(
            bool(np.allclose(df2.loc[valid, "nloss"], 2.0 * df2.loc[valid, "xatr"]))
        )

    def test_stop_below_price_in_uptrend_above_in_downtrend(self):
        c = np.concatenate([100.0 + 2.0 * np.arange(150), 400.0 - 2.0 * np.arange(150)])
        df = indicators.add_indicators(_df_from_c(c))
        up = df.iloc[40:140]
        self.assertTrue(bool((up["ut_stop"] < up["c"]).all()))
        down = df.iloc[200:290]
        self.assertTrue(bool((down["ut_stop"] > down["c"]).all()))

    def test_stop_never_moves_against_trend(self):
        # uptrend: stop is non-decreasing once established; downtrend: non-increasing
        c = np.concatenate([100.0 + 2.0 * np.arange(150), 400.0 - 2.0 * np.arange(150)])
        df = indicators.add_indicators(_df_from_c(c))
        up_stop = df["ut_stop"].iloc[40:140].to_numpy()
        self.assertTrue(bool((np.diff(up_stop) >= -1e-9).all()))
        down_stop = df["ut_stop"].iloc[200:290].to_numpy()
        self.assertTrue(bool((np.diff(down_stop) <= 1e-9).all()))

    def test_down_then_up_fires_long(self):
        c = np.concatenate([400.0 - 2.0 * np.arange(150), 100.0 + 2.0 * np.arange(150)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 150 for b in entries))

    def test_up_then_down_fires_short(self):
        c = np.concatenate([100.0 + 2.0 * np.arange(150), 400.0 - 2.0 * np.arange(150)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 150 for b in entries))

    def test_flat_series_stop_tracks_below_close(self):
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        valid = df.iloc[30:]
        self.assertFalse(valid["ut_stop"].isna().any())
        # flat: true range is the 0.4 spread, ATR small, stop sits just below close
        self.assertTrue(bool((valid["ut_stop"] < valid["c"]).all()))
        self.assertTrue(bool((valid["ut_stop"] > valid["c"] - 1.0).all()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("xatr", "nloss", "ut_stop"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_exits_are_opposite_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_key_value_param_widens_stop(self):
        df1 = indicators.add_indicators(_rand_df(), key_value=1.0)
        df3 = indicators.add_indicators(_rand_df(), key_value=3.0)
        # wider KeyValue -> stop further from price in a clean uptrend
        c = 100.0 + 2.0 * np.arange(200)
        d1 = indicators.add_indicators(_df_from_c(c), key_value=1.0)
        d3 = indicators.add_indicators(_df_from_c(c), key_value=3.0)
        gap1 = (d1["c"] - d1["ut_stop"]).iloc[60:]
        gap3 = (d3["c"] - d3["ut_stop"]).iloc[60:]
        self.assertTrue(bool((gap3 > gap1).all()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("xatr", "nloss", "ut_stop"):
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
        import strategies.ut_bot as mod

        self.assertEqual(mod.SPEC.slug, "ut_bot")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

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
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
