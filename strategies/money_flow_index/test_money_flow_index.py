"""Money Flow Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

import strategies.money_flow_index  # noqa: F401  (registers SPEC)
from strategies.money_flow_index import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(pairs, vols=None):
    o = np.array([p[0] for p in pairs], dtype=float)
    c = np.array([p[1] for p in pairs], dtype=float)
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    n = len(pairs)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    v = np.full(n, 100.0) if vols is None else np.array(vols, dtype=float)
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


def _signal_frame(mfi):
    n = len(mfi)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.full(n, 100.0), "h": np.full(n, 101.0),
                         "l": np.full(n, 99.0), "c": np.full(n, 100.0),
                         "v": np.full(n, 100.0), "mfi": mfi})


class TestMoneyFlowIndex(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        self.assertIn("mfi", df.columns)
        self.assertIn("atr", df.columns)
        self.assertFalse(df["mfi"].iloc[risk.WARMUP:].isna().any())
        sub = df["mfi"].iloc[risk.WARMUP:]
        self.assertTrue(((sub >= 0) & (sub <= 100)).all())

    def test_all_down_window_gives_mfi_zero(self):
        pairs = [(200 - 2 * i, 200 - 2 * i) for i in range(20)]
        df = indicators.add_indicators(_frame(pairs))
        self.assertEqual(df["mfi"].iloc[-1], 0.0)

    def test_all_up_window_gives_mfi_100(self):
        pairs = [(100 + 2 * i, 100 + 2 * i) for i in range(20)]
        df = indicators.add_indicators(_frame(pairs))
        self.assertEqual(df["mfi"].iloc[-1], 100.0)

    def test_flat_window_gives_mfi_50(self):
        pairs = [(100, 100)] * 20
        df = indicators.add_indicators(_frame(pairs))
        self.assertEqual(df["mfi"].iloc[-1], 50.0)

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_constructed_long_fires(self):
        # 16 falling bars drive MFI to 0; rising bars pull it
        # back above 20 (oversold recovery).
        pairs = [(200 - 2 * i, 200 - 2 * i) for i in range(16)]
        pairs += [(170 + 2 * i, 170 + 2 * i) for i in range(10)]
        df = _run(_frame(pairs))
        self.assertTrue(df["long_entry"].any())
        i = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertGreater(df["mfi"].iloc[i], 20)
        self.assertLessEqual(df["mfi"].iloc[i - 1], 20)

    def test_constructed_short_fires(self):
        pairs = [(100 + 2 * i, 100 + 2 * i) for i in range(16)]
        pairs += [(130 - 2 * i, 130 - 2 * i) for i in range(10)]
        df = _run(_frame(pairs))
        self.assertTrue(df["short_entry"].any())
        i = int(np.argmax(df["short_entry"].to_numpy()))
        self.assertLess(df["mfi"].iloc[i], 80)
        self.assertGreaterEqual(df["mfi"].iloc[i - 1], 80)

    def test_exit_on_midline_cross(self):
        # MFI falling through 50: a long exit, no entry.
        df = signals.add_signals(_signal_frame(
            [60.0, 55.0, 45.0, 40.0]))
        self.assertTrue(df["long_exit"].iloc[2])
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
        self.assertEqual(risk.WARMUP, 20)

    def test_registry_import(self):
        self.assertIn("money_flow_index", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["money_flow_index"].slug, "money_flow_index")
        self.assertEqual(strategies.money_flow_index.SPEC.slug, "money_flow_index")

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
