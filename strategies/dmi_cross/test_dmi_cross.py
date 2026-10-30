"""DMI cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

import strategies.dmi_cross  # noqa: F401  (registers SPEC)
from strategies.dmi_cross import indicators, risk, signals
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


def _signal_frame(plus, minus, adx):
    n = len(plus)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.full(n, 100.0), "h": np.full(n, 101.0),
                         "l": np.full(n, 99.0), "c": np.full(n, 100.0),
                         "v": np.full(n, 100.0),
                         "plus_di": plus, "minus_di": minus, "adx": adx})


class TestDmiCross(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("adx", "plus_di", "minus_di", "atr"):
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].iloc[risk.WARMUP:].isna().any(), col)
        self.assertTrue(((df["adx"].iloc[risk.WARMUP:] >= 0)
                         & (df["adx"].iloc[risk.WARMUP:] <= 100)).all())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_constructed_long_fires(self):
        # 40 falling bars build -DI dominance and ADX > 20,
        # then 15 rising bars flip +DI above -DI.
        pairs = [(200 - 2 * i, 200 - 2 * i) for i in range(40)]
        pairs += [(122 + 3 * i, 122 + 3 * i) for i in range(15)]
        df = _run(_frame(pairs))
        self.assertTrue(df["long_entry"].any())
        i = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreater(df["plus_di"].iloc[i], df["minus_di"].iloc[i])
        self.assertGreater(df["adx"].iloc[i], 20)

    def test_constructed_short_fires(self):
        pairs = [(100 + 2 * i, 100 + 2 * i) for i in range(40)]
        pairs += [(178 - 3 * i, 178 - 3 * i) for i in range(15)]
        df = _run(_frame(pairs))
        self.assertTrue(df["short_entry"].any())
        i = int(np.argmax(df["short_entry"].to_numpy()))
        self.assertGreater(df["minus_di"].iloc[i], df["plus_di"].iloc[i])
        self.assertGreater(df["adx"].iloc[i], 20)

    def test_weak_adx_blocks_entry(self):
        # Same DI cross, ADX stuck at 15: no entry.
        df = signals.add_signals(_signal_frame(
            [10.0] * 10 + [20.0], [20.0] * 10 + [10.0], [15.0] * 11))
        self.assertFalse(df["long_entry"].any())

    def test_strong_adx_allows_entry(self):
        df = signals.add_signals(_signal_frame(
            [10.0] * 10 + [20.0], [20.0] * 10 + [10.0], [25.0] * 11))
        self.assertTrue(df["long_entry"].iloc[-1])

    def test_exit_on_opposite_cross(self):
        # +DI crosses below -DI: a long exit, no short entry
        # gate issue (ADX 25 passes the gate, but the point here
        # is the exit column itself).
        df = signals.add_signals(_signal_frame(
            [20.0] * 10 + [10.0], [10.0] * 10 + [20.0], [25.0] * 11))
        self.assertTrue(df["long_exit"].iloc[-1])
        self.assertTrue(df["short_entry"].iloc[-1])

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
        self.assertEqual(risk.WARMUP, 40)

    def test_registry_import(self):
        self.assertIn("dmi_cross", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["dmi_cross"].slug, "dmi_cross")
        self.assertEqual(strategies.dmi_cross.SPEC.slug, "dmi_cross")

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
