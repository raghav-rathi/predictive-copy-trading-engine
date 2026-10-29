"""Abandoned baby tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.abandoned_baby_pattern import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _bars(rows, prefix=30):
    """rows: list of (o, h, l, c, v). Prefix flat bars at 100, vol 100."""
    data = [(100.0, 100.1, 99.9, 100.0, 100.0)] * prefix + list(rows)
    df = pd.DataFrame(data, columns=["o", "h", "l", "c", "v"])
    n = len(df)
    df.insert(0, "t", (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"))
    return df


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


BULL_BABY = [
    (100.0, 101.0, 89.0, 90.0, 100.0),   # long black candle
    (85.0, 86.0, 84.0, 85.0, 100.0),     # doji gapped below (86 < 89)
    (88.0, 99.0, 88.0, 98.0, 500.0),     # white gap-up, close past midpoint 95
]
BEAR_BABY = [
    (90.0, 101.0, 89.0, 100.0, 100.0),   # long white candle
    (105.0, 106.0, 104.0, 105.0, 100.0), # doji gapped above (104 > 101)
    (102.0, 102.0, 91.0, 92.0, 500.0),   # black gap-down, close past midpoint 95
]


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


class TestAbandonedBaby(unittest.TestCase):
    def test_bullish_baby_long(self):
        df = _run(_bars(BULL_BABY))
        self.assertTrue((df["ab_dir"] == 1).any())
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_bearish_baby_short(self):
        df = _run(_bars(BEAR_BABY))
        self.assertTrue((df["ab_dir"] == -1).any())
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_no_gap_no_pattern(self):
        # doji overlaps the first candle: gap condition fails
        rows = [
            (100.0, 101.0, 89.0, 90.0, 100.0),
            (90.0, 91.0, 89.5, 90.0, 100.0),  # doji high 91 > low 89: no gap
            (92.0, 99.0, 92.0, 98.0, 500.0),
        ]
        df = _run(_bars(rows))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_low_volume_no_pattern(self):
        # textbook gaps but third-bar volume below its 20-bar average
        rows = [BULL_BABY[0], BULL_BABY[1], (88.0, 99.0, 88.0, 98.0, 50.0)]
        df = _run(_bars(rows))
        self.assertFalse(df["long_entry"].any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertFalse(tail["atr"].isna().any())

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
        self.assertIn("abandoned_baby_pattern", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 30)

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
