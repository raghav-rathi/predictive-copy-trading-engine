"""Tweezer top/bottom reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tweezer_reversal import indicators, risk, signals
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


def _flat_frame(n=130, close=100.0, hi=101.0, lo=99.0, vol=100.0):
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


def _downtrend_base(n=130):
    # Linear decline 120 -> 100: closes sit below SMA(50) throughout.
    c = np.linspace(120, 100, n)
    return _frame(c, highs=c + 1.0, lows=c - 1.0)


def _uptrend_base(n=130):
    # Linear rise 100 -> 120: closes sit above SMA(50) throughout.
    c = np.linspace(100, 120, n)
    return _frame(c, highs=c + 1.0, lows=c - 1.0)


def _bottom_bars():
    # Bar 1 bearish (o=100, c=99, l=98.9), bar 2 bullish (o=99,
    # c=99.8, l=99.0) closing above bar 1's midpoint 99.5; lows
    # differ by 0.1, within 0.1 x ATR(~2) = 0.2.
    return _frame([99.0, 99.8], highs=[100.5, 100.2], lows=[98.9, 99.0],
                  opens=[100.0, 99.0])


def _top_bars():
    # Bar 1 bullish (o=120, c=121, h=121.1), bar 2 bearish (o=121,
    # c=120.2, h=121.0) closing below bar 1's midpoint 120.5; highs
    # differ by 0.1, within 0.1 x ATR(~2) = 0.2.
    return _frame([121.0, 120.2], highs=[121.1, 121.0], lows=[119.5, 119.8],
                  opens=[120.0, 121.0])


class TestTweezerReversal(unittest.TestCase):
    def test_registered(self):
        self.assertIn("tweezer_reversal", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat 100, h=101, l=99: SMA50=100, TR=2 so ATR14=2; no
        # pattern forms (no strictly bearish/bullish bars, no trend).
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["sma50"], 100.0))
        self.assertTrue(np.allclose(tail["atr14"], 2.0))
        self.assertFalse(df["twz_bottom"].any())
        self.assertFalse(df["twz_top"].any())
        self.assertTrue(df["twz_low"].isna().all())
        self.assertTrue(df["twz_high"].isna().all())

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            self.assertAlmostEqual(df["sma50"].iloc[i], df["c"].iloc[i - 49:i + 1].mean(), places=9)

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

    def test_long_entry_tweezer_bottom(self):
        df = _run(pd.concat([_downtrend_base(), _bottom_bars()], ignore_index=True))
        self.assertTrue(df["twz_bottom"].iloc[-1])
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])
        self.assertAlmostEqual(df["twz_low"].iloc[-1], 98.9, places=9)

    def test_short_entry_tweezer_top(self):
        df = _run(pd.concat([_uptrend_base(), _top_bars()], ignore_index=True))
        self.assertTrue(df["twz_top"].iloc[-1])
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertAlmostEqual(df["twz_high"].iloc[-1], 121.1, places=9)

    def test_no_entry_lows_too_far_apart(self):
        # Bar 2 low 99.5 vs bar 1 low 98.9: diff 0.6 > 0.1 x ATR.
        bars = _frame([99.0, 99.8], highs=[100.5, 100.2], lows=[98.9, 99.5],
                      opens=[100.0, 99.0])
        df = _run(pd.concat([_downtrend_base(), bars], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_bar2_below_midpoint(self):
        # Bar 2 closes 99.3, below bar 1's midpoint 99.5.
        bars = _frame([99.0, 99.3], highs=[100.5, 100.2], lows=[98.9, 99.0],
                      opens=[100.0, 99.0])
        df = _run(pd.concat([_downtrend_base(), bars], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_bar1_not_bearish(self):
        # Bar 1 bullish: no tweezer bottom.
        bars = _frame([101.0, 101.8], highs=[101.5, 102.2], lows=[100.9, 101.0],
                      opens=[100.0, 101.0])
        df = _run(pd.concat([_downtrend_base(), bars], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_without_downtrend(self):
        # Same bottom shape on a rising base: no downtrend, no entry.
        df = _run(pd.concat([_uptrend_base(), _bottom_bars()], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_long_exit_below_tweezer_low(self):
        base = pd.concat([_downtrend_base(), _bottom_bars()], ignore_index=True)
        bar = _frame([98.5], highs=[99.0], lows=[98.0], opens=[99.8])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])
        # A close above the tweezer low is not an exit.
        bar2 = _frame([99.5], highs=[100.0], lows=[99.0], opens=[99.8])
        df = _run(pd.concat([base, bar2], ignore_index=True))
        self.assertFalse(df["long_exit"].iloc[-1])

    def test_short_exit_above_tweezer_high(self):
        base = pd.concat([_uptrend_base(), _top_bars()], ignore_index=True)
        bar = _frame([121.5], highs=[122.0], lows=[121.0], opens=[120.2])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the SMA window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): ATR is 0 and no candle is
        # strictly bearish/bullish, so no pattern forms.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
