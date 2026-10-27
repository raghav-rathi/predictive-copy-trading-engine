"""Tests for bat_pattern. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bat_pattern import indicators, risk, signals
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


class TestBatPattern(unittest.TestCase):
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
        self.assertIn("bat_pattern", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["bat_pattern"].slug, "bat_pattern")
        self.assertEqual(risk.WARMUP, 60)

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

    def test_bat_fires_on_synthetic_xabcd(self):
        # Legs of 8 bars: 120->100 (X) ->130 (A) ->115 (B) ->125 (C)
        # ->103.4 (D): AB/XA=0.50, BC/AB=0.667, CD/BC=2.16, AD/XA=0.887.
        import numpy as np
        segs = [(120, 100), (100, 130), (130, 115), (115, 125), (125, 103.4)]
        closes = []
        for a, b in segs:
            closes.extend(np.linspace(a, b, 8, endpoint=False))
        closes.extend([104.0, 105.0, 104.5, 105.0, 104.8, 105.2, 105.0, 105.5, 105.0, 105.5])
        closes = np.asarray(closes, dtype=float)
        o = np.concatenate([[closes[0]], closes[:-1]])
        h = np.maximum(o, closes)
        l = np.minimum(o, closes)
        df = _run(_ohlc(o, h, l, closes))
        self.assertTrue(df["long_entry"].iloc[40:].any())

    def test_gartley_ratios_do_not_fire_bat(self):
        # A Gartley (AD/XA=0.786) must NOT classify as a Bat (0.886).
        import numpy as np
        segs = [(120, 100), (100, 130), (130, 115), (115, 125), (125, 106.4)]
        closes = []
        for a, b in segs:
            closes.extend(np.linspace(a, b, 8, endpoint=False))
        closes.extend([107.0, 108.0, 107.5, 108.0, 107.8, 108.2, 108.0, 108.5, 108.0, 108.5])
        closes = np.asarray(closes, dtype=float)
        o = np.concatenate([[closes[0]], closes[:-1]])
        h = np.maximum(o, closes)
        l = np.minimum(o, closes)
        df = _run(_ohlc(o, h, l, closes))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
