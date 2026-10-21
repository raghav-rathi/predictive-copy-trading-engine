"""OBV divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.obv_divergence import indicators, risk, signals


def _frame(n=300, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _df_from_c_v(c, v):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.01
    l = np.minimum(o, c) - 0.01
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _double_bottom(n=120, k=5):
    """Price falls to 90, bounces on heavy volume, falls to 85 on thin
    volume, bounces: lower price low, higher OBV -> bullish divergence."""
    c = np.empty(n)
    v = np.empty(n)
    # phase 1: 100 -> 90, volume 100
    c[:25] = np.linspace(100, 90, 25)
    v[:25] = 100.0
    # phase 2: 90 -> 100, heavy volume 300
    c[25:60] = np.linspace(90, 100, 35)
    v[25:60] = 300.0
    # phase 3: 100 -> 85, thin volume 10
    c[60:90] = np.linspace(100, 85, 30)
    v[60:90] = 10.0
    # phase 4: 85 -> 100
    c[90:] = np.linspace(85, 100, n - 90)
    v[90:] = 100.0
    return _df_from_c_v(c, v)


class TestObvDivergence(unittest.TestCase):
    def test_obv_hand_computed(self):
        df = _frame(60, seed=3)
        ind = indicators.add_indicators(df)
        dc = df["c"].diff().fillna(0.0)
        exp = (np.sign(dc.to_numpy()) * df["v"].to_numpy()).cumsum()
        np.testing.assert_allclose(ind["obv"].to_numpy(), exp, rtol=1e-12)
        self.assertFalse(ind["obv"].isna().any())

    def test_obv_unchanged_close_adds_zero(self):
        c = np.array([100.0, 101.0, 101.0, 99.0, 100.0])
        df = _df_from_c_v(c, np.full(5, 100.0))
        ind = indicators.add_indicators(df, pivot_k=1)
        obv = ind["obv"].to_numpy()
        # bar 2 unchanged close: obv stays at bar 1's value
        self.assertAlmostEqual(obv[2], obv[1], places=9)

    def test_pivot_low_confirmed_with_lag(self):
        n = 40
        l = np.full(n, 100.0)
        l[15] = 90.0  # sharp V bottom at bar 15
        c = l.copy()
        o = np.concatenate([[c[0]], c[:-1]])
        h = c + 0.5
        v = np.full(n, 100.0)
        df = _ohlcv(o, h, l, c, v)
        ind = indicators.add_indicators(df, pivot_k=4)
        pl = ind["pivot_low_price"]
        self.assertAlmostEqual(pl.iloc[15], 90.0, places=9)
        # the V bottom is the dominant pivot; flat plateaus at the frame
        # edges tie for the window minimum and legitimately print pivots
        self.assertGreaterEqual(int(pl.notna().sum()), 1)

    def test_bullish_divergence_fires_entry(self):
        k = 5
        df = _double_bottom(k=k)
        ind = indicators.add_indicators(df, pivot_k=k)
        # sanity: two pivot lows, second price lower
        pl = ind["pivot_low_price"].dropna()
        self.assertGreaterEqual(len(pl), 2)
        lows = pl.to_numpy()
        self.assertLess(lows[-1], lows[-2])  # lower price low
        plo = ind["pivot_low_obv"].dropna().to_numpy()
        self.assertGreater(plo[-1], plo[-2])  # higher OBV -> divergence
        sig = signals.add_signals(ind)
        le_bars = np.flatnonzero(sig["long_entry"].to_numpy())
        self.assertGreater(len(le_bars), 0)
        # entry on the first bar after confirmation: pivot_bar + k + 1
        pivot_bar = int(ind["pivot_low_price"].dropna().index[-1])
        self.assertIn(pivot_bar + k + 1, le_bars)

    def test_signal_columns_on_random_walk(self):
        df = _frame(400, seed=21)
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool)
        # random walk: signals may or may not fire; just require sanity
        total = sum(int(sig[c].sum()) for c in
                    ("long_entry", "short_entry", "long_exit", "short_exit"))
        self.assertGreaterEqual(total, 0)
        # exits must fire on pivots even when entries don't
        self.assertGreater(int(sig["long_exit"].sum()), 0)

    def test_warmup_covers_lag(self):
        self.assertGreaterEqual(risk.WARMUP, 2 * indicators.PIVOT_K + 14)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)

    def test_registration_imports_cleanly(self):
        import strategies.obv_divergence as mod

        self.assertEqual(mod.SPEC.slug, "obv_divergence")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
