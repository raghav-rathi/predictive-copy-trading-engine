"""Rob Carver EWMAC tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.carver_ewmac import indicators, risk, signals
from strategies import base as B


def _df_from_c(c):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


class TestCarverEwmac(unittest.TestCase):
    def test_raw_rule_hand_computed(self):
        # raw(8,32) = EMA(8) - EMA(32) of close, hand-computed
        n = 300
        c = 100.0 + 0.3 * np.arange(n) + np.sin(np.arange(n) / 9.0)
        df = indicators.add_indicators(_df_from_c(c))
        exp = B.ema(pd.Series(c), 8) - B.ema(pd.Series(c), 32)
        got = df["ewmac_raw_8_32"]
        mask = exp.notna()
        self.assertTrue(np.allclose(got[mask], exp[mask], rtol=1e-9))
        self.assertEqual(int(got.isna().sum()), int(exp.isna().sum()))

    def test_zscore_formula_hand_computed(self):
        n = 300
        c = 100.0 + 0.3 * np.arange(n) + np.sin(np.arange(n) / 9.0)
        df = indicators.add_indicators(_df_from_c(c))
        raw = df["ewmac_raw_16_64"]
        vol = raw.rolling(252, min_periods=252).std()
        exp = raw / vol.replace(0, np.nan)
        got = df["ewmac_z_16_64"]
        mask = exp.notna()
        self.assertTrue(np.allclose(got[mask], exp[mask], rtol=1e-9))
        # z undefined before the 252-bar std window fills
        self.assertTrue(bool(got.iloc[:260].isna().all()))

    def test_forecast_is_mean_of_z_clipped(self):
        n = 400
        i = np.arange(n)
        c = 100.0 + 30.0 * np.sin(i / 40.0) + 0.05 * i
        df = indicators.add_indicators(_df_from_c(c))
        zcols = [c_ for c_ in df.columns if c_.startswith("ewmac_z_")]
        self.assertEqual(len(zcols), 3)
        exp = (10.0 * df[zcols].mean(axis=1)).clip(-20.0, 20.0)
        got = df["forecast"]
        mask = exp.notna()
        self.assertTrue(np.allclose(got[mask], exp[mask], rtol=1e-9))
        self.assertTrue(bool((got[mask].abs() <= 20.0 + 1e-9).all()))

    def test_forecast_clips_on_extreme_trend(self):
        n = 400
        c = 100.0 + 2.0 * np.arange(n)  # extreme sustained trend
        df = indicators.add_indicators(_df_from_c(c))
        valid = df["forecast"].dropna()
        self.assertGreater(len(valid), 0)
        self.assertAlmostEqual(float(valid.iloc[-1]), 20.0, places=9)

    def test_cross_above_ten_fires_long(self):
        n = 600
        i = np.arange(n)
        c = 100.0 + 30.0 * np.sin(i / 40.0) + 0.05 * i
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        f = indicators.add_indicators(_df_from_c(c))["forecast"]
        for j in idx:
            self.assertLessEqual(f.iloc[j - 1], 10.0)
            self.assertGreater(f.iloc[j], 10.0)

    def test_cross_below_minus_ten_fires_short(self):
        n = 600
        i = np.arange(n)
        c = 100.0 + 30.0 * np.sin(i / 40.0) - 0.05 * i
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        f = indicators.add_indicators(_df_from_c(c))["forecast"]
        for j in idx:
            self.assertGreaterEqual(f.iloc[j - 1], -10.0)
            self.assertLess(f.iloc[j], -10.0)

    def test_flat_between_thresholds_exits_long(self):
        # strong uptrend then reversal: long_entry fires, then the fade
        # pushes the forecast back below +10 and long_exit fires
        n = 500
        c = np.concatenate([100.0 + 0.8 * np.arange(300),
                            340.0 - 1.2 * np.arange(200)])
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        le = sig.index[sig["long_entry"]]
        self.assertGreater(len(le), 0)
        f = ind["forecast"]
        self.assertGreater(f.iloc[le[0]], 10.0)
        # long_exit exactly where forecast < 10
        exp = (f < 10.0).fillna(False)
        self.assertTrue(bool((sig["long_exit"] == exp).all()))
        # an exit fires after the entry once the forecast fades
        self.assertTrue(bool(sig["long_exit"].iloc[le[0] + 1 :].any()))
        k = sig.index[sig["long_exit"]][sig.index[sig["long_exit"]] > le[0]][0]
        self.assertLess(f.iloc[k], 10.0)

    def test_signal_logic_exact_formulas(self):
        n = 400
        i = np.arange(n)
        c = 100.0 + 0.3 * i + np.sin(i / 9.0)
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        f, prev = ind["forecast"], ind["forecast"].shift(1)
        self.assertTrue(
            bool((sig["long_entry"] == ((prev <= 10) & (f > 10)).fillna(False)).all())
        )
        self.assertTrue(
            bool((sig["short_entry"] == ((prev >= -10) & (f < -10)).fillna(False)).all())
        )
        self.assertTrue(bool((sig["long_exit"] == (f < 10).fillna(False)).all()))
        self.assertTrue(bool((sig["short_exit"] == (f > -10).fillna(False)).all()))

    def test_no_lookahead_truncation(self):
        n = 600
        i = np.arange(n)
        c = 100.0 + 30.0 * np.sin(i / 40.0) + 0.05 * i
        full = _df_from_c(c)
        ind_full = indicators.add_indicators(full)
        for j in (400, 550):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("ewmac_raw_8_32", "ewmac_z_32_128",
                        "ewmac_combined_z", "forecast"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        n = 500
        i = np.arange(n)
        c = 100.0 + 0.3 * i + np.sin(i / 9.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.carver_ewmac as mod

        self.assertEqual(mod.SPEC.slug, "carver_ewmac")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 300)


if __name__ == "__main__":
    unittest.main()
