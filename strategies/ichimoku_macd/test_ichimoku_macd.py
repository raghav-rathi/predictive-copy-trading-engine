"""Ichimoku MACD tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ichimoku_macd import indicators, risk, signals
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


def _step_frame():
    """Bars 0-39 range 90-110 (mid 100), bars 40+ range 100-120
    (mid 110). Tenkan at bar 48 is (120+100)/2 = 110; Kijun at
    bar 48 is (120+90)/2 = 105 (26-bar window still reaches back
    into the old range). Senkou A plotted at bar 74 is
    (tenkan[48] + kijun[48]) / 2 = 107.5."""
    n = 100
    highs = [110.0] * 40 + [120.0] * 60
    lows = [90.0] * 40 + [100.0] * 60
    closes = [100.0] * 40 + [110.0] * 60
    return _frame(closes, highs=highs, lows=lows)


class TestIchimokuMacd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ichimoku_macd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_no_chikou_column(self):
        # Chikou is close.shift(-26) — 26 bars into the future —
        # so it must never be shipped.
        df = indicators.add_indicators(_random_walk_frame())
        self.assertNotIn("chikou", df.columns)

    def test_tenkan_kijun_exact_constant_range(self):
        # Constant 90-110 range: tenkan = kijun = 100 once filled.
        df = indicators.add_indicators(
            _frame([100.0] * 60, highs=[110.0] * 60, lows=[90.0] * 60))
        self.assertAlmostEqual(df["tenkan"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["kijun"].iloc[-1], 100.0)
        self.assertTrue(np.isnan(df["tenkan"].iloc[7]))
        self.assertTrue(np.isnan(df["kijun"].iloc[24]))

    def test_senkou_displacement_exact(self):
        # Senkou A plotted at bar i comes from tenkan/kijun at
        # bar i-26: at bar 60 both are still 100 (step at bar 40
        # not yet in the i-26 window), at bar 74 it is 107.5.
        df = indicators.add_indicators(_step_frame())
        self.assertTrue(np.isnan(df["senkou_a"].iloc[30]))
        self.assertAlmostEqual(df["senkou_a"].iloc[60], 100.0)
        self.assertAlmostEqual(df["senkou_a"].iloc[74], 107.5)
        # Tenkan/Kijun at bar 48 themselves (unshifted).
        self.assertAlmostEqual(df["tenkan"].iloc[48], 110.0)
        self.assertAlmostEqual(df["kijun"].iloc[48], 105.0)

    def test_macd_hist_sign_on_trends(self):
        # Linear trends (not geometric: on a geometric fall the
        # MACD line decays toward zero and the lagging signal sits
        # below it, flipping the histogram sign).
        up = 100 + 0.5 * np.arange(200)
        df = indicators.add_indicators(_frame(up))
        self.assertGreater(df["macd_hist"].iloc[-1], 0)
        down = 200 - 0.5 * np.arange(200)
        df = indicators.add_indicators(_frame(down))
        self.assertLess(df["macd_hist"].iloc[-1], 0)

    def test_signal_logic_crafted_rows(self):
        # Close above both spans + Tenkan crosses above Kijun +
        # histogram > 0 -> long entry.
        rows = [dict(c=110.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=102.0, kijun=103.0, macd_hist=1.0),
                dict(c=112.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=104.0, kijun=103.0, macd_hist=1.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Mirror: close below both spans + cross down + hist < 0.
        rows = [dict(c=90.0, senkou_a=100.0, senkou_b=102.0,
                     tenkan=104.0, kijun=103.0, macd_hist=-1.0),
                dict(c=88.0, senkou_a=100.0, senkou_b=102.0,
                     tenkan=102.0, kijun=103.0, macd_hist=-1.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_entry_blocked_without_all_conditions(self):
        base = dict(c=112.0, senkou_a=100.0, senkou_b=98.0,
                    tenkan=104.0, kijun=103.0, macd_hist=1.0)
        prev = dict(c=110.0, senkou_a=100.0, senkou_b=98.0,
                    tenkan=102.0, kijun=103.0, macd_hist=1.0)
        # Histogram negative: no long.
        rows = [prev, dict(base, macd_hist=-1.0)]
        self.assertFalse(signals.add_signals(pd.DataFrame(rows))["long_entry"].iloc[1])
        # Close inside the cloud (below Senkou A): no long.
        rows = [prev, dict(base, c=99.0)]
        self.assertFalse(signals.add_signals(pd.DataFrame(rows))["long_entry"].iloc[1])
        # No Tenkan/Kijun cross (already above): no long.
        rows = [dict(prev, tenkan=104.0),
                dict(base, tenkan=105.0)]
        self.assertFalse(signals.add_signals(pd.DataFrame(rows))["long_entry"].iloc[1])

    def test_exit_on_tk_cross_back_and_on_cloud_entry(self):
        # Tenkan crosses below Kijun -> long exit.
        rows = [dict(c=112.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=104.0, kijun=103.0, macd_hist=1.0),
                dict(c=112.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=102.0, kijun=103.0, macd_hist=1.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        # Close falls into the cloud (<= higher span) with no
        # cross -> long exit too.
        rows = [dict(c=112.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=104.0, kijun=103.0, macd_hist=1.0),
                dict(c=99.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=104.0, kijun=103.0, macd_hist=1.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        # Close stays above the cloud, no cross -> no exit.
        rows = [dict(c=112.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=104.0, kijun=103.0, macd_hist=1.0),
                dict(c=113.0, senkou_a=100.0, senkou_b=98.0,
                     tenkan=105.0, kijun=103.0, macd_hist=1.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertFalse(df["long_exit"].iloc[1])

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
        self.assertEqual(risk.WARMUP, 120)

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
        # Flat: tenkan == kijun == 100, close == cloud top, so no
        # cross and no above/below-cloud entry on either side.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("tenkan", "kijun", "senkou_a", "senkou_b",
                    "macd_hist", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["senkou_a"].isna().all())


if __name__ == "__main__":
    unittest.main()
