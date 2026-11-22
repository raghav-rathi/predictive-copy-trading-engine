"""ICT inducement -> sweep -> MSS -> OTE tests. Network-free, synthetic data only.

The bullish fixture is a hand-built 46-bar path (see _bullish_path):
bars 0-19 downtrend; bar 20 displacement up (range 9.4, ATR ~1.6)
with the last down candle (bar 19) as the OB [100.5, 101.5];
bar 24 a swing low at 103.0 (confirmed at bar 27, above the OB
top); bar 28 sweeps through it (close 101, into the OB zone);
bar 31 closes above the structure high 106.8 (MSS) on a small-range
bar; bar 32 is a
displacement bar (range 9.0) leaving an FVG (low 106.0 > high two
bars earlier 105.5); leg [100.5, 115] gives OTE 104.7775; bar 35
touches it (low 104.5) and fires the long.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ict_inducement_sweep import indicators, risk, signals


def _bullish_path():
    """Return (o, h, l, c) lists for the bullish fixture, 46 bars."""
    o, h, l, c = [], [], [], []
    # Bars 0-19: downtrend, closes 120..101, range 1.0 bars.
    for k in range(20):
        ck = 120.0 - k
        c.append(ck)
        o.append(ck + 1.0)
        h.append(ck + 0.5)
        l.append(ck - 0.5)
    # Bar 20: displacement up. Bar 19 is the OB candle [100.5, 101.5].
    o.append(101.0); c.append(109.0); h.append(110.0); l.append(100.6)
    # Bars 21-23: pullback.
    for ok, ck, hk, lk in [(109.0, 107.0, 109.5, 106.5),
                           (107.0, 105.0, 107.5, 104.8),
                           (105.0, 104.5, 105.5, 104.0)]:
        o.append(ok); c.append(ck); h.append(hk); l.append(lk)
    # Bar 24: inducement swing low 103.0 (confirms at bar 27).
    o.append(104.5); c.append(104.0); h.append(105.0); l.append(103.0)
    # Bars 25-27: recovery.
    for ok, ck, hk, lk in [(104.0, 105.0, 105.5, 103.8),
                           (105.0, 106.0, 106.5, 104.2),
                           (106.0, 105.5, 106.8, 104.8)]:
        o.append(ok); c.append(ck); h.append(hk); l.append(lk)
    # Bar 28: sweep (close 101 < inducement 103, into OB zone).
    o.append(105.5); c.append(101.0); h.append(105.5); l.append(100.5)
    # Bars 29-31: recovery; bar 31 closes 107.0 > structure high 106.8
    # (MSS) on a small-range bar, so it is NOT itself the displacement
    # bar — the displacement comes at bar 32 (sequential path).
    for ok, ck, hk, lk in [(101.0, 103.0, 103.5, 100.8),
                           (103.0, 105.0, 105.5, 102.5),
                           (105.0, 107.0, 107.2, 104.5)]:
        o.append(ok); c.append(ck); h.append(hk); l.append(lk)
    # Bar 32: displacement + FVG (low 106.0 > high two bars back 105.5).
    o.append(107.5); c.append(114.0); h.append(115.0); l.append(106.0)
    # Bars 33-35: retrace; bar 35 touches OTE 104.7775 (low 104.5).
    for ok, ck, hk, lk in [(114.0, 110.0, 114.5, 109.0),
                           (110.0, 106.0, 110.5, 105.5),
                           (106.0, 105.0, 106.5, 104.5)]:
        o.append(ok); c.append(ck); h.append(hk); l.append(lk)
    # Bars 36-45: gentle drift up, no displacement.
    prev = 105.0
    for k in range(10):
        ck = prev + 0.5
        o.append(prev); c.append(ck); h.append(ck + 0.5); l.append(ck - 0.5)
        prev = ck
    return o, h, l, c


def _frame_from_ohlc(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.full(n, 100.0)})


def _random_walk_frame(n=500, seed=7):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.005, n)))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _mirror(o, h, l, c):
    """Mirror a path around 200 -> the bearish version of the same bars."""
    return ([200.0 - x for x in o], [200.0 - x for x in l],
            [200.0 - x for x in h], [200.0 - x for x in c])


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("ict_dir", "ict_ote_level", "ict_ob_lo", "ict_ob_hi", "atr"):
            self.assertIn(col, ind.columns)

    def test_bullish_sequence_fires_at_ote(self):
        o, h, l, c = _bullish_path()
        ind = indicators.add_indicators(_frame_from_ohlc(o, h, l, c))
        fires = np.where(ind["ict_dir"] == 1)[0]
        self.assertListEqual([int(x) for x in fires], [35])
        # Leg [100.5, 115]: OTE = 115 - 0.705 * 14.5 = 104.7775.
        self.assertAlmostEqual(float(ind["ict_ote_level"].iloc[35]),
                               104.7775, places=4)
        self.assertAlmostEqual(float(ind["ict_ob_lo"].iloc[35]), 100.5,
                               places=6)
        self.assertAlmostEqual(float(ind["ict_ob_hi"].iloc[35]), 101.5,
                               places=6)

    def test_bearish_mirror_fires(self):
        o, h, l, c = _mirror(*_bullish_path())
        ind = indicators.add_indicators(_frame_from_ohlc(o, h, l, c))
        fires = np.where(ind["ict_dir"] == -1)[0]
        self.assertListEqual([int(x) for x in fires], [35])
        # Leg [85, 99.5]: OTE = 85 + 0.705 * 14.5 = 95.2225.
        self.assertAlmostEqual(float(ind["ict_ote_level"].iloc[35]),
                               95.2225, places=4)

    def test_mss_bar_can_be_the_displacement_bar(self):
        # Merged path: bar 31 breaks structure (close 110 > 106.8) on
        # a displacement bar (range 6.5) leaving an FVG (low 104.5 >
        # high two bars back 103.5), so MSS + displacement complete
        # in one bar. Leg [100.5, 111] gives OTE 103.5975; bar 34
        # touches it (low 103.5) and fires.
        o, h, l, c = _bullish_path()
        o[31] = 105.0; c[31] = 110.0; h[31] = 111.0; l[31] = 104.5
        o[32] = 110.0; c[32] = 107.0; h[32] = 110.5; l[32] = 106.0
        o[33] = 107.0; c[33] = 105.0; h[33] = 107.5; l[33] = 104.5
        o[34] = 105.0; c[34] = 104.0; h[34] = 105.5; l[34] = 103.5
        ind = indicators.add_indicators(_frame_from_ohlc(o, h, l, c))
        fires = np.where(ind["ict_dir"] == 1)[0]
        self.assertListEqual([int(x) for x in fires], [34])
        self.assertAlmostEqual(float(ind["ict_ote_level"].iloc[34]),
                               103.5975, places=4)

    def test_no_fire_without_sweep(self):
        # Bar 28 closes 104 (above the 103 inducement): no sweep, no fire.
        o, h, l, c = _bullish_path()
        c[28] = 104.0
        o[29] = 104.0
        ind = indicators.add_indicators(_frame_from_ohlc(o, h, l, c))
        self.assertFalse((ind["ict_dir"] != 0).any())

    def test_no_fire_without_retracement(self):
        # After the displacement leg (bar 32), price stays above the OTE
        # level for 30 bars: the setup expires, no entry.
        o, h, l, c = _bullish_path()
        o, h, l, c = o[:33], h[:33], l[:33], c[:33]
        for _ in range(30):
            o.append(114.0); c.append(112.0); h.append(114.5); l.append(111.0)
        ind = indicators.add_indicators(_frame_from_ohlc(o, h, l, c))
        self.assertFalse((ind["ict_dir"] != 0).any())

    def test_poi_violation_drops_setup(self):
        # Deep sweep (bar 28 low 94) puts the OTE level (100.195) below
        # the OB low (100.5). Bar 33 then closes 100.4 — below the OB
        # low, above the OTE level — so the POI has failed and the
        # setup is dropped; the later touch of the OTE level must not fire.
        o, h, l, c = _bullish_path()
        o[28] = 105.5; c[28] = 95.0; h[28] = 105.5; l[28] = 94.0
        o[33] = 114.0; c[33] = 100.4; h[33] = 114.5; l[33] = 100.3
        o[34] = 100.4; c[34] = 99.0; h[34] = 101.0; l[34] = 98.5
        ind = indicators.add_indicators(_frame_from_ohlc(o, h, l, c))
        self.assertFalse((ind["ict_dir"] != 0).any())

    def test_no_fire_without_displacement(self):
        # Flat random walk: displacement bars are rare, the full
        # sequence rarer still. Bound is generous (<= 5 across 10
        # walks) so the test asserts rarity, not an exact count.
        total = 0
        for seed in range(10):
            ind = indicators.add_indicators(_random_walk_frame(seed=seed))
            total += int((ind["ict_dir"] != 0).sum())
        self.assertLessEqual(total, 5)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        full = indicators.add_indicators(df)
        short = indicators.add_indicators(df.iloc[:200])
        pd.testing.assert_series_equal(
            full["ict_dir"].iloc[:200].reset_index(drop=True),
            short["ict_dir"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_bullish_entry_maps_to_long(self):
        o, h, l, c = _bullish_path()
        sig = signals.add_signals(
            indicators.add_indicators(_frame_from_ohlc(o, h, l, c)))
        self.assertTrue(sig["long_entry"].iloc[35])
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertFalse(sig["short_entry"].any())

    def test_bearish_entry_maps_to_short(self):
        o, h, l, c = _mirror(*_bullish_path())
        sig = signals.add_signals(
            indicators.add_indicators(_frame_from_ohlc(o, h, l, c)))
        self.assertTrue(sig["short_entry"].iloc[35])
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertFalse(sig["long_entry"].any())

    def test_no_signal_exits(self):
        # Trade management is the harness stop/target/max-hold.
        o, h, l, c = _bullish_path()
        sig = signals.add_signals(
            indicators.add_indicators(_frame_from_ohlc(o, h, l, c)))
        self.assertFalse(sig["long_exit"].any())
        self.assertFalse(sig["short_exit"].any())


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertEqual(r.target_atr_mult, 4.0)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 100)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
