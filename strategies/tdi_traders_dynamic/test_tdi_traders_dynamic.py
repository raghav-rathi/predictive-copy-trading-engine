"""Traders Dynamic Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tdi_traders_dynamic import indicators, risk, signals


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


class TestTdi(unittest.TestCase):
    def test_rsi_bounded_0_100(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        valid = df["tdi_rsi"].iloc[40:]
        self.assertFalse(valid.isna().any())
        self.assertTrue(bool(((valid >= 0) & (valid <= 100)).all()))

    def test_bands_bracket_base(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        valid = df.iloc[40:]
        self.assertTrue(bool((valid["tdi_band_upper"] >= valid["tdi_base"]).all()))
        self.assertTrue(bool((valid["tdi_band_lower"] <= valid["tdi_base"]).all()))

    def test_band_width_is_1p6185_sigma(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        sd = df["tdi_rsi"].rolling(34, min_periods=34).std()
        width = (df["tdi_band_upper"] - df["tdi_base"]) / 1.6185
        self.assertTrue(bool(np.allclose(width.iloc[40:], sd.iloc[40:], atol=1e-9)))

    def test_price_line_is_sma2_of_rsi(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect = df["tdi_rsi"].rolling(2, min_periods=2).mean()
        self.assertTrue(bool(np.allclose(df["tdi_price"].iloc[40:], expect.iloc[40:], atol=1e-9, equal_nan=True)))

    def test_strong_uptrend_fires_long_not_short(self):
        rng = np.random.default_rng(0)
        c = 100.0 + np.cumsum(rng.normal(0.8, 1.0, 400))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].iloc[40:].any()))
        self.assertFalse(bool(sig["short_entry"].iloc[40:].any()))

    def test_strong_downtrend_fires_short_not_long(self):
        rng = np.random.default_rng(0)
        c = 400.0 + np.cumsum(rng.normal(-0.8, 1.0, 400))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["short_entry"].iloc[40:].any()))
        self.assertFalse(bool(sig["long_entry"].iloc[40:].any()))

    def test_long_requires_base_above_50(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        longs = sig[sig["long_entry"]]
        self.assertTrue(len(longs) > 0)
        self.assertTrue(bool((longs["tdi_base"] > 50).all()))
        self.assertTrue(bool((longs["tdi_price"] > longs["tdi_base"]).all()))

    def test_short_requires_base_below_50(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        shorts = sig[sig["short_entry"]]
        self.assertTrue(len(shorts) > 0)
        self.assertTrue(bool((shorts["tdi_base"] < 50).all()))
        self.assertTrue(bool((shorts["tdi_price"] < shorts["tdi_base"]).all()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("tdi_rsi", "tdi_price", "tdi_signal", "tdi_base", "tdi_band_upper", "tdi_band_lower"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_exits_are_opposite_crosses(self):
        df = indicators.add_indicators(_rand_df())
        sig = signals.add_signals(df)
        cross_up = (df["tdi_price"] > df["tdi_signal"]) & (df["tdi_price"].shift(1) <= df["tdi_signal"].shift(1))
        cross_down = (df["tdi_price"] < df["tdi_signal"]) & (df["tdi_price"].shift(1) >= df["tdi_signal"].shift(1))
        self.assertTrue(bool((sig["long_exit"] == cross_down.fillna(False)).all()))
        self.assertTrue(bool((sig["short_exit"] == cross_up.fillna(False)).all()))

    def test_rsi_param_changes_output(self):
        d1 = indicators.add_indicators(_rand_df(), rsi_n=10)
        d2 = indicators.add_indicators(_rand_df(), rsi_n=21)
        self.assertFalse(bool(np.allclose(d1["tdi_rsi"].iloc[60:], d2["tdi_rsi"].iloc[60:])))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("tdi_rsi", "tdi_price", "tdi_signal", "tdi_base", "tdi_band_upper", "tdi_band_lower"):
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
        import strategies.tdi_traders_dynamic as mod

        self.assertEqual(mod.SPEC.slug, "tdi_traders_dynamic")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
