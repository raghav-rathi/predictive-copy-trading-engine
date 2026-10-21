"""Know Sure Thing (KST) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kst import indicators, risk, signals
from strategies.base import crossed_above, crossed_below


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


class TestKst(unittest.TestCase):
    def test_roc_formula(self):
        c = 100.0 * (1.01 ** np.arange(80))
        df = indicators.add_indicators(_df_from_c(c))
        expect = 100.0 * (c[50] / c[20] - 1.0)  # ROC(30) at bar 50
        rcma4 = df["kst"].iloc[50]
        # reconstruct KST by hand: 1*SMA(ROC10,10)+2*SMA(ROC15,10)
        #   +3*SMA(ROC20,10)+4*SMA(ROC30,15) at bar 50
        wsum = 0.0
        for n, m, w in zip((10, 15, 20, 30), (10, 10, 10, 15), (1, 2, 3, 4)):
            r = 100.0 * (c[50 - m + 1 : 51] / c[50 - m + 1 - n : 51 - n] - 1.0)
            wsum += w * r.mean()
        self.assertAlmostEqual(float(df["kst"].iloc[50]), wsum, places=6)
        # flat series -> KST of zero
        flat = indicators.add_indicators(_df_from_c(np.full(120, 100.0)))
        self.assertAlmostEqual(float(flat["kst"].iloc[-1]), 0.0, places=9)

    def test_signal_line_is_sma9(self):
        df = indicators.add_indicators(_rand_df())
        expect = df["kst"].iloc[91:100].mean()
        self.assertAlmostEqual(float(df["kst_signal"].iloc[99]), float(expect), places=9)

    def test_warmup_nan_handling(self):
        df = indicators.add_indicators(_rand_df())
        # longest spin-up: SMA(ROC(30),15) valid from bar 44,
        # +8 more bars for the 9-bar signal line -> first full KST at 52
        self.assertTrue(df["kst"].iloc[:44].isna().all())
        self.assertEqual(int(df["kst"].first_valid_index()), 44)
        self.assertEqual(int(df["kst_signal"].first_valid_index()), 52)
        self.assertFalse(df["kst"].iloc[80:].isna().any())
        self.assertFalse(df["kst_signal"].iloc[80:].isna().any())

    def test_rally_fires_long(self):
        # fall then strong rally: KST crosses up its signal while negative
        c = np.concatenate([200.0 - 0.4 * np.arange(70),
                            172.0 + 1.2 * np.arange(150)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))

    def test_crash_fires_short(self):
        # mid-rally shakeout: a dip crosses KST below its signal while
        # KST is still positive -> short_entry fires. (A plain
        # rally-then-crash only crosses down after KST has already gone
        # negative, which the sign gate correctly suppresses.)
        c = np.concatenate([100.0 + 1.0 * np.arange(60),
                            160.0 - 0.3 * np.arange(40),
                            148.0 + 1.0 * np.arange(60),
                            208.0 - 1.5 * np.arange(120)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_sign_gate_reduces_entries(self):
        # ungated crosses should fire at least as often as sign-gated ones
        sig = signals.add_signals(indicators.add_indicators(_rand_df(600, seed=3)))
        raw_up = crossed_above(sig["kst"], sig["kst_signal"]).fillna(False).sum()
        raw_dn = crossed_below(sig["kst"], sig["kst_signal"]).fillna(False).sum()
        self.assertLessEqual(int(sig["long_entry"].sum()), int(raw_up))
        self.assertLessEqual(int(sig["short_entry"].sum()), int(raw_dn))

    def test_entries_match_spec(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        up = crossed_above(sig["kst"], sig["kst_signal"]).fillna(False).astype(bool)
        dn = crossed_below(sig["kst"], sig["kst_signal"]).fillna(False).astype(bool)
        neg = (sig["kst"] < 0).fillna(False).astype(bool)
        pos = (sig["kst"] > 0).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_entry"] == (up & neg)).all()))
        self.assertTrue(bool((sig["short_entry"] == (dn & pos)).all()))
        self.assertTrue(bool((sig["long_exit"] == dn).all()))
        self.assertTrue(bool((sig["short_exit"] == up).all()))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("kst", "kst_signal"):
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
        import strategies.kst as mod

        self.assertEqual(mod.SPEC.slug, "kst")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
