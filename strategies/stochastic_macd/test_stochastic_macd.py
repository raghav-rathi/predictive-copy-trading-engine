"""Stochastic %K/%D cross + MACD histogram tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stochastic_macd import indicators, risk, signals
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


def _dip_recovery_frame():
    """Uptrend 100->120, sharp 3-bar dip to 108, recovery to 118.
    %K crosses back above %D at bar 45 while %K < 30, but the dip
    flipped the MACD histogram negative, so NO long entry fires."""
    closes = (list(np.linspace(100, 120, 40)) + [116, 112, 108]
              + list(np.linspace(108, 118, 10)) + [118.0] * 10)
    return _frame(closes)


def _spike_fall_frame():
    """Mirror of _dip_recovery_frame: downtrend 120->100, sharp
    3-bar spike to 112, fall back to 102. %K crosses below %D at
    bar 45 while %K > 70, but the spike flipped the MACD histogram
    positive, so NO short entry fires."""
    closes = (list(np.linspace(120, 100, 40)) + [104, 108, 112]
              + list(np.linspace(112, 102, 10)) + [102.0] * 10)
    return _frame(closes)


class TestStochasticMacd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("stochastic_macd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_stochastic_midrange(self):
        # Flat range 90-110, close 100 -> raw %K = 50, so %K = %D = 50.
        df = indicators.add_indicators(_flat_frame(n=40, close=100.0, hi=110.0, lo=90.0))
        self.assertAlmostEqual(df["stoch_k"].iloc[39], 50.0)
        self.assertAlmostEqual(df["stoch_d"].iloc[39], 50.0)

    def test_stochastic_extremes(self):
        # Close pinned at the 14-bar high -> %K = 100; at the low -> 0.
        df_hi = indicators.add_indicators(
            _frame([110.0] * 20, highs=[110.0] * 20, lows=[90.0] * 20))
        self.assertAlmostEqual(df_hi["stoch_k"].iloc[19], 100.0)
        df_lo = indicators.add_indicators(
            _frame([90.0] * 20, highs=[110.0] * 20, lows=[90.0] * 20))
        self.assertAlmostEqual(df_lo["stoch_k"].iloc[19], 0.0)

    def test_stoch_d_is_sma_of_k(self):
        df = indicators.add_indicators(_random_walk_frame())
        expect = df["stoch_k"].rolling(3, min_periods=3).mean()
        pd.testing.assert_series_equal(df["stoch_d"], expect, check_names=False)

    def test_warmup_nans(self):
        df = indicators.add_indicators(_flat_frame())
        # raw %K needs 14 bars, %K smooths 3 more, %D 3 more.
        self.assertTrue(df["stoch_k"].iloc[:15].isna().all())
        self.assertFalse(np.isnan(df["stoch_k"].iloc[15]))
        self.assertTrue(df["stoch_d"].iloc[:17].isna().all())
        self.assertFalse(np.isnan(df["stoch_d"].iloc[17]))

    def test_macd_hist_sign_follows_trend(self):
        up = indicators.add_indicators(_frame(list(np.linspace(100, 200, 100))))
        self.assertGreater(up["macd_hist"].iloc[-1], 0)
        dn = indicators.add_indicators(_frame(list(np.linspace(200, 100, 100))))
        self.assertLess(dn["macd_hist"].iloc[-1], 0)

    def test_long_entry_fires_on_random_walk(self):
        # Seeded walk (seed 7): first long at bar 490, %K < 30, hist > 0.
        df = _run(_random_walk_frame(seed=7))
        self.assertFalse(df["long_entry"].iloc[:490].any())
        self.assertTrue(df["long_entry"].iloc[490])
        self.assertLess(df["stoch_k"].iloc[490], 30)
        self.assertGreater(df["macd_hist"].iloc[490], 0)
        # %K crossed above %D on that bar.
        self.assertGreater(df["stoch_k"].iloc[490], df["stoch_d"].iloc[490])
        self.assertLessEqual(df["stoch_k"].iloc[489], df["stoch_d"].iloc[489])

    def test_short_entry_fires_on_random_walk(self):
        # Same walk: first short at bar 926, %K > 70, hist < 0.
        df = _run(_random_walk_frame(seed=7))
        self.assertFalse(df["short_entry"].iloc[:926].any())
        self.assertTrue(df["short_entry"].iloc[926])
        self.assertGreater(df["stoch_k"].iloc[926], 70)
        self.assertLess(df["macd_hist"].iloc[926], 0)
        self.assertLess(df["stoch_k"].iloc[926], df["stoch_d"].iloc[926])
        self.assertGreaterEqual(df["stoch_k"].iloc[925], df["stoch_d"].iloc[925])

    def test_no_long_when_hist_negative_at_cross(self):
        # %K crosses above %D at bar 45 with %K < 30, but the MACD
        # histogram is negative there -> the agreement gate blocks it.
        df = _run(_dip_recovery_frame())
        self.assertFalse(df["long_entry"].any())
        k, d = df["stoch_k"], df["stoch_d"]
        self.assertTrue(bool((k > d).iloc[45] and (k <= d).iloc[44]))
        self.assertLess(k.iloc[45], 30)
        self.assertLess(df["macd_hist"].iloc[45], 0)

    def test_no_short_when_hist_positive_at_cross(self):
        df = _run(_spike_fall_frame())
        self.assertFalse(df["short_entry"].any())
        k, d = df["stoch_k"], df["stoch_d"]
        self.assertTrue(bool((k < d).iloc[45] and (k >= d).iloc[44]))
        self.assertGreater(k.iloc[45], 70)
        self.assertGreater(df["macd_hist"].iloc[45], 0)

    def test_long_exit_after_entry(self):
        df = _run(_random_walk_frame(seed=7))
        self.assertTrue(df["long_exit"].iloc[491:].any())

    def test_exit_columns_direct(self):
        rows = pd.DataFrame([dict(
            stoch_k=25.0, stoch_d=20.0, macd_hist=-0.5),
            dict(stoch_k=75.0, stoch_d=80.0, macd_hist=0.5),
            dict(stoch_k=50.0, stoch_d=50.0, macd_hist=0.0)])
        df = signals.add_signals(rows)
        # Row 0: hist flipped negative -> long exit.
        self.assertTrue(df["long_exit"].iloc[0])
        # Row 1: hist flipped positive -> short exit.
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])

    def test_no_entry_on_flat_frame(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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
        self.assertGreater(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("stoch_k", "stoch_d", "macd_hist",
                    "long_entry", "short_entry", "long_exit"):
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
