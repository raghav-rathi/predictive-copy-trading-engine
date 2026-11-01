"""FVG Mitigation tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fvg_mitigation import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes * 1.001
    l = np.array(lows, dtype=float) if lows is not None else closes * 0.999
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": closes, "h": h, "l": l, "c": closes, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestFvgMitigation(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("atr",):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_registered_in_registry(self):
        self.assertIn("fvg_mitigation", registry.REGISTRY)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        self.assertTrue(np.isfinite(res.equity).all())

    def test_bullish_gap_detected(self):
        # Bars: (h,l) = (100,99), (102,101), (104,103): bar 2 low 103 >
        # bar 0 high 100, so a bullish gap [100, 103] forms at bar 2.
        df = _run(_frame([99.5, 101.5, 103.5],
                          highs=[100.0, 102.0, 104.0],
                          lows=[99.0, 101.0, 103.0]))
        self.assertAlmostEqual(df["bull_gap_bottom"].iloc[2], 100.0)
        self.assertAlmostEqual(df["bull_gap_top"].iloc[2], 103.0)

    def test_mitigation_entry_fires_on_retracement(self):
        # Gap [100, 103] forms at bar 2; bar 3 dips to 102 (inside the
        # gap) and closes at 102.5 (above the bottom): long entry.
        df = _run(_frame([99.5, 101.5, 103.5, 102.5],
                          highs=[100.0, 102.0, 104.0, 103.0],
                          lows=[99.0, 101.0, 103.0, 102.0]))
        self.assertTrue(df["long_entry"].iloc[3])

    def test_no_gap_without_displacement(self):
        # Overlapping bars never form a gap.
        df = _run(_frame([100.0, 100.5, 100.2],
                          highs=[101.0, 101.5, 101.2],
                          lows=[99.0, 99.5, 99.2]))
        self.assertTrue(df["bull_gap_top"].isna().all())
        self.assertTrue(df["bear_gap_top"].isna().all())


if __name__ == "__main__":
    unittest.main()
