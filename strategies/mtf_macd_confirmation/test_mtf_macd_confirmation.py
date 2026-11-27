"""Multi-timeframe MACD confirmation tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mtf_macd_confirmation import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC (hour-aligned)


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=600, seed=7):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _signal_frame(macd, sig, hist4):
    """Hand-set indicator frame: tests signal logic deterministically."""
    n = len(macd)
    return pd.DataFrame(
        {
            "t": (T0 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0),
            "h": np.full(n, 100.2),
            "l": np.full(n, 99.8),
            "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
            "macd": np.asarray(macd, float),
            "macd_signal": np.asarray(sig, float),
            "macd_hist_4h": np.asarray(hist4, float),
        }
    )


class TestMtfMacdConfirmation(unittest.TestCase):
    def test_constant_series_macd_is_zero(self):
        # A flat close makes every EMA equal to the close, so the
        # MACD line, signal and histogram are exactly 0 once warm.
        ind = indicators.add_indicators(_df_from_c(np.full(300, 100.0)))
        self.assertAlmostEqual(float(ind["macd"].iloc[100]), 0.0, places=9)
        self.assertAlmostEqual(float(ind["macd_signal"].iloc[100]), 0.0, places=9)
        self.assertAlmostEqual(float(ind["macd_hist"].iloc[100]), 0.0, places=9)
        self.assertAlmostEqual(float(ind["macd_hist_4h"].iloc[200]), 0.0, places=9)

    def test_rising_series_macd_positive(self):
        # On a steady rise the fast EMA sits above the slow EMA,
        # so both the 1h and the 4h MACD lines are positive.
        c = 100.0 + 0.5 * np.arange(300)
        ind = indicators.add_indicators(_df_from_c(c))
        self.assertGreater(float(ind["macd"].iloc[200]), 0.0)
        self.assertGreater(float(ind["macd_4h"].iloc[200]), 0.0)
        self.assertGreater(float(ind["macd_hist_4h"].iloc[200]), 0.0)

    def test_4h_hist_nan_until_first_completed_4h_macd(self):
        # The 4h MACD needs 26 4h bars for the slow EMA and 9 more
        # for the signal EMA: the first valid 4h histogram belongs
        # to 4h bar 33, available to 1h bar 136. Before that it is
        # NaN -- the 4h filter cannot fire on incomplete data.
        ind = indicators.add_indicators(_df_from_c(np.full(300, 100.0)))
        self.assertTrue(np.isnan(ind["macd_hist_4h"].iloc[135]))
        self.assertFalse(np.isnan(ind["macd_hist_4h"].iloc[136]))
        self.assertTrue(ind["macd_hist_4h"].iloc[:136].isna().all())

    def test_1h_macd_nan_before_slow_ema_warmup(self):
        ind = indicators.add_indicators(_df_from_c(np.full(300, 100.0)))
        # Slow EMA (26) needs 26 observations: first valid MACD at
        # index 25 (the 26th bar).
        self.assertTrue(ind["macd"].iloc[:25].isna().all())
        self.assertFalse(ind["macd"].iloc[25:].isna().any())

    def test_long_entry_on_cross_up_with_positive_4h_hist(self):
        # MACD crosses above its signal at bar 3; 4h hist > 0.
        sig = signals.add_signals(
            _signal_frame(
                [1, 1, 1, 2, 3, 2, 1, 0, -1, -2],
                [1.5] * 10,
                [0.1] * 10,
            )
        )
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [3])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_long_exit_on_cross_back(self):
        # Same frame: MACD crosses back below its signal at bar 6.
        sig = signals.add_signals(
            _signal_frame(
                [1, 1, 1, 2, 3, 2, 1, 0, -1, -2],
                [1.5] * 10,
                [0.1] * 10,
            )
        )
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [6])

    def test_short_entry_on_cross_down_with_negative_4h_hist(self):
        sig = signals.add_signals(
            _signal_frame(
                [-1, -1, -1, -2, -3, -2, -1, 0, 1, 2],
                [-1.5] * 10,
                [-0.1] * 10,
            )
        )
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [3])
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [6])

    def test_4h_filter_blocks_long_when_hist_negative(self):
        # Same cross-up shape, but the 4h histogram is negative:
        # no long entry. (The cross-down at bar 6 IS a valid short
        # entry under the negative 4h trend, which the filter allows.)
        sig = signals.add_signals(
            _signal_frame(
                [1, 1, 1, 2, 3, 2, 1, 0, -1, -2],
                [1.5] * 10,
                [-0.1] * 10,
            )
        )
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [6])

    def test_4h_filter_blocks_short_when_hist_positive(self):
        sig = signals.add_signals(
            _signal_frame(
                [-1, -1, -1, -2, -3, -2, -1, 0, 1, 2],
                [-1.5] * 10,
                [0.1] * 10,
            )
        )
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [6])

    def test_long_exit_on_4h_hist_cross_below_zero(self):
        # MACD stays above its signal throughout; the 4h histogram
        # crossing below zero at bar 3 exits the long.
        sig = signals.add_signals(
            _signal_frame(
                [2.0] * 10,
                [1.5] * 10,
                [0.1, 0.1, 0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1, -0.1],
            )
        )
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [3])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_level_condition_does_not_refire(self):
        # MACD above its signal for 10 straight bars with a
        # positive 4h histogram: a level condition would fire
        # every bar, a cross fires never (no cross in the frame).
        sig = signals.add_signals(
            _signal_frame([2.0] * 10, [1.5] * 10, [0.1] * 10)
        )
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_entries_only_when_filter_holds_on_random_walk(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(600, seed=7)))
        # Every long entry sits on a cross-up with a positive 4h
        # histogram; every short entry on a cross-down with a
        # negative one. (Property check over the full pipeline.)
        for i in sig.index[sig["long_entry"]]:
            self.assertGreater(float(sig["macd_hist_4h"].iloc[i]), 0.0)
            self.assertGreater(float(sig["macd"].iloc[i]), float(sig["macd_signal"].iloc[i]))
            self.assertLessEqual(float(sig["macd"].iloc[i - 1]), float(sig["macd_signal"].iloc[i - 1]))
        for i in sig.index[sig["short_entry"]]:
            self.assertLess(float(sig["macd_hist_4h"].iloc[i]), 0.0)
        self.assertTrue(len(sig.index[sig["long_entry"]]) + len(sig.index[sig["short_entry"]]) > 0)

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(600, seed=7)))
        for col in ("macd", "macd_signal", "macd_hist", "macd_4h",
                    "macd_signal_4h", "macd_hist_4h", "atr14"):
            self.assertFalse(sig[col].iloc[250:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(400)
        ind_full = indicators.add_indicators(full)
        for j in (200, 350):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("macd", "macd_signal", "macd_hist", "macd_4h",
                        "macd_signal_4h", "macd_hist_4h", "atr14"):
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
        import strategies.mtf_macd_confirmation as mod

        self.assertEqual(mod.SPEC.slug, "mtf_macd_confirmation")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 168)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 200)


if __name__ == "__main__":
    unittest.main()
