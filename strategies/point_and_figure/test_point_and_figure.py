"""Point & Figure tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.point_and_figure import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes + 0.05,
                         "l": closes - 0.05, "c": closes,
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestPointAndFigure(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("pf_dir", "pf_box", "pf_col_high", "pf_col_low",
                    "pf_signal", "pf_reversal", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_double_top_long(self):
        # X to 110, 3-box reversal to O (low 105), reversal to X,
        # new X high 111 exceeds previous X high 110 -> breakout.
        closes = [100, 102, 104, 106, 108, 110, 108, 107, 106, 105,
                  107, 108, 109, 111]
        df = _run(_frame(closes))
        self.assertEqual(df["pf_signal"].iloc[-1], 1)
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_double_bottom_short(self):
        # O to 90, reversal to X (high 95), 3-box reversal to O,
        # new O low 89 below previous O low 90 -> breakdown.
        closes = [100, 98, 96, 94, 92, 90, 92, 93, 94, 95, 92, 91, 89]
        df = _run(_frame(closes))
        self.assertEqual(df["pf_signal"].iloc[-1], -1)
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_box_stable_within_column(self):
        # Rising column: box stays 1% of the column-start price (100)
        # even as price rises to 110.
        closes = [100, 102, 104, 106, 108, 110]
        df = _run(_frame(closes))
        self.assertTrue((df["pf_box"].iloc[1:] == 1.0).all())

    def test_reversal_exits_position(self):
        # Long on the double top, then a 3-box fall flips the column
        # to O and must exit the long.
        closes = [100, 102, 104, 106, 108, 110, 108, 107, 106, 105,
                  107, 108, 109, 111, 110, 108, 107]
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("point_and_figure", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["point_and_figure"].slug,
                         "point_and_figure")
        self.assertEqual(risk.WARMUP, 30)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
