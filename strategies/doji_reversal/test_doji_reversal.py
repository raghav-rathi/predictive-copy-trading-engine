"""Tests for doji_reversal. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.doji_reversal import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame_from_close(c, seed=7, vol=100.0):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    # Fixed offsets (not sequential RNG draws): the truncated frame must
    # contain exactly the full frame's first bars, or the no-lookahead
    # test compares two different inputs instead of one causal pipeline.
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    v = np.full(n, vol)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _ohlc(o, h, l, c, v=None):
    o = np.asarray(o, dtype=float); h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float); c = np.asarray(c, dtype=float)
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.asarray(v, dtype=float)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestDojiReversal(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        df = _run(_frame_from_close(np.concatenate([np.linspace(100, 80, 60), np.linspace(80, 120, 60)])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_flat_data_no_entries(self):
        df = _run(_frame_from_close(np.full(120, 100.0)))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        series = np.concatenate([np.linspace(100, 80, 60), np.linspace(80, 120, 60)])
        full = _run(_frame_from_close(series))
        trunc = _run(_frame_from_close(series[:100]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        self.assertIn("doji_reversal", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["doji_reversal"].slug, "doji_reversal")
        self.assertEqual(risk.WARMUP, 15)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)

    def test_backtest_smoke_on_synthetic(self):
        df = _run(_frame_from_close(np.concatenate([np.linspace(100, 80, 100), np.linspace(80, 130, 100)])))
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h", warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("net_pnl_usd", m)
        self.assertIn("trades", m)

    def test_doji_fires_at_low(self):
        o, h, l, c = [], [], [], []
        for i in range(12):
            px = 120 - i
            o.append(px + 0.5); c.append(px); h.append(px + 1.0); l.append(px - 1.0)
        # Doji at a fresh low: body 0, range 1.
        o.append(108.0); c.append(108.0); h.append(108.5); l.append(107.5)
        df = _run(_ohlc(o, h, l, c))
        self.assertTrue(df["long_entry"].any())

    def test_midrange_doji_ignored(self):
        # Doji NOT at an extreme must not fire.
        o, h, l, c = [], [], [], []
        for i in range(12):
            px = 100 + 0.1 * i
            o.append(px); c.append(px + 0.5); h.append(px + 1.0); l.append(px - 1.0)
        o.append(101.0); c.append(101.0); h.append(101.5); l.append(100.5)
        df = _run(_ohlc(o, h, l, c))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
