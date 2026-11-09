"""Ichimoku Kumo twist tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kumo_twist import indicators, risk, signals
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


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(senkou_a, senkou_b, closes=None):
    n = len(senkou_a)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "c": c,
        "senkou_a": np.array(senkou_a, dtype=float),
        "senkou_b": np.array(senkou_b, dtype=float),
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


class TestKumoTwist(unittest.TestCase):
    def test_registered(self):
        self.assertIn("kumo_twist", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes with a fixed 2-point range: every line sits at the
        # midpoint 100, spans are equal, no twist ever.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["senkou_a"], 100.0))
        self.assertTrue(np.allclose(tail["senkou_b"], 100.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.isfinite(tail["senkou_a"]).all())
        self.assertTrue(np.isfinite(tail["senkou_b"]).all())
        # Spans stay inside the observed price range.
        self.assertTrue((tail["senkou_a"] >= df["l"].min()).all())
        self.assertTrue((tail["senkou_a"] <= df["h"].max()).all())
        self.assertTrue((tail["senkou_b"] >= df["l"].min()).all())
        self.assertTrue((tail["senkou_b"] <= df["h"].max()).all())

    def test_indicator_values_uptrend(self):
        # Steady 1% per-bar rally: the faster Span A (built on 9/26-bar
        # lines) sits above the slower 52-bar Span B once warmed up.
        closes = 100 * (1.01 ** np.arange(250))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[200:]
        self.assertTrue((tail["senkou_a"] > tail["senkou_b"]).all())
        # Span A equals the average of Tenkan and Kijun; Span B equals
        # the 52-bar midpoint — check one bar by hand.
        i = 220
        sa = (df["tenkan"].iloc[i] + df["kijun"].iloc[i]) / 2
        sb = (df["h"].iloc[i - 51:i + 1].max() + df["l"].iloc[i - 51:i + 1].min()) / 2
        self.assertAlmostEqual(df["senkou_a"].iloc[i], sa, places=9)
        self.assertAlmostEqual(df["senkou_b"].iloc[i], sb, places=9)

    def test_spans_are_unshifted(self):
        # The spans at bar i must equal the values computed from data
        # through bar i — NOT the textbook 26-bar-forward plot. On a
        # rising series the unshifted Span B at bar i is strictly above
        # the value the displaced plot would show there (which would be
        # the 52-bar midpoint as of bar i-26).
        closes = 100 * (1.01 ** np.arange(250))
        df = indicators.add_indicators(_frame(closes))
        i = 220
        displaced_sb = (
            df["h"].iloc[i - 26 - 51:i - 26 + 1].max()
            + df["l"].iloc[i - 26 - 51:i - 26 + 1].min()
        ) / 2
        self.assertGreater(df["senkou_b"].iloc[i], displaced_sb)

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

    def test_long_entry_on_twist_up(self):
        # Span A crosses above Span B at index 2.
        df = signals.add_signals(_signal_frame(
            [90, 95, 105, 110, 112], [100, 100, 100, 100, 100]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_twist_down(self):
        # Span A crosses below Span B at index 2.
        df = signals.add_signals(_signal_frame(
            [110, 105, 95, 90, 88], [100, 100, 100, 100, 100]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_no_entry_without_twist(self):
        # Span A stays above Span B throughout: no twist, no entry.
        df = signals.add_signals(_signal_frame(
            [105, 106, 107, 108, 109], [100, 100, 100, 100, 100]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exits_on_opposite_twist(self):
        # A twist down exits a long; a twist up exits a short.
        df = signals.add_signals(_signal_frame([110, 105, 95], [100, 100, 100]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame([90, 95, 105], [100, 100, 100]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        # Both spans on bar i must not change when later bars are appended.
        full = indicators.add_indicators(_random_walk_frame())
        trunc = indicators.add_indicators(_random_walk_frame().iloc[:200])
        for col in ("senkou_a", "senkou_b"):
            a = full[col].iloc[:200].to_numpy()
            b = trunc[col].to_numpy()
            self.assertTrue(np.allclose(a, b, equal_nan=True))

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the 52-bar Span B window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): spans equal close, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        self.assertTrue(np.allclose(df.iloc[risk.WARMUP:]["senkou_a"], 100.0))
        self.assertTrue(np.allclose(df.iloc[risk.WARMUP:]["senkou_b"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
