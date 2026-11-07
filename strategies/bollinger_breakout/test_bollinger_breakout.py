"""Bollinger Band squeeze breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_breakout import indicators, risk, signals
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


def _squeeze_breakout_frame(direction=1):
    # 60 flat bars (bandwidth collapses to zero -> squeeze), then a
    # steady breakout, then a pullback back inside the bands.
    closes = [100.0] * 60
    if direction > 0:
        closes += list(np.linspace(101, 118, 20))
        closes += [110.0, 106.0, 104.0, 103.0, 102.0]
    else:
        closes += list(np.linspace(99, 82, 20))
        closes += [90.0, 94.0, 96.0, 97.0, 98.0]
    return _frame(closes)


class TestBollingerBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bollinger_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values(self):
        df = indicators.add_indicators(_frame(list(np.linspace(100, 120, 60))))
        tail = df.iloc[40:]
        self.assertTrue(np.isfinite(tail["bb_mid"]).all())
        # Bands are symmetric around the mid by construction.
        np.testing.assert_allclose(
            tail["bb_upper"] - tail["bb_mid"],
            tail["bb_mid"] - tail["bb_lower"],
            rtol=1e-9,
        )
        np.testing.assert_allclose(
            tail["bb_width"], tail["bb_upper"] - tail["bb_lower"], rtol=1e-9
        )

    def test_squeeze_detected_on_flat(self):
        df = indicators.add_indicators(_frame([100.0] * 80))
        self.assertTrue(df["bb_squeeze"].iloc[60:].all())
        self.assertTrue(df["bb_squeeze_armed"].iloc[60:].all())

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["bb_mid"]).all())
        self.assertTrue(np.isfinite(tail["bb_bandwidth"]).all())

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

    def test_long_entry_after_squeeze(self):
        df = _run(_squeeze_breakout_frame(1))
        self.assertTrue(df["long_entry"].any())
        idx = df.index[df["long_entry"]][0]
        self.assertTrue(df.loc[idx, "c"] > df.loc[idx, "bb_upper"])
        self.assertTrue(df.loc[idx, "bb_squeeze_armed"])

    def test_short_entry_after_squeeze(self):
        df = _run(_squeeze_breakout_frame(-1))
        self.assertTrue(df["short_entry"].any())
        idx = df.index[df["short_entry"]][0]
        self.assertTrue(df.loc[idx, "c"] < df.loc[idx, "bb_lower"])

    def test_exit_on_close_back_inside(self):
        df = _run(_squeeze_breakout_frame(1))
        long_idx = df.index[df["long_entry"]][0]
        self.assertTrue(df.loc[long_idx:, "long_exit"].any())

    def test_no_entry_without_squeeze(self):
        # Volatility grows steadily, so bandwidth is always near its
        # 50-bar high: no squeeze, no armed entry — even though the
        # close eventually breaks above the upper band.
        n = 120
        amp = np.linspace(2, 20, n)
        closes = 100 + amp * np.sin(np.arange(n) * 0.7)
        # Sharp two-bar jump: clears the (wide, high-volatility) upper
        # band in one move.
        closes = list(closes) + [closes[-1] + 25, closes[-1] + 45]
        df = _run(_frame(closes))
        breakout = df["c"] > df["bb_upper"]
        self.assertTrue(breakout.any())
        self.assertFalse(df.loc[breakout, "bb_squeeze_armed"].any())
        self.assertFalse(df["long_entry"].any())

    def test_no_lookahead_flat(self):
        closes = [100.0] * 150
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
