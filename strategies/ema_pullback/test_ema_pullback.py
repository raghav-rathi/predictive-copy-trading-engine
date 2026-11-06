"""EMA Pullback tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ema_pullback import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes * 1.001
    l = np.array(lows, dtype=float) if lows is not None else closes * 0.999
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
        "o": o, "h": c * 1.001, "l": c * 0.999, "c": c,
        "v": np.full(n, 100.0),
    })


def _long_frame():
    # Steady rise, then a pullback that dips to the EMA(20) band, then a
    # bounce back above EMA(20) with a rising close.
    rise = [100 + 0.5 * i for i in range(70)]
    dip = [134.0, 131.0, 128.0, 126.0, 127.5, 130.0, 132.0]
    tail = [132 + 0.5 * i for i in range(10)]
    return _frame(rise + dip + tail)


def _short_frame():
    # Mirror image: steady fall, pullback up to the EMA(20) band, then a
    # drop back below EMA(20) with a falling close.
    fall = [130 - 0.5 * i for i in range(70)]
    bounce = [96.0, 99.0, 102.0, 104.0, 102.5, 100.0, 98.0]
    tail = [98 - 0.5 * i for i in range(10)]
    return _frame(fall + bounce + tail)


class TestEmaPullback(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ema_pullback", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
            self.assertTrue(np.isfinite(tail[col].dropna()).all())

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

    def test_long_entry_on_pullback_bounce(self):
        df = _run(_long_frame())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_on_pullback_rejection(self):
        df = _run(_short_frame())
        self.assertTrue(df["short_entry"].any())

    def test_no_lookahead_flat_data(self):
        # Flat closes: price sits on its EMAs, never above EMA(20) with a
        # rising close after a touch, so no entry can occur.
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_touch(self):
        # A steady rise with no pullback near EMA(20): the touch condition
        # never fires, so no long entry despite the uptrend.
        rise = [100 + 0.5 * i for i in range(120)]
        df = _run(_frame(rise))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
