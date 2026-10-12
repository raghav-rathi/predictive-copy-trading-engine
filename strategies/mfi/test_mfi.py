"""Money Flow Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mfi import indicators, risk, signals


def _frame(n=400, seed=7, drift=0.0, vol=0.008):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestMfi(unittest.TestCase):
    def test_indicator_values_hand_built(self):
        # Monotonic up-move with constant volume: every bar has positive
        # money flow, so MFI must be exactly 100 (the defined limit).
        n = 40
        c = 100.0 + np.arange(n)
        v = np.full(n, 100.0)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.concatenate([[100.0], c[:-1]]),
                "h": c + 0.3,
                "l": c - 0.3,
                "c": c,
                "v": v,
            }
        )
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["mfi"].iloc[-1], 100.0, places=6)

    def test_indicator_values_hand_built_down(self):
        # Monotonic down-move: MFI must be exactly 0.
        n = 40
        c = 100.0 - np.arange(n)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": np.concatenate([[100.0], c[:-1]]),
                "h": c + 0.3,
                "l": c - 0.3,
                "c": c,
                "v": np.full(n, 100.0),
            }
        )
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["mfi"].iloc[-1], 0.0, places=6)

    def test_flat_market_is_nan(self):
        n = 40
        c = np.full(n, 100.0)
        df = pd.DataFrame(
            {
                "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
                "o": c,
                "h": c + 0.01,
                "l": c - 0.01,
                "c": c,
                "v": np.full(n, 100.0),
            }
        )
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["mfi"].iloc[-1:].isna().all())

    def test_mfi_bounds(self):
        ind = indicators.add_indicators(_frame(600, seed=5, vol=0.015))
        valid = ind["mfi"].dropna()
        self.assertTrue(((valid >= 0.0) & (valid <= 100.0)).all())

    def test_entries_are_20_80_crosses(self):
        df = _run(_frame(800, seed=11, vol=0.015))
        mfi = df["mfi"]
        le = df["long_entry"]
        self.assertGreater(int(le.sum()), 0)
        self.assertTrue(((mfi[le] > 20) & (mfi.shift(1)[le] <= 20)).all())
        se = df["short_entry"]
        self.assertGreater(int(se.sum()), 0)
        self.assertTrue(((mfi[se] < 80) & (mfi.shift(1)[se] >= 80)).all())

    def test_no_lookahead_truncation(self):
        full = _frame(400, seed=3)
        ind_full = indicators.add_indicators(full)
        for i in (150, 300):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            a, b = ind_full["mfi"].iloc[i], ind_tr["mfi"].iloc[i]
            self.assertTrue((pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9)

    def test_signals_boolean_clean(self):
        df = _run(_frame(300))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 168)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
