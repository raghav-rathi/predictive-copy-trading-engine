"""Elliott wave-count tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elliott_wave_count import indicators, risk, signals


def _zigzag(turns, n=60, vol=100.0):
    """Frame from (bar, price) turning points, linear between turns."""
    bars = np.arange(n)
    xs = [t[0] for t in turns]
    ys = [t[1] for t in turns]
    c = np.interp(bars, xs, ys)
    o = np.concatenate([[c[0]], c[:-1]])
    h = c + 0.05
    l = c - 0.05
    v = np.full(n, vol, dtype=float)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


# Full long count: W1 100->110 @10-15, W2 low 104 @20 (60% retrace),
# W3 top 120 @30, W4 low 114 @35, W5 target 110.05+1.618*10.1=126.39,
# reached at bar 45 (close 127).
LONG_TURNS = [(5, 105), (10, 100), (15, 110), (20, 104),
              (30, 120), (35, 114), (45, 127)]
# Mirror short count (reflect around 110).
SHORT_TURNS = [(5, 115), (10, 120), (15, 110), (20, 116),
               (30, 100), (35, 106), (45, 93)]


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("swing_high", "swing_low", "atr"):
            self.assertIn(col, ind.columns)

    def test_pivots_detected_at_known_bars(self):
        ind = indicators.add_indicators(_zigzag(LONG_TURNS))
        self.assertAlmostEqual(ind["swing_low"].iloc[12], 100 - 0.05)
        self.assertAlmostEqual(ind["swing_high"].iloc[17], 110 + 0.05)
        self.assertAlmostEqual(ind["swing_low"].iloc[22], 104 - 0.05)
        self.assertAlmostEqual(ind["swing_high"].iloc[32], 120 + 0.05)
        self.assertAlmostEqual(ind["swing_low"].iloc[37], 114 - 0.05)

    def test_flat_stretch_has_no_pivots(self):
        df = _frame()
        df["c"] = df["h"] = df["l"] = 50.0
        ind = indicators.add_indicators(df)
        self.assertEqual(ind["swing_high"].notna().sum(), 0)
        self.assertEqual(ind["swing_low"].notna().sum(), 0)

    def test_warmup_nans(self):
        ind = indicators.add_indicators(_frame())
        self.assertTrue(ind["swing_high"].iloc[:4].isna().all())
        self.assertTrue(ind["atr"].iloc[:13].isna().all())
        self.assertFalse(ind["atr"].iloc[14:].isna().any())

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_state_progression_long(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(LONG_TURNS)))
        self.assertEqual(sig["ew_state"].iloc[17], 1)   # have wave 1
        self.assertEqual(sig["ew_state"].iloc[22], 2)   # armed (W2 valid)
        self.assertEqual(sig["ew_state"].iloc[24], 3)   # in wave 3
        self.assertEqual(sig["ew_state"].iloc[37], 4)   # in wave 5
        self.assertEqual(sig["ew_state"].iloc[45], 0)   # target hit, idle

    def test_wave_levels_recorded(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(LONG_TURNS)))
        self.assertAlmostEqual(sig["ew_w1_hi"].iloc[22], 110.05)
        self.assertAlmostEqual(sig["ew_w1_lo"].iloc[22], 99.95)
        self.assertAlmostEqual(sig["ew_w2"].iloc[22], 103.95)
        # 161.8% extension of wave 1 (10.1) above the wave-1 high
        self.assertAlmostEqual(sig["ew_w5_target"].iloc[37],
                               110.05 + 1.618 * 10.1, places=6)

    def test_long_entry_on_wave3_breakout(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(LONG_TURNS)))
        self.assertTrue(sig["long_entry"].iloc[24])  # close 110.4 > 110.05
        self.assertEqual(sig["long_entry"].sum(), 1)
        self.assertFalse(sig["long_entry"].iloc[23])

    def test_long_exit_on_wave5_target(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(LONG_TURNS)))
        self.assertTrue(sig["long_exit"].iloc[45])  # close 127 >= 126.39
        self.assertEqual(sig["long_exit"].sum(), 1)

    def test_short_count_mirror(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(SHORT_TURNS)))
        self.assertEqual(sig["ew_state"].iloc[22], -2)
        self.assertTrue(sig["short_entry"].iloc[24])  # close 109.6 < 109.95
        self.assertEqual(sig["short_entry"].sum(), 1)
        self.assertTrue(sig["short_exit"].iloc[45])   # close 93 <= 93.61
        self.assertEqual(sig["short_exit"].sum(), 1)

    def test_long_exit_on_overlap_invalidation(self):
        turns = [(5, 105), (10, 100), (15, 110), (20, 104),
                 (25, 112), (30, 108)]
        sig = signals.add_signals(indicators.add_indicators(_zigzag(turns)))
        self.assertTrue(sig["long_entry"].iloc[24])
        # close falls back under the wave-1 high (110.05) at bar 28
        self.assertTrue(sig["long_exit"].iloc[28])
        self.assertEqual(sig["ew_state"].iloc[28], 0)

    def test_no_entry_when_wave2_too_deep(self):
        # wave 2 retraces 110% of wave 1 -- count void
        turns = [(5, 105), (10, 100), (15, 110), (20, 99),
                 (30, 120), (40, 127)]
        sig = signals.add_signals(indicators.add_indicators(_zigzag(turns)))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_no_entry_when_wave2_too_shallow(self):
        # wave 2 retraces only 30% of wave 1 -- below the 38.2% band
        turns = [(5, 105), (10, 100), (15, 110), (20, 107), (30, 120)]
        sig = signals.add_signals(indicators.add_indicators(_zigzag(turns)))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_wave3_shortest_invalidates(self):
        # W3 only runs 112 (len 8.1) vs W1 len 10.1 -- shortest, exit
        # at the wave-4 pivot confirmation (bar 37)
        turns = [(5, 105), (10, 100), (15, 110), (20, 104),
                 (30, 112), (35, 111), (40, 113)]
        sig = signals.add_signals(indicators.add_indicators(_zigzag(turns)))
        # slower rise to the 112 top: breakout fires at bar 28
        self.assertTrue(sig["long_entry"].iloc[28])
        # wave-4 pivot (111) confirms at bar 37: no overlap, but wave 3
        # (len 8.1) is shorter than wave 1 (len 10.1) -- invalid
        self.assertTrue(sig["long_exit"].iloc[37])
        self.assertEqual(sig["ew_state"].iloc[37], 0)

    def test_wave4_overlap_via_pivot_invalidates(self):
        # W4 low pivot prints at 109, inside wave-1 territory (< 110.05)
        turns = [(5, 105), (10, 100), (15, 110), (20, 104),
                 (30, 120), (35, 109), (40, 113)]
        sig = signals.add_signals(indicators.add_indicators(_zigzag(turns)))
        self.assertTrue(sig["long_entry"].iloc[24])
        # close 109 at bar 35 is already under the wave-1 high, so the
        # close-driven invalidation fires before the pivot confirms
        self.assertTrue(sig["long_exit"].iloc[35])
        self.assertEqual(sig["ew_state"].iloc[35], 0)

    def test_no_lookahead(self):
        df = _zigzag(LONG_TURNS)
        full = signals.add_signals(indicators.add_indicators(df))
        j = 24
        trunc = signals.add_signals(
            indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertEqual(risk.WARMUP, 100)

    def test_registration(self):
        import strategies.elliott_wave_count as mod
        from strategies.registry import REGISTRY

        self.assertIn("elliott_wave_count", REGISTRY)
        self.assertIs(REGISTRY["elliott_wave_count"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "elliott_wave_count")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
