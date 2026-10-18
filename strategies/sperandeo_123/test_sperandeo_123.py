"""Victor Sperandeo 1-2-3 tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sperandeo_123 import indicators, risk, signals


def _build(mid):
    """Bars with a +-1 range around mid; pivots of l/h follow pivots of mid."""
    n = len(mid)
    o = np.concatenate([[mid[0]], mid[:-1]])
    h, l = mid + 1.0, mid - 1.0
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": mid, "v": np.full(n, 100.0)}
    )


def _bearish_123_series(bounce_slope=1.2):
    """Designed bearish 1-2-3.

    Bars 0-99: rising staircase; 5-bar pivot lows exactly on the line
    100 + 0.5*(i-10) at bars 24..94, bumps between keep the line valid.
    Bars 100-108: sharp drop -> trend-line break (point 1).
    Bars 109-116: bounce to a pivot high below the break-bar high (point 2).
    Bars 125+: decline through the interim low -> short_entry.
    """
    P = [10, 24, 38, 52, 66, 80, 94]

    def line(i):
        return 100.0 + 0.5 * (i - 10)

    n = 160
    mid = np.zeros(n)
    for i in range(100):
        if i < 10:
            e = 1.0
        elif i <= 94:
            k = max(p for p in P if p <= i)
            kn = min(p for p in P if p >= i)
            d1, d2 = i - k, kn - i
            e = 0.0 if d1 == 0 else min(0.9 * d1, 0.9 * d2, 2.0)
        else:
            e = min(0.9 * (i - 94), 2.0)
        mid[i] = line(i) + e
    for i in range(100, 109):
        mid[i] = 140.0 - 3.0 * (i - 100)
    for i in range(109, 117):
        mid[i] = mid[108] + bounce_slope * (i - 108)
    for i in range(117, 125):
        mid[i] = mid[116] - bounce_slope * (i - 116)
    for i in range(125, 160):
        mid[i] = mid[124] - 1.5 * (i - 124)
    return _build(mid)


class TestSperandeo123(unittest.TestCase):
    def test_pivot_low_hand_computed(self):
        # valley shape: strict 5-bar pivot low at bar 10
        mid = np.array([5.0 + abs(i - 10) * 1.5 for i in range(21)])
        ind = indicators.add_indicators(_build(mid))
        self.assertTrue(bool(ind["piv_low"].iloc[10]))
        self.assertFalse(bool(ind["piv_low"].iloc[9]))
        self.assertFalse(bool(ind["piv_low"].iloc[11]))
        self.assertEqual(int(ind["piv_low"].sum()), 1)

    def test_pivot_high_hand_computed(self):
        mid = np.array([10.0 + (10 - abs(i - 10)) * 1.5 for i in range(21)])
        ind = indicators.add_indicators(_build(mid))
        self.assertTrue(bool(ind["piv_high"].iloc[10]))
        self.assertEqual(int(ind["piv_high"].sum()), 1)

    def test_uptrend_line_anchors(self):
        df = _bearish_123_series()
        ind = indicators.add_indicators(df)
        low = ind["l"].to_numpy()
        piv = np.flatnonzero(ind["piv_low"].values)
        fit = signals._fit_uptrend(low, piv, 99, signals.LOOKBACK)
        self.assertIsNotNone(fit)
        ja, px_a, slope = fit
        self.assertEqual(ja, 24)  # lowest pivot low in the window
        self.assertAlmostEqual(slope, 0.5, places=6)
        # the line touches the pivot lows and never cuts through price
        for jb in (38, 52, 66, 80, 94):
            self.assertAlmostEqual(px_a + slope * (jb - ja), low[jb], places=6)

    def test_uptrend_line_never_crosses_price(self):
        # even with a gouge below the staircase, any returned line must
        # respect price between its anchors
        mid = np.zeros(60)
        P = [10, 24, 38, 52]
        for i in range(60):
            if i < 10:
                e = 1.0
            else:
                k = max(p for p in P if p <= i)
                rest = [p for p in P if p >= i]
                kn = min(rest) if rest else i
                d1, d2 = i - k, kn - i
                e = 0.0 if d1 == 0 else min(0.9 * d1, 0.9 * d2, 2.0)
            mid[i] = 100.0 + 0.5 * (i - 10) + e
        mid[30] -= 5.0  # gouge below every long candidate line
        ind = indicators.add_indicators(_build(mid))
        low = ind["l"].to_numpy()
        piv = np.flatnonzero(ind["piv_low"].values)
        fit = signals._fit_uptrend(low, piv, 55, signals.LOOKBACK)
        self.assertIsNotNone(fit)
        ja, px_a, slope = fit
        # recover the second anchor: highest pivot after ja sitting on the line
        jb = ja
        for j in piv[piv > ja]:
            if abs(low[j] - (px_a + slope * (j - ja))) < 1e-6 and j > jb:
                jb = j
        self.assertGreater(jb, ja)
        ks = np.arange(ja + 1, jb)
        self.assertTrue(bool(np.all(low[ks] >= px_a + slope * (ks - ja) - 1e-9)))
        # the gouge bar itself is not spanned by a crossing line
        self.assertFalse(ja < 30 < jb and slope > 0.4)

    def test_full_bearish_123_fires_short(self):
        sig = signals.add_signals(indicators.add_indicators(_bearish_123_series()))
        se = np.flatnonzero(sig["short_entry"].values)
        self.assertEqual(list(se), [125])
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        # nothing fires during the clean uptrend (no hallucinated reversals)
        self.assertEqual(int(sig["short_entry"].iloc[:100].sum()), 0)
        self.assertEqual(int(sig["long_entry"].iloc[:100].sum()), 0)

    def test_failed_retest_invalidates(self):
        # bounce takes out the break-bar high -> pattern dead, no entry
        df = _bearish_123_series(bounce_slope=4.0).iloc[:130]
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_bullish_mirror_fires_long(self):
        df = _bearish_123_series()
        mid = df["c"].to_numpy()
        mirror = _build(300.0 - mid)
        sig = signals.add_signals(indicators.add_indicators(mirror))
        le = np.flatnonzero(sig["long_entry"].values)
        self.assertEqual(list(le), [125])
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_exit_is_opposite_entry(self):
        sig = signals.add_signals(indicators.add_indicators(_bearish_123_series()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_no_lookahead_truncation(self):
        df = _bearish_123_series()
        full_ind = indicators.add_indicators(df)
        full_sig = signals.add_signals(full_ind)
        for j in (110, 140):
            tr_ind = indicators.add_indicators(df.iloc[: j + 1])
            tr_sig = signals.add_signals(tr_ind)
            # confirmed pivots (formation bar <= j-2) are identical
            for col in ("piv_low", "piv_high"):
                self.assertEqual(
                    bool(full_ind[col].iloc[j - 2]), bool(tr_ind[col].iloc[j - 2]),
                    (col, j),
                )
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(full_sig[col].iloc[j]), bool(tr_sig[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_bearish_123_series()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.sperandeo_123 as mod

        self.assertEqual(mod.SPEC.slug, "sperandeo_123")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 210)


if __name__ == "__main__":
    unittest.main()
