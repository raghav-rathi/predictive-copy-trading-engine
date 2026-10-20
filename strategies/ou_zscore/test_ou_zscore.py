"""OU half-life z-score mean-reversion tests. Network-free, synthetic data."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ou_zscore import indicators, risk, signals


def _df_from_c(c, spread=0.2, vol=100.0):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, vol)}
    )


def _rand_df(n=600, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _ar1_df(n=600, seed=7, theta_true=-0.3, sigma=1.0):
    """dev follows dev(t) = dev(t-1) + theta*dev(t-1) + noise (mean-reverting)."""
    rng = np.random.default_rng(seed)
    dev = np.zeros(n)
    for i in range(1, n):
        dev[i] = dev[i - 1] + theta_true * dev[i - 1] + rng.normal(0, sigma)
    c = 100.0 * np.exp(dev)
    return _df_from_c(c)


class TestOuIndicators(unittest.TestCase):
    def test_adds_expected_columns(self):
        ind = indicators.add_indicators(_rand_df())
        for col in ("dev", "theta", "half_life", "hl_valid", "zscore"):
            self.assertIn(col, ind.columns)

    def test_theta_recovers_true_ar1_slope(self):
        # true theta = -0.3 -> HL = -ln2/-0.3 ~= 2.31 (< 5, invalid),
        # so use theta=-0.05 -> HL ~= 13.86, valid
        ind = indicators.add_indicators(_ar1_df(theta_true=-0.05, seed=3))
        th = ind["theta"].dropna()
        self.assertGreater(len(th), 100)
        # median estimated theta should be negative and roughly in band
        self.assertLess(float(np.median(th)), -0.01)
        self.assertGreater(float(np.median(th)), -0.5)

    def test_hl_valid_flags_fast_mean_reversion(self):
        ind = indicators.add_indicators(_ar1_df(theta_true=-0.05, seed=3))
        self.assertTrue(ind["hl_valid"].iloc[200:].any())
        # half-life for theta=-0.05 is ~13.9; check the estimate lands in band
        hl = ind.loc[ind["hl_valid"], "half_life"]
        self.assertTrue(((hl >= 5.0) & (hl <= 120.0)).all())

    def test_non_mean_reverting_regimes_not_tradable(self):
        # flat prices: dev is constant 0 -> theta NaN -> invalid
        ind = indicators.add_indicators(_df_from_c(np.full(600, 100.0)))
        self.assertFalse(ind["hl_valid"].iloc[150:].any())
        # accelerating (quadratic log-price) trend: theta >= 0 -> invalid,
        # so momentum regimes are excluded from mean-reversion trades
        t = np.arange(600)
        c = 100.0 * np.exp(0.0002 * t**2)
        ind2 = indicators.add_indicators(_df_from_c(c))
        self.assertLess(ind2["hl_valid"].iloc[150:].mean(), 0.1)

    def test_no_lookahead(self):
        df = _rand_df(500)
        full = indicators.add_indicators(df)
        trunc = indicators.add_indicators(df.iloc[:400].copy())
        for col in ("dev", "theta", "half_life", "zscore"):
            a = full[col].iloc[:400].to_numpy()
            b = trunc[col].to_numpy()
            m = ~np.isnan(a) & ~np.isnan(b)
            np.testing.assert_allclose(a[m], b[m], rtol=1e-9)

    def test_zscore_consistent_with_dev(self):
        df = _rand_df(400)
        ind = indicators.add_indicators(df)
        dev = df["c"].pipe(np.log) - np.log(df["c"]).rolling(50, min_periods=50).mean()
        std = dev.rolling(50, min_periods=50).std()
        expect = dev / std.replace(0.0, np.nan)
        pd.testing.assert_series_equal(
            ind["zscore"], expect.rename("zscore"), check_names=False
        )


class TestOuSignals(unittest.TestCase):
    def test_signal_columns_boolean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(600)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool)

    def test_long_entry_needs_negative_z_and_valid_hl(self):
        ind = indicators.add_indicators(_rand_df(600))
        sig = signals.add_signals(ind)
        longs = sig[sig["long_entry"]]
        if len(longs):
            self.assertTrue((ind.loc[longs.index, "zscore"] < -2.0).all())
            self.assertTrue(ind.loc[longs.index, "hl_valid"].all())

    def test_exit_on_zero_cross(self):
        ind = indicators.add_indicators(_rand_df(600))
        sig = signals.add_signals(ind)
        z = ind["zscore"]
        pd.testing.assert_series_equal(
            sig["long_exit"], (z >= 0.0).fillna(False).astype(bool), check_names=False
        )
        pd.testing.assert_series_equal(
            sig["short_exit"], (z <= 0.0).fillna(False).astype(bool), check_names=False
        )

    def test_forced_deep_z_fires_when_valid(self):
        ind = indicators.add_indicators(_rand_df(600))
        ind["zscore"] = -3.0
        ind["hl_valid"] = True
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[150:].all())
        self.assertFalse(sig["short_entry"].any())

    def test_risk_config(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertEqual(risk.WARMUP, 120)


if __name__ == "__main__":
    unittest.main()
