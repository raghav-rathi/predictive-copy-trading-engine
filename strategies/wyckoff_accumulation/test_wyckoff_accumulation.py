"""Wyckoff accumulation tests. Network-free, synthetic data only.

Base series: bars 0-119 decline linearly 110 -> 100 (so the
decline gate is true from bar 120 on), bars 120-129 flat at
100. A spring dips to 95 at bar 130 and reclaims the same
bar; SOS fires at 135 (close 103.5 above the ~102.1 range
midpoint); LPS fires at 136 (low 97 holds above the spring
low 95, close 101 above the range low).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wyckoff_accumulation import indicators, risk, signals

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
    """Decline 110 -> 100 over bars 0-119, flat 100 after."""
    c = np.full(n, 100.0)
    c[:120] = 110.0 - 10.0 * np.arange(120) / 119.0
    h = c + 0.2
    l = c - 0.2
    o = c.copy()
    v = np.full(n, 100.0)
    return o, h, l, c, v


def _full_series():
    o, h, l, c, v = _base_arrays(146)  # truncated at the exit bar:
    # bar 145's dip (low 93.5) would otherwise start a second
    # spring reclaimed at bar 146 -- genuine per the rules, but
    # it is not what this series is testing.
    # Bar 130: spring dip to 95, close reclaims to 100.5.
    o[130], h[130], l[130], c[130] = 100.0, 101.0, 95.0, 100.5
    # Bars 131-134: flat 100.
    # Bar 135: SOS -- close 103.5 above the ~102.1 midpoint.
    o[135], h[135], l[135], c[135], v[135] = 100.0, 104.0, 100.0, 103.5, 150.0
    # Bar 136: LPS -- low 97 holds above spring low 95.
    o[136], h[136], l[136], c[136] = 102.0, 102.5, 97.0, 101.0
    # Bars 137-144: flat 101.
    c[137:145] = 101.0
    h[137:145] = 101.2
    l[137:145] = 100.8
    o[137:145] = 101.0
    # Bar 145: close 94 breaks the spring low 95 -> exit.
    o[145], h[145], l[145], c[145] = 101.0, 94.5, 93.5, 94.0
    return _df(o, h, l, c, v)


class TestWyckoffAccumulation(unittest.TestCase):
    def test_range_high_low_hand_computed(self):
        ind = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertTrue(np.isnan(ind["range_high_120"].iloc[118]))
        self.assertAlmostEqual(float(ind["range_high_120"].iloc[119]), 100.2, places=6)
        self.assertAlmostEqual(float(ind["range_low_120"].iloc[119]), 99.8, places=6)

    def test_decline_gate(self):
        ind = indicators.add_indicators(_df(*_base_arrays(200)))
        # c[0]=110 >= 1.05 * c[120]=100 -> gate true at 120.
        self.assertTrue(bool(ind["decline_gate"].iloc[120]))
        # Flat series: no 5% decline anywhere.
        ind_flat = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertFalse(bool(ind_flat["decline_gate"].any()))

    def test_climax_flag(self):
        # Flat 100, then a climax bar: range 6 (> 2x ATR ~0.4),
        # close 96.5 in the lower 25% of [96, 102], volume 200
        # (> 1.5x vol-SMA 100).
        o, h, l, c, v = _base_arrays(200)
        c[:] = 100.0
        h[:] = 100.2
        l[:] = 99.8
        o[150], h[150], l[150], c[150], v[150] = 100.0, 102.0, 96.0, 96.5, 200.0
        ind = indicators.add_indicators(_df(o, h, l, c, v))
        self.assertEqual(ind.index[ind["climax"]].tolist(), [150])
        # And no spring: the decline gate is false on a flat series.
        self.assertFalse(bool(ind["spring"].any()))

    def test_spring_sos_lps_fire(self):
        ind = indicators.add_indicators(_full_series())
        self.assertEqual(ind.index[ind["spring"]].tolist(), [130])
        self.assertAlmostEqual(float(ind["spring_low"].iloc[130]), 95.0, places=6)
        self.assertAlmostEqual(float(ind["spring_low"].iloc[140]), 95.0, places=6)
        self.assertEqual(ind.index[ind["sos"]].tolist(), [135])
        self.assertEqual(ind.index[ind["lps"]].tolist(), [136])

    def test_entries_on_spring_and_lps(self):
        sig = signals.add_signals(indicators.add_indicators(_full_series()))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [130, 136])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_exit_below_spring_low(self):
        sig = signals.add_signals(indicators.add_indicators(_full_series()))
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [145])

    def test_exit_above_range_projection(self):
        # Spring at 130 (range high ~109.3, range low 95 ->
        # projection ~123.6); a close of 126 at bar 140 exits.
        o, h, l, c, v = _base_arrays(200)
        o[130], h[130], l[130], c[130] = 100.0, 101.0, 95.0, 100.5
        # Volume stays 100 on the projection bar so it is not
        # also an SOS (no LPS re-entry at bar 141 to muddy the
        # exit assertion).
        o[140], h[140], l[140], c[140] = 110.0, 127.0, 110.0, 126.0
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [130])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [140])

    def test_no_spring_without_decline_gate(self):
        # Flat series, then a dip to 95 with a reclaiming
        # close: no 5% decline, so no spring and no entry.
        o, h, l, c, v = _base_arrays(200)
        c[:] = 100.0
        h[:] = 100.2
        l[:] = 99.8
        o[150], h[150], l[150], c[150] = 100.0, 101.0, 95.0, 100.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["spring"].any()))

    def test_no_spring_without_reclaim_within_3_bars(self):
        # Dip at 130 (low 95, close 96 -- no reclaim), closes
        # stay below the dip level 99.8 through bar 133; the
        # reclaim at bar 134 is 4 bars late: no spring.
        o, h, l, c, v = _base_arrays(200)
        o[130], h[130], l[130], c[130] = 100.0, 101.0, 95.0, 96.0
        for i in (131, 132, 133):
            o[i], h[i], l[i], c[i] = 96.0, 97.0, 96.0, 96.5
        o[134], h[134], l[134], c[134] = 96.5, 101.0, 99.0, 100.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertFalse(bool(sig["spring"].any()))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_sos_without_spring(self):
        # A wide up bar closing above the midpoint, but no
        # spring in the last 48 bars: no SOS, no LPS, no entry.
        o, h, l, c, v = _base_arrays(200)
        o[150], h[150], l[150], c[150], v[150] = 100.0, 104.0, 100.0, 103.5, 150.0
        ind = indicators.add_indicators(_df(o, h, l, c, v))
        self.assertFalse(bool(ind["sos"].any()))
        self.assertFalse(bool(ind["lps"].any()))

    def test_lps_expires_24_bars_after_sos(self):
        # Spring 130, SOS 135, then bars 136-159 hold exactly
        # at the spring low (low 95.0, not above it -- no LPS),
        # and the first qualifying pullback bar at 160 is 25
        # bars after the SOS: the LPS window has expired.
        o, h, l, c, v = _base_arrays(200)
        o[130], h[130], l[130], c[130] = 100.0, 101.0, 95.0, 100.5
        o[135], h[135], l[135], c[135], v[135] = 100.0, 104.0, 100.0, 103.5, 150.0
        for i in range(136, 160):
            o[i], h[i], l[i], c[i] = 101.0, 101.2, 95.0, 101.0
        o[160], h[160], l[160], c[160] = 102.0, 102.5, 97.0, 101.0
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c, v)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [130])
        self.assertFalse(bool(sig["lps"].any()))

    def test_long_only_no_shorts(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("range_high_120", "range_low_120", "atr14", "vol_sma20"):
            self.assertFalse(sig[col].iloc[300:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "decline_gate", "climax", "spring", "sos", "lps"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (200, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("range_high_120", "range_low_120", "decline_gate",
                        "atr14", "vol_sma20", "climax", "spring",
                        "spring_low", "sos", "lps"):
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
        import strategies.wyckoff_accumulation as mod

        self.assertEqual(mod.SPEC.slug, "wyckoff_accumulation")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 240)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 200)


if __name__ == "__main__":
    unittest.main()
