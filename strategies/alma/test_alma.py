"""ALMA dual-cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.alma import indicators, risk, signals
from strategies.base import crossed_above, crossed_below


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


class TestAlma(unittest.TestCase):
    def test_sustained_rally_fast_above_slow(self):
        # steady climb: ALMA(9) responds faster, ends above ALMA(21)
        c = 100.0 + 2.0 * np.arange(150)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertFalse(df["alma_fast"].iloc[130:].isna().any())
        self.assertTrue(bool((df["alma_fast"].iloc[130:] > df["alma_slow"].iloc[130:]).all()))

    def test_sustained_fall_fast_below_slow(self):
        # rally then deep fall: fast drops through slow
        c = np.concatenate([100.0 + 2.0 * np.arange(80),
                            260.0 - 3.0 * np.arange(80)])
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool(df["alma_fast"].iloc[-1] < df["alma_slow"].iloc[-1]))

    def test_cross_up_with_new_high_fires_long(self):
        # grind up (new highs) with a fast/slow cross -> long_entry fires
        c = np.concatenate([np.full(60, 100.0),
                            100.0 + 0.5 * np.arange(140)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))

    def test_cross_up_without_new_high_fires_nothing(self):
        # oscillating inside a box: crosses may print but no fresh extreme
        rng = np.random.default_rng(7)
        c = 100.0 + 1.5 * np.sin(np.arange(300) / 6.0) + rng.normal(0, 0.05, 300)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_cross_down_with_new_low_fires_short(self):
        # flat then steady fall with new lows -> short_entry fires
        c = np.concatenate([np.full(60, 200.0),
                            200.0 - 0.5 * np.arange(140)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exits_are_pure_opposite_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        expect_up = crossed_above(sig["alma_fast"], sig["alma_slow"]).fillna(False).astype(bool)
        expect_dn = crossed_below(sig["alma_fast"], sig["alma_slow"]).fillna(False).astype(bool)
        self.assertTrue(bool((sig["short_exit"] == expect_up).all()))
        self.assertTrue(bool((sig["long_exit"] == expect_dn).all()))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("alma_fast", "alma_slow", "alma_diff"):
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

    def test_alma_weights_normalize_and_peak_near_edge(self):
        w = indicators.alma_weights(9)
        self.assertAlmostEqual(float(w.sum()), 1.0, places=10)
        # offset 0.85: peak sits near the newest end of the window
        self.assertGreaterEqual(int(np.argmax(w)), 6)
        # a flat series reproduces the level exactly (no lag when there's
        # nothing to lag behind)
        df = indicators.add_indicators(_df_from_c(np.full(120, 100.0)))
        self.assertAlmostEqual(float(df["alma_fast"].iloc[-1]), 100.0, places=9)

    def test_registration_imports_cleanly(self):
        import strategies.alma as mod

        self.assertEqual(mod.SPEC.slug, "alma")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
