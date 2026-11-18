"""Bollinger MACD tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_macd import indicators, risk, signals
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


def _risk_checks(tc):
    tc.assertEqual(risk.RISK.atr_window, 14)
    tc.assertEqual(risk.RISK.stop_atr_mult, 2.0)
    tc.assertEqual(risk.RISK.trail_atr_mult, 2.5)
    tc.assertIsNone(risk.RISK.target_atr_mult)
    tc.assertEqual(risk.RISK.max_hold_bars, 120)
    tc.assertEqual(risk.RISK.risk_frac, 0.01)
    tc.assertEqual(risk.RISK.max_leverage, 3.0)
    tc.assertEqual(risk.RISK.fee_rate, 0.00045)
    tc.assertEqual(risk.RISK.slippage_rate, 0.0001)
    tc.assertTrue(risk.RISK.allow_longs)
    tc.assertTrue(risk.RISK.allow_shorts)
    tc.assertEqual(risk.WARMUP, 60)


class TestBollingerMacd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bollinger_macd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_bollinger_bands_ordered(self):
        df = indicators.add_indicators(_random_walk_frame())
        sub = df.dropna(subset=["bb_upper", "bb_lower"])
        self.assertTrue((sub["bb_upper"] >= sub["bb_mid"]).all())
        self.assertTrue((sub["bb_mid"] >= sub["bb_lower"]).all())

    def test_macd_hist_positive_on_rise(self):
        closes = [100.0 + i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertGreater(df["macd_hist"].iloc[-1], 0)

    def test_macd_hist_negative_on_fall(self):
        closes = [200.0 - i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertLess(df["macd_hist"].iloc[-1], 0)

    def test_signal_logic_crafted_rows(self):
        # MACD crosses up + low touched lower band in last 3 bars -> long.
        rows = pd.DataFrame([
            dict(c=100.0, h=101.0, l=99.0, macd=-0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=102.0, h=103.0, l=89.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Mirror: cross down + high touched upper band -> short.
        rows = pd.DataFrame([
            dict(c=100.0, h=101.0, l=99.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=98.0, h=111.0, l=97.0, macd=-0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_no_entry_without_band_touch(self):
        rows = pd.DataFrame([
            dict(c=100.0, h=101.0, l=99.0, macd=-0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=102.0, h=103.0, l=95.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_no_entry_without_macd_cross(self):
        # MACD already above signal on both bars -> no cross.
        rows = pd.DataFrame([
            dict(c=100.0, h=101.0, l=89.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=102.0, h=103.0, l=89.0, macd=0.6, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])

    def test_band_touch_looks_back_2_bars(self):
        # Touch was 2 bars ago (low 89 at row 0), cross on row 2 -> entry.
        rows = pd.DataFrame([
            dict(c=100.0, h=101.0, l=89.0, macd=-0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=100.0, h=101.0, l=99.0, macd=-0.4, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=102.0, h=103.0, l=99.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[2])

    def test_band_touch_too_old_no_entry(self):
        # Touch 3 bars ago is outside the 3-bar window.
        rows = pd.DataFrame([
            dict(c=100.0, h=101.0, l=89.0, macd=-0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=100.0, h=101.0, l=99.0, macd=-0.4, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=100.0, h=101.0, l=99.0, macd=-0.3, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=102.0, h=103.0, l=99.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[3])

    def test_exit_long_on_macd_cross_down(self):
        rows = pd.DataFrame([
            dict(c=100.0, h=101.0, l=99.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
            dict(c=98.0, h=99.0, l=97.0, macd=-0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])

    def test_exit_long_on_opposite_band(self):
        rows = pd.DataFrame([dict(c=111.0, h=112.0, l=110.0, macd=0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(c=89.0, h=90.0, l=88.0, macd=-0.5, macd_signal=0.0, bb_upper=110.0, bb_lower=90.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_risk_config_sane(self):
        _risk_checks(self)

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
        for col in ("bb_lower", "macd_hist", "long_entry", "long_exit"):
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
