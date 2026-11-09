"""Chikou-span cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.chikou_span_cross import indicators, risk, signals


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=120, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(closes, ref):
    return pd.DataFrame({
        "c": np.array(closes, dtype=float),
        "chikou_ref": np.array(ref, dtype=float),
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


class TestChikouSpanCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("chikou_span_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: ref equals the close once warmed up, diff 0.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[indicators.CHIKOU_PERIOD:]
        self.assertTrue(np.allclose(tail["chikou_ref"], 100.0))
        self.assertTrue(np.allclose(tail["chikou_diff"], 0.0))
        self.assertTrue(df["chikou_ref"].iloc[: indicators.CHIKOU_PERIOD].isna().all())

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        # ref[i] must equal close[i-26] exactly.
        for i in (50, 150, 399):
            self.assertAlmostEqual(df["chikou_ref"].iloc[i],
                                   df["c"].iloc[i - 26], places=9)
        self.assertTrue(np.isfinite(df["chikou_ref"].iloc[26:]).all())

    def test_indicator_values_uptrend(self):
        # Steady 1% per-bar rally: close is always above the close
        # 26 bars ago once warmed up (diff > 0).
        closes = 100 * (1.01 ** np.arange(200))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[50:]
        self.assertTrue((tail["chikou_diff"] > 0).all())
        # diff / ref is exactly the 26-bar return: 1.01**26 - 1.
        expect = 1.01 ** 26 - 1
        self.assertTrue(np.allclose(tail["chikou_diff"] / tail["chikou_ref"],
                                    expect, rtol=1e-9))

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
        # Close crosses above a flat ref=100 at index 2.
        df = signals.add_signals(_signal_frame(
            [98, 99, 101, 102], [100, 100, 100, 100]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_cross(self):
        # Close crosses below a flat ref=100 at index 2.
        df = signals.add_signals(_signal_frame(
            [102, 101, 99, 98], [100, 100, 100, 100]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_no_entry_without_cross(self):
        # Close stays above ref the whole time: no fresh cross.
        df = signals.add_signals(_signal_frame(
            [101, 102, 103, 104], [100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exits_on_opposite_cross(self):
        # Opposite cross exits the open side.
        df = signals.add_signals(_signal_frame(
            [102, 101, 99], [100, 100, 100]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame(
            [98, 99, 101], [100, 100, 100]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_step(self):
        # A step up at the END of the frame must not create an entry
        # at or before the step: entries can only follow the cross.
        closes = [100.0] * 60 + [110.0]
        df = _run(_frame(closes))
        # The cross happens at the last bar (index 60) only.
        self.assertFalse(df["long_entry"].iloc[:60].any())
        self.assertTrue(df["long_entry"].iloc[60])

    def test_edge_short_frame(self):
        # Fewer bars than the 26-bar lookback: ref is all NaN, no entries.
        df = _run(_flat_frame(n=10))
        self.assertTrue(df["chikou_ref"].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
