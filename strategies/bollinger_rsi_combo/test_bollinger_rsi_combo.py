"""Bollinger + RSI(2) mean-reversion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_rsi_combo import indicators, risk, signals
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


def _flat_frame(n=130, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(closes, mids, uppers, lowers, rsi2s):
    return pd.DataFrame({
        "c": np.array(closes, dtype=float),
        "bb_mid": np.array(mids, dtype=float),
        "bb_upper": np.array(uppers, dtype=float),
        "bb_lower": np.array(lowers, dtype=float),
        "rsi2": np.array(rsi2s, dtype=float),
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


class TestBollingerRsiCombo(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bollinger_rsi_combo", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: std = 0, so all bands collapse to the price;
        # RSI(2) is 0 (no gains at all).
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["bb_mid"], 100.0))
        self.assertTrue(np.allclose(tail["bb_upper"], 100.0))
        self.assertTrue(np.allclose(tail["bb_lower"], 100.0))
        self.assertTrue(np.allclose(tail["rsi2"], 0.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            window = df["c"].iloc[i - 19:i + 1]
            mid = window.mean()
            sd = window.std()
            self.assertAlmostEqual(df["bb_mid"].iloc[i], mid, places=9)
            self.assertAlmostEqual(df["bb_upper"].iloc[i], mid + 2 * sd, places=9)
            self.assertAlmostEqual(df["bb_lower"].iloc[i], mid - 2 * sd, places=9)
        valid = df["rsi2"].dropna()
        self.assertGreater(len(valid), 50)
        self.assertTrue(((valid >= 0) & (valid <= 100)).all())

    def test_drop_recovery_entry_pipeline(self):
        # 100 flat bars, a two-bar crash below the lower band with
        # RSI(2) collapsing, then a recovery close back inside the band.
        closes = [100.0] * 100 + [90.0, 82.0, 92.0, 95.0, 98.0]
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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

    def test_long_entry_on_recovery_close(self):
        # Bar 0 closes below the lower band (90 < 95) with RSI(2) = 5;
        # bar 1 closes back inside (96 > 95) -> long entry on bar 1.
        df = signals.add_signals(_signal_frame(
            [90, 96, 97], [100, 100, 100], [105, 105, 105],
            [95, 95, 95], [5, 8, 20]))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_recovery_close(self):
        # Bar 0 closes above the upper band (110 > 105) with RSI(2) = 95;
        # bar 1 closes back inside (104 < 105) -> short entry on bar 1.
        df = signals.add_signals(_signal_frame(
            [110, 104, 103], [100, 100, 100], [105, 105, 105],
            [95, 95, 95], [95, 92, 80]))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_negative_cases(self):
        # Setup but no recovery close (stays below the lower band).
        df = signals.add_signals(_signal_frame(
            [90, 94], [100, 100], [105, 105], [95, 95], [5, 4]))
        self.assertFalse(df["long_entry"].iloc[1])
        # Close below the lower band but RSI(2) not oversold (20 > 10).
        df = signals.add_signals(_signal_frame(
            [90, 96], [100, 100], [105, 105], [95, 95], [20, 25]))
        self.assertFalse(df["long_entry"].iloc[1])
        # RSI(2) oversold but close never went below the lower band.
        df = signals.add_signals(_signal_frame(
            [96, 97], [100, 100], [105, 105], [95, 95], [5, 8]))
        self.assertFalse(df["long_entry"].iloc[1])
        # Short mirror: setup but no recovery close back inside.
        df = signals.add_signals(_signal_frame(
            [110, 106], [100, 100], [105, 105], [95, 95], [95, 96]))
        self.assertFalse(df["short_entry"].iloc[1])

    def test_exits(self):
        # Long exit on close at/above the middle band, or RSI(2) > 90.
        df = signals.add_signals(_signal_frame(
            [96, 100, 97], [100, 100, 100], [105, 105, 105],
            [95, 95, 95], [30, 40, 95]))
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[1])   # close 100 >= mid 100
        self.assertTrue(df["long_exit"].iloc[2])   # RSI(2) 95 > 90
        # Short exit mirror: close at/below mid, or RSI(2) < 10.
        df = signals.add_signals(_signal_frame(
            [104, 100, 103], [100, 100, 100], [105, 105, 105],
            [95, 95, 95], [70, 60, 5]))
        self.assertFalse(df["short_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[1])  # close 100 <= mid 100
        self.assertTrue(df["short_exit"].iloc[2])  # RSI(2) 5 < 10

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame(self):
        # Fewer bars than the Bollinger window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars: bands collapse to the price, no entries.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertTrue(np.allclose(df.iloc[risk.WARMUP:]["bb_mid"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
