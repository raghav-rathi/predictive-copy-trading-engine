"""Harmonic Gartley tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.harmonic_gartley import indicators, risk, signals
from strategies.harmonic_gartley.indicators import _classify, zigzag_pivots


def _df(o, h, l, c, v=None):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _bullish_pivots():
    # exact-ratio bullish Gartley: XA=10, AB=6.18 (0.618), BC=4.326 (0.70),
    # CD=6.0564 (1.40xBC), AD=7.9104 (0.79104xXA, within 6% of 0.786)
    X, A, B, C, D = 100.0, 110.0, 103.82, 108.146, 102.0896
    return [(0, X, -1), (1, A, 1), (2, B, -1), (3, C, 1), (4, D, -1)]


def _bearish_pivots():
    X, A, B, C, D = 110.0, 100.0, 106.18, 101.854, 107.9104
    return [(0, X, 1), (1, A, -1), (2, B, 1), (3, C, -1), (4, D, 1)]


def _gartley_bars(anchors):
    """Build OHLC bars by linear interpolation between (bar, price) anchors.

    Interior anchors must strictly alternate local high/low. Each interior
    anchor is marked as a swing extreme so the 5-bar zigzag finds exactly
    those pivots; the lead and tail segments are gentle monotonic runs that
    produce no spurious pivots.
    """
    n = anchors[-1][0] + 1
    c = np.zeros(n)
    for (b0, p0), (b1, p1) in zip(anchors, anchors[1:]):
        c[b0 : b1 + 1] = np.linspace(p0, p1, b1 - b0 + 1)
    o = np.concatenate([[c[0]], c[:-1]])
    h = c + 0.05
    l = c - 0.05
    for k in range(1, len(anchors) - 1):
        b, p = anchors[k]
        p_prev, p_next = anchors[k - 1][1], anchors[k + 1][1]
        if p > p_prev and p > p_next:
            h[b] = p + 0.30   # swing high
        elif p < p_prev and p < p_next:
            l[b] = p - 0.30   # swing low
        else:
            raise ValueError(f"anchor {k} is not a strict local extreme")
    return _df(o, h, l, c)


def _bullish_df():
    anchors = [(0, 101.5), (20, 100.0), (40, 110.0), (60, 103.82),
               (80, 108.146), (100, 102.0896), (140, 104.0)]
    return _gartley_bars(anchors)


def _bearish_df():
    anchors = [(0, 108.5), (20, 110.0), (40, 100.0), (60, 106.18),
               (80, 101.854), (100, 107.9104), (140, 106.0)]
    return _gartley_bars(anchors)


class TestHarmonicGartley(unittest.TestCase):
    def test_classify_bullish_exact_ratios(self):
        self.assertEqual(_classify(_bullish_pivots()), "bull")

    def test_classify_bearish_exact_ratios(self):
        self.assertEqual(_classify(_bearish_pivots()), "bear")

    def test_classify_rejects_bad_ab_ratio(self):
        bad = [(0, 100.0, -1), (1, 110.0, 1), (2, 100.0, -1),  # AB/XA = 1.0
               (3, 108.146, 1), (4, 102.0896, -1)]
        self.assertIsNone(_classify(bad))

    def test_classify_rejects_bad_bc_range(self):
        bad = [(0, 100.0, -1), (1, 110.0, 1), (2, 103.82, -1),
               (3, 103.9, 1), (4, 102.0896, -1)]  # BC/AB tiny
        self.assertIsNone(_classify(bad))

    def test_classify_rejects_d_beyond_x(self):
        bad = [(0, 100.0, -1), (1, 110.0, 1), (2, 103.82, -1),
               (3, 108.146, 1), (4, 99.0, -1)]  # D < X invalid
        self.assertIsNone(_classify(bad))

    def test_classify_rejects_wrong_alternation(self):
        bad = [(0, 100.0, -1), (1, 110.0, -1), (2, 103.82, -1),
               (3, 108.146, 1), (4, 102.0896, -1)]
        self.assertIsNone(_classify(bad))

    def test_classify_tolerance_boundary(self):
        # AB/XA 6% tolerance: edge at 0.618*1.06 = 0.65508
        piv = [(0, 100.0, -1), (1, 110.0, 1), (2, 110.0 - 10.0 * 0.655, -1),
               (3, 108.146, 1), (4, 102.0896, -1)]
        self.assertEqual(_classify(piv), "bull")
        # just outside the edge -> rejected
        piv2 = [(0, 100.0, -1), (1, 110.0, 1), (2, 110.0 - 10.0 * 0.657, -1),
                (3, 108.146, 1), (4, 102.0896, -1)]
        self.assertIsNone(_classify(piv2))

    def test_zigzag_finds_exact_pivots(self):
        df = _bullish_df()
        piv = zigzag_pivots(df)
        self.assertEqual([p[0] for p in piv], [20, 40, 60, 80, 100])
        self.assertEqual([p[2] for p in piv], [-1, 1, -1, 1, -1])

    def test_full_pipeline_fires_once_on_completion(self):
        df = _bullish_df()
        ind = indicators.add_indicators(df)
        # D pivot at bar 100 confirms 5 bars later -> single PRZ print at 105
        self.assertEqual(int(ind["prz"].sum()), 1)
        fire = int(ind.index[ind["prz"] == 1][0])
        self.assertEqual(fire, 105)
        self.assertEqual(int(ind["gartley_dir"].iloc[fire]), 1)
        sig = signals.add_signals(ind)
        self.assertTrue(bool(sig["long_entry"].iloc[fire]))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertEqual(int(sig["short_entry"].sum()), 0)
        # no repeated signal after the pattern completes
        self.assertEqual(int(ind["prz"].iloc[fire + 1 :].sum()), 0)

    def test_full_pipeline_bearish(self):
        df = _bearish_df()
        ind = indicators.add_indicators(df)
        self.assertEqual(int(ind["prz"].sum()), 1)
        fire = int(ind.index[ind["prz"] == 1][0])
        self.assertEqual(int(ind["gartley_dir"].iloc[fire]), -1)
        sig = signals.add_signals(ind)
        self.assertTrue(bool(sig["short_entry"].iloc[fire]))
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_no_pattern_no_signal(self):
        # monotone drift: no zigzag pivots at all -> no signals
        n = 300
        c = 100.0 + 0.1 * np.arange(n)
        df = _df(np.concatenate([[c[0]], c[:-1]]), c + 0.5, c - 0.5, c)
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_signal_logic_exact_formulas(self):
        df = _bullish_df()
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        gdir = ind["gartley_dir"].fillna(0)
        self.assertTrue(bool((sig["long_entry"] == (gdir == 1)).all()))
        self.assertTrue(bool((sig["short_entry"] == (gdir == -1)).all()))
        self.assertTrue(bool((sig["long_exit"] == (gdir == -1)).all()))
        self.assertTrue(bool((sig["short_exit"] == (gdir == 1)).all()))

    def test_no_lookahead_truncation(self):
        df = _bullish_df()
        ind_full = indicators.add_indicators(df)
        for j in (110, 130):
            ind_tr = indicators.add_indicators(df.iloc[: j + 1])
            for col in ("prz", "gartley_dir"):
                self.assertEqual(int(ind_full[col].iloc[j]), int(ind_tr[col].iloc[j]),
                                 (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        ind = indicators.add_indicators(_bullish_df())
        sig = signals.add_signals(ind)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(ind["prz"].isna().any())
        self.assertFalse(ind["gartley_dir"].isna().any())
        self.assertTrue(set(ind["gartley_dir"].unique()) <= {1, -1, 0})

    def test_registration_imports_cleanly(self):
        import strategies.harmonic_gartley as mod

        self.assertEqual(mod.SPEC.slug, "harmonic_gartley")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertIn("gartley", mod.SPEC.source_url)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.target_atr_mult, 4.0)
        self.assertEqual(risk.RISK.max_hold_bars, 100)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
