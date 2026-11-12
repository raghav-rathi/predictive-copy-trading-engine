"""Ehlers Instantaneous Trendline tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_instantaneous_trendline import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _it_manual(c, alpha=0.07):
    """Independent re-implementation of the Ehlers recursion."""
    c = np.asarray(c, dtype=float)
    n = len(c)
    it = np.empty(n)
    it[0] = c[0]
    if n > 1:
        it[1] = 0.5 * (c[0] + c[1])
    for i in range(2, n):
        it[i] = ((alpha - alpha * alpha / 4.0) * c[i]
                 + 0.5 * alpha * alpha * c[i - 1]
                 - (alpha - 0.75 * alpha * alpha) * c[i - 2]
                 + 2.0 * (1.0 - alpha) * it[i - 1]
                 - (1.0 - alpha) * (1.0 - alpha) * it[i - 2])
    return it


class TestEhlersInstantaneousTrendline(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ehlers_instantaneous_trendline", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_it_values_hand_computed(self):
        # Step series: 100, 100, then 110 flat. By hand:
        # it[0] = 100, it[1] = 100,
        # it[2] = 0.068775*110 + 0.00245*100 - 0.066325*100
        #       + 1.86*100 - 0.8649*100 = 100.68775.
        closes = [100.0, 100.0] + [110.0] * 50
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["it"].iloc[0], 100.0, places=9)
        self.assertAlmostEqual(df["it"].iloc[1], 100.0, places=9)
        self.assertAlmostEqual(df["it"].iloc[2], 100.68775, places=6)
        # Full-series cross-check against the independent recursion.
        expected = _it_manual(np.array(closes, dtype=float))
        np.testing.assert_allclose(df["it"].to_numpy(), expected, rtol=0, atol=1e-9)

    def test_it_matches_manual_on_random_walk(self):
        closes = 100 * np.exp(np.cumsum(
            np.random.default_rng(11).normal(0.0, 0.005, 200)))
        df = indicators.add_indicators(_frame(closes))
        expected = _it_manual(closes)
        np.testing.assert_allclose(df["it"].to_numpy(), expected, rtol=0, atol=1e-9)

    def test_it_converges_to_flat_price(self):
        # On a flat series the trendline must sit on the price.
        df = indicators.add_indicators(_flat_frame(n=200))
        tail = df["it"].iloc[100:]
        self.assertTrue(np.allclose(tail, 100.0, atol=1e-6))

    def test_cross_up_fires_long(self):
        # Flat at 100, then a steady rise to 130, then a steady fall
        # back to 100: close must cross above the trendline on the
        # rise and below it on the fall.
        closes = ([100.0] * 60
                  + list(np.linspace(100.0, 130.0, 30))
                  + list(np.linspace(130.0, 100.0, 30)))
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["short_entry"].any())
        # Every long entry is a genuine close/trendline cross.
        for i in np.where(df["long_entry"])[0]:
            self.assertGreater(df["c"].iloc[i], df["it"].iloc[i])
            self.assertLessEqual(df["c"].iloc[i - 1], df["it"].iloc[i - 1])
        for i in np.where(df["short_entry"])[0]:
            self.assertLess(df["c"].iloc[i], df["it"].iloc[i])
            self.assertGreaterEqual(df["c"].iloc[i - 1], df["it"].iloc[i - 1])
        # No entry while the series is still flat (before bar 60).
        self.assertFalse(df["long_entry"].iloc[:60].any())
        self.assertFalse(df["short_entry"].iloc[:60].any())

    def test_flat_data_no_signals(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("it", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # 1- and 2-bar flat frames: no crash, no entries.
        df = _run(_frame([100.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        df = _run(_frame([100.0, 100.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
