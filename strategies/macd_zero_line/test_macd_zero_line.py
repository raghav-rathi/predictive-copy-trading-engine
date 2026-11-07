"""MACD zero-line cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_zero_line import indicators, risk, signals
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


def _trend_frame():
    # Downtrend then uptrend: MACD line goes negative, then crosses
    # back above zero. Then a downtrend again for the short cross.
    closes = list(np.linspace(120, 80, 60))
    closes += list(np.linspace(80, 140, 80))
    closes += list(np.linspace(140, 90, 60))
    return _frame(closes)


class TestMacdZeroLine(unittest.TestCase):
    def test_registered(self):
        self.assertIn("macd_zero_line", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values(self):
        df = indicators.add_indicators(_frame(list(np.linspace(100, 130, 60))))
        tail = df.iloc[40:]
        self.assertTrue(np.isfinite(tail["macd_line"]).all())
        # In a steady uptrend the fast EMA sits above the slow EMA.
        self.assertTrue((tail["macd_line"] > 0).all())
        # Histogram is line minus signal by construction.
        np.testing.assert_allclose(
            tail["macd_hist"], tail["macd_line"] - tail["macd_signal"], rtol=1e-9
        )
        # MACD line equals EMA(12) - EMA(26) of close.
        c = df["c"]
        expected = (
            c.ewm(span=12, adjust=False, min_periods=12).mean()
            - c.ewm(span=26, adjust=False, min_periods=26).mean()
        )
        np.testing.assert_allclose(
            tail["macd_line"], expected.iloc[40:], rtol=1e-9, equal_nan=True
        )

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["macd_line"]).all())
        self.assertTrue(np.isfinite(tail["macd_signal"]).all())

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_uptrend_after_downtrend(self):
        df = _run(_trend_frame())
        self.assertTrue(df["long_entry"].any())
        # Every long entry bar has the MACD line above zero.
        self.assertTrue((df.loc[df["long_entry"], "macd_line"] > 0).all())

    def test_short_entry_on_downtrend(self):
        df = _run(_trend_frame())
        self.assertTrue(df["short_entry"].any())
        self.assertTrue((df.loc[df["short_entry"], "macd_line"] < 0).all())

    def test_exit_on_reverse_cross(self):
        df = _run(_trend_frame())
        # A long exit (reverse cross) must follow the long entries.
        long_idx = df.index[df["long_entry"]]
        self.assertTrue(len(long_idx) > 0)
        self.assertTrue(df.loc[long_idx[0]:, "long_exit"].any())

    def test_no_lookahead_flat(self):
        closes = [100.0] * 150
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_entry_in_pure_downtrend(self):
        # The MACD line is born negative in a downtrend that starts at
        # bar 0 (no zero cross from above), so there is no long entry
        # at all; the short cross is covered by the trend frame test.
        closes = list(np.linspace(150, 60, 200))
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["long_exit"].any())


if __name__ == "__main__":
    unittest.main()
