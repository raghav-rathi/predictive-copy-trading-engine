"""Dow Theory trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dow_theory_trend import indicators, risk, signals


def _zigzag(turns, n=60, vol=100.0, vol_spikes=None):
    """Frame from (bar, price) turning points, linear between turns.

    Turns are >= 5 bars apart so each is a strict 5-bar pivot; the
    lead-in is flat at the first turn's price.  h/l hug the close.
    """
    bars = np.arange(n)
    xs = [t[0] for t in turns]
    ys = [t[1] for t in turns]
    c = np.interp(bars, xs, ys)
    o = np.concatenate([[c[0]], c[:-1]])
    h = c + 0.05
    l = c - 0.05
    v = np.full(n, vol, dtype=float)
    if vol_spikes:
        for b, vv in vol_spikes.items():
            v[b] = vv
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


# Uptrend frame: L0=100@10, H1=110@15, L1=105@20, H2=115@25,
# pullback to 110@30 (50% of the 115-105 leg), reclaim 115 -> 116@35.
UP_TURNS = [(5, 110), (10, 100), (15, 110), (20, 105),
            (25, 115), (30, 110), (35, 116)]
# Mirror downtrend frame.
DN_TURNS = [(5, 110), (10, 120), (15, 110), (20, 115),
            (25, 105), (30, 110), (35, 104)]


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("swing_high", "swing_low", "vol_ratio", "atr"):
            self.assertIn(col, ind.columns)

    def test_pivots_detected_at_known_bars(self):
        ind = indicators.add_indicators(_zigzag(UP_TURNS))
        # pivots confirm 2 bars after the turn bar, at the turn price
        self.assertAlmostEqual(ind["swing_low"].iloc[12], 100 - 0.05)
        self.assertAlmostEqual(ind["swing_high"].iloc[17], 110 + 0.05)
        self.assertAlmostEqual(ind["swing_low"].iloc[22], 105 - 0.05)
        self.assertAlmostEqual(ind["swing_high"].iloc[27], 115 + 0.05)
        self.assertAlmostEqual(ind["swing_low"].iloc[32], 110 - 0.05)
        # and nowhere else in the first 36 bars
        self.assertEqual(ind["swing_high"].iloc[:36].notna().sum(), 2)
        self.assertEqual(ind["swing_low"].iloc[:36].notna().sum(), 3)

    def test_flat_stretch_has_no_pivots(self):
        df = _frame()
        df["c"] = 50.0
        df["h"] = 50.0
        df["l"] = 50.0
        ind = indicators.add_indicators(df)
        self.assertEqual(ind["swing_high"].notna().sum(), 0)
        self.assertEqual(ind["swing_low"].notna().sum(), 0)

    def test_vol_ratio_constant_volume_is_one(self):
        df = _frame()
        df["v"] = 100.0
        ind = indicators.add_indicators(df)
        self.assertTrue(
            np.allclose(ind["vol_ratio"].dropna(), 1.0))

    def test_vol_ratio_spike(self):
        df = _zigzag(UP_TURNS, vol_spikes={35: 500.0})
        ind = indicators.add_indicators(df)
        self.assertGreater(ind["vol_ratio"].iloc[35], 1.0)
        self.assertAlmostEqual(ind["vol_ratio"].iloc[35], 500 / 120, places=6)

    def test_atr_zero_on_flat_data(self):
        df = _frame()
        df["c"] = df["h"] = df["l"] = 50.0
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["atr"].dropna(), 0.0))

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

    def test_trend_confirms_hh_hl(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(UP_TURNS)))
        self.assertEqual(sig["trend"].iloc[21], 0)
        self.assertEqual(sig["trend"].iloc[27], 1)
        self.assertEqual(sig["trend"].iloc[35], 1)

    def test_trend_confirms_lh_ll(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(DN_TURNS)))
        self.assertEqual(sig["trend"].iloc[27], -1)
        self.assertEqual(sig["trend"].iloc[35], -1)

    def test_pullback_depth_and_arming(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(UP_TURNS)))
        # leg 115-105; pullback to 110 is 50%
        self.assertAlmostEqual(sig["pullback_depth"].iloc[30], 0.5)
        self.assertTrue(sig["armed_long"].iloc[30])
        self.assertFalse(sig["armed_long"].iloc[27])  # only 20% deep

    def test_long_entry_on_breakout_with_volume(self):
        df = _zigzag(UP_TURNS, vol_spikes={35: 500.0})
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["long_entry"].iloc[35])
        self.assertEqual(sig["long_entry"].sum(), 1)

    def test_no_long_entry_without_volume(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag(UP_TURNS)))
        self.assertEqual(sig["long_entry"].sum(), 0)

    def test_no_entry_on_shallow_pullback(self):
        turns = [(5, 110), (10, 100), (15, 110), (20, 105),
                 (25, 115), (30, 113), (35, 116)]
        df = _zigzag(turns, vol_spikes={35: 500.0})
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig["long_entry"].sum(), 0)  # depth only 20%

    def test_no_entry_on_deep_pullback(self):
        turns = [(5, 110), (10, 100), (15, 110), (20, 105),
                 (25, 115), (30, 107), (35, 116)]
        df = _zigzag(turns, vol_spikes={35: 500.0})
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig["long_entry"].sum(), 0)  # depth 80% > 66%

    def test_short_entry_mirror(self):
        df = _zigzag(DN_TURNS, vol_spikes={35: 500.0})
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertTrue(sig["short_entry"].iloc[35])
        self.assertEqual(sig["short_entry"].sum(), 1)

    def test_long_exit_on_lower_low(self):
        # Wick-driven lower low: closes stay flat at 113.5 (above the
        # 66% line of the 116.05-109.95 leg = 112.02), but bar 40's
        # low dips to 108.9 -- a swing low below the prev low 109.95.
        df = _zigzag(UP_TURNS)
        for b in range(36, 45):
            df.loc[b, "c"] = 113.5
            df.loc[b, "o"] = 113.5
            df.loc[b, "h"] = 113.55
            df.loc[b, "l"] = 113.45
        df.loc[40, "l"] = 108.9
        sig = signals.add_signals(indicators.add_indicators(df))
        # swing low 108.9 < prev 109.95 confirms at bar 42; the deep
        # retracement line (112.02) is never crossed by a close
        self.assertFalse(sig["long_exit"].iloc[40])
        self.assertFalse(sig["long_exit"].iloc[41])
        self.assertTrue(sig["long_exit"].iloc[42])

    def test_long_exit_on_deep_retracement(self):
        turns = UP_TURNS + [(40, 107), (45, 112)]
        sig = signals.add_signals(indicators.add_indicators(_zigzag(turns)))
        # bar 35 (116) confirms as a swing high at bar 37, re-freezing
        # the leg to 116.05-109.95; the 66% line is 112.02, crossed by
        # the close at bar 38 (110.6) before any pivot confirms
        self.assertTrue(sig["long_exit"].iloc[38])
        self.assertFalse(sig["long_exit"].iloc[37])

    def test_no_lookahead(self):
        df = _zigzag(UP_TURNS, vol_spikes={35: 500.0})
        full = signals.add_signals(indicators.add_indicators(df))
        j = 35
        trunc = signals.add_signals(
            indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]))


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.target_atr_mult, 4.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        import strategies.dow_theory_trend as mod
        from strategies.registry import REGISTRY

        self.assertIn("dow_theory_trend", REGISTRY)
        self.assertIs(REGISTRY["dow_theory_trend"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "dow_theory_trend")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
