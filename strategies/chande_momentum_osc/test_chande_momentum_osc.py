"""Chande Momentum Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chande_momentum_osc import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": closes, "h": closes * 1.001,
                         "l": closes * 0.999, "c": closes,
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


class TestChandeMomentumOsc(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("cmo", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_cmo_hand_computed_extremes(self):
        # 14 straight +1 moves: UpSum 14, DnSum 0 -> CMO = +100.
        up = [100.0 + i for i in range(20)]
        df = indicators.add_indicators(_frame(up))
        self.assertAlmostEqual(df["cmo"].iloc[14], 100.0, places=9)
        # 14 straight -1 moves -> CMO = -100.
        dn = [100.0 - i for i in range(20)]
        df = indicators.add_indicators(_frame(dn))
        self.assertAlmostEqual(df["cmo"].iloc[14], -100.0, places=9)

    def test_cmo_zero_on_flat_and_balanced(self):
        df = indicators.add_indicators(_frame([100.0] * 40))
        self.assertEqual(df["cmo"].iloc[20], 0.0)
        alt = [100.0 if i % 2 == 0 else 101.0 for i in range(40)]
        df = indicators.add_indicators(_frame(alt))
        self.assertAlmostEqual(df["cmo"].iloc[20], 0.0, places=9)

    def test_cmo_bounded(self):
        df = _run(_random_walk_frame())
        cmo = df["cmo"].iloc[risk.WARMUP:]
        self.assertTrue(((cmo >= -100.0) & (cmo <= 100.0)).all())

    def test_long_entry_leaving_oversold(self):
        # 14 down moves put CMO at -100; the 4th up move lifts it to
        # -42.86, crossing above -50.
        closes = [114.0 - i for i in range(15)]  # 114 down to 100
        closes += [100.0 + i for i in range(1, 8)]  # up to 107
        df = _run(_frame(closes))
        # Index of the 4th up bar: start 15 + 3 = 18.
        self.assertTrue(df["long_entry"].iloc[18])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_leaving_overbought(self):
        closes = [100.0 + i for i in range(15)]  # 100 up to 114
        closes += [114.0 - i for i in range(1, 8)]  # down to 107
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].iloc[18])
        self.assertFalse(df["long_entry"].any())

    def test_long_exit_on_cross_below_zero(self):
        # Full cycle: 14 down, 14 up, 14 down. The second down leg
        # drags CMO back below 0, exiting the long entered on the way up.
        closes = [114.0 - i for i in range(15)]
        closes += [100.0 + i for i in range(1, 15)]
        closes += [114.0 - i for i in range(1, 15)]
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        entry_idx = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertTrue(df["long_exit"].iloc[entry_idx + 1:].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:200])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_last_bar_change_keeps_earlier_signals(self):
        closes = [114.0 - i for i in range(15)]
        closes += [100.0 + i for i in range(1, 15)]
        closes += [114.0 - i for i in range(1, 15)]
        df1 = _run(_frame(closes))
        closes2 = list(closes)
        closes2[-1] = closes2[-1] * 1.5
        df2 = _run(_frame(closes2))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:-1].reset_index(drop=True),
                df2[col].iloc[:-1].reset_index(drop=True), check_names=False)

    def test_registration_and_warmup(self):
        self.assertIn("chande_momentum_osc", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["chande_momentum_osc"].slug,
                         "chande_momentum_osc")
        self.assertEqual(risk.WARMUP, 20)

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
