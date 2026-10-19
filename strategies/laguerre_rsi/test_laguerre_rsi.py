"""Laguerre RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.laguerre_rsi import indicators, risk, signals


def _df_from_c(c):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


class TestLaguerreRsi(unittest.TestCase):
    def test_recurrence_hand_computed(self):
        # hand-compute the first 4 bars of the Laguerre loop, gamma=0.5
        g = 0.5
        c = np.array([100.0, 101.0, 99.5, 100.5, 102.0])
        df = indicators.add_indicators(_df_from_c(c), gamma=g)
        L0 = np.empty(5); L1 = np.empty(5); L2 = np.empty(5); L3 = np.empty(5)
        L0[0] = L1[0] = L2[0] = L3[0] = c[0]
        for i in range(1, 5):
            L0[i] = (1 - g) * c[i] + g * L0[i - 1]
            L1[i] = -g * L0[i] + L0[i - 1] + g * L1[i - 1]
            L2[i] = -g * L1[i] + L1[i - 1] + g * L2[i - 1]
            L3[i] = -g * L2[i] + L2[i - 1] + g * L3[i - 1]
        for col, exp in (("lag_L0", L0), ("lag_L1", L1),
                         ("lag_L2", L2), ("lag_L3", L3)):
            self.assertTrue(np.allclose(df[col].to_numpy(), exp, rtol=1e-12), col)

    def test_lrsi_formula_from_cu(self):
        # per-bar source formula, hand-rolled loop (independent of the
        # vectorized implementation): up/down of CU, ratio, 0/0 -> prev
        n = 120
        i = np.arange(n)
        c = 100.0 + 8.0 * np.sin(i / 12.0) + 0.1 * i
        df = indicators.add_indicators(_df_from_c(c))
        cu = df["lag_CU"].to_numpy()
        exp = [0.5]
        for k in range(1, n):
            d = cu[k] - cu[k - 1]
            if d > 0:
                exp.append(1.0)
            elif d < 0:
                exp.append(0.0)
            else:
                exp.append(exp[-1])
        self.assertTrue(np.allclose(df["lrsi"].to_numpy(), exp, rtol=1e-12))

    def test_lrsi_takes_only_sign_values(self):
        # per-bar ratio of a single signed diff: {0, 0.5, 1}
        i = np.arange(300)
        c = 100.0 + 8.0 * np.sin(i / 12.0) + 0.1 * i
        r = indicators.add_indicators(_df_from_c(c))["lrsi"]
        self.assertTrue(set(np.unique(r)) <= {0.0, 0.5, 1.0})

    def test_lrsi_bounded_and_flat_is_half(self):
        # flat price: CU never moves -> 0/0 -> 0.5 everywhere
        df = indicators.add_indicators(_df_from_c(np.full(200, 50.0)))
        r = df["lrsi"]
        self.assertTrue(bool((r >= 0.0 - 1e-12).all() and (r <= 1.0 + 1e-12).all()))
        self.assertTrue(bool((r == 0.5).all()))
        self.assertFalse(r.isna().any())
        # oscillating series stays in [0, 1] with no NaN
        i = np.arange(400)
        c = 100.0 + 10.0 * np.sin(i / 8.0)
        df2 = indicators.add_indicators(_df_from_c(c))
        r2 = df2["lrsi"]
        self.assertFalse(r2.isna().any())
        self.assertTrue(bool((r2 >= 0.0).all() and (r2 <= 1.0).all()))

    def test_gamma_changes_output(self):
        i = np.arange(200)
        c = 100.0 + 5.0 * np.sin(i / 10.0)
        r05 = indicators.add_indicators(_df_from_c(c), gamma=0.5)["lrsi"]
        r03 = indicators.add_indicators(_df_from_c(c), gamma=0.3)["lrsi"]
        self.assertFalse(bool(np.allclose(r05, r03)))

    def test_cross_up_through_02_fires_long(self):
        # crash then rebound: lrsi sinks below 0.2, then crosses back up
        n = 400
        down = 100.0 - 0.6 * np.arange(250)
        up = down[-1] + 0.9 * np.arange(150)
        c = np.concatenate([down, up])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        r = indicators.add_indicators(_df_from_c(c))["lrsi"]
        for j in idx:
            self.assertLessEqual(r.iloc[j - 1], 0.2)
            self.assertGreater(r.iloc[j], 0.2)

    def test_cross_down_through_08_fires_short(self):
        n = 400
        rise = 100.0 + 0.6 * np.arange(250)
        fall = rise[-1] - 0.9 * np.arange(150)
        c = np.concatenate([rise, fall])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        r = indicators.add_indicators(_df_from_c(c))["lrsi"]
        for j in idx:
            self.assertGreaterEqual(r.iloc[j - 1], 0.8)
            self.assertLess(r.iloc[j], 0.8)

    def test_signal_logic_exact_formulas(self):
        i = np.arange(500)
        c = 100.0 + 12.0 * np.sin(i / 15.0) + 0.05 * i
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        r, prev = ind["lrsi"], ind["lrsi"].shift(1)
        self.assertTrue(
            bool((sig["long_entry"] == ((prev <= 0.2) & (r > 0.2)).fillna(False)).all())
        )
        self.assertTrue(
            bool((sig["short_entry"] == ((prev >= 0.8) & (r < 0.8)).fillna(False)).all())
        )
        self.assertTrue(
            bool((sig["long_exit"] == ((prev >= 0.5) & (r < 0.5)).fillna(False)).all())
        )
        self.assertTrue(
            bool((sig["short_exit"] == ((prev <= 0.5) & (r > 0.5)).fillna(False)).all())
        )

    def test_no_lookahead_truncation(self):
        i = np.arange(600)
        c = 100.0 + 12.0 * np.sin(i / 15.0) + 0.05 * i
        full = _df_from_c(c)
        ind_full = indicators.add_indicators(full)
        for j in (200, 550):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("lag_L0", "lag_CU", "lrsi"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-12, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        i = np.arange(500)
        c = 100.0 + 12.0 * np.sin(i / 15.0) + 0.05 * i
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.laguerre_rsi as mod

        self.assertEqual(mod.SPEC.slug, "laguerre_rsi")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 50)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
