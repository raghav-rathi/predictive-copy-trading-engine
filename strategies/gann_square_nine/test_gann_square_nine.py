"""Gann Square of Nine tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.gann_square_nine import indicators, risk, signals


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=130, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


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


class TestGannSquareNine(unittest.TestCase):
    def test_registered(self):
        self.assertIn("gann_square_nine", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Price 100: sqrt = 10, base = 10, so the ladder is
        # L0 = 100, L1 = 10.25^2 = 105.0625, next up 10.5^2 = 110.25,
        # next down 9.75^2 = 95.0625.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        row = df.iloc[10]
        self.assertAlmostEqual(row["gann_level_above"], 105.0625, places=9)
        self.assertAlmostEqual(row["gann_level_below"], 100.0, places=9)
        self.assertAlmostEqual(row["gann_next_up"], 110.25, places=9)
        self.assertAlmostEqual(row["gann_next_down"], 95.0625, places=9)
        self.assertAlmostEqual(row["gann_dist_above_pct"], 0.050625, places=9)
        self.assertAlmostEqual(row["gann_dist_below_pct"], 0.0, places=9)
        self.assertTrue(df.iloc[0]["gann_level_above"] != df.iloc[0]["gann_level_above"])  # NaN on bar 0

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[1:]
        self.assertTrue(np.isfinite(tail["gann_level_above"]).all())
        self.assertTrue(np.isfinite(tail["gann_level_below"]).all())
        # Level below <= prior close < level above, by construction.
        prev = df["c"].shift(1)
        self.assertTrue((tail["gann_level_below"] <= prev.iloc[1:] + 1e-9).all())
        self.assertTrue((tail["gann_level_above"] > prev.iloc[1:]).all())
        # 45-degree step: sqrt(next_up) - sqrt(level_above) == 0.25.
        self.assertTrue(np.allclose(
            np.sqrt(tail["gann_next_up"]) - np.sqrt(tail["gann_level_above"]), 0.25))

    def test_indicator_values_uptrend(self):
        # Steady 0.3%/bar rally from 10000 (BTC-scale): the ladder
        # spacing there is ~0.5%, so entries must fire.
        closes = 10000 * (1.003 ** np.arange(200))
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.WARMUP, 50)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_cross(self):
        # Prior close 10001: sqrt ~ 100.005, base 100, level above
        # 100.25^2 = 10050.0625, 0.49% above the prior close (passes
        # the 0.5% filter). Close 10060 crosses it.
        df = _run(_frame([10001.0, 10001.0, 10060.0, 10055.0]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_cross(self):
        # Same setup downward: level below is 100^2 = 10000, 0.01%
        # below the prior close; close 9990 crosses below it.
        df = _run(_frame([10001.0, 10001.0, 9990.0, 9995.0]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_no_entry_when_level_too_far(self):
        # Price 100: level above is 105.0625, 5.06% away — the 0.5%
        # filter blocks the entry even though the close crosses it.
        df = _run(_frame([100.0, 100.0, 106.0, 107.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_long_exit_on_target(self):
        # Entry level 10050.0625, next level up (100.5)^2 = 10100.25.
        df = _run(_frame([10001.0, 10001.0, 10060.0, 10105.0]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[3])
        self.assertFalse(df["short_exit"].iloc[3])

    def test_long_exit_back_below_entry_level(self):
        # Close 10040 falls back below the entry level 10050.0625.
        df = _run(_frame([10001.0, 10001.0, 10060.0, 10040.0]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[3])

    def test_short_exit(self):
        # Short entry level 10000; close 10005 rises back above it.
        df = _run(_frame([10001.0, 10001.0, 9990.0, 10005.0]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertTrue(df["short_exit"].iloc[3])
        # And reaching the next level down (99.75^2 = 9950.0625) exits.
        df = _run(_frame([10001.0, 10001.0, 9990.0, 9940.0]))
        self.assertTrue(df["short_exit"].iloc[3])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_determinism(self):
        # Appending different future bars must not change earlier signals.
        closes = list(10000 * (1.003 ** np.arange(100)))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [20000.0] * 50))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue((df1[col].iloc[:100] == df2[col].iloc[:100]).all())

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["gann_level_above"].iloc[1:].notna().all())


if __name__ == "__main__":
    unittest.main()
