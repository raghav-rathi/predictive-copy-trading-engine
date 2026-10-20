"""Ross Hook continuation tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ross_hook import indicators, risk, signals


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


def _rand_df(n=500, seed=21):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 0.8, n))
    return _df_from_c(c)


def _bullish_123_hook():
    """Monotone segments with sharp Vs: P1 low @10, P2 high @20,
    P3 higher low @30, breakout past P2, hook top @40, entry @43."""
    seg = []
    seg += list(np.linspace(110, 100, 11))      # 0..10 decline -> P1 low @10
    seg += list(np.linspace(100, 110, 11))[1:]  # 11..20 rally -> P2 high @20
    seg += list(np.linspace(110, 103, 11))[1:]  # 21..30 pullback -> P3 @30
    seg += list(np.linspace(103, 112, 11))[1:]  # 31..40 breakout rally -> hook @40
    seg += list(np.linspace(112, 108, 5))[1:]   # 41..44 pullback
    seg += list(np.linspace(108, 114, 6))[1:]   # 45..50 push -> entry @45/46
    return _df_from_c(seg)


def _bearish_123_hook():
    """Mirror: P1 high @10, P2 low @20, P3 lower high @30, breakdown,
    hook bottom @40, short entry."""
    seg = []
    seg += list(np.linspace(90, 100, 11))       # 0..10 rally -> P1 high @10
    seg += list(np.linspace(100, 90, 11))[1:]   # 11..20 fall -> P2 low @20
    seg += list(np.linspace(90, 97, 11))[1:]    # 21..30 bounce -> P3 @30
    seg += list(np.linspace(97, 88, 11))[1:]    # 31..40 breakdown -> hook @40
    seg += list(np.linspace(88, 92, 5))[1:]     # 41..44 bounce
    seg += list(np.linspace(92, 86, 6))[1:]     # 45..50 drop -> entry
    return _df_from_c(seg)


class TestRossHook(unittest.TestCase):
    def test_pivots_detected(self):
        df = indicators.add_indicators(_bullish_123_hook())
        # pivots confirmed 2 bars after their center
        self.assertTrue(bool(df["piv_low"].iloc[12]))   # P1 @10
        self.assertTrue(bool(df["piv_high"].iloc[22]))  # P2 @20
        self.assertTrue(bool(df["piv_low"].iloc[32]))   # P3 @30
        self.assertTrue(bool(df["piv_high"].iloc[42]))  # hook @40

    def test_pivot_prices_are_center_prices(self):
        df = indicators.add_indicators(_bullish_123_hook())
        # P1 center bar 10 low; the flag sits at bar 12
        self.assertAlmostEqual(df["piv_low_px"].iloc[12], df["l"].iloc[10])
        self.assertAlmostEqual(df["piv_high_px"].iloc[22], df["h"].iloc[20])

    def test_bullish_entry_fires(self):
        sig = signals.add_signals(indicators.add_indicators(_bullish_123_hook()))
        entries = sig.index[sig["long_entry"]]
        self.assertEqual(len(entries), 1)
        # close above the hook high (bar 40's high) first happens at bar 48
        self.assertEqual(entries[0], 48)
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_bearish_entry_fires(self):
        sig = signals.add_signals(indicators.add_indicators(_bearish_123_hook()))
        entries = sig.index[sig["short_entry"]]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0], 48)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_p3_below_p1_restarts(self):
        # P3 undercuts P1: no valid 1-2-3, so no breakout entry
        seg = list(np.linspace(110, 100, 11))
        seg += list(np.linspace(100, 110, 11))[1:]
        seg += list(np.linspace(110, 99, 11))[1:]   # P3 below P1
        seg += list(np.linspace(99, 112, 11))[1:]   # rally anyway
        seg += list(np.linspace(112, 114, 6))[1:]
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(seg)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_breakout_without_hook_no_entry(self):
        # 1-2-3 completes and breaks out, but price never forms a
        # confirmed pivot high after the breakout -> no hook, no entry
        seg = list(np.linspace(110, 100, 11))
        seg += list(np.linspace(100, 110, 11))[1:]
        seg += list(np.linspace(110, 103, 11))[1:]
        seg += list(np.linspace(103, 120, 21))[1:]  # straight up, no pivot
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(seg)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_invalidation_on_close_through_p1(self):
        # 1-2-3 completes, then price collapses through P1 before any
        # breakout: sequence resets, no entry
        seg = list(np.linspace(110, 100, 11))
        seg += list(np.linspace(100, 110, 11))[1:]
        seg += list(np.linspace(110, 103, 11))[1:]
        seg += list(np.linspace(103, 95, 11))[1:]    # through P1
        seg += list(np.linspace(95, 115, 11))[1:]    # recovers
        seg += list(np.linspace(115, 108, 5))[1:]
        seg += list(np.linspace(108, 116, 6))[1:]
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(seg)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exits_are_opposite_entries(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(400)
        ind_full = indicators.add_indicators(full)
        for j in (200, 350):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("piv_high", "piv_low"):
                self.assertEqual(bool(ind_full[col].iloc[j]),
                                 bool(ind_tr[col].iloc[j]), (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry"):
                self.assertEqual(bool(sig_full[col].iloc[j]),
                                 bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_monotone_trend_no_entries(self):
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_c(100.0 + np.arange(200) * 0.5)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_registration_imports_cleanly(self):
        import strategies.ross_hook as mod

        self.assertEqual(mod.SPEC.slug, "ross_hook")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.target_atr_mult, 2.5)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
