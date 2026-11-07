"""Fibonacci retracement tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fibonacci_retracement import indicators, risk, signals
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


def _legs_frame(legs, tail, preamble=30, step=6):
    closes = [legs[0]] * preamble
    for a, b in zip(legs, legs[1:]):
        for k in range(1, step + 1):
            closes.append(a + (b - a) * k / step)
    closes.extend(tail)
    return _frame(closes)


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


# Uptrend swing: A=90 (low), B=110 (high). Pivots are h/l-based
# (A=89.5, B=110.5, leg 21): golden zone 97.52-102.48.
LONG_LEGS = [100, 90, 110]
LONG_TAIL = [108, 105, 102, 100, 101, 103, 105, 108, 110, 112]
# Downtrend mirror: A=110 (high), B=90 (low); zone 97.52-102.48.
SHORT_LEGS = [100, 110, 90]
SHORT_TAIL = [92, 95, 98, 100, 99, 97, 94, 90, 88]


class TestFibonacciRetracement(unittest.TestCase):
    def test_registered(self):
        self.assertIn("fibonacci_retracement", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["atr14"]).all())

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

    def test_golden_zone_levels(self):
        df = indicators.add_indicators(_legs_frame(LONG_LEGS, LONG_TAIL))
        act = df[df["fib_dir"] == 1.0]
        self.assertTrue(len(act) > 0)
        self.assertAlmostEqual(act["fib_zone_lo"].iloc[0], 97.522, places=2)
        self.assertAlmostEqual(act["fib_zone_hi"].iloc[0], 102.478, places=2)
        self.assertAlmostEqual(act["fib_a"].iloc[0], 89.5, places=4)
        self.assertAlmostEqual(act["fib_b"].iloc[0], 110.5, places=4)

    def test_long_entry_on_first_green_close_in_zone(self):
        df = _run(_legs_frame(LONG_LEGS, LONG_TAIL))
        # Touch at bar 44 (low 101.5 <= 102.48), red closes at 44-45,
        # first green close in/above the zone at bar 46 (101).
        self.assertEqual(int(df["fib_touched"].iloc[44]), 1)
        self.assertTrue(df.loc[46, "long_entry"])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_short_entry_on_first_red_close_in_zone(self):
        df = _run(_legs_frame(SHORT_LEGS, SHORT_TAIL))
        # Touch at bar 44 (high 98.5 >= 97.52), green closes at 44-45,
        # first red close in/below the zone at bar 46 (99).
        self.assertEqual(int(df["fib_touched"].iloc[44]), 1)
        self.assertTrue(df.loc[46, "short_entry"])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_long_exit_at_old_high(self):
        df = _run(_legs_frame(LONG_LEGS, LONG_TAIL))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())
        entry_i = df.index[df["long_entry"]][0]
        exit_i = df.index[df["long_exit"]][0]
        self.assertGreater(exit_i, entry_i)
        self.assertGreaterEqual(df.loc[exit_i, "c"], 110.5)

    def test_no_lookahead_flat(self):
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_touch(self):
        # Pullback never reaches the zone; price runs straight to B.
        df = _run(_legs_frame(LONG_LEGS, [108, 109, 110, 111, 112]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_when_pullback_blows_through_a(self):
        # All-red slide through A with no green close in the zone.
        df = _run(_legs_frame(LONG_LEGS, [108, 105, 102, 100, 98, 95, 92, 89, 88]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_with_short_leg(self):
        # Impulse leg 0.5 points, far below 1.0x ATR: no swing, no setup.
        closes = [100.0] * 30
        for a, b in [(100, 80), (80, 80.5), (80.5, 80.2)]:
            for k in range(1, 7):
                closes.append(a + (b - a) * k / 6)
        closes.extend([80.6, 81.0, 81.5])
        arr = np.array(closes)
        df = _run(_frame(arr, highs=arr + 0.05, lows=arr - 0.05))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
