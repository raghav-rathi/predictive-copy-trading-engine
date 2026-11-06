"""Wolfe Wave tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wolfe_wave import indicators, risk, signals
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
    """Closes: flat preamble at legs[0], then linear legs to each next
    price over `step` bars, then the tail closes appended."""
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


# Bullish Wolfe: L1=90, H2=100, L3=88, H4=93, L5=80 (below 1-3 line
# ~86 at point 5; lines 1-3 and 2-4 converge ahead), then rally
# crossing back above the 1-3 line.
LONG_LEGS = [100, 90, 100, 88, 93, 80]
LONG_TAIL = [82, 84, 86, 88, 90, 92, 94, 96, 98, 98, 98, 98]
# Bearish mirror: H1=110, L2=100, H3=112, L4=107, H5=120 (above 1-3
# line ~114 at point 5), then sell-off crossing back below the line.
SHORT_LEGS = [100, 110, 100, 112, 107, 120]
SHORT_TAIL = [118, 116, 114, 112, 110, 108, 106, 104, 102, 102, 102, 102]


class TestWolfeWave(unittest.TestCase):
    def test_registered(self):
        self.assertIn("wolfe_wave", registry.REGISTRY)

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

    def test_long_entry_on_completed_wave(self):
        df = _run(_legs_frame(LONG_LEGS, LONG_TAIL))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["ww_bullish"].any())

    def test_short_entry_on_completed_wave(self):
        df = _run(_legs_frame(SHORT_LEGS, SHORT_TAIL))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue(df["ww_bearish"].any())

    def test_no_lookahead_flat(self):
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_before_point5_completes(self):
        # Same bullish wave but the tail is cut off right after point 5
        # is confirmed: no close has crossed back above the 1-3 line yet.
        df = _run(_legs_frame(LONG_LEGS, [80.5, 81.0]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_without_point5(self):
        # Only 4 pivots (no point 5 break below the 1-3 line): no wave.
        df = _run(_legs_frame([100, 90, 100, 88, 93], [94, 95, 96, 97, 98]))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
