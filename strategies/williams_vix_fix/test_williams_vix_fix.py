"""Williams VIX Fix tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.williams_vix_fix import indicators, risk, signals
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


def _crash_frame():
    """60 flat bars at 100 (h=101, l=99) then a crash bar:
    close 85, high 86, low 80."""
    closes = [100.0] * 60 + [85.0]
    highs = [101.0] * 60 + [86.0]
    lows = [99.0] * 60 + [80.0]
    return _frame(closes, highs=highs, lows=lows)


def _spike_frame():
    """60 flat bars at 100 (h=101, l=99) then a spike bar:
    close 115, high 120, low 114."""
    closes = [100.0] * 60 + [115.0]
    highs = [101.0] * 60 + [120.0]
    lows = [99.0] * 60 + [114.0]
    return _frame(closes, highs=highs, lows=lows)


class TestWilliamsVixFix(unittest.TestCase):
    def test_registered(self):
        self.assertIn("williams_vix_fix", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_wvf_hand_computed(self):
        # 25 bars at close 100, h=l=100, except the last bar's low is 90.
        # Highest close over 22 bars is 100, so WVF = 100*(100-90)/100 = 10.
        closes = [100.0] * 25
        lows = [100.0] * 24 + [90.0]
        df = indicators.add_indicators(
            _frame(closes, highs=[100.0] * 25, lows=lows))
        self.assertAlmostEqual(df["wvf"].iloc[24], 10.0, places=9)

    def test_inv_wvf_hand_computed(self):
        # Same frame, inverted: lowest close over 22 is 100, high is 100
        # on the last bar -> inv = 100*(100-100)/100 = 0. On a spike bar
        # (high 120, lowest close 100) inv = 100*(120-100)/100 = 20.
        df = indicators.add_indicators(_spike_frame())
        self.assertAlmostEqual(df["inv_wvf"].iloc[60], 20.0, places=9)

    def test_wvf_upper_on_constant_wvf(self):
        # closes 100, h=100, l=99 -> WVF is exactly 1.0 every bar once
        # the 22-bar window is full. SMA(20) = 1, std = 0, upper = 1.0;
        # range high = 0.85 * 1 = 0.85.
        df = indicators.add_indicators(
            _frame([100.0] * 80, highs=[100.0] * 80, lows=[99.0] * 80))
        self.assertAlmostEqual(df["wvf"].iloc[50], 1.0, places=9)
        self.assertAlmostEqual(df["wvf_upper"].iloc[50], 1.0, places=9)
        # Range high needs 50 defined WVF values (first at bar 70).
        self.assertAlmostEqual(df["wvf_range_high"].iloc[70], 0.85, places=9)

    def test_green_flash_on_crash(self):
        df = indicators.add_indicators(_crash_frame())
        # WVF at the crash bar: highest close 100, low 80 -> 20.0.
        self.assertAlmostEqual(df["wvf"].iloc[60], 20.0, places=9)
        self.assertTrue(df["green_flash"].iloc[60])

    def test_inv_flash_on_spike(self):
        df = indicators.add_indicators(_spike_frame())
        self.assertTrue(df["inv_flash"].iloc[60])
        self.assertFalse(df["green_flash"].iloc[60])

    def test_entry_is_transition_only(self):
        df = pd.DataFrame({
            "green_flash": [False, False, True, True, False, True],
            "inv_flash": [False, False, False, False, False, False],
        })
        out = signals.add_signals(df)
        self.assertEqual(list(out["long_entry"]),
                         [False, False, True, False, False, True])
        self.assertFalse(out["short_entry"].any())

    def test_short_entry_is_transition_only(self):
        df = pd.DataFrame({
            "green_flash": [False] * 6,
            "inv_flash": [False, True, True, False, True, True],
        })
        out = signals.add_signals(df)
        self.assertEqual(list(out["short_entry"]),
                         [False, True, False, False, True, False])
        self.assertFalse(out["long_entry"].any())

    def test_exit_is_opposite_flash(self):
        df = pd.DataFrame({
            "green_flash": [False, True, False, False],
            "inv_flash": [False, False, True, False],
        })
        out = signals.add_signals(df)
        # Long exits on any inverted flash; short exits on any green flash.
        self.assertTrue(out["long_exit"].iloc[2])
        self.assertFalse(out["long_exit"].iloc[1])
        self.assertTrue(out["short_exit"].iloc[1])
        self.assertFalse(out["short_exit"].iloc[2])

    def test_no_entry_while_flash_persists(self):
        df = pd.DataFrame({
            "green_flash": [True] * 10,
            "inv_flash": [False] * 10,
        })
        out = signals.add_signals(df)
        self.assertEqual(int(out["long_entry"].sum()), 1)

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["wvf"].iloc[:21].isna().all())
        self.assertFalse(np.isnan(df["wvf"].iloc[21]))
        self.assertTrue(df["wvf_upper"].iloc[:40].isna().all())
        self.assertFalse(np.isnan(df["wvf_upper"].iloc[40]))
        self.assertFalse(df["green_flash"].iloc[:21].any())

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
        self.assertEqual(risk.WARMUP, 70)

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
        for col in ("wvf", "wvf_upper", "green_flash", "inv_wvf",
                    "inv_flash", "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["wvf"].isna().all())
        self.assertTrue(df["inv_wvf"].isna().all())


if __name__ == "__main__":
    unittest.main()
