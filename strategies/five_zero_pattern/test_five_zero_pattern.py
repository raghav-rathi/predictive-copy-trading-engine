"""5-0 Pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.five_zero_pattern import indicators, risk, signals
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


# Bullish 5-0: 0=100, X=110 (XA=10), A=102, B=115 (AB=13 = 1.30x XA),
# C=91.6 (BC=23.4 = 1.80x AB). D = 91.6 + 0.5*23.4 = 103.3.
LONG_LEGS = [105, 100, 110, 102, 115, 91.6]
LONG_TAIL = [94, 96.5, 99, 101.5, 104, 106, 108, 108, 108]
# Bearish mirror: 0=100, X=90 (XA=10), A=98, B=85 (AB=13),
# C=108.4 (BC=23.4). D = 108.4 - 11.7 = 96.7.
SHORT_LEGS = [95, 100, 90, 98, 85, 108.4]
SHORT_TAIL = [106, 103, 100, 97, 95, 93, 91, 91, 91]


class TestFiveZeroPattern(unittest.TestCase):
    def test_registered(self):
        self.assertIn("five_zero_pattern", registry.REGISTRY)

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
        self.assertTrue(df["fz_bullish"].any())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_on_completed_pattern(self):
        df = _run(_legs_frame(SHORT_LEGS, SHORT_TAIL))
        self.assertTrue(df["fz_bearish"].any())
        self.assertTrue(df["short_entry"].any())

    def test_no_lookahead_flat(self):
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_before_d_reached(self):
        # C completes but price never rallies back to the D level
        # (103.3): no long entry.
        df = _run(_legs_frame(LONG_LEGS, [92, 93, 94, 95, 96, 97]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_with_wrong_ratios(self):
        # AB only 1.0x XA and BC only 1.0x AB: not a 5-0 pattern.
        df = _run(_legs_frame([105, 100, 110, 102, 112, 102],
                              [104, 106, 108, 110]))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
