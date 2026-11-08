"""EMA ribbon tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ema_ribbon import indicators, risk, signals
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


def _signal_frame(emas, closes, spreads):
    """emas: list of (ema8, ema13, ema21, ema34, ema55) rows."""
    arr = np.array(emas, dtype=float)
    return pd.DataFrame({
        "c": np.array(closes, dtype=float),
        "ema8": arr[:, 0], "ema13": arr[:, 1], "ema21": arr[:, 2],
        "ema34": arr[:, 3], "ema55": arr[:, 4],
        "ribbon_spread": np.array(spreads, dtype=float),
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


class TestEmaRibbon(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ema_ribbon", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: every EMA converges to the price, spread is 0.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        for n in (8, 13, 21, 34, 55):
            self.assertTrue(np.allclose(tail[f"ema{n}"], 100.0))
        self.assertTrue(np.allclose(tail["ribbon_spread"], 0.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            expect = df["c"].iloc[:i + 1].ewm(span=55, adjust=False, min_periods=55).mean().iloc[-1]
            self.assertAlmostEqual(df["ema55"].iloc[i], expect, places=9)
            spread = (df["ema8"].iloc[i] - df["ema55"].iloc[i]) / df["ema55"].iloc[i]
            self.assertAlmostEqual(df["ribbon_spread"].iloc[i], spread, places=9)

    def test_uptrend_alignment_and_entry(self):
        # Steady 0.5%/bar rally: the ribbon must align bullish and fire
        # a long entry once (first-alignment bar only).
        closes = 100 * (1.005 ** np.arange(300))
        df = _run(_frame(closes))
        tail = df.iloc[150:]
        self.assertTrue((tail["ema8"] > tail["ema13"]).all())
        self.assertTrue((tail["ema34"] > tail["ema55"]).all())
        self.assertTrue(df["long_entry"].any())
        first = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreaterEqual(first, 54)  # slowest EMA needs 55 bars
        self.assertFalse(df["short_entry"].any())

    def test_downtrend_alignment_and_entry(self):
        # Steady 0.5%/bar decline: mirror — bearish alignment, short entry.
        closes = 100 * (0.995 ** np.arange(300))
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].any())
        first = int(np.argmax(df["short_entry"].to_numpy()))
        self.assertGreaterEqual(first, 54)  # slowest EMA needs 55 bars
        self.assertFalse(df["long_entry"].any())

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

    def test_long_entry_on_first_alignment(self):
        # Alignment first becomes fully bullish at index 2, close above
        # ema8, spread 0.083 > 0.002.
        df = signals.add_signals(_signal_frame(
            [(96, 97, 98, 99, 100), (98, 97, 98, 99, 100),
             (104, 102, 100, 98, 96), (106, 103, 100, 98, 96),
             (108, 104, 101, 99, 97)],
            [96, 98, 105, 107, 109], [-0.04, -0.02, 0.083, 0.10, 0.11]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[4])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_on_first_alignment(self):
        # Alignment first becomes fully bearish at index 2, close below
        # ema8, spread -0.077 < -0.002.
        df = signals.add_signals(_signal_frame(
            [(104, 103, 102, 101, 100), (102, 103, 102, 101, 100),
             (96, 98, 100, 102, 104), (94, 97, 100, 102, 104),
             (92, 96, 99, 102, 104)],
            [104, 102, 95, 93, 91], [0.04, 0.02, -0.077, -0.09, -0.11]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_negative_cases(self):
        base_emas = [(96, 97, 98, 99, 100), (98, 97, 98, 99, 100),
                     (104, 102, 100, 98, 96)]
        # Spread too small (0.001 < 0.002): no entry.
        df = signals.add_signals(_signal_frame(
            base_emas, [96, 98, 105], [-0.04, -0.02, 0.001]))
        self.assertFalse(df["long_entry"].iloc[2])
        # Close below ema8 at the alignment bar: no entry.
        df = signals.add_signals(_signal_frame(
            base_emas, [96, 98, 103], [-0.04, -0.02, 0.083]))
        self.assertFalse(df["long_entry"].iloc[2])
        # Already aligned on the previous bar (no first-alignment):
        # fires once at the transition (index 1), then stays silent.
        df = signals.add_signals(_signal_frame(
            [(96, 97, 98, 99, 100), (104, 102, 100, 98, 96),
             (106, 104, 101, 99, 97), (108, 105, 102, 100, 98)],
            [96, 105, 107, 109], [-0.04, 0.083, 0.09, 0.09]))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])

    def test_exits(self):
        # Long exit when ema8 falls below ema21, or close below ema34.
        df = signals.add_signals(_signal_frame(
            [(104, 102, 100, 98, 96), (98, 101, 100, 98, 96),
             (106, 104, 101, 99, 97)],
            [105, 100, 97], [0.083, 0.02, 0.09]))
        self.assertTrue(df["long_exit"].iloc[1])   # ema8 98 < ema21 100
        self.assertTrue(df["long_exit"].iloc[2])   # close 97 < ema34 99
        # Short exit mirror: ema8 above ema21, or close above ema34.
        df = signals.add_signals(_signal_frame(
            [(96, 98, 100, 102, 104), (102, 99, 100, 102, 104),
             (94, 96, 99, 101, 103)],
            [95, 100, 103], [-0.077, -0.02, -0.09]))
        self.assertTrue(df["short_exit"].iloc[1])  # ema8 102 > ema21 100
        self.assertTrue(df["short_exit"].iloc[2])  # close 103 > ema34 101

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame(self):
        # Fewer bars than the slowest EMA: no crash, no entries.
        df = _run(_flat_frame(n=30))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars: EMAs equal the price, spread 0, no entries.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertTrue(np.allclose(df.iloc[risk.WARMUP:]["ema55"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
