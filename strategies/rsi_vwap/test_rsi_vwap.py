"""RSI + session VWAP tests. Network-free, synthetic data only.

All series are UTC-hour aligned: bar 0 is 2023-11-15 00:00 UTC
(t0 = 1700006400000), so the session VWAP resets every 24 bars.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_vwap import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC


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


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _long_series():
    # Two flat days, then a day-3 dip (99..96) and recovery.
    # RSI crosses up through 30 at bar 53 (23.1 -> 38.4) with
    # the close (98) above the session VWAP (97.61). Long fires
    # at bar 53.
    return np.concatenate(
        [np.full(48, 100.0), [99, 98, 97, 96, 97, 98, 99, 100, 101, 102, 103, 104],
         np.full(24, 104.0)]
    )


def _short_series():
    # Steady rise (RSI high), then a drop: RSI crosses down
    # through 70 at bar 43 (70.4 -> 62.0) with the close (132)
    # below the session VWAP (132.05). Short fires at bar 43.
    return np.concatenate(
        [100 + 1.0 * np.arange(40), [138, 136, 134, 132, 130, 128, 126, 124, 122, 120],
         np.full(30, 120.0)]
    )


def _blocked_series():
    # Day 2 sits at 102 (VWAP ~102), dips to 98, then recovers.
    # RSI crosses up through 30 at bar 44 (12.0 -> 30.4) but the
    # close (99) is still below the session VWAP (101.4): the
    # VWAP side blocks the entry. Only the day-open gap entry at
    # bar 24 fires.
    return np.concatenate(
        [np.full(24, 100.0), np.full(16, 102.0),
         [101, 100, 99, 98, 99, 100, 101, 102, 103, 104], np.full(20, 104.0)]
    )


class TestRsiVwap(unittest.TestCase):
    def test_vwap_matches_direct_computation(self):
        df = indicators.add_indicators(_rand_df(200, seed=3))
        tp = (df["h"] + df["l"] + df["c"]) / 3.0
        day = (df["t"].to_numpy() // 86_400_000)
        for j in (30, 100, 180):
            mask = day == day[j]
            idx = np.where(mask)[0]
            upto = idx[idx <= j]
            expect = (tp.iloc[upto] * 100.0).sum() / (100.0 * len(upto))
            self.assertAlmostEqual(float(df["vwap"].iloc[j]), float(expect), places=6)

    def test_vwap_resets_at_utc_day_boundary(self):
        df = indicators.add_indicators(_df_from_c(_long_series()))
        # Bar 48 is the first bar of day 3: session_bar 1 and
        # VWAP equal to that bar's typical price.
        self.assertEqual(int(df["session_bar"].iloc[48]), 1)
        tp48 = (df["h"].iloc[48] + df["l"].iloc[48] + df["c"].iloc[48]) / 3.0
        self.assertAlmostEqual(float(df["vwap"].iloc[48]), float(tp48), places=9)
        self.assertEqual(int(df["session_bar"].iloc[47]), 24)

    def test_rsi_bounded_and_defined_after_warmup(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((df["rsi"].iloc[40:] >= 0) & (df["rsi"].iloc[40:] <= 100)).all()))
        self.assertFalse(df["rsi"].iloc[40:].isna().any())

    def test_long_fires_on_rsi_cross_up_above_vwap(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_long_series())))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [53])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_fires_on_rsi_cross_down_below_vwap(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_short_series())))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [43])
        # A long also fires at bar 14: the first defined RSI bar
        # jumps 0 -> 100 (base.rsi 0-fills the spin-up), which
        # registers as a cross through 30. It is inside WARMUP
        # (40), so the harness never trades it; assert only that
        # no long fires at/after warmup.
        self.assertFalse(bool(sig["long_entry"].iloc[40:].any()))

    def test_vwap_blocks_rsi_cross_below_it(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_blocked_series())))
        # The recovery cross at bar 44 is blocked; only the
        # day-open gap entry at bar 24 fires.
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [24])

    def test_long_exit_on_rsi_cross_below_50(self):
        # Long at 53, then a decline: RSI crosses below 50 at
        # bar 63 (53.4 -> 47.9) -- the first exit after entry.
        c = np.concatenate(
            [np.full(48, 100.0), [99, 98, 97, 96, 97, 98, 99, 100, 101, 102, 103, 104],
             [103, 102, 101, 100, 99, 98, 97, 96], np.full(24, 96.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [53])
        exits = [e for e in sig.index[sig["long_exit"]].tolist() if e > 53]
        self.assertEqual(exits[0], 63)
        self.assertLess(float(sig["rsi"].iloc[63]), 50.0)

    def test_short_exit_on_vwap_cross(self):
        # Short at 43, then a bounce: the close crosses back
        # above the session VWAP at bar 51 -- the first exit
        # after entry (the RSI-50 cross comes later, at 53).
        c = np.concatenate(
            [100 + 1.0 * np.arange(40), [138, 136, 134, 132, 130, 128, 126, 124, 122, 120],
             [121, 123, 125, 127, 129, 131], np.full(20, 131.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [43])
        exits = [e for e in sig.index[sig["short_exit"]].tolist() if e > 43]
        self.assertEqual(exits[0], 51)
        self.assertGreater(float(sig["c"].iloc[51]), float(sig["vwap"].iloc[51]))

    def test_oversold_param_changes_entry(self):
        # With the oversold level at 20, the RSI cross in the
        # long series happens at bar 52 (0.0 -> 23.1) while the
        # close (97) is still below the VWAP (97.6): no entry.
        # The shipped 30 fires at bar 53.
        sig_shipped = signals.add_signals(indicators.add_indicators(_df_from_c(_long_series())))
        sig_alt = signals.add_signals(
            indicators.add_indicators(_df_from_c(_long_series())),
            rsi_oversold=20.0)
        self.assertEqual(sig_shipped.index[sig_shipped["long_entry"]].tolist(), [53])
        self.assertFalse(bool(sig_alt["long_entry"].any()))

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("vwap", "rsi", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("vwap", "rsi", "atr14"):
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
        import strategies.rsi_vwap as mod

        self.assertEqual(mod.SPEC.slug, "rsi_vwap")
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
