"""Connors TPS tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.connors_tps import indicators, risk, signals


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


def _pullback_long_series():
    # Steady 0.25/bar rise for 200 bars, then a sharp two-bar
    # pullback (150 -> 140 -> 130) while the close stays above
    # SMA(200) (~125.2), then a recovery. Long fires at bar 201.
    return np.concatenate([100 + 0.25 * np.arange(200),
                           [140, 130, 135, 145, 155], np.full(20, 155.0)])


def _rally_short_series():
    # Steady 0.25/bar decline for 200 bars, then a sharp two-bar
    # rally (100 -> 110 -> 120) while the close stays below
    # SMA(200) (~124.8), then a fade. Short fires at bar 201.
    return np.concatenate([150 - 0.25 * np.arange(200),
                           [110, 120, 115, 105, 95], np.full(20, 95.0)])


class TestConnorsTps(unittest.TestCase):
    def test_sma200_is_rolling_mean(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect = df["c"].rolling(200, min_periods=200).mean()
        valid = expect.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "sma200"], expect[valid])))

    def test_rsi2_bounded_and_defined_after_warmup(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((df["rsi2"].iloc[210:] >= 0) & (df["rsi2"].iloc[210:] <= 100)).all()))
        self.assertFalse(df["rsi2"].iloc[210:].isna().any())

    def test_long_fires_on_second_oversold_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_pullback_long_series())))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertEqual(entries, [201])
        i = entries[0]
        self.assertGreater(float(sig["c"].iloc[i]), float(sig["sma200"].iloc[i]))
        self.assertLess(float(sig["rsi2"].iloc[i]), 25.0)
        self.assertLess(float(sig["rsi2"].iloc[i - 1]), 25.0)

    def test_short_fires_on_second_overbought_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_rally_short_series())))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertEqual(entries, [201])
        i = entries[0]
        self.assertLess(float(sig["c"].iloc[i]), float(sig["sma200"].iloc[i]))
        self.assertGreater(float(sig["rsi2"].iloc[i]), 75.0)
        self.assertGreater(float(sig["rsi2"].iloc[i - 1]), 75.0)

    def test_single_oversold_bar_does_not_fire(self):
        # Same uptrend, but only ONE sharp down bar before the
        # recovery — the two-consecutive-bar rule must block it.
        c = np.concatenate([100 + 0.25 * np.arange(200),
                            [140, 145, 155], np.full(20, 155.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertLess(float(sig["rsi2"].iloc[200]), 25.0)

    def test_trend_filter_blocks_countertrend_long(self):
        # Steady decline: RSI(2) sits below 25 for bar after bar,
        # but the close is below SMA(200) the whole time — no long.
        c = np.concatenate([150 - 0.25 * np.arange(200),
                            [99, 98, 97], np.full(20, 97.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertLess(float(sig["rsi2"].iloc[201]), 25.0)

    def test_trend_filter_blocks_countertrend_short(self):
        # Steady rise: RSI(2) sits above 75, but the close is
        # above SMA(200) the whole time — no short.
        c = np.concatenate([100 + 0.25 * np.arange(200),
                            [151, 152, 153], np.full(20, 153.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertGreater(float(sig["rsi2"].iloc[201]), 75.0)

    def test_long_exit_when_rsi2_closes_above_70(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_pullback_long_series())))
        entries = sig.index[sig["long_entry"]].tolist()
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(any(e > entries[0] for e in exits))
        e = next(x for x in exits if x > entries[0])
        self.assertGreater(float(sig["rsi2"].iloc[e]), 70.0)

    def test_short_exit_when_rsi2_closes_below_30(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_rally_short_series())))
        entries = sig.index[sig["short_entry"]].tolist()
        exits = sig.index[sig["short_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(any(e > entries[0] for e in exits))
        e = next(x for x in exits if x > entries[0])
        self.assertLess(float(sig["rsi2"].iloc[e]), 30.0)

    def test_entry_threshold_param_moves_setup(self):
        ind = indicators.add_indicators(_df_from_c(_pullback_long_series()))
        sig_loose = signals.add_signals(ind, entry_low=30.0)
        sig_tight = signals.add_signals(ind, entry_low=0.5)
        # RSI(2) at the pullback is ~0.8-2.5: fires at 30 and at
        # 25, but not at 0.5.
        self.assertTrue(bool(sig_loose["long_entry"].any()))
        self.assertFalse(bool(sig_tight["long_entry"].any()))

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("sma200", "rsi2", "atr14"):
            self.assertFalse(sig[col].iloc[220:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(500)
        ind_full = indicators.add_indicators(full)
        for j in (300, 450):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("sma200", "rsi2", "atr14"):
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
        import strategies.connors_tps as mod

        self.assertEqual(mod.SPEC.slug, "connors_tps")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 10)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 210)


if __name__ == "__main__":
    unittest.main()
