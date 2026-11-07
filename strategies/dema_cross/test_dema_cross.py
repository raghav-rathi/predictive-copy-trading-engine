"""DEMA Crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dema_cross import indicators, risk, signals
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


def _v_frame():
    # Downtrend, then a sharp reversal into an uptrend, then a reversal
    # back down: fast DEMA should cross slow in both directions.
    closes = [120.0 - 0.1 * i for i in range(150)]
    closes += [105.0 + 0.2 * i for i in range(150)]
    closes += [135.0 - 0.2 * i for i in range(150)]
    return _frame(closes)


class TestDemaCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("dema_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_dema_equals_close_on_flat(self):
        # On a constant series both DEMAs converge to the price.
        df = indicators.add_indicators(_frame([100.0] * 200))
        self.assertAlmostEqual(df["dema_fast"].iloc[-1], 100.0, places=6)
        self.assertAlmostEqual(df["dema_slow"].iloc[-1], 100.0, places=6)

    def test_fast_above_slow_on_uptrend(self):
        # On a sustained uptrend the fast DEMA leads the slow one.
        closes = [100.0 + 0.2 * i for i in range(200)]
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[100:]
        self.assertTrue((tail["dema_fast"] > tail["dema_slow"]).all())

    def test_dema_less_lag_than_ema(self):
        # DEMA tracks a step change faster than a plain EMA(12):
        # after a step up, DEMA(12) is closer to the new level.
        closes = [100.0] * 100 + [110.0] * 30
        df = indicators.add_indicators(_frame(closes))
        from strategies import base as B
        ema12 = B.ema(pd.Series(closes, dtype=float), 12)
        self.assertGreater(df["dema_fast"].iloc[-1], ema12.iloc[-1])

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["dema_fast"]).all())
        self.assertTrue(np.isfinite(tail["dema_slow"]).all())

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

    def test_both_crosses_on_v_frame(self):
        df = _run(_v_frame())
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["short_entry"].any())

    def test_exits_mirror_reverse_cross(self):
        df = _run(_v_frame())
        self.assertTrue((df["long_exit"] == df["short_entry"]).all())
        self.assertTrue((df["short_exit"] == df["long_entry"]).all())

    def test_no_lookahead_flat(self):
        closes = [100.0] * 200
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_cross_on_pure_trend(self):
        # A single uninterrupted uptrend: at most one long cross, no
        # short cross.
        closes = [100.0 + 0.2 * i for i in range(300)]
        df = _run(_frame(closes))
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
