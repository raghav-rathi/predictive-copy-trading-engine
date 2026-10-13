"""Mass Index tests. Network-free."""

import os
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strategies.mass_index import indicators, risk, signals


def _frame(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 10.0)}
    )


def _bulge_series(seed=11, n=140):
    """Quiet -> volatility explosion -> quiet. Produces an MI bulge > 27 that
    completes with close > SMA(20) (short case)."""
    rng = np.random.default_rng(seed)
    c = np.zeros(n)
    c[:60] = 200 - np.arange(60) * 0.2 + rng.normal(0, 0.1, 60)
    c[60:80] = c[59] + np.cumsum(rng.normal(0, 3.0, 20))
    c[80:] = c[79] - np.arange(1, n - 79) * 0.2 + rng.normal(0, 0.1, n - 80)
    o = np.empty(n)
    o[0] = c[0]
    o[1:] = c[:-1]
    return _frame(o, np.maximum(o, c) + 0.5, np.minimum(o, c) - 0.5, c)


def _constant_range(n=300):
    c = 100 + np.arange(n) * 0.05
    o = np.empty(n)
    o[0] = c[0]
    o[1:] = c[:-1]
    return _frame(o, np.maximum(o, c) + 0.5, np.minimum(o, c) - 0.5, c)


class TestMassIndex(unittest.TestCase):
    def test_mi_converges_to_25_on_constant_range(self):
        df = indicators.add_indicators(_constant_range())
        # ratio of single/double EMA of a constant range -> 1, sum of 25 -> 25
        self.assertAlmostEqual(float(df["mi"].iloc[-1]), 25.0, places=2)
        self.assertFalse(bool((df["mi"].dropna() > 27).any()))

    def test_bulge_forms_and_completes_short(self):
        df = indicators.add_indicators(_bulge_series())
        self.assertGreater(float(df["mi"].max()), 27.0)
        shorts = np.where(df["bulge_short"].to_numpy())[0]
        self.assertGreater(len(shorts), 0)
        b = shorts[0]
        self.assertGreater(df["c"].iloc[b], df["sma20"].iloc[b])

    def test_bulge_completes_long_on_mirror(self):
        base = _bulge_series()
        cc = (400.0 - base["c"]).to_numpy()
        oo = np.empty(len(cc))
        oo[0] = cc[0]
        oo[1:] = cc[:-1]
        mir = _frame(oo, np.maximum(oo, cc) + 0.5, np.minimum(oo, cc) - 0.5, cc)
        mir["t"] = base["t"].to_numpy()
        df = indicators.add_indicators(mir)
        longs = np.where(df["bulge_long"].to_numpy())[0]
        self.assertGreater(len(longs), 0)
        self.assertEqual(int(df["bulge_short"].sum()), 0)
        b = longs[0]
        self.assertLess(df["c"].iloc[b], df["sma20"].iloc[b])

    def test_no_bulge_without_expansion(self):
        df = indicators.add_indicators(_constant_range())
        self.assertEqual(int(df["bulge_long"].sum()), 0)
        self.assertEqual(int(df["bulge_short"].sum()), 0)

    def test_signals_wire_bulges(self):
        df = signals.add_signals(indicators.add_indicators(_bulge_series()))
        self.assertTrue((df["long_entry"] == df["bulge_long"]).all())
        self.assertTrue((df["short_entry"] == df["bulge_short"]).all())
        self.assertTrue((df["long_exit"] == df["bulge_short"]).all())
        self.assertTrue((df["short_exit"] == df["bulge_long"]).all())

    def test_no_lookahead(self):
        df = _bulge_series()
        full = signals.add_signals(indicators.add_indicators(df))
        cut = signals.add_signals(indicators.add_indicators(df.iloc[:100]))
        for col in ("bulge_long", "bulge_short", "mi"):
            a = full[col].iloc[:100].to_numpy()
            b = cut[col].to_numpy()
            if np.issubdtype(a.dtype, np.floating):
                self.assertTrue(np.allclose(a, b, equal_nan=True), col)
            else:
                self.assertTrue((a == b).all(), col)

    def test_clean_booleans(self):
        df = signals.add_signals(indicators.add_indicators(_bulge_series()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_risk_sanity(self):
        r = risk.RISK
        self.assertEqual(r.trail_atr_mult, 3.0)
        self.assertGreater(r.stop_atr_mult, 0)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertTrue(0 < r.risk_frac < 1)
        self.assertGreaterEqual(r.max_leverage, 1.0)
        self.assertGreaterEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
