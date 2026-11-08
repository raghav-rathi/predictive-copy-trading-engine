"""Narrow-range breakout (NR7) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.narrow_range_breakout import indicators, risk, signals
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


def _rising_base(n=260, start=100.0, step=0.1):
    c = start + step * np.arange(n)
    return _frame(c)


def _falling_base(n=260, start=100.0, step=0.1):
    c = start - step * np.arange(n)
    return _frame(c)


class TestNarrowRangeBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("narrow_range_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Constant range 2.0: every bar is NR7; SMA50 == SMA200 == 100
        # on flat closes, so setup direction is NaN (no trend).
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["nr_range"], 2.0))
        self.assertTrue(tail["nr_is_nr7"].all())
        self.assertTrue(np.allclose(tail["sma50"], 100.0))
        self.assertTrue(np.allclose(tail["sma200"], 100.0))
        self.assertTrue(tail["nr_setup_dir"].isna().all())

    def test_nr7_detection(self):
        # Ranges: 3s, then a 1 (NR7), then 3, then a 5 (not NR7).
        ranges = [3.0] * 7 + [1.0, 3.0, 5.0]
        closes = [100.0] * len(ranges)
        highs = [100.0 + r / 2 for r in ranges]
        lows = [100.0 - r / 2 for r in ranges]
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["nr_is_nr7"].iloc[7])
        self.assertFalse(df["nr_is_nr7"].iloc[9])
        self.assertTrue(np.allclose(df["nr_range"], ranges))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            rng7 = (df["h"] - df["l"]).iloc[i - 6:i + 1]
            self.assertEqual(df["nr_is_nr7"].iloc[i],
                             bool((df["h"].iloc[i] - df["l"].iloc[i]) == rng7.min()))

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

    def _setup_then_breakout(self, base, setup_close, setup_hi, setup_lo,
                             break_close):
        # Append a narrow-range setup bar, then a breakout bar.
        setup = _frame([setup_close], highs=[setup_hi], lows=[setup_lo])
        brk = _frame([break_close], highs=[break_close + 0.5],
                     lows=[break_close - 0.5])
        return _run(pd.concat([base, setup, brk], ignore_index=True))

    def test_long_entry_above_setup_high(self):
        base = _rising_base()
        df = self._setup_then_breakout(base, 126.0, 126.1, 125.9, 127.0)
        # The bar before the breakout is the setup bar (NR7, uptrend).
        self.assertTrue(df["nr_is_nr7"].iloc[-2])
        self.assertEqual(df["nr_setup_dir"].iloc[-1], 1.0)
        self.assertAlmostEqual(df["nr_setup_high"].iloc[-1], 126.1)
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_short_entry_below_setup_low(self):
        base = _falling_base()
        df = self._setup_then_breakout(base, 74.0, 74.1, 73.9, 73.0)
        self.assertTrue(df["nr_is_nr7"].iloc[-2])
        self.assertEqual(df["nr_setup_dir"].iloc[-1], -1.0)
        self.assertAlmostEqual(df["nr_setup_low"].iloc[-1], 73.9)
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_without_breakout(self):
        # Breakout bar closes inside the setup bar's range: no entry.
        base = _rising_base()
        df = self._setup_then_breakout(base, 126.0, 126.1, 125.9, 126.0)
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_no_entry_wrong_trend(self):
        # Setup bar in a downtrend: a close above its high is not a
        # long entry (setup direction is short).
        base = _falling_base()
        df = self._setup_then_breakout(base, 74.0, 74.1, 73.9, 75.0)
        self.assertEqual(df["nr_setup_dir"].iloc[-1], -1.0)
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_newer_setup_replaces_old(self):
        # Two setups in a row, the second with a strictly smaller
        # range: the entry must use the newer one's high.
        base = _rising_base()
        s1 = _frame([126.0], highs=[126.2], lows=[125.8])
        s2 = _frame([126.2], highs=[126.3], lows=[126.1])
        brk = _frame([126.25], highs=[126.5], lows=[126.0])
        df = _run(pd.concat([base, s1, s2, brk], ignore_index=True))
        # 126.25 breaks the old setup high (126.2) but not the new
        # one (126.3): no entry.
        self.assertAlmostEqual(df["nr_setup_high"].iloc[-1], 126.3)
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_setup_window_expires_after_24_bars(self):
        base = _rising_base()
        setup = _frame([126.0], highs=[126.1], lows=[125.9])
        # 24 bars after the setup with steadily widening ranges
        # (so no bar is ever the smallest of its trailing 7 and no
        # new setup forms): setup levels still valid on the 24th bar.
        ranges24 = 1.0 + 0.1 * np.arange(24)
        flat24 = _frame([126.0] * 24, highs=126.0 + ranges24 / 2,
                        lows=126.0 - ranges24 / 2)
        df = _run(pd.concat([base, setup, flat24], ignore_index=True))
        self.assertAlmostEqual(df["nr_setup_high"].iloc[-1], 126.1)
        # One more bar (25th after setup): levels expired.
        ranges25 = 1.0 + 0.1 * np.arange(25)
        flat25 = _frame([126.0] * 25, highs=126.0 + ranges25 / 2,
                        lows=126.0 - ranges25 / 2)
        df = _run(pd.concat([base, setup, flat25], ignore_index=True))
        self.assertTrue(pd.isna(df["nr_setup_high"].iloc[-1]))
        self.assertTrue(pd.isna(df["nr_setup_low"].iloc[-1]))

    def test_long_exit_below_setup_low(self):
        base = _rising_base()
        df = self._setup_then_breakout(base, 126.0, 126.1, 125.9, 125.0)
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_short_exit_above_setup_high(self):
        base = _falling_base()
        df = self._setup_then_breakout(base, 74.0, 74.1, 73.9, 75.0)
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_long_exit_on_short_setup_trigger(self):
        # Signals-level check: a fresh NR7 bar with a downtrend
        # triggers a long exit even if the close is inside the range.
        df = _run(_random_walk_frame())
        df = df.copy()
        df.loc[df.index[-1], "nr_is_nr7"] = True
        df.loc[df.index[-1], "sma50"] = 90.0
        df.loc[df.index[-1], "sma200"] = 100.0
        df = signals.add_signals(df)
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the SMA200 window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): NR7 every bar, no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["nr_range"], 0.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
