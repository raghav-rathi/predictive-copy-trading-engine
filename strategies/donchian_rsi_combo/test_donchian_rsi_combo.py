"""Donchian RSI combo tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian_rsi_combo import indicators, risk, signals


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


def _breakout_long_series():
    # flat, then three down bars (so Wilder RSI has a real average
    # loss — after a pure flat stretch RSI sits at 0 and the first
    # up bar prints RSI ~76, which would block the long), then a
    # breakout above the prior 20-bar high. Long fires at bar 44.
    return np.concatenate(
        [np.full(40, 100.0), [98, 97, 96, 99, 102, 105, 108, 112, 118, 125, 135, 150],
         np.full(30, 150.0)]
    )


def _breakout_short_series():
    # steady rise (RSI high), then a drop below the prior 20-bar low
    # while RSI is still above 30. Short fires at bar 43.
    return np.concatenate(
        [100 + 1.0 * np.arange(40), [138, 130, 122, 115, 108, 100, 95, 90],
         np.full(30, 90.0)]
    )


class TestDonchianRsiCombo(unittest.TestCase):
    def test_donchian_channels_are_rolling_extremes(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect_high = df["h"].rolling(20, min_periods=20).max()
        expect_low = df["l"].rolling(20, min_periods=20).min()
        valid = expect_high.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "donchian_high_20"], expect_high[valid])))
        self.assertTrue(bool(np.allclose(df.loc[valid, "donchian_low_20"], expect_low[valid])))
        expect_low10 = df["l"].rolling(10, min_periods=10).min()
        self.assertTrue(bool(np.allclose(df.loc[valid, "donchian_low_10"], expect_low10[valid])))

    def test_rsi_bounded_and_defined_after_warmup(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((df["rsi"].iloc[30:] >= 0) & (df["rsi"].iloc[30:] <= 100)).all()))
        self.assertFalse(df["rsi"].iloc[30:].isna().any())

    def test_long_fires_on_breakout_with_rsi_below_70(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_breakout_long_series())))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertEqual(entries, [44])
        self.assertLess(float(sig["rsi"].iloc[44]), 70.0)

    def test_short_fires_on_breakdown_with_rsi_above_30(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_breakout_short_series())))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertEqual(entries, [43])
        self.assertGreater(float(sig["rsi"].iloc[43]), 30.0)

    def test_rsi_filter_blocks_overextended_long(self):
        ind = indicators.add_indicators(_df_from_c(_breakout_long_series()))
        ind["rsi"] = 80.0  # overbought: the same breakout must not fire
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_rsi_filter_blocks_oversold_short(self):
        ind = indicators.add_indicators(_df_from_c(_breakout_short_series()))
        ind["rsi"] = 20.0  # oversold: the same breakdown must not fire
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_turtle_exit_fires_after_long(self):
        c = np.concatenate(
            [np.full(40, 100.0), [98, 97, 96, 99, 102, 105, 108, 112, 118, 125, 135, 150],
             np.full(5, 150.0), [140, 130, 120, 110, 100], np.full(20, 100.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(any(e > entries[0] for e in exits))

    def test_exit_uses_prior_channel(self):
        # After a breakout to 150 and a flat stretch, a pullback to
        # 140 is below the prior 10-bar low (~149.8) and must exit —
        # the unshifted 10-bar low (which includes the current bar's
        # own low) could never be broken by the close.
        c = np.concatenate(
            [np.full(40, 100.0), [98, 97, 96, 99, 102, 105, 108, 112, 118, 125, 135, 150],
             np.full(10, 150.0), [140.0], np.full(10, 140.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_exit"].iloc[62]))

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_entry_window_param_changes_channel(self):
        df1 = indicators.add_indicators(_rand_df(), entry_n=10)
        df2 = indicators.add_indicators(_rand_df(), entry_n=20)
        self.assertFalse(bool(np.allclose(
            df1["donchian_high_10"].iloc[30:], df2["donchian_high_20"].iloc[30:])))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("donchian_high_20", "donchian_low_20", "donchian_high_10",
                    "donchian_low_10", "rsi", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("donchian_high_20", "donchian_low_20", "donchian_high_10",
                        "donchian_low_10", "rsi", "atr14"):
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
        import strategies.donchian_rsi_combo as mod

        self.assertEqual(mod.SPEC.slug, "donchian_rsi_combo")
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
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
