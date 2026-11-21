"""Accumulation/Distribution Line tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.accumulation_distribution import indicators, risk, signals
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


def _ad_expected(df0, sma_n=20):
    """Independent loop recomputation of AD and its SMA."""
    h = df0["h"].to_numpy(float)
    l = df0["l"].to_numpy(float)
    c = df0["c"].to_numpy(float)
    v = df0["v"].to_numpy(float)
    ad = np.zeros(len(df0))
    run = 0.0
    for i in range(len(df0)):
        mfm = 0.0 if h[i] == l[i] else ((c[i] - l[i]) - (h[i] - c[i])) / (h[i] - l[i])
        run += mfm * v[i]
        ad[i] = run
    sma = np.full(len(df0), np.nan)
    for i in range(sma_n - 1, len(df0)):
        sma[i] = ad[i - sma_n + 1:i + 1].mean()
    return ad, sma


class TestAccumulationDistribution(unittest.TestCase):
    def test_registered(self):
        self.assertIn("accumulation_distribution", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_mfm_hand_computed(self):
        # H=110, L=100, C=108, V=1000: MFM = ((8)-(2))/10 = 0.6,
        # MFV = 600, AD after one bar = 600.
        df = indicators.add_indicators(_frame(
            [108.0], highs=[110.0], lows=[100.0], vols=[1000.0]))
        self.assertAlmostEqual(df["mfm"].iloc[0], 0.6)
        self.assertAlmostEqual(df["mfv"].iloc[0], 600.0)
        self.assertAlmostEqual(df["ad"].iloc[0], 600.0)

    def test_ad_cumulative_two_bars(self):
        # Bar 2: C=102 -> MFM = ((2)-(8))/10 = -0.6, MFV = -600,
        # AD returns to 0.
        df = indicators.add_indicators(_frame(
            [108.0, 102.0], highs=[110.0, 110.0], lows=[100.0, 100.0],
            vols=[1000.0, 1000.0]))
        self.assertAlmostEqual(df["mfm"].iloc[1], -0.6)
        self.assertAlmostEqual(df["mfv"].iloc[1], -600.0)
        self.assertAlmostEqual(df["ad"].iloc[1], 0.0)

    def test_mfm_extremes(self):
        # Close at high -> +1; close at low -> -1; midrange -> 0.
        df = indicators.add_indicators(_frame(
            [110.0, 100.0, 105.0], highs=[110.0] * 3, lows=[100.0] * 3,
            vols=[100.0] * 3))
        self.assertAlmostEqual(df["mfm"].iloc[0], 1.0)
        self.assertAlmostEqual(df["mfm"].iloc[1], -1.0)
        self.assertAlmostEqual(df["mfm"].iloc[2], 0.0)

    def test_h_equals_l_guard(self):
        # H == L: MFM 0, MFV 0, AD unchanged (no divide-by-zero).
        df = indicators.add_indicators(_frame(
            [100.0, 100.0, 108.0], highs=[100.0, 100.0, 110.0],
            lows=[100.0, 100.0, 100.0], vols=[1000.0, 1000.0, 1000.0]))
        self.assertAlmostEqual(df["mfm"].iloc[1], 0.0)
        self.assertAlmostEqual(df["mfv"].iloc[1], 0.0)
        self.assertAlmostEqual(df["ad"].iloc[1], 0.0)
        self.assertAlmostEqual(df["ad"].iloc[2], 600.0)

    def test_ad_matches_loop_recomputation(self):
        df0 = _random_walk_frame()
        df = indicators.add_indicators(df0)
        ad, sma = _ad_expected(df0)
        for i in (0, 1, 19, 100, 1499):
            self.assertAlmostEqual(df["ad"].iloc[i], ad[i], places=6)
            if i >= 19:
                self.assertAlmostEqual(df["ad_sma"].iloc[i], sma[i], places=6)

    def test_ad_sma_hand_computed(self):
        # Close at high every bar, V=100: MFV=100, AD[i]=100*(i+1).
        # SMA(20) at i=19 = mean(100..2000) = 1050.
        df = indicators.add_indicators(_frame(
            [110.0] * 30, highs=[110.0] * 30, lows=[100.0] * 30,
            vols=[100.0] * 30))
        self.assertAlmostEqual(df["ad"].iloc[19], 2000.0)
        self.assertAlmostEqual(df["ad_sma"].iloc[19], 1050.0)
        self.assertTrue(df["ad_sma"].iloc[:19].isna().all())

    def test_mfm_bounds(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(((df["mfm"] >= -1.0) & (df["mfm"] <= 1.0)).all())

    def test_long_entry_cross_up_sma(self):
        # 30 bars closing at the low (AD falling), then 30 closing at
        # the high (AD rising through its SMA once).
        closes = [100.0] * 30 + [110.0] * 30
        highs = [110.0] * 60
        lows = [100.0] * 60
        df0 = _frame(closes, highs=highs, lows=lows, vols=[100.0] * 60)
        df = _run(df0)
        ad, sma = _ad_expected(df0)
        expected = [i for i in range(1, 60)
                    if not np.isnan(sma[i]) and not np.isnan(sma[i - 1])
                    and ad[i] > sma[i] and ad[i - 1] <= sma[i - 1]]
        self.assertEqual(len(expected), 1)
        self.assertTrue(df["long_entry"].iloc[expected[0]])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_short_entry_cross_down_sma(self):
        closes = [110.0] * 30 + [100.0] * 30
        df0 = _frame(closes, highs=[110.0] * 60, lows=[100.0] * 60,
                     vols=[100.0] * 60)
        df = _run(df0)
        ad, sma = _ad_expected(df0)
        expected = [i for i in range(1, 60)
                    if not np.isnan(sma[i]) and not np.isnan(sma[i - 1])
                    and ad[i] < sma[i] and ad[i - 1] >= sma[i - 1]]
        self.assertEqual(len(expected), 1)
        self.assertTrue(df["short_entry"].iloc[expected[0]])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_exit_is_opposite_cross(self):
        df = pd.DataFrame({"ad": [0.0, 10.0, -10.0, 0.0],
                           "ad_sma": [5.0, 5.0, 5.0, 5.0]})
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["short_entry"].iloc[2])
        self.assertTrue(out["long_exit"].iloc[2])
        self.assertTrue(out["short_exit"].iloc[1])

    def test_no_entry_while_ad_flat(self):
        # Midrange closes: MFM 0, AD flat at 0, AD == SMA -> no cross.
        df = _run(_frame([105.0] * 100, highs=[110.0] * 100,
                         lows=[100.0] * 100, vols=[100.0] * 100))
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
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("ad", "ad_sma", "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([105.0] * 5, highs=[110.0] * 5, lows=[100.0] * 5,
                         vols=[100.0] * 5))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["ad_sma"].isna().all())
        self.assertFalse(df["ad"].isna().any())


if __name__ == "__main__":
    unittest.main()
