"""Wyckoff distribution tests. Network-free, synthetic data only.

Base series: bars 0-119 advance linearly 100 -> 110 (so the
advance gate is true from bar 120 on), bars 120-129 flat at
110. A UTAD pokes to 115 at bar 130 and reclaims the same
bar; SOW fires at 135 (close 106.5 below the ~108.1 range
midpoint); LPSY fires at 136 (high 108.5 holds below the
UTAD high 115, close 107 below the range high).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wyckoff_distribution import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC


def _df(o, h, l, c, v=None):
    o = np.asarray(o, float)
    h = np.asarray(h, float)
    l = np.asarray(l, float)
    c = np.asarray(c, float)
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _base_arrays(n=200):
    """Advance 100 -> 110 over bars 0-119, flat 110 after."""
    c = np.full(n, 110.0)
    c[:120] = 100.0 + 10.0 * np.arange(120) / 119.0
    h = c + 0.2
    l = c - 0.2
    o = c.copy()
    v = np.full(n, 100.0)
    return o, h, l, c, v


def _full_series():
    o, h, l, c, v = _base_arrays(146)  # truncated at the exit bar:
    # bar 145's poke (high 116.5) would otherwise start a second
    # UTAD reclaimed at bar 146 -- genuine per the rules, but
    # it is not what this series is testing.
    # Bar 130: UTAD poke to 115, close reclaims to 109.5.
    o[130], h[130], l[130], c[130] = 110.0, 115.0, 109.0, 109.5
    # Bars 131-134: flat 110.
    # Bar 135: SOW -- close 106.5 below the ~108.1 midpoint.
    o[135], h[135], l[135], c[135], v[135] = 110.0, 110.0, 106.0, 106.5, 150.0
    # Bar 136: LPSY -- high 108.5 holds below UTAD high 115.
    o[136], h[136], l[136], c[136] = 108.0, 108.5, 106.0, 107.0
    # Bars 137-144: flat 107.
    c[137:145] = 107.0
    h[137:145] = 107.2
    l[137:145] = 106.8
    o[137:145] = 107.0
    # Bar 145: close 116 breaks the UTAD high 115 -> exit.
    o[145], h[145], l[145], c[145] = 107.0, 116.5, 106.0, 116.0
    return _df(o, h, l, c, v)


class TestWyckoffDistribution(unittest.TestCase):
    def test_range_high_low_hand_computed(self):
        ind = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertTrue(np.isnan(ind["range_high_120"].iloc[118]))
        self.assertAlmostEqual(float(ind["range_high_120"].iloc[119]), 100.2, places=6)
        self.assertAlmostEqual(float(ind["range_low_120"].iloc[119]), 99.8, places=6)

    def test_advance_gate(self):
        ind = indicators.add_indicators(_df(*_base_arrays(200)))
        # c[0]=100 <= 0.95 * c[120]=110 -> gate true at 120.
        self.assertTrue(bool(ind["advance_gate"].iloc[120]))
        # Flat series: no 5% advance anywhere.
        ind_flat = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertFalse(bool(ind_flat["advance_gate"].any()))

    def test_climax_flag(self):
        # Flat 110, then a buying-climax bar: range 6 (> 2x
        # ATR ~0.4), close 111.5 in the upper 25% of [106,
        # 112], volume 200 (> 1.5x vol-SMA 100).
        o, h, l, c, v = _base_arrays(200)
        c[:] = 110.0
        h[:] = 110.2
        l[:] = 109.8
        o[150], h[150], l[150], c[150], v[150] = 110.0, 112.0, 106.0, 111.5, 200.0
        ind = indicators.add_indicators(_df(o, h, l, c, v))
        self.assertEqual(ind.index[ind["climax"]].tolist(), [150])
        # And no UTAD: the advance gate is false on a flat series.
        self.assertFalse(bool(ind["utad"].any()))

    def test_utad_sow_lpsy_fire(self):
        ind = indicators.add_indicators(_full_series())
        self.assertEqual(ind.index[ind["utad"]].tolist(), [130])
        self.assertAlmostEqual(float(ind["utad_high"].iloc[130]), 115.0, places=6)
        self.assertAlmostEqual(float(ind["utad_high"].iloc[140]), 115.0, places=6)
        self.assertEqual(ind.index[ind["sow"]].tolist(), [135])
        self.assertEqual(ind.index[ind["lpsy"]].tolist(), [136])

    def test_entries_on_utad_and_lpsy(self):
        sig = signals.add_signals(indicators.add_indicators(_full_series()))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [130, 136])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exit_above_utad_high(self):
        sig = signals.add_signals(indicators.add_indicators(_full_series()))
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [145])

    def test_exit_below_range_projection(self):
        # UTAD at 130 (range high 115, range low ~100.7 ->
        # projection ~86.4); a close of 84 at bar 140 exits.
        o, h, l, c, v = _base_arrays(200)
        o[130], h[130], l[130], c[130] = 110.0, 115.0, 109.0, 109.5
        # Volume stays 100 on the projection bar so it is not
        # also an SOW (no LPSY re-entry at bar 141 to muddy the
        # exit assertion).
        o[140], h[140], l[140], c[140] = 90.0, 90.0, 83.0, 84.0
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [130])
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [140])

    def test_no_utad_without_advance_gate(self):
        # Flat series, then a poke to 115 with a reclaiming
        # close: no 5% advance, so no UTAD and no entry.
        o, h, l, c, v = _base_arrays(200)
        c[:] = 110.0
        h[:] = 110.2
        l[:] = 109.8
        o[150], h[150], l[150], c[150] = 110.0, 115.0, 109.0, 109.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["utad"].any()))

    def test_no_utad_without_reclaim_within_3_bars(self):
        # Poke at 130 (high 115, close 111 -- no reclaim),
        # closes stay above the poke level 110.2 through bar
        # 133; the reclaim at bar 134 is 4 bars late: no UTAD.
        o, h, l, c, v = _base_arrays(200)
        o[130], h[130], l[130], c[130] = 110.0, 115.0, 109.0, 111.0
        for i in (131, 132, 133):
            o[i], h[i], l[i], c[i] = 111.0, 111.2, 110.8, 111.0
        o[134], h[134], l[134], c[134] = 111.0, 110.5, 109.0, 109.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertFalse(bool(sig["utad"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_sow_without_utad(self):
        # A wide down bar closing below the midpoint, but no
        # UTAD in the last 48 bars: no SOW, no LPSY, no entry.
        o, h, l, c, v = _base_arrays(200)
        o[150], h[150], l[150], c[150], v[150] = 110.0, 110.0, 105.5, 106.0, 150.0
        ind = indicators.add_indicators(_df(o, h, l, c, v))
        self.assertFalse(bool(ind["sow"].any()))
        self.assertFalse(bool(ind["lpsy"].any()))

    def test_lpsy_expires_24_bars_after_sow(self):
        # UTAD 130, SOW 135, then bars 136-159 hold exactly
        # at the UTAD high (high 115.0, not below it -- no
        # LPSY), and the first qualifying pullback bar at 160
        # is 25 bars after the SOW: the LPSY window has expired.
        o, h, l, c, v = _base_arrays(200)
        o[130], h[130], l[130], c[130] = 110.0, 115.0, 109.0, 109.5
        o[135], h[135], l[135], c[135], v[135] = 110.0, 110.0, 106.0, 106.5, 150.0
        for i in range(136, 160):
            o[i], h[i], l[i], c[i] = 107.0, 115.0, 106.0, 107.0
        o[160], h[160], l[160], c[160] = 108.0, 108.5, 106.0, 107.0
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [130])
        self.assertFalse(bool(sig["lpsy"].any()))

    def test_short_only_no_longs(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["long_exit"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("range_high_120", "range_low_120", "atr14", "vol_sma20"):
            self.assertFalse(sig[col].iloc[300:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "advance_gate", "climax", "utad", "sow", "lpsy"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (200, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("range_high_120", "range_low_120", "advance_gate",
                        "atr14", "vol_sma20", "climax", "utad",
                        "utad_high", "sow", "lpsy"):
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
        import strategies.wyckoff_distribution as mod

        self.assertEqual(mod.SPEC.slug, "wyckoff_distribution")
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
        self.assertFalse(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 150)


if __name__ == "__main__":
    unittest.main()
