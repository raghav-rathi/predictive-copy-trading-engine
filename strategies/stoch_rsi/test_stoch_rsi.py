"""StochRSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stoch_rsi import indicators, risk, signals


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


class TestStochRsi(unittest.TestCase):
    def test_indicator_values_hand_built(self):
        # Hand-built RSI: 14 straight up bars then the stoch window is flat.
        n = 40
        c = np.concatenate([[100.0], 100.0 + np.arange(1, n)])
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
        # RSI of a pure up-move is 100; stochrsi of a flat RSI window is NaN
        # (zero range), not a fake 100.
        self.assertAlmostEqual(ind["rsi"].iloc[-1], 100.0, places=3)
        self.assertTrue(pd.isna(ind["stochrsi"].iloc[-1]))

    def test_stochrsi_bounds_and_smoothing(self):
        ind = indicators.add_indicators(_frame())
        valid = ind["stochrsi"].dropna()
        self.assertTrue(((valid >= 0.0) & (valid <= 100.0)).all())
        k, d = ind["stochrsi_k"].iloc[-1], ind["stochrsi_d"].iloc[-1]
        self.assertTrue(pd.isna(k) or 0.0 <= k <= 100.0)
        self.assertTrue(pd.isna(d) or 0.0 <= d <= 100.0)

    def test_flat_market_is_nan_not_fake(self):
        n = 60
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
        self.assertTrue(ind["stochrsi"].iloc[-1:].isna().all())

    def test_no_lookahead_truncation(self):
        full = _frame(400, seed=3)
        ind_full = indicators.add_indicators(full)
        for i in (150, 300):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("stochrsi", "stochrsi_k", "stochrsi_d", "rsi"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_entries_gated_to_zones(self):
        df = _run(_frame(800, seed=11, vol=0.015))
        k, d = df["stochrsi_k"], df["stochrsi_d"]
        le = df["long_entry"]
        self.assertGreater(int(le.sum()), 0)
        self.assertTrue(((k[le] < 20) & (d[le] < 20)).all())
        se = df["short_entry"]
        self.assertGreater(int(se.sum()), 0)
        self.assertTrue(((k[se] > 80) & (d[se] > 80)).all())

    def test_exits_are_opposite_crosses(self):
        df = _run(_frame(800, seed=11, vol=0.015))
        from strategies import base as B

        pd.testing.assert_series_equal(
            df["long_exit"],
            B.crossed_below(df["stochrsi_k"], df["stochrsi_d"])
            .fillna(False)
            .astype(bool),
            check_names=False,
        )
        pd.testing.assert_series_equal(
            df["short_exit"],
            B.crossed_above(df["stochrsi_k"], df["stochrsi_d"])
            .fillna(False)
            .astype(bool),
            check_names=False,
        )

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
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
