"""Chaikin Money Flow tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chaikin_money_flow import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.array(o, float), "h": np.array(h, float),
                         "l": np.array(l, float), "c": np.array(c, float),
                         "v": np.array(v, float)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestChaikinMoneyFlow(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("mfm", "mfv", "cmf", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_cmf_bounded(self):
        df = _run(_random_walk_frame())
        self.assertTrue((df["cmf"].iloc[risk.WARMUP:].abs() <= 1.0 + 1e-9).all())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_hand_computed_cmf(self):
        # 20 bars closing mid-range (MFM 0), then one bar closing at
        # its high (MFM 1, MFV 100): CMF = 100 / 2000 = 0.05.
        n = 21
        df = _run(_frame([100.0] * n, [110.0] * n, [90.0] * n,
                         [100.0] * 20 + [110.0], [100.0] * n))
        self.assertAlmostEqual(df["cmf"].iloc[20], 0.05, places=9)
        self.assertAlmostEqual(df["mfm"].iloc[20], 1.0, places=9)

    def test_zero_range_guard(self):
        # H == L on every bar: MFM must be 0, never NaN/inf.
        n = 30
        df = _run(_frame([100.0] * n, [100.0] * n, [100.0] * n,
                         [100.0] * n, [100.0] * n))
        self.assertTrue((df["mfm"] == 0.0).all())
        self.assertTrue((df["cmf"].iloc[20:] == 0.0).all())

    def test_zero_volume_guard(self):
        n = 30
        df = _run(_frame([100.0] * n, [110.0] * n, [90.0] * n,
                         [105.0] * n, [0.0] * n))
        self.assertTrue((df["cmf"].iloc[20:] == 0.0).all())

    def test_long_on_cross_above_zero(self):
        # 20 bars closing at the low (CMF -1), then 11 bars closing
        # at the high: CMF = k/10 - 1, crossing above 0 at k=11.
        n = 31
        df = _run(_frame([100.0] * n, [110.0] * n, [90.0] * n,
                         [90.0] * 20 + [110.0] * 11, [100.0] * n))
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertFalse(df["long_entry"].iloc[:30].any())

    def test_short_on_cross_below_zero(self):
        n = 31
        df = _run(_frame([100.0] * n, [110.0] * n, [90.0] * n,
                         [110.0] * 20 + [90.0] * 11, [100.0] * n))
        self.assertTrue(df["short_entry"].iloc[30])

    def test_exit_on_opposite_cross(self):
        # Long at bar 30 (see above), then 21 bars closing at the low
        # drive CMF back below 0 -> long_exit must fire.
        n = 52
        df = _run(_frame([100.0] * n, [110.0] * n, [90.0] * n,
                         [90.0] * 20 + [110.0] * 11 + [90.0] * 21,
                         [100.0] * n))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())
        self.assertGreater(df["long_exit"].idxmax(), df["long_entry"].idxmax())

    def test_no_lookahead_last_bar(self):
        closes = _random_walk_frame()
        df1 = _run(closes)
        mod = closes.copy()
        mod.loc[mod.index[-1], "c"] = mod["c"].iloc[-1] * 1.5
        mod.loc[mod.index[-1], "h"] = mod["h"].iloc[-1] * 1.5
        df2 = _run(mod)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("chaikin_money_flow", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 25)

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
