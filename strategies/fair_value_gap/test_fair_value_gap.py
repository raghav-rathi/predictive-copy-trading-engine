"""Fair Value Gap tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fair_value_gap import indicators, signals, risk
from strategies.fair_value_gap import SPEC


def _ohlc(bars):
    """Build an OHLCV frame from explicit (o, h, l, c) tuples."""
    o, h, l, c = (np.array([b[i] for b in bars], dtype=float) for i in range(4))
    n = len(bars)
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _chop(n=40, px=100.0, rng=0.1):
    """Quiet chop: range 0.2 bars so ATR(14) settles at ~0.2."""
    return [(px, px + rng, px - rng, px)] * n


def _bull_gap_frame(extra=()):
    # bars 40,41,42: chop / impulsive-up displacement / gap formation.
    # ATR(14) ~ 0.2 -> displacement threshold 1.5*0.2 = 0.3; bar 41 range 2.2.
    bars = _chop(40)
    bars += [(100, 100.1, 99.9, 100)]      # 40 (i-2)
    bars += [(100, 102.2, 100.0, 102)]     # 41 (i-1) displacement
    bars += [(102, 103.2, 101.0, 103)]     # 42 (i) gap -> zone [100.1, 101.0]
    bars += list(extra)
    return _ohlc(bars)


def _bear_gap_frame(extra=()):
    bars = _chop(40)
    bars += [(100, 100.1, 99.9, 100)]      # 40 (i-2)
    bars += [(100, 100.1, 97.8, 98)]       # 41 (i-1) displacement, range 2.3
    bars += [(98, 98.5, 97.0, 97.2)]       # 42 (i) gap -> zone [98.5, 99.9]
    bars += list(extra)
    return _ohlc(bars)


def _random_frame(n=600, seed=11):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, n)))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.003, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.003, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def test_zone_columns_present(self):
        ind = indicators.add_indicators(_bull_gap_frame())
        for col in ("fvg_bull_low", "fvg_bull_high", "fvg_bear_low",
                    "fvg_bear_high", "atr"):
            self.assertIn(col, ind.columns)

    def test_bullish_gap_detected_at_formation_bar(self):
        ind = indicators.add_indicators(_bull_gap_frame())
        self.assertAlmostEqual(ind["fvg_bull_low"].iloc[42], 100.1)
        self.assertAlmostEqual(ind["fvg_bull_high"].iloc[42], 101.0)
        # bearish columns stay empty for a bullish gap
        self.assertTrue(ind["fvg_bear_low"].iloc[42] != ind["fvg_bear_low"].iloc[42])

    def test_no_zone_before_formation_bar_closes(self):
        # The gap is unknowable until bar i closes: all earlier rows NaN.
        ind = indicators.add_indicators(_bull_gap_frame())
        self.assertTrue(ind["fvg_bull_low"].iloc[:42].isna().all())
        self.assertTrue(ind["fvg_bull_high"].iloc[:42].isna().all())

    def test_non_impulsive_middle_candle_rejected(self):
        # Price gap exists (l[42]=101.5 > h[40]=100.1) but the middle
        # candle's range (0.1) is below 1.5xATR(~0.2) -> no FVG.
        bars = _chop(40)
        bars += [(100, 100.1, 99.9, 100)]
        bars += [(100, 100.05, 99.95, 100)]   # range 0.1, not impulsive
        bars += [(101.5, 101.7, 101.5, 101.6)]
        ind = indicators.add_indicators(_ohlc(bars))
        self.assertTrue(ind["fvg_bull_low"].iloc[42] != ind["fvg_bull_low"].iloc[42])
        self.assertTrue(ind["fvg_bear_low"].iloc[42] != ind["fvg_bear_low"].iloc[42])

    def test_mitigation_kills_bullish_zone(self):
        # bar 43 trades below fvg_low (100.1): zone dies and stays dead.
        df = _bull_gap_frame(extra=[(101.2, 101.3, 99.5, 100.6),
                                    (100.6, 100.8, 100.5, 100.7)])
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["fvg_bull_low"].iloc[43] != ind["fvg_bull_low"].iloc[43])
        self.assertTrue(ind["fvg_bull_low"].iloc[44] != ind["fvg_bull_low"].iloc[44])

    def test_bearish_mirror_detection_and_mitigation(self):
        df = _bear_gap_frame(extra=[(98.0, 98.4, 97.6, 98.0),
                                    (98.0, 100.5, 97.8, 100.2)])
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["fvg_bear_low"].iloc[42], 98.5)
        self.assertAlmostEqual(ind["fvg_bear_high"].iloc[42], 99.9)
        # bar 44 trades above fvg_high (99.9): bearish zone dies
        self.assertTrue(ind["fvg_bear_low"].iloc[44] != ind["fvg_bear_low"].iloc[44])

    def test_only_most_recent_zone_kept(self):
        # A second bullish gap later replaces the first, unmitigated zone.
        extra = [(101.0, 101.1, 100.9, 101.0),      # 43: quiet chop
                 (101.0, 105.5, 100.5, 105.0),      # 44: displacement, range 5
                 (105.0, 106.2, 104.6, 106.0)]     # 45: gap -> zone [101.1, 104.6]
        ind = indicators.add_indicators(_bull_gap_frame(extra=extra))
        self.assertAlmostEqual(ind["fvg_bull_low"].iloc[45], 101.1)
        self.assertAlmostEqual(ind["fvg_bull_high"].iloc[45], 104.6)

    def test_does_not_mutate_input(self):
        df = _bull_gap_frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def _sig(self, df):
        return signals.add_signals(indicators.add_indicators(df))

    def test_long_entry_on_dip_and_rejection(self):
        # bar 43 dips into the gap (l=100.5 < 101.0) and closes back
        # above it (c=101.3 > 101.0) -> long_entry True.
        df = _bull_gap_frame(extra=[(100.9, 101.4, 100.5, 101.3)])
        sig = self._sig(df)
        self.assertTrue(sig["long_entry"].iloc[43])

    def test_no_entry_on_formation_bar(self):
        # On the formation bar l[i] == fvg_high identically: the strict
        # inequality excludes it, requiring a genuine later-bar retest.
        sig = self._sig(_bull_gap_frame())
        self.assertFalse(sig["long_entry"].iloc[42])

    def test_no_entry_without_rejection_close(self):
        # Dips into the gap but closes INSIDE it (c=100.8 < 101.0) -> no entry.
        df = _bull_gap_frame(extra=[(101.2, 101.3, 100.5, 100.8)])
        sig = self._sig(df)
        self.assertFalse(sig["long_entry"].iloc[43])
        # ...and the zone survived (no mitigation on this bar)
        self.assertFalse(sig["long_exit"].iloc[43])

    def test_short_entry_mirror(self):
        # bar 43 spikes into the bearish gap (h=99.2 > 98.5) and closes
        # back below it (c=98.2 < 98.5) -> short_entry True.
        df = _bear_gap_frame(extra=[(98.6, 99.2, 98.4, 98.2)])
        sig = self._sig(df)
        self.assertTrue(sig["short_entry"].iloc[43])
        self.assertFalse(sig["short_entry"].iloc[42])  # not on formation bar

    def test_long_exit_on_mitigation(self):
        df = _bull_gap_frame(extra=[(101.2, 101.3, 99.5, 100.6)])
        sig = self._sig(df)
        self.assertTrue(sig["long_exit"].iloc[43])

    def test_short_exit_on_mitigation(self):
        df = _bear_gap_frame(extra=[(98.0, 100.5, 97.8, 100.2)])
        sig = self._sig(df)
        self.assertTrue(sig["short_exit"].iloc[43])

    def test_opposite_signal_exits_position(self):
        # Bull zone [100.1, 101.0] alive; bar 44 births a bearish gap
        # [100.8, 101.0]; bar 45 retests the bearish gap (short_entry)
        # without mitigating the bullish zone -> long_exit fires via the
        # opposite signal, not via mitigation.
        extra = [(103, 104, 101, 101),          # 43: impulsive down, bull zone survives
                 (101.3, 100.8, 100.4, 100.6),  # 44: bearish gap born [100.8, 101.0]
                 (100.6, 100.95, 100.2, 100.5)]  # 45: bearish retest
        sig = self._sig(_bull_gap_frame(extra=extra))
        self.assertTrue(sig["short_entry"].iloc[45])
        self.assertTrue(sig["long_exit"].iloc[45])
        self.assertFalse(sig["long_entry"].iloc[45])
        self.assertFalse(sig["short_exit"].iloc[45])

    def test_signal_columns_boolean_no_nan(self):
        sig = self._sig(_random_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(pd.api.types.is_bool_dtype(sig[col]), col)
            self.assertFalse(sig[col].isna().any(), col)


class TestRiskAndSpec(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertEqual(r.fee_rate, 0.00045)
        self.assertEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 80)

    def test_spec_registered(self):
        self.assertEqual(SPEC.slug, "fair_value_gap")
        self.assertEqual(SPEC.warmup_bars, 80)


if __name__ == "__main__":
    unittest.main()
