"""Rising/falling three methods tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rising_three_methods import indicators, risk, signals
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


def _uptrend_base(n=130):
    # Linear rise 90 -> 100: closes sit above SMA(50) throughout.
    c = np.linspace(90, 100, n)
    return _frame(c, highs=c + 1.0, lows=c - 1.0)


def _downtrend_base(n=130):
    # Linear decline 110 -> 100: closes sit below SMA(50) throughout.
    c = np.linspace(110, 100, n)
    return _frame(c, highs=c + 1.0, lows=c - 1.0)


def _bullish_bars():
    # Bar 1: o=100, c=103 (body 3 >= ATR ~2.1), h=103.5, l=99.5.
    # Bars 2-4: small bearish candles inside bar 1's range.
    # Bar 5: o=101, c=104, closing above bar 1's high 103.5.
    return _frame(
        [103.0, 102.0, 101.5, 101.0, 104.0],
        highs=[103.5, 102.8, 102.2, 101.8, 104.5],
        lows=[99.5, 101.5, 101.0, 100.5, 100.8],
        opens=[100.0, 102.5, 102.0, 101.5, 101.0],
    )


def _bearish_bars():
    # Bar 1: o=100, c=97 (body 3 >= ATR ~2.1), h=100.5, l=96.5.
    # Bars 2-4: small bullish candles inside bar 1's range.
    # Bar 5: o=99, c=96, closing below bar 1's low 96.5.
    return _frame(
        [97.0, 98.0, 98.5, 99.0, 96.0],
        highs=[100.5, 98.2, 98.8, 99.2, 99.5],
        lows=[96.5, 97.2, 97.5, 97.8, 95.5],
        opens=[100.0, 97.5, 98.0, 98.5, 99.0],
    )


class TestRisingThreeMethods(unittest.TestCase):
    def test_registered(self):
        self.assertIn("rising_three_methods", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat 100, h=101, l=99: SMA50=100, TR=2 so ATR14=2; no
        # pattern forms (no long bar-1 candle, no inside candles).
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["sma50"], 100.0))
        self.assertTrue(np.allclose(tail["atr14"], 2.0))
        self.assertFalse(df["rtm_bullish"].any())
        self.assertFalse(df["rtm_bearish"].any())
        self.assertTrue(df["rtm_bar1_high"].isna().all())
        self.assertTrue(df["rtm_bar1_low"].isna().all())

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

    def test_long_entry_rising_three_methods(self):
        df = _run(pd.concat([_uptrend_base(), _bullish_bars()], ignore_index=True))
        self.assertTrue(df["rtm_bullish"].iloc[-1])
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])
        self.assertAlmostEqual(df["rtm_bar1_high"].iloc[-1], 103.5, places=9)
        self.assertAlmostEqual(df["rtm_bar1_low"].iloc[-1], 99.5, places=9)

    def test_short_entry_falling_three_methods(self):
        df = _run(pd.concat([_downtrend_base(), _bearish_bars()], ignore_index=True))
        self.assertTrue(df["rtm_bearish"].iloc[-1])
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertAlmostEqual(df["rtm_bar1_high"].iloc[-1], 100.5, places=9)
        self.assertAlmostEqual(df["rtm_bar1_low"].iloc[-1], 96.5, places=9)

    def test_no_entry_bar_outside_range(self):
        # Bar 3 pokes above bar 1's high (104.0 > 103.5): not inside.
        bars = _frame(
            [103.0, 102.0, 101.5, 101.0, 104.0],
            highs=[103.5, 102.8, 104.0, 101.8, 104.5],
            lows=[99.5, 101.5, 101.0, 100.5, 100.8],
            opens=[100.0, 102.5, 102.0, 101.5, 101.0],
        )
        df = _run(pd.concat([_uptrend_base(), bars], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_bar5_below_bar1_high(self):
        # Bar 5 closes 103.0, below bar 1's high 103.5.
        bars = _frame(
            [103.0, 102.0, 101.5, 101.0, 103.0],
            highs=[103.5, 102.8, 102.2, 101.8, 103.5],
            lows=[99.5, 101.5, 101.0, 100.5, 100.8],
            opens=[100.0, 102.5, 102.0, 101.5, 101.0],
        )
        df = _run(pd.concat([_uptrend_base(), bars], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_bar1_body_too_small(self):
        # Bar 1 body 1.0 < ATR (~2.1): not a long candle.
        bars = _frame(
            [101.0, 102.0, 101.5, 101.0, 104.0],
            highs=[101.5, 102.8, 102.2, 101.8, 104.5],
            lows=[99.5, 101.5, 101.0, 100.5, 100.8],
            opens=[100.0, 102.5, 102.0, 101.5, 101.0],
        )
        df = _run(pd.concat([_uptrend_base(), bars], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_without_uptrend(self):
        # Same bullish shape on a steeply falling base (130 -> 100):
        # the bar-5 close 104 still sits below SMA(50) (~104.8), so
        # the uptrend filter fails and there is no entry.
        c = np.linspace(130, 100, 130)
        base = _frame(c, highs=c + 1.0, lows=c - 1.0)
        df = _run(pd.concat([base, _bullish_bars()], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_long_exit_below_bar1_low(self):
        base = pd.concat([_uptrend_base(), _bullish_bars()], ignore_index=True)
        bar = _frame([99.0], highs=[99.5], lows=[98.5], opens=[101.0])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])
        # A close above bar 1's low is not an exit.
        bar2 = _frame([100.0], highs=[100.5], lows=[99.8], opens=[101.0])
        df = _run(pd.concat([base, bar2], ignore_index=True))
        self.assertFalse(df["long_exit"].iloc[-1])

    def test_short_exit_above_bar1_high(self):
        base = pd.concat([_downtrend_base(), _bearish_bars()], ignore_index=True)
        bar = _frame([101.0], highs=[101.5], lows=[100.5], opens=[96.0])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the pattern needs: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): no long bar-1 candle exists.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
