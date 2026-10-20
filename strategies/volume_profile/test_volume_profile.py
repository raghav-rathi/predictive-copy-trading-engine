"""Volume profile value-area fade tests. Network-free, synthetic data."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.volume_profile import indicators, risk, signals


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


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


class TestVolumeProfileIndicators(unittest.TestCase):
    def test_adds_expected_columns(self):
        ind = indicators.add_indicators(_rand_df())
        for col in ("vp_val", "vp_vah", "vp_poc"):
            self.assertIn(col, ind.columns)

    def test_nan_before_window_forms(self):
        ind = indicators.add_indicators(_rand_df(200))
        self.assertTrue(ind["vp_val"].iloc[: indicators.WINDOW - 1].isna().all())
        self.assertFalse(ind["vp_val"].iloc[indicators.WINDOW:].isna().any())

    def test_val_leq_poc_leq_vah(self):
        ind = indicators.add_indicators(_rand_df(400))
        ok = ind["vp_val"].notna()
        self.assertTrue((ind.loc[ok, "vp_val"] <= ind.loc[ok, "vp_poc"]).all())
        self.assertTrue((ind.loc[ok, "vp_poc"] <= ind.loc[ok, "vp_vah"]).all())

    def test_poc_near_heavy_volume_region(self):
        # deterministic oscillation around 110 with volume concentrated
        # near 110: POC should land near 110
        n = 300
        c = 110.0 + 2.0 * np.sin(np.arange(n) * 0.5)
        df = _df_from_c(c)
        df["v"] = np.where(np.abs(c - 110.0) < 0.5, 1000.0, 10.0)
        ind = indicators.add_indicators(df)
        poc = ind["vp_poc"].iloc[-1]
        self.assertLess(abs(poc - 110.0), 3.0)

    def test_value_area_covers_majority_volume(self):
        # independent VA re-computation on the last bar's window
        df = _rand_df(300)
        ind = indicators.add_indicators(df)
        w = df.iloc[-indicators.WINDOW :]
        lo, hi = w["l"].min(), w["h"].max()
        width = (hi - lo) / indicators.BINS
        bl = np.clip(((w["l"].to_numpy() - lo) / width).astype(int), 0, 23)
        bh = np.clip(((w["h"].to_numpy() - lo) / width).astype(int), 0, 23)
        diff = np.zeros(25)
        for b, e, vv in zip(bl, bh, w["v"].to_numpy()):
            diff[b] += vv / (e - b + 1)
            diff[min(e + 1, 24)] -= vv / (e - b + 1)
        vol = np.cumsum(diff[:24])
        edges = np.linspace(lo, hi, 25)
        val, vah = ind["vp_val"].iloc[-1], ind["vp_vah"].iloc[-1]
        in_va = (edges[:-1] >= val - 1e-9) & (edges[1:] <= vah + 1e-9)
        self.assertGreaterEqual(vol[in_va].sum() / vol.sum(), 0.69)

    def test_no_lookahead(self):
        df = _rand_df(400)
        full = indicators.add_indicators(df)
        trunc = indicators.add_indicators(df.iloc[:300].copy())
        for col in ("vp_val", "vp_vah", "vp_poc"):
            a = full[col].iloc[:300].to_numpy()
            b = trunc[col].to_numpy()
            m = ~np.isnan(a) & ~np.isnan(b)
            np.testing.assert_allclose(a[m], b[m], rtol=1e-9)

    def test_flat_window_no_crash(self):
        df = _df_from_c(np.full(300, 100.0))
        ind = indicators.add_indicators(df)
        tail = ind.iloc[200:]
        self.assertFalse(tail["vp_val"].isna().any())
        # flat price must sit inside its own value area
        self.assertTrue((tail["vp_val"] <= 100.0).all())
        self.assertTrue((tail["vp_vah"] >= 100.0).all())

    def test_zero_volume_no_crash(self):
        df = _rand_df(300)
        df["v"] = 0.0
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        self.assertEqual(len(sig), len(df))


class TestVolumeProfileSignals(unittest.TestCase):
    def test_signal_columns_boolean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(400)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool)

    def test_failed_breakdown_fires_long(self):
        ind = indicators.add_indicators(_rand_df(400))
        ind["vp_val"] = 100.0
        ind["vp_vah"] = 110.0
        ind["c"] = 99.0
        ind.loc[ind.index[-1], "c"] = 101.0  # reclaim
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[-1])
        self.assertFalse(sig["short_entry"].iloc[-1])

    def test_failed_breakout_fires_short(self):
        ind = indicators.add_indicators(_rand_df(400))
        ind["vp_val"] = 90.0
        ind["vp_vah"] = 100.0
        ind["c"] = 101.0
        ind.loc[ind.index[-1], "c"] = 99.0  # back below VAH
        sig = signals.add_signals(ind)
        self.assertTrue(sig["short_entry"].iloc[-1])
        self.assertFalse(sig["long_entry"].iloc[-1])

    def test_no_hold_without_reclaim(self):
        ind = indicators.add_indicators(_rand_df(400))
        ind["vp_val"] = 100.0
        ind["vp_vah"] = 110.0
        ind["c"] = 99.0  # stays below VAL: no fade yet
        sig = signals.add_signals(ind)
        self.assertFalse(sig["long_entry"].any())

    def test_no_signal_exits(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(400)))
        self.assertFalse(sig["long_exit"].any())
        self.assertFalse(sig["short_exit"].any())

    def test_risk_config(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.WARMUP, 200)


if __name__ == "__main__":
    unittest.main()
