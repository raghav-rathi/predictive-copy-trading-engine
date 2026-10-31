"""VIDYA trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vidya_trend import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes + 0.5,
                         "l": closes - 0.5, "c": closes,
                         "v": np.full(n, 100.0)})


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


def _flat_then_rise_then_fall():
    flat = [100.0] * 30
    rise = [100.0 + i for i in range(1, 21)]   # 101..120
    fall = [120.0 - i for i in range(1, 21)]   # 119..100
    return flat + rise + fall


class TestVidyaTrend(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("vidya_cmo", "vidya_alpha", "vidya", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_hand_computed_all_up_moves(self):
        # Bars 0..8 flat at 100, bar 9 = 101, bar 10 = 102. At bar 9 the
        # 9 changes are eight 0s and one +1, so CMO = 100 and
        # alpha = (2/21) * 100/100 = 2/21. VIDYA(9) = 101 (init) and
        # VIDYA(10) = (2/21)*102 + (19/21)*101 = 101 + 2/21.
        closes = [100.0] * 9 + [101.0, 102.0]
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["vidya_cmo"].iloc[9], 100.0)
        self.assertAlmostEqual(df["vidya_alpha"].iloc[9], 2.0 / 21.0)
        self.assertAlmostEqual(df["vidya"].iloc[9], 101.0)
        self.assertAlmostEqual(df["vidya_cmo"].iloc[10], 100.0)
        self.assertAlmostEqual(df["vidya"].iloc[10], 101.0 + 2.0 / 21.0)

    def test_flat_series_stays_at_price(self):
        df = indicators.add_indicators(_frame([100.0] * 100))
        self.assertTrue((df["vidya_cmo"].iloc[30:] == 0.0).all())
        self.assertTrue((df["vidya_alpha"].iloc[30:] == 0.0).all())
        self.assertTrue((df["vidya"].iloc[30:] == 100.0).all())

    def test_cmo_and_alpha_bounds(self):
        df = indicators.add_indicators(_random_walk_frame())
        cmo = df["vidya_cmo"].iloc[risk.WARMUP:]
        a = df["vidya_alpha"].iloc[risk.WARMUP:]
        self.assertTrue(((cmo >= -100.0) & (cmo <= 100.0)).all())
        self.assertTrue(((a >= 0.0) & (a <= 2.0 / 21.0 + 1e-12)).all())

    def test_long_on_rise_short_on_fall(self):
        df = _run(_frame(_flat_then_rise_then_fall()))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["short_entry"].any())
        self.assertLess(df.index[df["long_entry"]][0],
                        df.index[df["short_entry"]][0])

    def test_no_lookahead_last_close(self):
        closes = _flat_then_rise_then_fall()
        df1 = _run(_frame(closes))
        closes2 = list(closes)
        closes2[-1] = closes2[-1] * 1.5
        df2 = _run(_frame(closes2))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("vidya_trend", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["vidya_trend"].slug, "vidya_trend")
        self.assertEqual(registry.REGISTRY["vidya_trend"].warmup_bars, risk.WARMUP)
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

    def test_warmup_gating_in_backtest(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        if len(res.trades):
            self.assertTrue(
                (res.trades["entry_t"] >= int(df["t"].iloc[risk.WARMUP])).all())

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
