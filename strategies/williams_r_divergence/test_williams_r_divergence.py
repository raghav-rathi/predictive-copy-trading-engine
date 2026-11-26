"""Williams %R divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.williams_r_divergence import indicators, risk, signals


def _frame(o, h, l, c, v=None):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _mk(c):
    """Frame with explicit h=c+1, l=c-1 so pivot lows/highs are
    strict extremes (real candles have distinct intraday lows;
    deriving l from min(o, c) would tie adjacent bars)."""
    c = np.asarray(c, dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    return _frame(o, c + 1.0, c - 1.0, c)


def _rand_df(n=500, seed=7):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _mk(c)


def _bullish_divergence_closes():
    """Sharp dip to 80, recovery, then a slow drift to a lower
    low of 75. Verified by hand against the pivot rule:
    confirmed pivot lows at bars 45 (price 79, %R -95.5) and
    84 (price 74, %R -93.6) — lower low with a HIGHER %R,
    i.e. bullish divergence confirmed at 84."""
    c = [100.0] * 40
    c += [95, 90, 85, 80, 85, 90, 95, 100]
    c += [100.0] * 10
    c += list(np.linspace(100, 75, 25))
    c += [78, 82, 88, 95, 100]
    c += [100.0] * 10
    return c


def _bearish_divergence_closes():
    """Mirror: spike to 120, fade, then a slow grind to a
    higher high of 125. Confirmed pivot highs at bars 45
    (price 121, %R -4.5) and 84 (price 126, %R -6.4) —
    higher high with a LOWER %R, bearish divergence at 84."""
    c = [100.0] * 40
    c += [105, 110, 115, 120, 115, 110, 105, 100]
    c += [100.0] * 10
    c += list(np.linspace(100, 125, 25))
    c += [122, 118, 112, 105, 100]
    c += [100.0] * 10
    return c


class TestWilliamsRDivergence(unittest.TestCase):
    def test_williams_r_matches_direct_computation(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        hh = df["h"].rolling(14, min_periods=14).max()
        ll = df["l"].rolling(14, min_periods=14).min()
        expect = -100.0 * (hh - df["c"]) / (hh - ll)
        valid = expect.notna() & ((hh - ll) > 0)
        self.assertTrue(bool(np.allclose(df.loc[valid, "williams_r"], expect[valid])))

    def test_williams_r_bounded_after_warmup(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((df["williams_r"].iloc[30:] >= -100) & (df["williams_r"].iloc[30:] <= 0)).all()))
        self.assertFalse(df["williams_r"].iloc[30:].isna().any())

    def test_flat_range_reads_minus_50(self):
        # h == l == c: zero 14-bar range -> neutral -50, no crash.
        n = 50
        df = indicators.add_indicators(_frame(
            np.full(n, 100.0), np.full(n, 100.0), np.full(n, 100.0),
            np.full(n, 100.0)))
        self.assertTrue(bool((df["williams_r"].iloc[14:] == -50.0).all()))

    def test_confirmed_pivots_follow_plus_minus_2_rule(self):
        ind = indicators.add_indicators(_mk(_bullish_divergence_closes()))
        self.assertEqual(ind.index[ind["pivot_low_confirmed"]].tolist(), [45, 84])
        self.assertEqual(float(ind["pivot_low_price"].iloc[45]), 79.0)
        self.assertEqual(float(ind["pivot_low_price"].iloc[84]), 74.0)

    def test_bullish_divergence_flag_conditions(self):
        ind = indicators.add_indicators(_mk(_bullish_divergence_closes()))
        flags = ind.index[ind["bullish_divergence"]].tolist()
        self.assertEqual(flags, [84])
        i = flags[0]
        self.assertLess(float(ind["pivot_low_price"].iloc[i]), 79.0)
        self.assertGreater(float(ind["pivot_low_wr"].iloc[i]),
                           float(ind["pivot_low_wr"].iloc[45]))
        self.assertLess(float(ind["pivot_low_wr"].iloc[i]), -80.0)

    def test_long_entry_fires_on_bullish_divergence(self):
        sig = signals.add_signals(indicators.add_indicators(_mk(_bullish_divergence_closes())))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [84])

    def test_bearish_divergence_flag_conditions(self):
        ind = indicators.add_indicators(_mk(_bearish_divergence_closes()))
        flags = ind.index[ind["bearish_divergence"]].tolist()
        self.assertEqual(flags, [84])
        i = flags[0]
        self.assertGreater(float(ind["pivot_high_price"].iloc[i]), 121.0)
        self.assertLess(float(ind["pivot_high_wr"].iloc[i]),
                        float(ind["pivot_high_wr"].iloc[45]))
        self.assertGreater(float(ind["pivot_high_wr"].iloc[i]), -20.0)

    def test_short_entry_fires_on_bearish_divergence(self):
        sig = signals.add_signals(indicators.add_indicators(_mk(_bearish_divergence_closes())))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [84])

    def test_long_exit_on_cross_below_minus_50(self):
        # Divergence entry at 84, recovery, then a fresh decline
        # drives %R back below -50.
        c = _bullish_divergence_closes() + [95, 90, 85, 80, 85, 90, 100] + [100.0] * 10
        sig = signals.add_signals(indicators.add_indicators(_mk(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(any(e > entries[0] for e in exits))
        e = next(x for x in exits if x > entries[0])
        self.assertLess(float(sig["williams_r"].iloc[e]), -50.0)
        self.assertGreaterEqual(float(sig["williams_r"].iloc[e - 1]), -50.0)

    def test_short_exit_on_cross_above_minus_50(self):
        c = _bearish_divergence_closes() + [105, 110, 115, 120, 115, 110, 100] + [100.0] * 10
        sig = signals.add_signals(indicators.add_indicators(_mk(c)))
        entries = sig.index[sig["short_entry"]].tolist()
        exits = sig.index[sig["short_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(any(e > entries[0] for e in exits))
        e = next(x for x in exits if x > entries[0])
        self.assertGreater(float(sig["williams_r"].iloc[e]), -50.0)
        self.assertLessEqual(float(sig["williams_r"].iloc[e - 1]), -50.0)

    def test_no_reentry_while_position_open(self):
        # Signal layer in isolation: %R pinned at -30 (no -50
        # cross, so no exit), bullish divergence flagged twice
        # while "long" — only the first may enter.
        ind = indicators.add_indicators(_rand_df(200, seed=9))
        ind["williams_r"] = -30.0
        ind["bullish_divergence"] = False
        ind["bearish_divergence"] = False
        ind.loc[100, "bullish_divergence"] = True
        ind.loc[120, "bullish_divergence"] = True
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [100])

    def test_opposite_divergence_flips_position(self):
        # Long at 100, bearish divergence at 120: exit + short
        # entry on the same bar.
        ind = indicators.add_indicators(_rand_df(200, seed=9))
        ind["williams_r"] = -30.0
        ind["bullish_divergence"] = False
        ind["bearish_divergence"] = False
        ind.loc[100, "bullish_divergence"] = True
        ind.loc[120, "bearish_divergence"] = True
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [100])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [120])
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [120])

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("williams_r", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("pivot_low_confirmed", "pivot_high_confirmed",
                    "bullish_divergence", "bearish_divergence",
                    "long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("williams_r", "atr14", "pivot_low_price",
                        "pivot_low_wr", "pivot_high_price", "pivot_high_wr"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            for col in ("pivot_low_confirmed", "pivot_high_confirmed",
                        "bullish_divergence", "bearish_divergence"):
                self.assertEqual(bool(ind_full[col].iloc[j]), bool(ind_tr[col].iloc[j]), (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_mk([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.williams_r_divergence as mod

        self.assertEqual(mod.SPEC.slug, "williams_r_divergence")
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
