"""TPO market-profile tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.market_profile_tpo import indicators, risk, signals


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=250, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(closes, vah, val):
    return pd.DataFrame({
        "c": np.array(closes, dtype=float),
        "tpo_vah": np.array(vah, dtype=float),
        "tpo_val": np.array(val, dtype=float),
    })


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


class TestMarketProfileTpo(unittest.TestCase):
    def test_registered(self):
        self.assertIn("market_profile_tpo", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat bars: every midpoint is 100, so all TPOs land in one
        # bin; POC = that bin's midpoint, VAH/VAL are that bin's edges.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[indicators.WINDOW_BARS:]
        # Range 99..101 split into 24 bins: midpoint 100 falls in bin 12,
        # whose midpoint is 99 + 12.5 * (2/24) = 100.0417. All 168 TPOs
        # are in that one bin, so the value area is just that bin.
        self.assertTrue(np.allclose(tail["tpo_poc"], 100.04166666666667))
        self.assertTrue(np.allclose(tail["tpo_vah"], 100.08333333333333))
        self.assertTrue(np.allclose(tail["tpo_val"], 100.0))
        self.assertTrue((tail["tpo_vah"] > tail["tpo_val"]).all())
        # First 167 bars have no full window.
        self.assertTrue(df["tpo_poc"].iloc[: indicators.WINDOW_BARS - 1].isna().all())

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[indicators.WINDOW_BARS:]
        self.assertTrue(np.isfinite(tail["tpo_poc"]).all())
        self.assertTrue((tail["tpo_val"] <= tail["tpo_poc"]).all())
        self.assertTrue((tail["tpo_poc"] <= tail["tpo_vah"]).all())
        self.assertTrue((tail["tpo_vah"] >= tail["tpo_val"]).all())

    def test_indicator_values_trend(self):
        # Steady 0.5% per-bar rally: midpoints are spread across the
        # window, so the POC sits inside the window's range (between
        # the close 168 bars ago and the current close) with VAH > VAL.
        closes = 100 * (1.005 ** np.arange(300))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[250:]
        self.assertTrue((tail["tpo_poc"] >= tail["c"] * 0.4).all())
        self.assertTrue((tail["tpo_poc"] <= tail["c"]).all())
        self.assertTrue((tail["tpo_vah"] > tail["tpo_val"]).all())

    def test_profile_unit_known_window(self):
        # Hand-built window: 168 bars, midpoints 100 (x100), 101 (x40),
        # 102 (x28). Range 99.5..102.5 -> width 0.125/bin; POC bin is
        # the 100 bin; 70% of 168 = 117.6 TPOs, so the VA must cover
        # the 100 bin (100) + the 101 bin (40) = 140 >= 117.6.
        mids = np.array([100.0] * 100 + [101.0] * 40 + [102.0] * 28)
        lows = mids - 0.5
        highs = mids + 0.5
        poc, vah, val = indicators._profile_poc_vah_val(lows, highs, mids)
        self.assertAlmostEqual(poc, 100.0625, places=9)
        self.assertGreaterEqual(vah, 101.0)
        self.assertLessEqual(val, 100.0)
        # Zero-range window collapses to the midpoint.
        poc, vah, val = indicators._profile_poc_vah_val(
            np.full(10, 99.0), np.full(10, 99.0), np.full(10, 99.0))
        self.assertEqual((poc, vah, val), (99.0, 99.0, 99.0))

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.WARMUP, 200)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_vah_break(self):
        # Close crosses above a flat VAH=110 at index 2.
        df = signals.add_signals(_signal_frame(
            [105, 108, 112, 113], [110, 110, 110, 110], [90, 90, 90, 90]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_val_break(self):
        # Close crosses below a flat VAL=90 at index 2.
        df = signals.add_signals(_signal_frame(
            [95, 92, 88, 87], [110, 110, 110, 110], [90, 90, 90, 90]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_exits_on_opposite_break(self):
        # Opposite VA break exits the open side.
        df = signals.add_signals(_signal_frame(
            [95, 92, 88], [110, 110, 110], [90, 90, 90]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame(
            [105, 108, 112], [110, 110, 110], [90, 90, 90]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): levels collapse to the close.
        df = _run(_frame([100.0] * 250, highs=[100.0] * 250,
                         lows=[100.0] * 250))
        tail = df.iloc[indicators.WINDOW_BARS:]
        self.assertTrue(np.allclose(tail["tpo_poc"], 100.0))
        self.assertTrue(np.allclose(tail["tpo_vah"], 100.0))
        self.assertTrue(np.allclose(tail["tpo_val"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
