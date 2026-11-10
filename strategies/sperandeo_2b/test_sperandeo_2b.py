"""Sperandeo 2B false-breakout reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sperandeo_2b import indicators, risk, signals
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


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
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


def _top_2b_frame():
    """Hand-built 2B Top: extreme bar 19 (h=110), 3 pullback bars,
    breakout bar 23 (close 112 > 110, low 108), failure bar 24
    (close 106 < 108) -> short_entry at 24 only."""
    n = 30
    closes = [100.0] * n
    highs = [101.0] * n
    lows = [99.0] * n
    closes[19], highs[19], lows[19] = 105.0, 110.0, 99.0
    for i in (20, 21, 22):
        closes[i], highs[i], lows[i] = 103.0, 106.0, 100.0
    closes[23], highs[23], lows[23] = 112.0, 115.0, 108.0
    closes[24], highs[24], lows[24] = 106.0, 110.0, 104.0
    return _frame(closes, highs=highs, lows=lows)


def _bottom_2b_frame():
    """Hand-built 2B Bottom (mirror): extreme bar 19 (l=90), 3 pullback
    bars, breakout bar 23 (close 88 < 90, high 92), failure bar 24
    (close 94 > 92) -> long_entry at 24 only."""
    n = 30
    closes = [100.0] * n
    highs = [101.0] * n
    lows = [99.0] * n
    closes[19], highs[19], lows[19] = 95.0, 101.0, 90.0
    for i in (20, 21, 22):
        closes[i], highs[i], lows[i] = 97.0, 100.0, 94.0
    closes[23], highs[23], lows[23] = 88.0, 92.0, 85.0
    closes[24], highs[24], lows[24] = 94.0, 96.0, 90.0
    return _frame(closes, highs=highs, lows=lows)


class TestSperandeo2b(unittest.TestCase):
    def test_registered(self):
        self.assertIn("sperandeo_2b", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_hand_computed(self):
        # 19 flat bars (h=100, l=90), bar 19 spikes to h=105/l=88,
        # bars 20-24 back to h=102/l=92.
        n = 25
        highs = [100.0] * 19 + [105.0] + [102.0] * 5
        lows = [90.0] * 19 + [88.0] + [92.0] * 5
        df = indicators.add_indicators(_frame([100.0] * n, highs=highs, lows=lows))
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        # First 19 bars have no 20-bar window yet.
        self.assertTrue(df["high20"].iloc[:19].isna().all())
        self.assertTrue(df["low20"].iloc[:19].isna().all())
        self.assertEqual(df["high20"].iloc[19], 105.0)
        self.assertEqual(df["low20"].iloc[19], 88.0)
        # Bar 24 window (bars 5..24) still contains the bar-19 spike.
        self.assertEqual(df["high20"].iloc[24], 105.0)
        self.assertEqual(df["low20"].iloc[24], 88.0)
        self.assertTrue(df["is_new_high"].iloc[19])
        self.assertTrue(df["is_new_low"].iloc[19])
        self.assertFalse(df["is_new_high"].iloc[24])
        self.assertFalse(df["is_new_low"].iloc[24])
        # Flat bars before the spike are not new extremes.
        self.assertFalse(bool(df["is_new_high"].iloc[20:].any()))

    def test_indicator_atr_hand_computed(self):
        # Constant true range 2 (h-l=2, flat closes): Wilder ATR(14)
        # converges to exactly 2.0 once the 14-bar minimum is met.
        df = indicators.add_indicators(_flat_frame(n=60))
        self.assertTrue(df["atr14"].iloc[:13].isna().all())
        self.assertTrue(np.isclose(df["atr14"].iloc[13], 2.0))
        self.assertTrue(np.allclose(df["atr14"].iloc[13:], 2.0))

    def test_2b_top_fires(self):
        df = _run(_top_2b_frame())
        self.assertTrue(df["short_entry"].iloc[24])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].iloc[:24].any())
        self.assertFalse(df["long_entry"].any())
        # Opposite-side exit fires on the same bar.
        self.assertTrue(df["long_exit"].iloc[24])
        self.assertFalse(df["short_exit"].iloc[24])

    def test_2b_bottom_fires(self):
        df = _run(_bottom_2b_frame())
        self.assertTrue(df["long_entry"].iloc[24])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["long_entry"].iloc[:24].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["short_exit"].iloc[24])
        self.assertFalse(df["long_exit"].iloc[24])

    def test_breakout_needs_three_pullback_bars(self):
        # Extreme bar 19 (h=110); only 2 pullback bars, then a bar
        # closing above the extreme (c=111) at bar 22. With pullback=2
        # that is NOT a breakout bar -- it is a newer 20-bar high, so
        # the pattern restarts from h=112 and no entry fires yet.
        n = 30
        closes = [100.0] * n
        highs = [101.0] * n
        lows = [99.0] * n
        closes[19], highs[19], lows[19] = 105.0, 110.0, 99.0
        for i in (20, 21):
            closes[i], highs[i], lows[i] = 103.0, 106.0, 100.0
        closes[22], highs[22], lows[22] = 111.0, 112.0, 107.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_newer_extreme_resets_pullback(self):
        # Extreme bar 19 (h=110), 2 pullback bars, then a newer high
        # h=112 at bar 22 (close 108, below the old extreme -- no
        # breakout). Pattern restarts: 3 pullback bars (23-25),
        # breakout bar 26 (close 113 > 112, low 110), failure bar 27
        # (close 109 < 110) -> short_entry at 27 only.
        n = 32
        closes = [100.0] * n
        highs = [101.0] * n
        lows = [99.0] * n
        closes[19], highs[19], lows[19] = 105.0, 110.0, 99.0
        for i in (20, 21):
            closes[i], highs[i], lows[i] = 103.0, 106.0, 100.0
        closes[22], highs[22], lows[22] = 108.0, 112.0, 104.0
        for i in (23, 24, 25):
            closes[i], highs[i], lows[i] = 105.0, 108.0, 102.0
        closes[26], highs[26], lows[26] = 113.0, 114.0, 110.0
        closes[27], highs[27], lows[27] = 109.0, 111.0, 106.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["short_entry"].iloc[27])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].iloc[:27].any())

    def test_breakout_without_failure_no_entry(self):
        # Full setup through the breakout bar, then price holds above
        # the breakout bar's low: no 2B signal.
        df0 = _top_2b_frame()
        df = _run(df0.iloc[:24])  # drop the failure bar
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertEqual(risk.RISK.target_atr_mult, 10.0)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("high20", "low20", "long_entry", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # Fewer bars than the 20-bar lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
