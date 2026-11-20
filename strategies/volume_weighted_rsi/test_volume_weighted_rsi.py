"""Volume-weighted RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies import registry
from strategies.backtest import run_backtest
from strategies.volume_weighted_rsi import indicators, risk, signals


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


def _rise_then_fall_frame():
    """Rise 100 -> 115 over 20 bars, then fall 115 -> 85 over 30 bars.
    VW-RSI crosses below 30 (long) at bar 40."""
    closes = np.concatenate([np.linspace(100, 115, 20),
                             np.linspace(115, 85, 30)])
    return _frame(closes)


def _fall_then_rise_frame():
    """Fall 100 -> 85 over 20 bars, then rise 85 -> 115 over 30 bars.
    VW-RSI crosses above 70 (short) at bar 40."""
    closes = np.concatenate([np.linspace(100, 85, 20),
                             np.linspace(85, 115, 30)])
    return _frame(closes)


class TestVolumeWeightedRsi(unittest.TestCase):
    def test_registered(self):
        self.assertIn("volume_weighted_rsi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_vwtp_constant_volume_is_rolling_mean_tp(self):
        # Constant volume -> VWTP is the 14-bar rolling mean of tp.
        closes = np.linspace(100, 120, 30)
        df = indicators.add_indicators(_frame(closes))
        tp = closes  # h = c+0.5, l = c-0.5 -> tp = c
        self.assertAlmostEqual(df["vwtp"].iloc[13], tp[:14].mean())
        self.assertAlmostEqual(df["vwtp"].iloc[29], tp[16:30].mean())

    def test_vwtp_volume_weighted_math(self):
        # 13 bars tp=100 v=1, then tp=200 v=3:
        # (13*100*1 + 200*3) / (13*1 + 3) = 1900/16 = 118.75.
        closes = [100.0] * 13 + [200.0]
        highs = [100.0] * 13 + [200.0]
        lows = [100.0] * 13 + [200.0]
        vols = [1.0] * 13 + [3.0]
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows, vols=vols))
        self.assertAlmostEqual(df["vwtp"].iloc[13], 118.75)

    def test_vwtp_nan_before_window(self):
        df = indicators.add_indicators(_frame(np.linspace(100, 120, 30)))
        self.assertTrue(df["vwtp"].iloc[:13].isna().all())
        self.assertTrue(pd.notna(df["vwtp"].iloc[13]))

    def test_vwtp_zero_volume_falls_back_to_close(self):
        df = indicators.add_indicators(_frame([100.0] * 20, vols=[0.0] * 20))
        self.assertTrue((df["vwtp"].iloc[13:] == 100.0).all())

    def test_volume_weighting_changes_vwtp(self):
        # Same closes, different volume placement -> different VWTP.
        closes = [100.0] * 13 + [200.0]
        base = indicators.add_indicators(_frame(closes, highs=closes, lows=closes))
        heavy = indicators.add_indicators(
            _frame(closes, highs=closes, lows=closes,
                   vols=[1.0] * 13 + [100.0]))
        self.assertNotAlmostEqual(base["vwtp"].iloc[13], heavy["vwtp"].iloc[13])
        self.assertAlmostEqual(heavy["vwtp"].iloc[13],
                               (13 * 100 * 1 + 200 * 100) / (13 + 100))

    def test_rsi_extremes_on_monotonic_series(self):
        up = indicators.add_indicators(_frame(np.linspace(100, 130, 60)))
        self.assertGreater(up["vw_rsi"].iloc[59], 90)
        dn = indicators.add_indicators(_frame(np.linspace(100, 70, 60)))
        self.assertLess(dn["vw_rsi"].iloc[59], 10)

    def test_long_entry_on_rise_then_fall(self):
        df = _run(_rise_then_fall_frame())
        self.assertTrue(df["long_entry"].iloc[40])
        self.assertFalse(df["long_entry"].iloc[:40].any())

    def test_short_entry_on_fall_then_rise(self):
        df = _run(_fall_then_rise_frame())
        self.assertTrue(df["short_entry"].iloc[40])
        self.assertFalse(df["long_entry"].any())

    def test_first_valid_rsi_cross_suppressed_by_warmup(self):
        # B.rsi fills pre-valid values with 0, so the first genuine RSI
        # value (~bar 27, after the VWTP + RSI warmups) registers as a
        # cross from 0 -- a spurious short_entry at bar 27 on the
        # rise-then-fall frame. WARMUP=40 means the harness never
        # trades it: no backtest entry may occur before bar 41. The
        # frame is extended with a second rise so the long entered
        # at bar 41 exits (VW-RSI back above 50) inside the frame.
        df = _run(_rise_then_fall_frame())
        self.assertTrue(df["short_entry"].iloc[27])
        closes = np.concatenate([np.linspace(100, 115, 20),
                                 np.linspace(115, 85, 30),
                                 np.linspace(85, 115, 30)])
        df_ext = _run(_frame(closes))
        res = run_backtest(df_ext, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        self.assertGreater(len(res.trades), 0)
        self.assertTrue((res.trades["entry_t"] >= df["t"].iloc[41]).all())

    def test_exit_long_on_cross_above_50(self):
        rows = pd.DataFrame({"vw_rsi": [40.0, 60.0]})
        df = signals.add_signals(rows)
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

    def test_exit_short_on_cross_below_50(self):
        rows = pd.DataFrame({"vw_rsi": [60.0, 40.0]})
        df = signals.add_signals(rows)
        self.assertFalse(df["short_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])

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
        for col in ("vwtp", "vw_rsi", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
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
