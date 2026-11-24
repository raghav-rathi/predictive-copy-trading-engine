"""Pi Cycle Top tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pi_cycle import indicators, risk, signals


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


def _rand_df(n=800, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _jump_df():
    # flat 100 for 400 bars, jump to 1000 for 150, back to 100 for 400:
    # sma111 crosses ABOVE 2*sma350 at bar 433 and back BELOW at 553
    c = np.concatenate(
        [np.full(400, 100.0), np.full(150, 1000.0), np.full(400, 100.0)]
    )
    return _df_from_c(c)


class TestPiCycle(unittest.TestCase):
    def test_sma_math_on_linear_ramp(self):
        # on a linear ramp SMA(n) at bar j is the mean of the last n closes
        c = 100.0 + 0.1 * np.arange(600)
        df = indicators.add_indicators(_df_from_c(c))
        j = 500
        self.assertAlmostEqual(
            df["sma111"].iloc[j], c[j - 110 : j + 1].mean(), places=9
        )
        self.assertAlmostEqual(
            df["sma350"].iloc[j], c[j - 349 : j + 1].mean(), places=9
        )
        # shorter average above longer average in an uptrend
        self.assertTrue(bool((df["sma111"].iloc[400:] > df["sma350"].iloc[400:]).all()))

    def test_pi_top_is_multiplier_times_sma350(self):
        df = indicators.add_indicators(_rand_df())
        m = df["sma350"].notna()
        expect = 2.0 * df["sma350"]
        self.assertTrue(bool(((df["pi_top"][m] - expect[m]).abs() < 1e-9).all()))
        ratio = df["sma111"] / df["sma350"]
        self.assertTrue(bool(((df["pi_ratio"][m] - ratio[m]).abs() < 1e-9).all()))

    def test_multiplier_param_changes_top_line(self):
        df = indicators.add_indicators(_rand_df(), mult=1.9)
        expect = 1.9 * df["sma350"]
        ok = ((df["pi_top"] - expect).abs() < 1e-9) | (
            df["pi_top"].isna() & expect.isna()
        )
        self.assertTrue(bool(ok.all()))

    def test_warmup_nan_head(self):
        df = indicators.add_indicators(_rand_df())
        self.assertTrue(df["sma350"].iloc[:349].isna().all())
        self.assertFalse(df["sma350"].iloc[400:].isna().any())
        self.assertFalse(df["sma111"].iloc[400:].isna().any())
        self.assertFalse(df["pi_top"].iloc[400:].isna().any())
        self.assertFalse(df["pi_ratio"].iloc[400:].isna().any())

    def test_jump_series_crosses_into_and_out_of_top_zone(self):
        df = indicators.add_indicators(_jump_df())
        self.assertTrue(bool((df["pi_ratio"].iloc[433:553] >= 2.0).all()))
        sig = signals.add_signals(df)
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertEqual(int(sig.index[sig["short_entry"]][0]), 433)
        self.assertEqual(int(sig.index[sig["long_entry"]][0]), 553)

    def test_exits_are_opposite_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
            self.assertTrue(sig[col].dtype == bool, col)

    def test_flat_series_never_enters_top_zone(self):
        # flat price: sma111 == sma350, ratio 1.0 forever, no crosses
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(np.full(800, 100.0))))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["long_exit"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(600)
        ind_full = indicators.add_indicators(full)
        for j in (450, 550):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("sma111", "sma350", "pi_top", "pi_ratio"):
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
        import strategies.pi_cycle as mod

        self.assertEqual(mod.SPEC.slug, "pi_cycle")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        # regime system: no max-hold cap by design (see risk.py)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 400)


if __name__ == "__main__":
    unittest.main()
