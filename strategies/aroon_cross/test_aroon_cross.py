"""Aroon cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

import strategies.aroon_cross  # noqa: F401  (registers SPEC)
from strategies.aroon_cross import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(pairs):
    o = np.array([p[0] for p in pairs], dtype=float)
    c = np.array([p[1] for p in pairs], dtype=float)
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
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


def _signal_frame(up, down):
    n = len(up)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.full(n, 100.0), "h": np.full(n, 101.0),
                         "l": np.full(n, 99.0), "c": np.full(n, 100.0),
                         "v": np.full(n, 100.0),
                         "aroon_up": up, "aroon_down": down})


class TestAroonCross(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("aroon_up", "aroon_down", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)
        sub = df.iloc[risk.WARMUP:]
        self.assertTrue(((sub["aroon_up"] >= 0) & (sub["aroon_up"] <= 100)).all())
        self.assertTrue(((sub["aroon_down"] >= 0) & (sub["aroon_down"] <= 100)).all())

    def test_new_high_gives_aroon_up_100(self):
        pairs = [(100, 100)] * 25 + [(200, 200)]
        df = indicators.add_indicators(_frame(pairs))
        self.assertEqual(df["aroon_up"].iloc[-1], 100.0)

    def test_new_low_gives_aroon_down_100(self):
        pairs = [(100, 100)] * 25 + [(50, 50)]
        df = indicators.add_indicators(_frame(pairs))
        self.assertEqual(df["aroon_down"].iloc[-1], 100.0)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_constructed_long_fires(self):
        # 30 falling bars: Aroon Down pinned at 100, Up near 4.
        # One bar jumping above every prior high flips Up to 100.
        pairs = [(200 - 2 * i, 200 - 2 * i) for i in range(30)]
        pairs += [(300, 300)]
        df = _run(_frame(pairs))
        self.assertTrue(df["long_entry"].any())
        i = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreater(df["aroon_up"].iloc[i], 70)

    def test_constructed_short_fires(self):
        pairs = [(100 + 2 * i, 100 + 2 * i) for i in range(30)]
        pairs += [(50, 50)]
        df = _run(_frame(pairs))
        self.assertTrue(df["short_entry"].any())
        i = int(np.argmax(df["short_entry"].to_numpy()))
        self.assertGreater(df["aroon_down"].iloc[i], 70)

    def test_weak_cross_blocked_by_70_gate(self):
        # Up crosses Down but only reaches 60: no long entry.
        df = signals.add_signals(_signal_frame(
            [40.0] * 10 + [60.0], [50.0] * 10 + [55.0]))
        self.assertFalse(df["long_entry"].any())

    def test_exit_on_opposite_cross(self):
        df = signals.add_signals(_signal_frame(
            [80.0] * 10 + [40.0], [40.0] * 10 + [80.0]))
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)

    def test_registry_import(self):
        self.assertIn("aroon_cross", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["aroon_cross"].slug, "aroon_cross")
        self.assertEqual(strategies.aroon_cross.SPEC.slug, "aroon_cross")

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
