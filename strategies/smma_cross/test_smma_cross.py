"""SMMA crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.smma_cross import indicators, risk, signals
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


def _flat_frame(n=100, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(fast, slow, closes=None):
    n = len(fast)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "c": c,
        "smma_fast": np.array(fast, dtype=float),
        "smma_slow": np.array(slow, dtype=float),
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


class TestSmmaCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("smma_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: SMMA is the flat price from its seed bar onward.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(df["smma_fast"].iloc[: indicators.FAST_PERIOD - 1].isna().all())
        self.assertTrue(df["smma_slow"].iloc[: indicators.SLOW_PERIOD - 1].isna().all())
        self.assertTrue(np.allclose(df["smma_fast"].iloc[indicators.FAST_PERIOD - 1:], 100.0))
        self.assertTrue(np.allclose(df["smma_slow"].iloc[indicators.SLOW_PERIOD - 1:], 100.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.isfinite(tail["smma_fast"]).all())
        self.assertTrue(np.isfinite(tail["smma_slow"]).all())
        # SMMA(9) vs the Wilder recursion recomputed by hand.
        c = df["c"].to_numpy()
        expect = np.full(len(c), np.nan)
        expect[8] = c[:9].mean()
        for i in range(9, len(c)):
            expect[i] = (expect[i - 1] * 8 + c[i]) / 9
        for i in (100, 250, 399):
            self.assertAlmostEqual(df["smma_fast"].iloc[i], expect[i], places=9)
        # Both SMMAs stay within 15% of the close.
        self.assertTrue((np.abs(tail["smma_fast"] - tail["c"]) / tail["c"] < 0.15).all())

    def test_indicator_values_uptrend(self):
        # Steady 1% per-bar rally: the fast SMMA must sit above the slow.
        closes = 100 * (1.01 ** np.arange(200))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[100:]
        self.assertTrue((tail["smma_fast"] > tail["smma_slow"]).all())
        self.assertTrue((tail["smma_fast"] < tail["c"]).all())  # lagging average

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.WARMUP, 50)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_cross(self):
        # SMMA(9) crosses above SMMA(21) at index 2.
        df = signals.add_signals(_signal_frame(
            [10, 11, 13, 14, 15], [12, 12, 12, 12, 12]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_cross(self):
        # SMMA(9) crosses below SMMA(21) at index 2.
        df = signals.add_signals(_signal_frame(
            [14, 13, 11, 10, 9], [12, 12, 12, 12, 12]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_exits(self):
        # Opposite cross exits the open side.
        df = signals.add_signals(_signal_frame(
            [14, 13, 11], [12, 12, 12]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame(
            [10, 11, 13], [12, 12, 12]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("smma_fast", "smma_slow", "long_entry", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the slow SMMA seed: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): SMMAs equal the price, no entries.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["smma_fast"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
