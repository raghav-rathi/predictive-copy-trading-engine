"""RSI(2) System tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi2_system import indicators, risk, signals
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


def _uptrend_drop_frame():
    # Gentle uptrend (close stays above SMA(200)), then a sharp 2-bar
    # -1.5% drop, then a recovery. RSI(2) collapses to ~3 on the drop.
    closes = [100.0 + 0.05 * i for i in range(260)]
    closes.append(closes[-1] * 0.985)
    closes.append(closes[-1] * 0.985)
    for _ in range(10):
        closes.append(closes[-1] * 1.01)
    return _frame(closes)


def _downtrend_spike_frame():
    # Gentle downtrend (close stays below SMA(200)), then a sharp 2-bar
    # +1.5% spike, then a fade.
    closes = [100.0 - 0.05 * i for i in range(260)]
    closes.append(closes[-1] * 1.015)
    closes.append(closes[-1] * 1.015)
    for _ in range(10):
        closes.append(closes[-1] * 0.99)
    return _frame(closes)


class TestRsi2System(unittest.TestCase):
    def test_registered(self):
        self.assertIn("rsi2_system", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_rsi2_collapses_on_sharp_drop(self):
        df = indicators.add_indicators(_uptrend_drop_frame())
        self.assertLessEqual(df["rsi2"].iloc[261], 5.0)
        self.assertGreater(df["c"].iloc[261], df["sma200"].iloc[261])

    def test_long_entry_on_oversold_uptrend(self):
        df = _run(_uptrend_drop_frame())
        self.assertTrue(df["long_entry"].any())

    def test_short_entry_on_overbought_downtrend(self):
        df = _run(_downtrend_spike_frame())
        self.assertTrue(df["short_entry"].any())

    def test_exit_after_long_entry(self):
        df = _run(_uptrend_drop_frame())
        entry_idx = int(np.argmax(df["long_entry"].to_numpy()))
        self.assertTrue(df["long_exit"].iloc[entry_idx:].any())

    def test_no_long_entry_without_trend_filter(self):
        # Sharp drop while the close is BELOW SMA(200): no long entry
        # even though RSI(2) is oversold.
        closes = [100.0 - 0.05 * i for i in range(260)]
        closes.append(closes[-1] * 0.985)
        closes.append(closes[-1] * 0.985)
        df = _run(_frame(closes))
        self.assertTrue((df["rsi2"].iloc[260:] <= 5).any())
        self.assertFalse(df["long_entry"].any())

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame(n=500))
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["rsi2"]).all())
        self.assertTrue(np.isfinite(tail["sma200"]).all())
        self.assertTrue(np.isfinite(tail["sma5"]).all())

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame(n=500))
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        closes = [100.0] * 300
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_short_frame_no_crash(self):
        df = _run(_frame([100.0, 101.0, 102.0, 101.0, 100.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
