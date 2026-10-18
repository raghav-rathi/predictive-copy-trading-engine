"""Ehlers Cyber Cycle tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_cyber_cycle import indicators, risk, signals

# hand-derived recursion constants for alpha = 0.07
_K1 = (1.0 - 0.07 / 2.0) ** 2  # 0.931225
_K2 = 2.0 * (1.0 - 0.07)  # 1.86
_K3 = (1.0 - 0.07) ** 2  # 0.8649


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _df_from_smooth(sm):
    n = len(sm)
    h = sm + 0.5
    l = sm - 0.5
    o = np.concatenate([[sm[0]], sm[:-1]])
    return _ohlcv(o, h, l, sm)


class TestCyberCycle(unittest.TestCase):
    def test_recursion_hand_computed(self):
        sm = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        ind = indicators.add_indicators(_df_from_smooth(sm))
        got = ind["cyber_cycle"].to_numpy()
        exp0 = _K1 * 1.0
        exp1 = _K1 * (2.0 - 2.0 * 1.0) + _K2 * exp0
        exp2 = _K1 * (3.0 - 2.0 * 2.0 + 1.0) + _K2 * exp1 - _K3 * exp0
        exp3 = _K1 * (4.0 - 2.0 * 3.0 + 2.0) + _K2 * exp2 - _K3 * exp1
        for e, g in zip((exp0, exp1, exp2, exp3), got[:4]):
            self.assertAlmostEqual(g, e, places=9)

    def test_seeded_with_zero_not_nan(self):
        sm = np.full(10, 100.0)
        ind = indicators.add_indicators(_df_from_smooth(sm))
        self.assertFalse(ind["cyber_cycle"].isna().any())
        # first bar: all seeds zero -> k1 * smooth_0
        self.assertAlmostEqual(ind["cyber_cycle"].iloc[0], _K1 * 100.0, places=9)

    def test_trigger_is_cycle_lagged_one(self):
        n = 120
        i = np.arange(n)
        ind = indicators.add_indicators(_df_from_smooth(100.0 + 5.0 * np.sin(i / 4.0)))
        cyc = ind["cyber_cycle"].to_numpy()
        trig = ind["cyber_trigger"].to_numpy()
        self.assertTrue(np.isnan(trig[0]))
        for j in (10, 60, 119):
            self.assertAlmostEqual(trig[j], cyc[j - 1], places=12)

    def test_long_entry_on_cross_above_trigger(self):
        n = 200
        i = np.arange(n)
        ind = indicators.add_indicators(_df_from_smooth(100.0 + 5.0 * np.sin(i / 4.0)))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        cyc = ind["cyber_cycle"].to_numpy()
        trig = ind["cyber_trigger"].to_numpy()
        for j in idx:
            self.assertGreater(cyc[j], trig[j])
            self.assertLessEqual(cyc[j - 1], trig[j - 1])

    def test_short_entry_mirror(self):
        n = 200
        i = np.arange(n)
        ind = indicators.add_indicators(_df_from_smooth(100.0 - 5.0 * np.sin(i / 4.0)))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        cyc = ind["cyber_cycle"].to_numpy()
        trig = ind["cyber_trigger"].to_numpy()
        for j in idx:
            self.assertLess(cyc[j], trig[j])
            self.assertGreaterEqual(cyc[j - 1], trig[j - 1])

    def test_exit_is_opposite_cross(self):
        n = 200
        i = np.arange(n)
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_smooth(100.0 + 5.0 * np.sin(i / 4.0)))
        )
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))
        self.assertGreater(int(sig["long_entry"].sum() + sig["short_entry"].sum()), 0)

    def test_flat_market_no_chatter(self):
        # constant smooth: recursion settles to zero, no crosses
        ind = indicators.add_indicators(_df_from_smooth(np.full(300, 100.0)))
        sig = signals.add_signals(ind)
        self.assertEqual(int(sig["long_entry"].iloc[100:].sum()), 0)
        self.assertEqual(int(sig["short_entry"].iloc[100:].sum()), 0)

    def test_no_lookahead_truncation(self):
        n = 250
        i = np.arange(n)
        full = _df_from_smooth(100.0 + 5.0 * np.sin(i / 4.0) + 0.5 * np.sin(i / 1.7))
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (120, 200):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            self.assertAlmostEqual(ind_full["cyber_cycle"].iloc[j], ind_tr["cyber_cycle"].iloc[j], places=12)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        n = 200
        i = np.arange(n)
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_smooth(100.0 + 5.0 * np.sin(i / 4.0)))
        )
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 20)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        from strategies import ehlers_cyber_cycle as mod
        from strategies.registry import REGISTRY
        self.assertIn("ehlers_cyber_cycle", REGISTRY)
        self.assertIs(REGISTRY["ehlers_cyber_cycle"], mod.SPEC)


if __name__ == "__main__":
    unittest.main()
