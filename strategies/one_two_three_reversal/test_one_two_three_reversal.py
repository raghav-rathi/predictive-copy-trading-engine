"""1-2-3 Reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.one_two_three_reversal import indicators, risk, signals
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


# Bullish 1-2-3: P1=90 (low), P2=100 (rally high, leg 10 >= 1x ATR),
# P3=95 (pullback low holding above P1). Completes on close > 100.
LONG_LEGS = [105, 90, 100, 95]
LONG_TAIL = [96, 98, 101, 103, 105, 106, 106]
# Bearish mirror: P1=100 (high), P2=90 (decline low, leg 10),
# P3=98 (pullback high holding below P1). Completes on close < 90.
SHORT_LEGS = [95, 100, 90, 98]
SHORT_TAIL = [96, 94, 89, 87, 85, 85, 85]


class TestOneTwoThreeReversal(unittest.TestCase):
    def test_registered(self):
        self.assertIn("one_two_three_reversal", registry.REGISTRY)

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

    def test_long_entry_on_completed_pattern(self):
        df = _run(_legs_frame(LONG_LEGS, LONG_TAIL))
        self.assertTrue(df["otr_bullish"].any())
        self.assertTrue(df["long_entry"].any())
        # Entry only on a close above point 2 (100).
        first = df.index[df["long_entry"]][0]
        self.assertGreater(df.loc[first, "c"], 100.0)

    def test_short_entry_on_completed_pattern(self):
        df = _run(_legs_frame(SHORT_LEGS, SHORT_TAIL))
        self.assertTrue(df["otr_bearish"].any())
        self.assertTrue(df["short_entry"].any())
        first = df.index[df["short_entry"]][0]
        self.assertLess(df.loc[first, "c"], 90.0)

    def test_long_exit_below_point3(self):
        df = _run(_legs_frame(LONG_LEGS, [96, 98, 101, 103, 100, 97, 94, 93]))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())
        entry_i = df.index[df["long_entry"]][0]
        exit_i = df.index[df["long_exit"]][0]
        self.assertGreater(exit_i, entry_i)

    def test_no_lookahead_flat(self):
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_before_close_above_p2(self):
        # Pattern completes (P3 confirmed) but price never closes above P2.
        df = _run(_legs_frame(LONG_LEGS, [96, 97, 98, 99, 99.5, 99.0, 98.0]))
        self.assertFalse(df["long_entry"].any())

    def test_void_when_p3_below_p1(self):
        # Pullback low 89 falls below point 1 (90): pattern void.
        df = _run(_legs_frame([105, 90, 100, 89], [92, 93, 94, 95, 96]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_with_short_leg(self):
        # Sharp 20-point drop inflates ATR to ~1.1; the 0.5-point 1->2 leg
        # after it is far below 1.0x ATR: not a pattern, no entry even
        # though the tail closes above the rally high.
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
