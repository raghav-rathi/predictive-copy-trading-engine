"""Three white soldiers tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.three_white_soldiers import indicators, risk, signals
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


def _bullish_setup():
    # 100 flat bars, 5 declining bars (below SMA50), then 3 soldiers.
    base = _flat_frame(n=100)
    down = _frame([99.0, 98.0, 97.0, 96.0, 95.0],
                  opens=[100.0, 99.0, 98.0, 97.0, 96.0])
    soldiers = _frame([97.0, 98.5, 100.0],
                      highs=[97.2, 98.7, 100.2],
                      lows=[95.2, 96.2, 97.2],
                      opens=[95.5, 96.5, 97.5])
    return pd.concat([base, down, soldiers], ignore_index=True)


def _bearish_setup():
    # 100 flat bars, 5 rising bars (above SMA50), then 3 black crows.
    base = _flat_frame(n=100)
    up = _frame([101.0, 102.0, 103.0, 104.0, 105.0],
                opens=[100.0, 101.0, 102.0, 103.0, 104.0])
    crows = _frame([103.0, 101.5, 100.0],
                   highs=[104.8, 103.8, 102.8],
                   lows=[102.8, 101.3, 99.8],
                   opens=[104.5, 103.5, 102.5])
    return pd.concat([base, up, crows], ignore_index=True)


class TestThreeWhiteSoldiers(unittest.TestCase):
    def test_registered(self):
        self.assertIn("three_white_soldiers", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat 100, h=101, l=99: sma50=100, ATR(14)=2, no patterns.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["tws_sma50"], 100.0))
        self.assertTrue(np.allclose(tail["tws_atr14"], 2.0))
        self.assertFalse(tail["tws_bullish"].any())
        self.assertFalse(tail["tws_bearish"].any())

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            self.assertAlmostEqual(df["tws_sma50"].iloc[i],
                                   df["c"].iloc[i - 49:i + 1].mean(), places=9)
            self.assertTrue(np.isfinite(df["tws_atr14"].iloc[i]))
            self.assertGreater(df["tws_atr14"].iloc[i], 0)
        self.assertTrue(df["tws_bullish"].dtype == bool)
        self.assertTrue(df["tws_bearish"].dtype == bool)

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

    def test_long_entry_three_white_soldiers(self):
        df = _run(_bullish_setup())
        self.assertTrue(df["tws_bullish"].iloc[-1])
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])
        # Pattern completes only on the 3rd soldier.
        self.assertFalse(df["long_entry"].iloc[-2])
        self.assertFalse(df["long_entry"].iloc[-3])

    def test_short_entry_three_black_crows(self):
        df = _run(_bearish_setup())
        self.assertTrue(df["tws_bearish"].iloc[-1])
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-2])

    def test_no_entry_without_trend(self):
        # Three soldiers straight after flat bars: no 5-bar downtrend.
        base = _flat_frame(n=100)
        soldiers = _frame([101.0, 102.5, 104.0],
                          highs=[101.2, 102.7, 104.2],
                          lows=[99.2, 100.2, 101.2],
                          opens=[99.5, 100.5, 101.5])
        df = _run(pd.concat([base, soldiers], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_wick_too_big(self):
        # 3rd soldier with a 1.5 upper wick (> 25% of its 3.0 range).
        base = _flat_frame(n=100)
        down = _frame([99.0, 98.0, 97.0, 96.0, 95.0],
                      opens=[100.0, 99.0, 98.0, 97.0, 96.0])
        soldiers = _frame([97.0, 98.5, 100.0],
                          highs=[97.2, 98.7, 101.5],
                          lows=[95.2, 96.2, 97.2],
                          opens=[95.5, 96.5, 97.5])
        df = _run(pd.concat([base, down, soldiers], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_body_too_small(self):
        # Soldiers with tiny bodies (< 0.5 x ATR ~ 1.0).
        base = _flat_frame(n=100)
        down = _frame([99.0, 98.0, 97.0, 96.0, 95.0],
                      opens=[100.0, 99.0, 98.0, 97.0, 96.0])
        soldiers = _frame([95.4, 95.8, 96.2],
                          highs=[95.6, 96.0, 96.4],
                          lows=[95.0, 95.4, 95.8],
                          opens=[95.2, 95.6, 96.0])
        df = _run(pd.concat([base, down, soldiers], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_open_outside_prev_body(self):
        # 2nd soldier gaps up, opening above the 1st soldier's body.
        base = _flat_frame(n=100)
        down = _frame([99.0, 98.0, 97.0, 96.0, 95.0],
                      opens=[100.0, 99.0, 98.0, 97.0, 96.0])
        soldiers = _frame([97.0, 98.5, 100.0],
                          highs=[97.2, 98.7, 100.2],
                          lows=[95.2, 96.2, 97.2],
                          opens=[95.5, 97.5, 97.5])
        df = _run(pd.concat([base, down, soldiers], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_long_exit_below_first_soldier_open(self):
        # 1st soldier opened at 95.5; a close at 95.0 exits the long.
        raw = _bullish_setup().iloc[:, :6]
        bar = _frame([95.0], highs=[96.5], lows=[94.5],
                     vols=[100.0], opens=[96.0])
        df = _run(pd.concat([raw, bar], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])
        self.assertFalse(df["long_exit"].iloc[-2])

    def test_short_exit_above_first_crow_open(self):
        # 1st crow opened at 104.5; a close at 105.0 exits the short.
        raw = _bearish_setup().iloc[:, :6]
        bar = _frame([105.0], highs=[105.5], lows=[104.0],
                     vols=[100.0], opens=[104.0])
        df = _run(pd.concat([raw, bar], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars: no pattern can form (bodies are 0).
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
