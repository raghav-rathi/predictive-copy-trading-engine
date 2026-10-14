"""Force Index unit tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.force_index import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    vv = np.asarray(v, float)
    vv = vv if vv.ndim else np.full(n, float(v))
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": vv}
    )


def _rally_then_dip():
    """40 bars rising 0.5/bar at v=50, then one -1.0 dip at v=100."""
    c = np.empty(44)
    c[:40] = 100.0 + 0.5 * np.arange(40)
    c[40] = c[39] - 0.2
    c[41] = c[40] - 1.0          # dip: FI2 should dive under zero, FI13 stays up
    c[42] = c[41] + 0.8
    c[43] = c[42] + 1.0
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.2
    l = np.minimum(o, c) - 0.2
    v = np.full(44, 50.0)
    v[41] = 100.0
    return _ohlcv(o, h, l, c, v)


class TestForceIndex(unittest.TestCase):
    def test_fi_math_on_hand_values(self):
        c = np.array([100.0, 101.0, 100.5])
        o = np.array([100.0, 100.0, 101.0])
        h = np.array([100.2, 101.2, 101.1])
        l = np.array([99.8, 99.9, 100.4])
        df = indicators.add_indicators(_ohlcv(o, h, l, c, v=1000.0))
        # FI = dclose * volume: [NaN, 1000, -500]
        self.assertAlmostEqual(df["fi_raw"].iloc[1], 1000.0)
        self.assertAlmostEqual(df["fi_raw"].iloc[2], -500.0)
        # EMA(2) adjust=False, min_periods=2: seed 1000, then
        # 1000 + (2/3)*(-500-1000) = 0
        self.assertAlmostEqual(df["fi2"].iloc[2], 0.0, places=6)
        self.assertTrue(np.isnan(df["fi2"].iloc[0]))

    def test_signal_logic_on_hand_built_columns(self):
        n = 6
        df = _ohlcv(np.ones(n), np.ones(n) + 1, np.ones(n) - 1, np.ones(n))
        df = indicators.add_indicators(df)
        df["fi13"] = 1.0                      # force uptrend
        df["fi2"] = pd.Series([0.5, 0.4, -0.1, -0.3, 0.2, 0.6])
        df["fi2_prev"] = df["fi2"].shift(1)
        df = signals.add_signals(df)
        # crossed_below(fi2, 0) at bar 2 only -> single long entry
        self.assertEqual(df["long_entry"].sum(), 1)
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].any())
        # downtrend mirror
        df["fi13"] = -1.0
        df["fi2"] = pd.Series([-0.5, -0.4, 0.1, 0.3, -0.2, -0.6])
        df["fi2_prev"] = df["fi2"].shift(1)
        df = signals.add_signals(df)
        self.assertEqual(df["short_entry"].sum(), 1)
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].any())

    def test_end_to_end_pullback_entry(self):
        df = signals.add_signals(indicators.add_indicators(_rally_then_dip()))
        entries = df.index[df["long_entry"]]
        self.assertTrue(len(entries) > 0, "expected at least one long pullback entry")
        # entries only while FI13 positive
        self.assertTrue((df.loc[entries, "fi13"] > 0).all())
        # exits defined and boolean
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
            self.assertFalse(df[col].isna().any())

    def test_no_lookahead(self):
        df = indicators.add_indicators(_rally_then_dip())
        df_full = signals.add_signals(df.copy())
        df_tr = signals.add_signals(indicators.add_indicators(_rally_then_dip().iloc[:-1]))
        cols = ["fi13", "fi2", "atr", "long_entry", "short_entry",
                "long_exit", "short_exit"]
        for col in cols:
            a = df_full[col].iloc[:-1].fillna(-999.0).to_numpy()
            b = df_tr[col].fillna(-999.0).to_numpy()
            self.assertTrue(np.allclose(a, b, equal_nan=True),
                            f"lookahead leak in {col}")

    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertGreaterEqual(risk.WARMUP, 40)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)


if __name__ == "__main__":
    unittest.main()
