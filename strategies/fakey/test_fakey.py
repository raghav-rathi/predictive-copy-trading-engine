"""Fakey (false break of an inside bar) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fakey import indicators, risk, signals


def _df_from_ohlc(rows):
    """rows: list of (o, h, l, c)."""
    arr = np.asarray(rows, float)
    n = len(arr)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": arr[:, 0], "h": arr[:, 1], "l": arr[:, 2], "c": arr[:, 3],
         "v": np.full(n, 100.0)}
    )


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


def _rand_ohlc_df(n=800, seed=5):
    """Random walk with INDEPENDENT opens (small gap noise) and
    independent high/low wicks. The o=prev-close helper above can
    never produce an inside bar (consecutive bars share an endpoint),
    so fakey tests that need realistic inside-bar frequency use this."""
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    o = np.concatenate([[c[0]], c[:-1]]) + rng.normal(0, 0.3, n)
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.5, n))
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.5, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


# 5 neutral filler bars, then the 3-bar pattern at indices 5, 6, 7.
FILLER = [(100, 101, 99, 100)] * 5
MOTHER = (100, 110, 90, 100)
INSIDE = (100, 105, 95, 100)


class TestFakey(unittest.TestCase):
    def test_bullish_fakey_constructed(self):
        # break below inside low (93 < 95) but close back inside mother (101 > 90)
        rows = FILLER + [MOTHER, INSIDE, (100, 102, 93, 101)]
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(rows)))
        self.assertTrue(bool(sig["long_entry"].iloc[7]))
        self.assertFalse(bool(sig["short_entry"].iloc[7]))
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_bearish_fakey_constructed(self):
        # break above inside high (107 > 105) but close back inside mother (99 < 110)
        rows = FILLER + [MOTHER, INSIDE, (100, 107, 98, 99)]
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(rows)))
        self.assertTrue(bool(sig["short_entry"].iloc[7]))
        self.assertFalse(bool(sig["long_entry"].iloc[7]))
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_break_without_close_back_inside_is_not_fakey(self):
        # break below inside low AND close below mother low: a real break, not fake
        rows = FILLER + [MOTHER, INSIDE, (100, 102, 93, 89)]
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(rows)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_inside_bar_no_fakey(self):
        # second bar is NOT inside the mother (high 112 > 110), so no pattern
        rows = FILLER + [MOTHER, (100, 112, 95, 100), (100, 102, 93, 101)]
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(rows)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_bar_breaking_both_sides_fires_neither(self):
        # wide-range bar breaks both inside extremes (h 107 > 105,
        # l 93 < 95) while closing inside the mother range: ambiguous,
        # fires neither entry
        rows = FILLER + [MOTHER, INSIDE, (100, 107, 93, 100)]
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(rows)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_break_no_fakey(self):
        # inside bar, but bar i stays inside the inside bar's range: no break
        rows = FILLER + [MOTHER, INSIDE, (100, 103, 96, 100)]
        sig = signals.add_signals(indicators.add_indicators(_df_from_ohlc(rows)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_inside_bar_flag(self):
        rows = FILLER + [MOTHER, INSIDE, (100, 102, 93, 101)]
        df = indicators.add_indicators(_df_from_ohlc(rows))
        self.assertTrue(bool(df["is_inside"].iloc[6]))
        self.assertFalse(bool(df["is_inside"].iloc[5]))
        self.assertFalse(bool(df["is_inside"].iloc[7]))

    def test_confirm_inside_is_stricter(self):
        # close 94: back inside mother (94 > 90) but NOT back inside the
        # inside bar (94 < 95) -> mother confirms, inside does not
        rows = FILLER + [MOTHER, INSIDE, (100, 102, 93, 94)]
        df = indicators.add_indicators(_df_from_ohlc(rows))
        sig_mother = signals.add_signals(df, confirm="mother")
        sig_inside = signals.add_signals(df, confirm="inside")
        self.assertTrue(bool(sig_mother["long_entry"].iloc[7]))
        self.assertFalse(bool(sig_inside["long_entry"].iloc[7]))

    def test_exits_are_opposite_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_ohlc_df(800, seed=5)))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_signals_fire_on_random_walk(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_ohlc_df(800, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertTrue(bool(sig["long_exit"].any()))
        self.assertTrue(bool(sig["short_exit"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_ohlc_df(300, seed=11)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("is_inside",):
                self.assertEqual(bool(ind_full[col].iloc[j]), bool(ind_tr[col].iloc[j]), (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.fakey as mod

        self.assertEqual(mod.SPEC.slug, "fakey")
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
        self.assertEqual(risk.WARMUP, 5)


if __name__ == "__main__":
    unittest.main()
