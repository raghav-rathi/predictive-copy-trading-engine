"""Central Pivot Range tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.central_pivot_range import indicators, risk, signals
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


class TestCentralPivotRange(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("cpr_pivot", "cpr_tc", "cpr_bc", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_registered_in_registry(self):
        self.assertIn("central_pivot_range", registry.REGISTRY)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        self.assertTrue(np.isfinite(res.equity).all())

    def test_cpr_hand_computed(self):
        # Two UTC days, 24 hourly bars each. Day 1: high 110, low 90,
        # last close 100 -> Pivot 100, BC 100, TC 100. Day 2 levels must
        # equal 100 across the board (H+L)/2 = 100, (H+L+C)/3 = 100.
        n = 48
        t = (1_700_000_000_000 + __import__("numpy").arange(n) * 3_600_000)
        # Align day 1 to start exactly at a UTC midnight: pick t0 at
        # 2024-01-01 00:00 UTC = 1704067200000.
        t = (1_704_067_200_000 + __import__("numpy").arange(n) * 3_600_000)
        import pandas as pd
        day1_h = [110.0] * 24
        day1_l = [90.0] * 24
        day1_c = [100.0] * 24
        day2 = [105.0] * 24
        df = pd.DataFrame({
            "t": t.astype("int64"),
            "o": day1_c + day2,
            "h": day1_h + [106.0] * 24,
            "l": day1_l + [104.0] * 24,
            "c": day1_c + day2,
            "v": [100.0] * n,
        })
        out = _run(df)
        # Day 2 bars carry day 1's levels: Pivot = BC = TC = 100.
        self.assertAlmostEqual(out["cpr_pivot"].iloc[24], 100.0)
        self.assertAlmostEqual(out["cpr_bc"].iloc[24], 100.0)
        self.assertAlmostEqual(out["cpr_tc"].iloc[24], 100.0)
        # Day 1 bars have no prior day: levels NaN.
        self.assertTrue(out["cpr_pivot"].iloc[:24].isna().all())


if __name__ == "__main__":
    unittest.main()
