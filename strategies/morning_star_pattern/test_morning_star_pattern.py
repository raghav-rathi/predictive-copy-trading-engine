"""Morning/Evening Star tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.morning_star_pattern import indicators, risk, signals
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


def _trend_frame(start, end, n=60):
    """Linear trend frame, h/l straddling the close by 0.5."""
    closes = np.linspace(start, end, n)
    return _frame(closes)


def _append(df, rows):
    """rows: list of (o, h, l, c)."""
    extra = pd.DataFrame(rows, columns=["o", "h", "l", "c"])
    extra["v"] = 100.0
    last_t = int(df["t"].iloc[-1])
    extra["t"] = (last_t + 3_600_000 * (np.arange(len(rows)) + 1)).astype("int64")
    return pd.concat([df, extra[["t", "o", "h", "l", "c", "v"]]],
                     ignore_index=True)


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


# Downtrend 120 -> 100, then a textbook morning star:
# candle1 red 100 -> 90 (body 10), candle2 tiny 90.5 -> 90,
# candle3 green 90 -> 96, closing above candle1's body midpoint (95).
MORNING_STAR = [(100.0, 101.0, 89.0, 90.0),
                (90.5, 91.0, 89.5, 90.0),
                (90.0, 97.0, 89.5, 96.0)]
# Uptrend 80 -> 100, then a textbook evening star:
# candle1 green 100 -> 110, candle2 tiny 109.5 -> 110,
# candle3 red 110 -> 104, closing below candle1's midpoint (105).
EVENING_STAR = [(100.0, 111.0, 99.0, 110.0),
                (109.5, 110.5, 109.0, 110.0),
                (110.0, 110.5, 103.0, 104.0)]


class TestMorningStarPattern(unittest.TestCase):
    def test_registered(self):
        self.assertIn("morning_star_pattern", registry.REGISTRY)

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
        self.assertTrue(np.isfinite(tail["atr14"]).all())
        self.assertTrue(np.isfinite(tail["sma50"]).all())

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

    def test_morning_star_long_entry(self):
        df = _run(_append(_trend_frame(120, 100), MORNING_STAR))
        self.assertTrue(df["ms_morning"].iloc[-1] > 0)
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_evening_star_short_entry(self):
        df = _run(_append(_trend_frame(80, 100), EVENING_STAR))
        self.assertTrue(df["ms_evening"].iloc[-1] > 0)
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_exit_on_opposite_star(self):
        # A morning star is the exit signal for an open short and vice
        # versa.
        df = _run(_append(_trend_frame(120, 100), MORNING_STAR))
        self.assertTrue(df["short_exit"].iloc[-1])
        self.assertFalse(df["long_exit"].iloc[-1])
        df = _run(_append(_trend_frame(80, 100), EVENING_STAR))
        self.assertTrue(df["long_exit"].iloc[-1])
        self.assertFalse(df["short_exit"].iloc[-1])

    def test_no_entry_candle3_misses_midpoint(self):
        # Candle3 closes at 94, below candle1's body midpoint (95).
        bad = [(100.0, 101.0, 89.0, 90.0),
               (90.5, 91.0, 89.5, 90.0),
               (90.0, 95.0, 89.5, 94.0)]
        df = _run(_append(_trend_frame(120, 100), bad))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_candle1_body_too_small(self):
        # Candle1 body 0.5 is below 0.6x ATR(14) (~1.0 on the trend);
        # every other condition holds (tiny middle body, candle3 green
        # closing beyond the midpoint, close below SMA(50)).
        bad = [(100.0, 100.5, 99.0, 99.5),
               (99.6, 100.0, 99.0, 99.5),
               (99.5, 100.5, 99.0, 100.2)]
        df = _run(_append(_trend_frame(120, 100), bad))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_middle_body_too_big(self):
        # Candle2 body 5.0 exceeds 0.3x candle1's body (3.0).
        bad = [(100.0, 101.0, 89.0, 90.0),
               (95.0, 96.0, 89.5, 90.0),
               (90.0, 97.0, 89.5, 96.0)]
        df = _run(_append(_trend_frame(120, 100), bad))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_trend_filter_wrong(self):
        # Morning-star shape in an uptrend: close sits above SMA(50).
        df = _run(_append(_trend_frame(80, 100), MORNING_STAR))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_frame([100.0] * 150))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["ms_morning"].any())
        self.assertFalse(df["ms_evening"].any())

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
