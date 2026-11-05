"""ZLEMA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.zlema import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest
from strategies import base as B


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


class TestZlema(unittest.TestCase):
    def test_registered(self):
        self.assertIn("zlema", registry.REGISTRY)

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

    def test_zlema_faster_than_ema_on_step(self):
        # Price steps 100 -> 120; 5 bars after the step ZLEMA(20) must be
        # closer to the new level than a plain EMA(20).
        closes = [100.0] * 60 + [120.0] * 20
        df = indicators.add_indicators(_frame(closes))
        plain_ema = B.ema(pd.Series(closes), 20)
        i = 65
        self.assertGreater(df["zlema20"].iloc[i], plain_ema.iloc[i])
        self.assertLess(abs(df["zlema20"].iloc[i] - 120.0),
                        abs(plain_ema.iloc[i] - 120.0))

    def test_long_entry_on_fast_cross_above_slow(self):
        # 100 flat bars first so ZLEMA(50) is finite before the move, then a
        # steady rise: the fast ZLEMA must cross above the slow one.
        closes = [100.0] * 100 + list(100 * (1.01 ** i) for i in range(60))
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
