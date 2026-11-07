"""Chaikin Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chaikin_oscillator import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


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


def _cho_frame(direction=1, n_each=100):
    """Three phases. direction=1: A close at the low (MFV = -v, price
    drifting down), B close at the high (MFV = +v, price rising steeply
    so the close clears SMA(50) by the time CHO crosses up), C close
    at the low again (MFV = -v, CHO crosses back down -> long exit).
    direction=-1 mirrors it (short entry, then short exit)."""
    n = 3 * n_each
    idx = np.arange(n)
    if direction == 1:
        c = np.concatenate([
            np.linspace(100, 95, n_each),
            np.linspace(95, 130, n_each),
            np.linspace(130, 100, n_each),
        ])
        at_high = (idx >= n_each) & (idx < 2 * n_each)
    else:
        c = np.concatenate([
            np.linspace(100, 105, n_each),
            np.linspace(105, 70, n_each),
            np.linspace(70, 100, n_each),
        ])
        at_high = (idx < n_each) | (idx >= 2 * n_each)
    h = np.where(at_high, c, c + 1.0)
    l = np.where(at_high, c - 1.0, c)
    o = np.concatenate([[c[0]], c[:-1]])
    return _frame(c, highs=h, lows=l, vols=np.full(n, 100.0), opens=o)


class TestChaikinOscillator(unittest.TestCase):
    def test_registered(self):
        self.assertIn("chaikin_oscillator", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_mfv_sign(self):
        # Phase A closes at the range low -> MFV = -100 exactly;
        # phase B closes at the range high -> MFV = +100.
        df = indicators.add_indicators(_cho_frame(direction=1))
        self.assertTrue(np.allclose(df["co_mfv"].iloc[10:100], -100.0))
        self.assertTrue(np.allclose(df["co_mfv"].iloc[110:200], 100.0))
        # ADL falls through phase A, rises through phase B.
        self.assertLess(df["co_adl"].iloc[99], df["co_adl"].iloc[10])
        self.assertGreater(df["co_adl"].iloc[199], df["co_adl"].iloc[100])

    def test_indicator_values_cho_sign(self):
        df = indicators.add_indicators(_cho_frame(direction=1))
        tail_a = df["co_cho"].iloc[50:100]
        self.assertTrue(np.isfinite(tail_a).all())
        self.assertTrue((tail_a < 0).all())
        # CHO is EMA(3, ADL) - EMA(10, ADL): verify at one bar.
        i = 150
        adl = df["co_adl"]
        e3 = adl.ewm(span=3, adjust=False, min_periods=3).mean().iloc[i]
        e10 = adl.ewm(span=10, adjust=False, min_periods=10).mean().iloc[i]
        self.assertAlmostEqual(df["co_cho"].iloc[i], e3 - e10, places=6)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_zero_cross_up(self):
        df = _run(_cho_frame(direction=1))
        self.assertTrue(df["long_entry"].any())
        idx = df.index[df["long_entry"]][0]
        self.assertGreater(df["co_cho"].iloc[idx], 0)
        self.assertLessEqual(df["co_cho"].iloc[idx - 1], 0)
        self.assertGreater(df["c"].iloc[idx], df["sma50"].iloc[idx])

    def test_short_entry_on_zero_cross_down(self):
        df = _run(_cho_frame(direction=-1))
        self.assertTrue(df["short_entry"].any())
        idx = df.index[df["short_entry"]][0]
        self.assertLess(df["co_cho"].iloc[idx], 0)
        self.assertGreaterEqual(df["co_cho"].iloc[idx - 1], 0)
        self.assertLess(df["c"].iloc[idx], df["sma50"].iloc[idx])

    def test_exit_on_reverse_cross(self):
        # Long exit fires on the reverse (downward) zero cross.
        df = _run(_cho_frame(direction=1))
        self.assertTrue(df["long_exit"].any())
        idx = df.index[df["long_exit"]][0]
        self.assertLess(df["co_cho"].iloc[idx], 0)
        # Short exit fires on the upward zero cross.
        df = _run(_cho_frame(direction=-1))
        self.assertTrue(df["short_exit"].any())

    def test_no_entry_when_sma_filter_fails(self):
        # CHO crosses up, but the close sits below SMA(50): no long.
        # Build it by flipping phase B's price drift down while MFV
        # stays positive (close at range high, falling).
        n_each = 100
        c_a = np.linspace(100, 95, n_each)
        c_b = np.linspace(95, 85, n_each)
        c = np.concatenate([c_a, c_b])
        h = np.where(np.arange(2 * n_each) < n_each, c + 1.0, c)
        l = np.where(np.arange(2 * n_each) < n_each, c, c - 1.0)
        o = np.concatenate([[c[0]], c[:-1]])
        df = _run(_frame(c, highs=h, lows=l,
                         vols=np.full(2 * n_each, 100.0), opens=o))
        self.assertTrue(df["co_cho"].max() > 0)  # CHO did cross up
        self.assertFalse(df["long_entry"].any())

    def test_no_lookahead_flat(self):
        df = _run(_frame([100.0] * 200))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(np.allclose(df["co_cho"].iloc[risk.WARMUP:], 0.0))

    def test_edge_zero_range_and_short_frame(self):
        # h == l bars: MFV is 0, no NaNs, no crash.
        df = _run(_frame([100.0] * 150, highs=[100.0] * 150,
                         lows=[100.0] * 150))
        self.assertTrue(np.isfinite(df["co_cho"].iloc[risk.WARMUP:]).all())
        self.assertTrue(np.allclose(df["co_mfv"], 0.0))
        self.assertFalse(df["long_entry"].any())
        # Short frame: no crash, no entries.
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
