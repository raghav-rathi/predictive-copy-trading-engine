"""KAMA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.kama import indicators, risk, signals
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


class TestKama(unittest.TestCase):
    def test_registered(self):
        self.assertIn("kama", registry.REGISTRY)

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

    def test_kama_flat_series_stays_flat(self):
        # No movement -> ER = 0, KAMA must sit on the price.
        closes = [100.0] * 120
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(np.allclose(df["kama"].iloc[10:], 100.0, atol=1e-9))

    def test_kama_tracks_straight_line(self):
        # Perfect trend -> ER = 1, fastest smoothing; KAMA must hug the line.
        closes = [100.0 + i for i in range(120)]
        df = indicators.add_indicators(_frame(closes))
        tail_gap = (df["c"] - df["kama"]).iloc[-20:]
        self.assertTrue((tail_gap >= 0).all())
        self.assertLess(tail_gap.max(), 3.0)

    def test_long_entry_on_cross_above_rising_kama(self):
        closes = [100.0] * 40 + [100.0 + 0.5 * i for i in range(60)]
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        idx = df.index[df["long_entry"]][0]
        self.assertGreater(df["kama"].iloc[idx], df["kama"].iloc[idx - 1])


if __name__ == "__main__":
    unittest.main()
