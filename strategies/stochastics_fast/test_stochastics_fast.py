"""Fast stochastic %K/%D crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stochastics_fast import indicators, risk, signals
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


def _flat_frame(n=300, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


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


def _long_setup():
    # Rise 100 -> 150 over 250 bars (close above SMA(200)), then a
    # 13-bar dip 149 -> 137, then a bounce to 138.5: %K crosses above
    # %D (3.57 -> 15.38 vs %D 7.60) while %K < 20.
    c = list(np.linspace(100, 150, 250)) + list(np.arange(149, 136, -1)) + [138.5]
    return _frame(c)


def _short_setup():
    # Mirror: decline 150 -> 100 over 250 bars (close below SMA(200)),
    # then a 13-bar rally 101 -> 113, then a dip to 111.5: %K crosses
    # below %D (96.43 -> 84.62 vs %D 92.40) while %K > 80.
    c = list(np.linspace(150, 100, 250)) + list(np.arange(101, 114)) + [111.5]
    return _frame(c)


class TestStochasticsFast(unittest.TestCase):
    def test_registered(self):
        self.assertIn("stochastics_fast", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat 100, h=101, l=99: HH == LL is not the case (range 2),
        # %K = 100*(100-99)/2 = 50, %D = 50, SMA200 = 100.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["stoch_k"], 50.0))
        self.assertTrue(np.allclose(tail["stoch_d"], 50.0))
        self.assertTrue(np.allclose(tail["sma200"], 100.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (250, 300, 399):
            ll = df["l"].iloc[i - 13:i + 1].min()
            hh = df["h"].iloc[i - 13:i + 1].max()
            k = 100.0 * (df["c"].iloc[i] - ll) / (hh - ll)
            self.assertAlmostEqual(df["stoch_k"].iloc[i], k, places=9)
            d = df["stoch_k"].iloc[i - 2:i + 1].mean()
            self.assertAlmostEqual(df["stoch_d"].iloc[i], d, places=9)
            self.assertAlmostEqual(df["sma200"].iloc[i], df["c"].iloc[i - 199:i + 1].mean(), places=9)

    def test_zero_range_guard(self):
        # h == l == c: HH == LL, so %K must be 50, not NaN/inf.
        df = indicators.add_indicators(_frame([100.0] * 300, highs=[100.0] * 300,
                                              lows=[100.0] * 300))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["stoch_k"], 50.0))
        self.assertTrue(np.allclose(tail["stoch_d"], 50.0))
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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

    def test_long_entry_oversold_cross(self):
        df = _run(_long_setup())
        self.assertAlmostEqual(df["stoch_k"].iloc[-1], 15.38, places=1)
        self.assertLess(df["stoch_k"].iloc[-1], 20.0)
        self.assertGreater(df["c"].iloc[-1], df["sma200"].iloc[-1])
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])
        # No exit on the entry bar itself.
        self.assertFalse(df["long_exit"].iloc[-1])

    def test_short_entry_overbought_cross(self):
        df = _run(_short_setup())
        self.assertAlmostEqual(df["stoch_k"].iloc[-1], 84.62, places=1)
        self.assertGreater(df["stoch_k"].iloc[-1], 80.0)
        self.assertLess(df["c"].iloc[-1], df["sma200"].iloc[-1])
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_exit"].iloc[-1])

    def test_no_entry_cross_wrong_zone(self):
        # Same oversold cross shape, but the bounce is bigger (c=145):
        # %K crosses above %D with %K ~66, not < 20, so no entry.
        c = list(np.linspace(100, 150, 250)) + list(np.arange(149, 136, -1)) + [145.0]
        df = _run(_frame(c))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_wrong_side_of_trend(self):
        # Oversold cross while the close sits below SMA(200): the
        # dip is deepened (149 -> 127) so the bounce close 128.5 is
        # below SMA(200) (~133.1) even though %K (15.38) is < 20.
        c = list(np.linspace(100, 150, 250)) + list(np.arange(149, 126, -1)) + [128.5]
        df = _run(_frame(c))
        self.assertLess(df["stoch_k"].iloc[-1], 20.0)
        self.assertLess(df["c"].iloc[-1], df["sma200"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_long_exit_k_above_80(self):
        # Steady rally: %K ~91 > 80, so a long exits.
        df = _run(_frame(list(np.linspace(100, 200, 300))))
        self.assertGreater(df["stoch_k"].iloc[-1], 80.0)
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_short_exit_k_below_20(self):
        # Steady decline: %K ~9 < 20, so a short exits.
        df = _run(_frame(list(np.linspace(200, 100, 300))))
        self.assertLess(df["stoch_k"].iloc[-1], 20.0)
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_edge_short_frame(self):
        # Fewer bars than the %K window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
