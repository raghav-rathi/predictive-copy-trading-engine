"""VWAP Bollinger Bands tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.vwap_bollinger_bands import indicators, risk, signals

# 2023-11-15 00:00 UTC, so the first 24 bars are one UTC day.
MIDNIGHT = 1_700_006_400_000


def _frame(closes, highs=None, lows=None, vols=None, opens=None,
           t0=MIDNIGHT):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
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
        "t": (MIDNIGHT + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _oscillation_frame(drop_to=93.0):
    """30 bars oscillating 100.5/99.5 across the UTC-midnight boundary,
    then a drop to `drop_to`, a second low bar, and a recovery to 100.5.
    Long entry fires on the drop bar (bar 30); exit on the recovery
    bar (bar 32)."""
    osc = np.tile([100.5, 99.5], 15)
    closes = np.concatenate([osc, [drop_to, drop_to + 0.5, 100.5]])
    return _frame(closes)


def _oscillation_spike_frame(spike_to=107.0):
    """Mirror of _oscillation_frame: a spike above the upper band.
    Short entry fires on the spike bar (bar 30); exit on the
    recovery bar (bar 32)."""
    osc = np.tile([100.5, 99.5], 15)
    closes = np.concatenate([osc, [spike_to, spike_to - 0.5, 99.5]])
    return _frame(closes)


class TestVwapBollingerBands(unittest.TestCase):
    def test_registered(self):
        self.assertIn("vwap_bollinger_bands", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_vwap_math_equal_volumes(self):
        # h = l = c, constant volume: VWAP is the mean of tp, SD the
        # population std. tp = [100, 102, 104]: mean 102, SD sqrt(8/3).
        closes = [100.0, 102.0, 104.0]
        df = indicators.add_indicators(
            _frame(closes, highs=closes, lows=closes))
        self.assertAlmostEqual(df["vwap"].iloc[2], 102.0)
        self.assertAlmostEqual(df["vwap_sd"].iloc[2], (8 / 3) ** 0.5)
        self.assertAlmostEqual(df["vwap_upper"].iloc[2], 102.0 + 2 * (8 / 3) ** 0.5)
        self.assertAlmostEqual(df["vwap_lower"].iloc[2], 102.0 - 2 * (8 / 3) ** 0.5)

    def test_vwap_math_volume_weighted(self):
        # Bar 0: tp=100 v=100; bar 1: tp=110 v=300 ->
        # VWAP = (100*100 + 110*300) / 400 = 107.5.
        closes = [100.0, 110.0]
        df = indicators.add_indicators(
            _frame(closes, highs=closes, lows=closes, vols=[100.0, 300.0]))
        self.assertAlmostEqual(df["vwap"].iloc[1], 107.5)

    def test_vwap_resets_at_utc_midnight(self):
        # 24 bars at 100 (one UTC day), then a bar at 200: the new
        # day's VWAP is 200 with SD 0.
        closes = [100.0] * 24 + [200.0]
        df = indicators.add_indicators(
            _frame(closes, highs=closes, lows=closes))
        self.assertAlmostEqual(df["vwap"].iloc[23], 100.0)
        self.assertAlmostEqual(df["vwap"].iloc[24], 200.0)
        self.assertAlmostEqual(df["vwap_sd"].iloc[24], 0.0)

    def test_vwap_single_bar_session(self):
        df = indicators.add_indicators(
            _frame([100.0], highs=[100.0], lows=[100.0]))
        self.assertAlmostEqual(df["vwap"].iloc[0], 100.0)
        self.assertAlmostEqual(df["vwap_sd"].iloc[0], 0.0)

    def test_adx_nan_before_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["adx"].iloc[:13].isna().all())

    def test_long_entry_on_drop_below_lower_band(self):
        df = _run(_oscillation_frame())
        self.assertLess(df["adx"].iloc[30], 25)
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertFalse(df["long_entry"].iloc[:30].any())
        self.assertFalse(df["short_entry"].iloc[30])

    def test_long_exit_on_close_back_to_vwap(self):
        df = _run(_oscillation_frame())
        self.assertTrue(df["long_exit"].iloc[32])

    def test_short_entry_on_spike_above_upper_band(self):
        df = _run(_oscillation_spike_frame())
        self.assertLess(df["adx"].iloc[30], 25)
        self.assertTrue(df["short_entry"].iloc[30])
        self.assertFalse(df["short_entry"].iloc[:30].any())
        self.assertFalse(df["long_entry"].iloc[30])

    def test_short_exit_on_close_back_to_vwap(self):
        df = _run(_oscillation_spike_frame())
        self.assertTrue(df["short_exit"].iloc[32])

    def test_adx_filter_blocks_entry_in_strong_trend(self):
        # Steady rise 90 -> 110: ADX hits 100, so a close above the
        # upper band must NOT short.
        closes = np.concatenate([np.linspace(90, 110, 40), [112.0]])
        df = _run(_frame(closes))
        self.assertGreater(df["adx"].iloc[40], 25)
        self.assertGreater(df["c"].iloc[40], df["vwap_upper"].iloc[40])
        self.assertFalse(df["short_entry"].iloc[40])

    def test_adx_filter_direct(self):
        rows = pd.DataFrame({
            "c": [90.0, 90.0],
            "vwap": [100.0, 100.0],
            "vwap_lower": [95.0, 95.0],
            "vwap_upper": [105.0, 105.0],
            "adx": [30.0, 20.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])  # ADX 30 blocks
        self.assertTrue(df["long_entry"].iloc[1])   # ADX 20 allows

    def test_exit_on_close_exactly_at_vwap(self):
        rows = pd.DataFrame({
            "c": [100.0, 100.0],
            "vwap": [100.0, 100.0],
            "vwap_lower": [95.0, 95.0],
            "vwap_upper": [105.0, 105.0],
            "adx": [10.0, 10.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])

    def test_zero_volume_session_no_entries(self):
        df = _run(_frame([100.0] * 60, vols=[0.0] * 60))
        self.assertTrue(df["vwap"].isna().all())
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
        for col in ("vwap", "vwap_upper", "vwap_lower", "adx",
                    "long_entry", "short_entry", "long_exit", "short_exit"):
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
