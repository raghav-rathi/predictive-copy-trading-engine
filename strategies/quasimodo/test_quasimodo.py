"""Quasimodo reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.quasimodo import indicators, risk, signals
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


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _bear_qm_frame():
    """Bearish QM: H1=110 (centre 2, confirmed bar 4), L1=90
    (centre 7, bar 9), H2=120 head (centre 12, bar 14), break close
    88 < 90 at bar 16, retracement to 105, shoulder swing low 96
    (centre 23, confirmed bar 25), entry close 94 < 96 at bar 26."""
    highs = [100, 105, 110, 105, 100, 103, 101, 96, 99, 101,
             105, 110, 120, 112, 108, 96, 90, 90, 88, 93,
             100, 105, 101, 99, 101, 103, 97]
    lows = [99, 104, 109, 104, 99, 101, 98, 90, 95, 98,
            100, 105, 115, 108, 104, 92, 87, 85, 83, 90,
            97, 102, 99, 96, 98, 100, 93]
    closes = [100, 105, 110, 105, 100, 102, 100, 95, 98, 100,
              104, 109, 119, 111, 107, 95, 88, 86, 85, 92,
              99, 104, 100, 98, 100, 102, 94]
    return _frame(closes, highs=highs, lows=lows)


def _bull_qm_frame():
    """Mirror of _bear_qm_frame (prices reflected about 100):
    bullish QM, long trigger on the final bar."""
    df = _bear_qm_frame()
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


class TestQuasimodo(unittest.TestCase):
    def test_registered(self):
        self.assertIn("quasimodo", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_pivots_confirmed_at_centre_plus_two(self):
        df = indicators.add_indicators(_bear_qm_frame())
        # H1=110 (centre 2) is not visible before bar 4.
        self.assertTrue(np.isnan(df["swing_high"].iloc[3]))
        self.assertAlmostEqual(df["swing_high"].iloc[4], 110.0)
        # L1=90 (centre 7) visible from bar 9.
        self.assertTrue(np.isnan(df["swing_low"].iloc[8]))
        self.assertAlmostEqual(df["swing_low"].iloc[9], 90.0)
        # Head H2=120 (centre 12) visible from bar 14.
        self.assertAlmostEqual(df["swing_high"].iloc[14], 120.0)
        self.assertAlmostEqual(df["last_bear_head_high"].iloc[14], 120.0)

    def test_qm_state_progression(self):
        df = indicators.add_indicators(_bear_qm_frame())
        self.assertEqual(df["qm_state"].iloc[13], 0)  # head not yet confirmed
        self.assertEqual(df["qm_state"].iloc[14], 1)  # head formed
        self.assertEqual(df["qm_state"].iloc[16], 2)  # break confirmed
        self.assertEqual(df["qm_state"].iloc[25], 3)  # shoulder armed
        self.assertAlmostEqual(df["qm_level"].iloc[25], 96.0)

    def test_bear_short_trigger_on_close_below_shoulder_low(self):
        df = _run(_bear_qm_frame())
        self.assertFalse(df["short_entry"].iloc[:26].any())
        self.assertTrue(df["short_entry"].iloc[26])
        self.assertFalse(df["long_entry"].iloc[26])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_bull_long_trigger_on_mirrored_frame(self):
        df = _run(_bull_qm_frame())
        self.assertFalse(df["long_entry"].iloc[:26].any())
        self.assertTrue(df["long_entry"].iloc[26])
        self.assertFalse(df["short_entry"].iloc[26])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertAlmostEqual(df["qm_level"].iloc[25], 104.0)

    def test_no_entry_without_break(self):
        # Same head, but price never closes below L1=90.
        df0 = _bear_qm_frame()
        closes = list(df0["c"])
        closes[16] = 95.0
        closes[17] = 96.0
        closes[18] = 97.0
        df = _run(_frame(closes, highs=list(df0["h"]), lows=list(df0["l"])))
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_when_retracement_exceeds_head(self):
        # Retracement prints a high above the head 120 -> invalid.
        df0 = _bear_qm_frame()
        highs = list(df0["h"])
        highs[21] = 125.0
        closes = list(df0["c"])
        closes[21] = 122.0
        df = _run(_frame(closes, highs=highs, lows=list(df0["l"])))
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_shoulder(self):
        # Break happens, but the retracement never forms a swing low
        # above the break low -> no shoulder, no entry.
        closes = [100.0] * 20 + [88.0, 86.0, 84.0, 82.0, 80.0]
        highs = [110.0] * 20 + [96.0, 90.0, 88.0, 86.0, 84.0]
        lows = [90.0] * 20 + [87.0, 85.0, 83.0, 81.0, 79.0]
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=94.0, long_trigger=False, short_trigger=True,
            last_bull_head_low=83.0, last_bear_head_high=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_head_invalidation(self):
        rows = pd.DataFrame([dict(
            c=82.0, long_trigger=False, short_trigger=False,
            last_bull_head_low=83.0, last_bear_head_high=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(
            c=121.0, long_trigger=False, short_trigger=False,
            last_bull_head_low=83.0, last_bear_head_high=120.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("swing_high", "qm_state", "qm_level", "long_entry",
                    "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
