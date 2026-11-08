"""Dark cloud cover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dark_cloud_cover import indicators, risk, signals
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


def _bearish_setup():
    # 100 flat bars, 5 rising bars, then dark cloud cover bars 1-2.
    base = _flat_frame(n=100)
    up = _frame([101.0, 102.0, 103.0, 104.0, 105.0],
                opens=[100.0, 101.0, 102.0, 103.0, 104.0])
    bar1 = _frame([108.0], highs=[108.5], lows=[104.5], opens=[105.0])
    bar2 = _frame([106.0], highs=[109.5], lows=[105.5], opens=[109.0])
    return pd.concat([base, up, bar1, bar2], ignore_index=True)


def _bullish_setup():
    # 100 flat bars, 5 declining bars, then piercing pattern bars 1-2.
    base = _flat_frame(n=100)
    down = _frame([99.0, 98.0, 97.0, 96.0, 95.0],
                  opens=[100.0, 99.0, 98.0, 97.0, 96.0])
    bar1 = _frame([92.0], highs=[95.5], lows=[91.5], opens=[95.0])
    bar2 = _frame([94.0], highs=[94.5], lows=[90.5], opens=[91.0])
    return pd.concat([base, down, bar1, bar2], ignore_index=True)


class TestDarkCloudCover(unittest.TestCase):
    def test_registered(self):
        self.assertIn("dark_cloud_cover", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat 100: sma50=100, no patterns, bar-2 extremes all NaN.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["dcc_sma50"], 100.0))
        self.assertFalse(tail["dcc_bearish"].any())
        self.assertFalse(tail["dcc_bullish"].any())
        self.assertTrue(tail["dcc_bar2_high"].isna().all())
        self.assertTrue(tail["dcc_bar2_low"].isna().all())

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            self.assertAlmostEqual(df["dcc_sma50"].iloc[i],
                                   df["c"].iloc[i - 49:i + 1].mean(), places=9)
            if df["dcc_bearish"].iloc[i]:
                self.assertEqual(df["dcc_bar2_high"].iloc[i], df["h"].iloc[i])
            if df["dcc_bullish"].iloc[i]:
                self.assertEqual(df["dcc_bar2_low"].iloc[i], df["l"].iloc[i])
        self.assertTrue(df["dcc_bearish"].dtype == bool)
        self.assertTrue(df["dcc_bullish"].dtype == bool)

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

    def test_short_entry_dark_cloud_cover(self):
        df = _run(_bearish_setup())
        self.assertTrue(df["dcc_bearish"].iloc[-1])
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-2])
        self.assertEqual(df["dcc_bar2_high"].iloc[-1], 109.5)

    def test_long_entry_piercing_pattern(self):
        df = _run(_bullish_setup())
        self.assertTrue(df["dcc_bullish"].iloc[-1])
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-2])
        self.assertEqual(df["dcc_bar2_low"].iloc[-1], 90.5)

    def test_no_entry_bar2_closes_above_midpoint(self):
        # Bar 2 closes at 107, above bar 1's midpoint 106.5.
        base = _flat_frame(n=100)
        up = _frame([101.0, 102.0, 103.0, 104.0, 105.0],
                    opens=[100.0, 101.0, 102.0, 103.0, 104.0])
        bar1 = _frame([108.0], highs=[108.5], lows=[104.5], opens=[105.0])
        bar2 = _frame([107.0], highs=[109.5], lows=[105.5], opens=[109.0])
        df = _run(pd.concat([base, up, bar1, bar2], ignore_index=True))
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_no_entry_bar2_no_gap(self):
        # Bar 2 opens at 108.0, below bar 1's high 108.5: no gap up.
        base = _flat_frame(n=100)
        up = _frame([101.0, 102.0, 103.0, 104.0, 105.0],
                    opens=[100.0, 101.0, 102.0, 103.0, 104.0])
        bar1 = _frame([108.0], highs=[108.5], lows=[104.5], opens=[105.0])
        bar2 = _frame([106.0], highs=[109.5], lows=[105.5], opens=[108.0])
        df = _run(pd.concat([base, up, bar1, bar2], ignore_index=True))
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_no_entry_bar1_body_too_small(self):
        # Bar 1 body 1.0 < 0.6 x its 4.0 range (2.4).
        base = _flat_frame(n=100)
        up = _frame([101.0, 102.0, 103.0, 104.0, 105.0],
                    opens=[100.0, 101.0, 102.0, 103.0, 104.0])
        bar1 = _frame([106.0], highs=[108.5], lows=[104.5], opens=[105.0])
        bar2 = _frame([104.0], highs=[109.5], lows=[103.5], opens=[109.0])
        df = _run(pd.concat([base, up, bar1, bar2], ignore_index=True))
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_no_entry_without_trend(self):
        # Bar 1 closes below SMA50 after a decline: no uptrend.
        base = _flat_frame(n=100)
        down = _frame([99.0, 98.0, 97.0, 96.0, 95.0],
                      opens=[100.0, 99.0, 98.0, 97.0, 96.0])
        bar1 = _frame([98.0], highs=[98.5], lows=[94.5], opens=[95.0])
        bar2 = _frame([96.0], highs=[99.5], lows=[95.5], opens=[99.0])
        df = _run(pd.concat([base, down, bar1, bar2], ignore_index=True))
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_short_exit_above_bar2_high(self):
        # Bar 2's high was 109.5; a close at 110.0 exits the short.
        raw = _bearish_setup().iloc[:, :6]
        bar = _frame([110.0], highs=[110.5], lows=[109.0],
                     vols=[100.0], opens=[109.0])
        df = _run(pd.concat([raw, bar], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])
        self.assertFalse(df["short_exit"].iloc[-2])

    def test_long_exit_below_bar2_low(self):
        # Bar 2's low was 90.5; a close at 90.0 exits the long.
        raw = _bullish_setup().iloc[:, :6]
        bar = _frame([90.0], highs=[91.0], lows=[89.5],
                     vols=[100.0], opens=[91.0])
        df = _run(pd.concat([raw, bar], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])
        self.assertFalse(df["long_exit"].iloc[-2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars: bar-1 bodies are 0, so no pattern can form.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
