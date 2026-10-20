"""VPIN toxicity-exhaustion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vpin import indicators, risk, signals


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


def _rand_df(n=600, seed=11, drift=0.0):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(drift, 1.0, n))
    vols = np.abs(rng.normal(100.0, 30.0, n)) + 1.0
    df = _df_from_c(c)
    df["v"] = vols
    return df


class TestVpinIndicators(unittest.TestCase):
    def test_adds_expected_columns(self):
        ind = indicators.add_indicators(_rand_df())
        for col in ("buy_v", "sell_v", "vpin", "vpin_pctile", "low_20", "high_20"):
            self.assertIn(col, ind.columns)

    def test_buy_sell_split_consistent(self):
        ind = indicators.add_indicators(_rand_df())
        np.testing.assert_allclose(
            ind["buy_v"] + ind["sell_v"], ind["v"], rtol=1e-9
        )

    def test_full_body_up_bar_all_buy(self):
        # close == high, low below: buy_frac = 1
        df = _df_from_c([100.0, 101.0, 102.0])
        df["h"] = df["c"]
        df["l"] = df["c"] - 1.0
        ind = indicators.add_indicators(df)
        self.assertTrue((ind["buy_v"] == ind["v"]).all())
        self.assertTrue((ind["sell_v"] == 0.0).all())

    def test_flat_bar_splits_half(self):
        df = _df_from_c([100.0, 100.0, 100.0])
        df["h"] = df["l"] = df["c"]
        ind = indicators.add_indicators(df)
        np.testing.assert_allclose(ind["buy_v"], 0.5 * ind["v"], rtol=1e-9)

    def test_vpin_bounded_where_valid(self):
        ind = indicators.add_indicators(_rand_df(700))
        valid = ind["vpin"].dropna()
        self.assertGreater(len(valid), 50)
        self.assertTrue(((valid >= 0.0) & (valid <= 1.0)).all())

    def test_vpin_nan_before_buckets_form(self):
        ind = indicators.add_indicators(_rand_df(60))
        self.assertTrue(ind["vpin"].iloc[:40].isna().all())

    def test_pctile_bounded_where_valid(self):
        ind = indicators.add_indicators(_rand_df(700))
        valid = ind["vpin_pctile"].dropna()
        self.assertGreater(len(valid), 10)
        self.assertTrue(((valid >= 0.0) & (valid <= 1.0)).all())

    def test_no_lookahead(self):
        df = _rand_df(500)
        full = indicators.add_indicators(df)
        trunc = indicators.add_indicators(df.iloc[:400].copy())
        for col in ("vpin", "vpin_pctile", "buy_v", "low_20"):
            a = full[col].iloc[:400].to_numpy()
            b = trunc[col].to_numpy()
            m = ~np.isnan(a) & ~np.isnan(b)
            np.testing.assert_allclose(a[m], b[m], rtol=1e-9)

    def test_zero_volume_no_crash(self):
        df = _rand_df(300)
        df["v"] = 0.0
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        self.assertEqual(len(sig), len(df))


class TestVpinSignals(unittest.TestCase):
    def test_signal_columns_boolean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(700)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool)

    def test_long_entry_requires_toxicity_and_panic_low(self):
        ind = indicators.add_indicators(_rand_df(700))
        sig = signals.add_signals(ind)
        longs = sig[sig["long_entry"]]
        if len(longs):
            self.assertTrue((ind.loc[longs.index, "vpin_pctile"] > 0.90).all())
            self.assertTrue(
                (ind.loc[longs.index, "c"] <= ind.loc[longs.index, "low_20"]).all()
            )

    def test_no_signal_exits(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(700)))
        self.assertFalse(sig["long_exit"].any())
        self.assertFalse(sig["short_exit"].any())

    def test_forced_extreme_fires_long(self):
        # panic-low close with maximal percentile: entry must fire
        ind = indicators.add_indicators(_rand_df(700))
        ind["vpin_pctile"] = 0.99
        ind["low_20"] = ind["c"]  # every bar a new 20-bar low
        sig = signals.add_signals(ind)
        valid = ind["vpin_pctile"].notna()
        self.assertTrue(sig.loc[valid, "long_entry"].any())

    def test_risk_config(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.target_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.WARMUP, 320)


if __name__ == "__main__":
    unittest.main()
