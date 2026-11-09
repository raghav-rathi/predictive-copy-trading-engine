"""Jurik MA trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.jurik_ma_trend import indicators, risk, signals


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=250, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(closes, jma, rising):
    return pd.DataFrame({
        "c": np.array(closes, dtype=float),
        "jma": np.array(jma, dtype=float),
        "jma_rising": np.array(rising, dtype=bool),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestJurikMaTrend(unittest.TestCase):
    def test_registered(self):
        self.assertIn("jurik_ma_trend", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: the recursion is seeded at the first close and
        # every stage's error term is zero, so JMA stays at the close.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(df["jma"], 100.0))
        self.assertFalse(df["jma_rising"].any())

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(np.isfinite(df["jma"]).all())
        # JMA tracks price: it must stay within 15% of the close.
        self.assertTrue((np.abs(df["jma"] / df["c"] - 1) < 0.15).all())
        # Recompute the recursion independently and compare exactly.
        beta = 0.45 * 13 / (0.45 * 13 + 2)
        alpha = beta ** 2
        pr = min(max(50.0 / 100 + 1.5, 0.5), 2.5)
        closes = df["c"].to_numpy()
        e0 = closes[0]
        e1 = 0.0
        e2 = 0.0
        jma = closes[0]
        expect = [jma]
        for i in range(1, len(closes)):
            e0 = (1 - alpha) * closes[i] + alpha * e0
            e1 = (closes[i] - e0) * (1 - beta) + beta * e1
            ma2 = e0 + pr * e1
            e2 = (ma2 - jma) * (1 - alpha) ** 2 + alpha ** 2 * e2
            jma = jma + e2
            expect.append(jma)
        expect = np.array(expect)
        self.assertTrue(np.allclose(df["jma"].to_numpy(), expect, rtol=1e-12))

    def test_indicator_values_uptrend(self):
        # Steady 1% per-bar rally: JMA must lag below the close and
        # rise every bar once the recursion is running.
        closes = 100 * (1.01 ** np.arange(200))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[100:]
        self.assertTrue((tail["jma"] < tail["c"]).all())
        self.assertTrue(tail["jma_rising"].all())
        # And it must be smoother (closer to price) than a 14-EMA lag:
        # JMA stays within 5% of the close on this steady trend.
        self.assertTrue((np.abs(tail["jma"] / tail["c"] - 1) < 0.05).all())

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.WARMUP, 100)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_cross_with_rising_jma(self):
        # Close crosses above a flat JMA=100 at index 2, JMA rising.
        df = signals.add_signals(_signal_frame(
            [98, 99, 101, 102], [100, 100, 100, 100], [True, True, True, True]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_no_long_entry_when_jma_flat(self):
        # Cross happens but the JMA is not rising: no long entry.
        df = signals.add_signals(_signal_frame(
            [98, 99, 101, 102], [100, 100, 100, 100], [False, False, False, False]))
        self.assertFalse(df["long_entry"].any())

    def test_short_entry_on_cross_with_falling_jma(self):
        # Close crosses below a falling JMA at index 2 (JMA 102->101->
        # 100->99; close 102->101->99->98).
        df = signals.add_signals(_signal_frame(
            [102, 101, 99, 98], [102, 101, 100, 99], [False, False, False, False]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_exits_on_cross_back(self):
        # Cross back exits the open side.
        df = signals.add_signals(_signal_frame(
            [102, 101, 99], [100, 100, 100], [False, False, False]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame(
            [98, 99, 101], [100, 100, 100], [True, True, True]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame(self):
        # 5 bars: recursion runs from the seed, no crash, no entries
        # (close never crosses a JMA that starts at the first close
        # and tracks it from below/above on flat data).
        df = _run(_flat_frame(n=5))
        self.assertTrue(np.isfinite(df["jma"]).all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
