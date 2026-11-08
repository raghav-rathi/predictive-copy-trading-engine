"""ADX / DI crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adx_di_cross import indicators, risk, signals
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


def _signal_frame(plus_di, minus_di, adx, closes=None):
    n = len(plus_di)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "c": c,
        "plus_di": np.array(plus_di, dtype=float),
        "minus_di": np.array(minus_di, dtype=float),
        "adx": np.array(adx, dtype=float),
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


class TestAdxDiCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("adx_di_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes with a fixed 2-point range: TR = 2, so the DI
        # lines are 0 (no directional movement), and DX = 0/0 -> ADX NaN.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(tail["adx"].isna().all())
        self.assertTrue(np.allclose(tail["plus_di"], 0.0))
        self.assertTrue(np.allclose(tail["minus_di"], 0.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        valid = df["adx"].dropna()
        self.assertGreater(len(valid), 50)
        self.assertTrue(((valid >= 0) & (valid <= 100)).all())
        self.assertTrue(((df["plus_di"].dropna() >= 0) & (df["plus_di"].dropna() <= 100)).all())
        self.assertTrue(((df["minus_di"].dropna() >= 0) & (df["minus_di"].dropna() <= 100)).all())
        # ADX must equal the Wilder-smoothed DX recomputed from the DI lines.
        dx = 100 * (df["plus_di"] - df["minus_di"]).abs() / (df["plus_di"] + df["minus_di"])
        expect = dx.ewm(alpha=1.0 / 14, adjust=False, min_periods=14).mean()
        for i in (150, 250, 399):
            self.assertAlmostEqual(df["adx"].iloc[i], expect.iloc[i], places=9)

    def test_indicator_values_uptrend(self):
        # Steady 1% per-bar rally: +DI must dominate -DI once warmed up.
        closes = 100 * (1.01 ** np.arange(200))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[150:]
        self.assertTrue((tail["plus_di"] > tail["minus_di"]).all())
        self.assertTrue(np.isfinite(tail["adx"]).all())
        self.assertTrue((tail["adx"] > 0).all())

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

    def test_long_entry_on_cross(self):
        # +DI crosses above -DI at index 2 with ADX 26 > 25, rising, spread 12.
        df = signals.add_signals(_signal_frame(
            [10, 12, 30, 32, 33], [30, 28, 18, 17, 16], [20, 22, 26, 30, 31]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_cross(self):
        # -DI crosses above +DI at index 2 with ADX 26 > 25, rising, spread 12.
        df = signals.add_signals(_signal_frame(
            [30, 28, 18, 17, 16], [10, 12, 30, 32, 33], [20, 22, 26, 30, 31]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_no_entry_without_strong_adx(self):
        # Cross happens but ADX is 24 at the cross: no entry.
        df = signals.add_signals(_signal_frame(
            [10, 12, 30, 32, 33], [30, 28, 18, 17, 16], [20, 22, 24, 30, 31]))
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_when_adx_falling(self):
        # Cross happens with ADX > 25 but falling (26 < 28): no entry.
        df = signals.add_signals(_signal_frame(
            [10, 12, 30, 32, 33], [30, 28, 18, 17, 16], [30, 28, 26, 24, 22]))
        self.assertFalse(df["long_entry"].iloc[2])

    def test_no_entry_when_spread_too_small(self):
        # Cross happens but the DI spread at the cross is only 2 (< 5).
        df = signals.add_signals(_signal_frame(
            [10, 12, 20, 22, 23], [30, 28, 18, 17, 16], [20, 22, 26, 30, 31]))
        self.assertFalse(df["long_entry"].iloc[2])

    def test_exits(self):
        # Opposite DI cross exits the open side.
        df = signals.add_signals(_signal_frame(
            [30, 28, 18], [10, 12, 30], [30, 30, 30]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        # ADX below 20 exits both sides.
        df = signals.add_signals(_signal_frame(
            [30, 32, 33], [10, 9, 8], [30, 25, 15]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertTrue(df["short_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the DMI warmup: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): indicators are NaN, no entries.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertTrue(df.iloc[risk.WARMUP:]["adx"].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
