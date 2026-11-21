"""On-Balance Volume Breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.obv_breakout import indicators, risk, signals
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


def _obv_frame():
    """25 flat bars at 100, 20 rising bars 101->120, 20 falling 119->90."""
    closes = ([100.0] * 25 + list(np.linspace(101, 120, 20))
              + list(np.linspace(119, 90, 20)))
    return _frame(closes, vols=[100.0] * len(closes))


class TestObvBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("obv_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_obv_math_hand_computed(self):
        # closes 100,101,101,99,102 with vols 10,20,30,40,50:
        # OBV = 0, +20, +0, -40, +50 -> 0, 20, 20, -20, 30.
        df = indicators.add_indicators(
            _frame([100, 101, 101, 99, 102], vols=[10, 20, 30, 40, 50]))
        self.assertEqual(df["obv"].tolist(), [0.0, 20.0, 20.0, -20.0, 30.0])

    def test_obv_levels_hand_computed(self):
        # Flat closes keep OBV at 0; the first rising bar adds 100.
        df = indicators.add_indicators(_obv_frame())
        self.assertAlmostEqual(df["obv"].iloc[24], 0.0)
        self.assertAlmostEqual(df["obv"].iloc[25], 100.0)
        # At bar 26 the prior-20 OBV high is max OBV of bars 6..25
        # = 100 (bar 25); at bar 25 it is 0 (all flat bars).
        self.assertAlmostEqual(df["obv_high"].iloc[25], 0.0)
        self.assertAlmostEqual(df["obv_high"].iloc[26], 100.0)
        self.assertAlmostEqual(df["obv_low"].iloc[25], 0.0)

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["obv_high"].iloc[:20].isna().all())
        self.assertTrue(df["obv_low"].iloc[:20].isna().all())
        self.assertFalse(np.isnan(df["obv_high"].iloc[20]))
        # OBV itself is defined from bar 0.
        self.assertFalse(df["obv"].isna().any())

    def test_long_entry_on_obv_breakout(self):
        df = _run(_obv_frame())
        self.assertTrue(df["long_entry"].iloc[25])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["long_exit"].iloc[25])

    def test_short_entry_on_obv_breakdown(self):
        df = _run(_obv_frame())
        # The falling leg drives OBV below its prior-20-bar low.
        self.assertTrue(df["short_entry"].iloc[55])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_long_exit_on_obv_breakdown(self):
        df = _run(_obv_frame())
        self.assertTrue(df["long_exit"].iloc[55])

    def test_exit_levels_manual(self):
        df = pd.DataFrame({
            "obv": [50.0, 35.0, 65.0],
            "obv_high": [60.0, 60.0, 60.0],
            "obv_low": [40.0, 40.0, 40.0],
        })
        out = signals.add_signals(df)
        self.assertFalse(out["long_exit"].iloc[0])
        self.assertTrue(out["long_exit"].iloc[1])   # OBV < prior-20 low
        self.assertTrue(out["short_exit"].iloc[2])  # OBV > prior-20 high
        # Row 2 also fires a long entry (OBV breaks above the prior-20
        # high from below) and row 1 a short entry (OBV breaks below
        # the prior-20 low from above): entries and exits are
        # evaluated independently per bar.
        self.assertTrue(out["long_entry"].iloc[2])
        self.assertTrue(out["short_entry"].iloc[1])

    def test_equal_closes_leave_obv_unchanged(self):
        # Flat closes with varying volume: OBV must stay at 0.
        df = indicators.add_indicators(
            _frame([100.0] * 30, vols=list(range(10, 40))))
        self.assertTrue((df["obv"] == 0.0).all())

    def test_no_entry_on_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_atr_on_flat_frame(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["atr"].iloc[100], 2.0, places=6)

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
        self.assertEqual(risk.WARMUP, 40)

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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("obv", "obv_high", "obv_low",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["obv_high"].isna().all())
        self.assertTrue((df["obv"] == 0.0).all())


if __name__ == "__main__":
    unittest.main()
