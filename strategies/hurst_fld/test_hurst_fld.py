"""Hurst FLD tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.hurst_fld import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _df_from_c(c):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    return _ohlcv(o, h, l, c)


class TestHurstFld(unittest.TestCase):
    def test_fld_formula_hand_computed(self):
        # FLD(N)[i] = median[i - N/2], hand-checked at the last bar
        n = 200
        med = np.linspace(100.0, 120.0, n)
        o = np.concatenate([[med[0]], med[:-1]])
        ind = indicators.add_indicators(_ohlcv(o, med + 1.0, med - 1.0, med))
        for p, shift in ((20, 10), (40, 20), (80, 40)):
            self.assertAlmostEqual(
                ind[f"fld_{p}"].iloc[-1], med[-1 - shift], places=9
            )
        # NaN lead-in equals exactly the shift length
        self.assertEqual(int(ind["fld_20"].isna().sum()), 10)
        self.assertEqual(int(ind["fld_80"].isna().sum()), 40)

    def test_bull_cascade_fires_long_entry(self):
        # strong steady uptrend: cascades must eventually align
        n = 400
        i = np.arange(n)
        c = 100.0 + 0.35 * i + 0.15 * np.sin(i / 3.0)
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        for j in idx:
            self.assertGreater(ind["c"].iloc[j], ind["fld_20"].iloc[j])
            self.assertGreater(ind["fld_20"].iloc[j], ind["fld_40"].iloc[j])
            self.assertGreater(ind["fld_40"].iloc[j], ind["fld_80"].iloc[j])

    def test_entry_fires_only_on_transition(self):
        n = 400
        i = np.arange(n)
        c = 100.0 + 0.35 * i
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["long_entry"]].tolist()
        self.assertGreater(len(idx), 0)
        # entries are single bars at cascade onset: no two consecutive entries
        self.assertFalse(any(b == a + 1 for a, b in zip(idx, idx[1:])))

    def test_bear_cascade_mirror(self):
        n = 400
        i = np.arange(n)
        c = 300.0 - 0.35 * i
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        for j in idx:
            self.assertLess(ind["c"].iloc[j], ind["fld_20"].iloc[j])
            self.assertLess(ind["fld_20"].iloc[j], ind["fld_40"].iloc[j])
            self.assertLess(ind["fld_40"].iloc[j], ind["fld_80"].iloc[j])

    def test_exit_on_cross_back_through_fld20(self):
        # uptrend then sharp reversal below FLD20 -> long exit must fire
        n = 500
        i = np.arange(n)
        c = np.where(i < 350, 100.0 + 0.3 * i, 100.0 + 0.3 * 350 - 1.5 * (i - 350))
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        self.assertGreater(int(sig["long_exit"].sum()), 0)
        j = sig.index[sig["long_exit"]][0]
        self.assertLess(ind["c"].iloc[j], ind["fld_20"].iloc[j])
        self.assertGreaterEqual(
            ind["c"].iloc[j - 1], ind["fld_20"].iloc[j - 1]
        )

    def test_flat_market_no_cascade_no_entry(self):
        n = 300
        c = np.full(n, 100.0)  # dead flat: FLDs all equal, no strict cascade
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_no_lookahead_truncation(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.20 * i + 0.5 * np.sin(i / 4.0)
        full = _df_from_c(c)
        ind_full = indicators.add_indicators(full)
        for j in (150, 280):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("fld_20", "fld_40", "fld_80", "median", "atr"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9,
                    (col, j),
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.10 * i + 0.5 * np.sin(i / 4.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.hurst_fld as mod
        self.assertEqual(mod.SPEC.slug, "hurst_fld")
        self.assertEqual(mod.SPEC.warmup_bars, 90)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 90)


if __name__ == "__main__":
    unittest.main()
