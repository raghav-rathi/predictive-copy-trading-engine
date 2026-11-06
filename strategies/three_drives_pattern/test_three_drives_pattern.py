"""Three Drives Pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.three_drives_pattern import indicators, risk, signals
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


# Bullish Three Drives: H0=110, D1=100, P1=106.18 (0.618 retrace of
# drive 10), D2=98.32 (1.272x pullback 6.18), P2=103.18 (0.618 of
# drive 7.86), D3=96.99 (1.272x pullback 4.86). Symmetric 6-bar drives.
LONG_LEGS = [105, 110, 100, 106.18, 98.32, 103.18, 96.99]
LONG_TAIL = [98, 100, 102, 104, 106, 108, 110, 110, 110]
# Bearish mirror: L0=90, D1=100, P1=93.82, D2=101.68, P2=96.82,
# D3=103.01.
SHORT_LEGS = [95, 90, 100, 93.82, 101.68, 96.82, 103.01]
SHORT_TAIL = [102, 100, 98, 96, 94, 92, 90, 90, 90]


class TestThreeDrivesPattern(unittest.TestCase):
    def test_registered(self):
        self.assertIn("three_drives_pattern", registry.REGISTRY)

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
        self.assertTrue(df["td_bullish"].any())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_on_completed_pattern(self):
        df = _run(_legs_frame(SHORT_LEGS, SHORT_TAIL))
        self.assertTrue(df["td_bearish"].any())
        self.assertTrue(df["short_entry"].any())

    def test_no_lookahead_flat(self):
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_before_d3_completes(self):
        # Pattern legs complete at D3 but the tail falls instead of
        # reversing up: no reversal bar, so no long entry.
        df = _run(_legs_frame(LONG_LEGS, [96.5, 96.0, 95.5, 95.0]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_with_wrong_ratios(self):
        # Same shape but pullbacks retrace only ~0.30 of the prior
        # drive (not 0.618/0.786): not a Three Drives pattern.
        df = _run(_legs_frame([105, 110, 100, 103.0, 98.0, 100.0, 96.0],
                              [98, 100, 102, 104]))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
