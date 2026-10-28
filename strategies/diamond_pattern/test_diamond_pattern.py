"""Diamond pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.diamond_pattern import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _diamond_frame(breakout_vol=300.0, breakout_close=104.0):
    # expanding ranges 1.0 -> 5.0 (bars 0-9), contracting 4.5 -> 1.0
    # (bars 10-20), flat center 100, then an upside breakout bar
    ranges = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.0,
              4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 1.0, 1.0, 1.0]
    h = [100.0 + r / 2 for r in ranges]
    l = [100.0 - r / 2 for r in ranges]
    c = [100.0] * len(ranges)
    o = [100.0] * len(ranges)
    v = [100.0] * len(ranges)
    h.append(breakout_close + 0.5)
    l.append(breakout_close - 0.5)
    c.append(breakout_close)
    o.append(100.0)
    v.append(breakout_vol)
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestDiamondPattern(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_diamond_breakout_long_fires(self):
        df = _run(_diamond_frame())
        self.assertTrue(df["long_entry"].any())
        self.assertEqual(int(df["long_entry"].idxmax()), 21)

    def test_breakout_without_volume_does_not_fire(self):
        df = _run(_diamond_frame(breakout_vol=100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_flat_data_no_entries(self):
        n = 60
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({"t": t, "o": np.full(n, 100.0),
                           "h": np.full(n, 100.05), "l": np.full(n, 99.95),
                           "c": np.full(n, 100.0), "v": np.full(n, 100.0)})
        df = _run(df)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        self.assertIn("diamond_pattern", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 50)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
