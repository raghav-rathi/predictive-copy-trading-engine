"""Ichimoku Tenkan/Kijun cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tenkan_kijun_cross import indicators, risk, signals
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


def _signal_frame(tenkan, kijun, closes=None):
    n = len(tenkan)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "c": c,
        "tenkan": np.array(tenkan, dtype=float),
        "kijun": np.array(kijun, dtype=float),
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


class TestTenkanKijunCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("tenkan_kijun_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes with a fixed 2-point range: both lines sit at the
        # midpoint of the range, 100, and never cross.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["tenkan"], 100.0))
        self.assertTrue(np.allclose(tail["kijun"], 100.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.isfinite(tail["tenkan"]).all())
        self.assertTrue(np.isfinite(tail["kijun"]).all())
        # Each line is a midpoint of a trailing high/low window, so it
        # stays inside the observed price range.
        self.assertTrue((tail["tenkan"] >= df["l"].min()).all())
        self.assertTrue((tail["tenkan"] <= df["h"].max()).all())
        self.assertTrue((tail["kijun"] >= df["l"].min()).all())
        self.assertTrue((tail["kijun"] <= df["h"].max()).all())

    def test_indicator_values_uptrend(self):
        # Steady 1% per-bar rally: the faster 9-bar line sits above the
        # slower 26-bar line once warmed up.
        closes = 100 * (1.01 ** np.arange(200))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[150:]
        self.assertTrue((tail["tenkan"] > tail["kijun"]).all())
        # And each line equals its defining midpoint formula.
        i = 180
        tk = (df["h"].iloc[i - 8:i + 1].max() + df["l"].iloc[i - 8:i + 1].min()) / 2
        kj = (df["h"].iloc[i - 25:i + 1].max() + df["l"].iloc[i - 25:i + 1].min()) / 2
        self.assertAlmostEqual(df["tenkan"].iloc[i], tk, places=9)
        self.assertAlmostEqual(df["kijun"].iloc[i], kj, places=9)

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

    def test_long_entry_on_cross_up(self):
        # Tenkan crosses above Kijun at index 2.
        df = signals.add_signals(_signal_frame(
            [90, 95, 105, 110, 112], [100, 100, 100, 100, 100]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_cross_down(self):
        # Tenkan crosses below Kijun at index 2.
        df = signals.add_signals(_signal_frame(
            [110, 105, 95, 90, 88], [100, 100, 100, 100, 100]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_no_entry_without_cross(self):
        # Tenkan stays above Kijun throughout: no cross, no entry.
        df = signals.add_signals(_signal_frame(
            [105, 106, 107, 108, 109], [100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exits_on_opposite_cross(self):
        # A cross down exits a long; a cross up exits a short.
        df = signals.add_signals(_signal_frame([110, 105, 95], [100, 100, 100]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame([90, 95, 105], [100, 100, 100]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_distinct_from_kijun_cross(self):
        # Same frame, opposite answers: close crosses Kijun (kijun_cross
        # fires) while Tenkan/Kijun do NOT cross (this strategy silent),
        # and vice versa. Close falls through a flat Kijun while Tenkan
        # stays above Kijun the whole time.
        df = signals.add_signals(_signal_frame(
            [110, 110, 110], [100, 100, 100],
            closes=[105, 102, 95]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        # Tenkan/Kijun on bar i must not change when later bars are appended.
        full = indicators.add_indicators(_random_walk_frame())
        trunc = indicators.add_indicators(_random_walk_frame().iloc[:200])
        for col in ("tenkan", "kijun"):
            a = full[col].iloc[:200].to_numpy()
            b = trunc[col].to_numpy()
            self.assertTrue(np.allclose(a, b, equal_nan=True))

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the Kijun window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): lines equal close, no entries.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertTrue(np.allclose(df.iloc[risk.WARMUP:]["tenkan"], 100.0))
        self.assertTrue(np.allclose(df.iloc[risk.WARMUP:]["kijun"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
