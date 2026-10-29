"""Tasuki gap pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tasuki_gap_pattern import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(pairs):
    o = np.array([p[0] for p in pairs], dtype=float)
    c = np.array([p[1] for p in pairs], dtype=float)
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    n = len(pairs)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


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


# Rising prefix (flat steps of +1 per bar) so the 5-bar trend
# filter passes, then the pattern bars.
def _uptrend_prefix(n=10, start=100):
    return [(start + i, start + i) for i in range(n)]


def _downtrend_prefix(n=10, start=100):
    return [(start - i, start - i) for i in range(n)]


class TestTasukiGapPattern(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        self.assertIn("tasuki_dir", df.columns)
        self.assertIn("atr", df.columns)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["tasuki_dir"].isna().any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_upside_tasuki_long(self):
        # white 110->118, white gap-up 120->128, black opening
        # inside bar 2's body (124) and closing inside the gap
        # (118 < 119 < 120)
        pairs = _uptrend_prefix(10, 100) + [(110, 118), (120, 128), (124, 119)]
        df = _run(_frame(pairs))
        self.assertEqual(df["tasuki_dir"].iloc[-1], 1)
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_downside_tasuki_short(self):
        pairs = _downtrend_prefix(10, 100) + [(90, 82), (80, 72), (76, 81)]
        # gap is (80, 82): third close 81 sits inside it, open 76
        # sits inside bar 2's body [72, 80]
        df = _run(_frame(pairs))
        self.assertEqual(df["tasuki_dir"].iloc[-1], -1)
        self.assertTrue(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_adaptation_close_above_second_open_still_counts(self):
        # continuous-market adaptation: the third candle may close
        # above the second candle's OPEN (122 > 120) as long as it
        # retraces below the second candle's close (122 < 128)
        # and holds above the first candle's close (122 > 118)
        pairs = _uptrend_prefix(10, 100) + [(110, 118), (120, 128), (124, 122)]
        df = _run(_frame(pairs))
        self.assertEqual(df["tasuki_dir"].iloc[-1], 1)
        self.assertTrue(df["long_entry"].any())

    def test_gap_closed_is_not_tasuki(self):
        # upside shape, but the third candle closes BELOW the
        # first candle's close (118) — the gap is fully closed
        pairs = _uptrend_prefix(10, 100) + [(110, 118), (120, 128), (124, 115)]
        df = _run(_frame(pairs))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_trend_no_tasuki(self):
        # same upside shape, but the first pattern candle's close
        # (118) sits BELOW the close 5 bars earlier (130, after a
        # spike-and-fall prefix): no uptrend, so the filter blocks it
        pairs = [(100, 100)] * 5 + [(130, 130)] * 5 + \
            [(110, 118), (120, 128), (124, 119)]
        df = _run(_frame(pairs))
        self.assertFalse(df["long_entry"].any())

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
        self.assertIn("tasuki_gap_pattern", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 20)

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
