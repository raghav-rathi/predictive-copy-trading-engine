"""Climax Reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.climax_reversal import indicators, risk, signals
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


def _signal_frame(rows):
    return pd.DataFrame(rows)


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


def _climax_frame():
    """20 quiet bars (vol 100, range 90-110, close 100), then one
    buying-climax bar: new high 120, vol 250, close 95 (lower third
    of the 90-120 range: (95-90)/30 = 1/6)."""
    n = 21
    closes = [100.0] * 20 + [95.0]
    highs = [110.0] * 20 + [120.0]
    lows = [90.0] * 20 + [90.0]
    vols = [100.0] * 20 + [250.0]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


def _selling_climax_frame():
    """Mirror: 20 quiet bars, then a selling-climax bar: new low 80,
    vol 250, close 105 (upper third of the 80-110 range:
    (105-80)/30 = 5/6)."""
    closes = [100.0] * 20 + [105.0]
    highs = [110.0] * 20 + [110.0]
    lows = [90.0] * 20 + [80.0]
    vols = [100.0] * 20 + [250.0]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


class TestClimaxReversal(unittest.TestCase):
    def test_registered(self):
        self.assertIn("climax_reversal", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_buying_climax_exact(self):
        df = indicators.add_indicators(_climax_frame())
        last = df.iloc[-1]
        # vol_mean_20 = mean of previous 20 bars = 100; ratio 2.5.
        self.assertAlmostEqual(last["vol_mean_20"], 100.0)
        self.assertAlmostEqual(last["vol_ratio"], 2.5)
        self.assertAlmostEqual(last["close_pos"], 1.0 / 6.0)
        self.assertEqual(last["high_20"], 120.0)
        self.assertTrue(last["buying_climax"])
        self.assertFalse(last["selling_climax"])
        # No climax on the quiet bars (volume not spiking).
        self.assertFalse(df["buying_climax"].iloc[:-1].any())
        self.assertFalse(df["selling_climax"].iloc[:-1].any())

    def test_selling_climax_exact(self):
        df = indicators.add_indicators(_selling_climax_frame())
        last = df.iloc[-1]
        self.assertAlmostEqual(last["vol_ratio"], 2.5)
        self.assertAlmostEqual(last["close_pos"], 5.0 / 6.0)
        self.assertEqual(last["low_20"], 80.0)
        self.assertTrue(last["selling_climax"])
        self.assertFalse(last["buying_climax"])

    def test_close_pos_exact(self):
        # Bar with h=110, l=90, c=95 -> close_pos 0.25 (lower third).
        df = indicators.add_indicators(_frame(
            [95.0] * 30, highs=[110.0] * 30, lows=[90.0] * 30))
        self.assertAlmostEqual(df["close_pos"].iloc[-1], 0.25)
        # c=105 -> 0.75 (upper third).
        df = indicators.add_indicators(_frame(
            [105.0] * 30, highs=[110.0] * 30, lows=[90.0] * 30))
        self.assertAlmostEqual(df["close_pos"].iloc[-1], 0.75)

    def test_no_climax_without_volume_spike(self):
        # New high + weak close but volume only 1.5x mean: no climax.
        df = indicators.add_indicators(_frame(
            [100.0] * 20 + [95.0], highs=[110.0] * 20 + [120.0],
            lows=[90.0] * 21, vols=[100.0] * 20 + [150.0]))
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 1.5)
        self.assertFalse(df["buying_climax"].iloc[-1])

    def test_no_climax_without_weak_close(self):
        # New high + volume spike but close in the upper third:
        # strong close, not a buying climax.
        df = indicators.add_indicators(_frame(
            [100.0] * 20 + [115.0], highs=[110.0] * 20 + [120.0],
            lows=[90.0] * 21, vols=[100.0] * 20 + [250.0]))
        self.assertAlmostEqual(df["close_pos"].iloc[-1], 25.0 / 30.0)
        self.assertFalse(df["buying_climax"].iloc[-1])

    def test_volume_threshold_strict(self):
        # Exactly 2.0x mean volume is NOT a spike (strict >).
        df = indicators.add_indicators(_frame(
            [100.0] * 20 + [95.0], highs=[110.0] * 20 + [120.0],
            lows=[90.0] * 21, vols=[100.0] * 20 + [200.0]))
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 2.0)
        self.assertFalse(df["buying_climax"].iloc[-1])

    def test_signal_logic_crafted_rows(self):
        # Buying climax -> short entry + long exit; selling climax
        # -> long entry + short exit.
        rows = [dict(buying_climax=True, selling_climax=False)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])
        rows = [dict(buying_climax=False, selling_climax=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        # No climax: nothing fires.
        rows = [dict(buying_climax=False, selling_climax=False)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])

    def test_entries_fire_on_climax_frames(self):
        df = _run(_climax_frame())
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertTrue(df["long_exit"].iloc[-1])
        df = _run(_selling_climax_frame())
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertTrue(df["short_exit"].iloc[-1])

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
        # Flat closes, constant volume: no new extremes, no climax.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("buying_climax", "selling_climax", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): close_pos NaN, no climax.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100, vols=[1000.0] * 100))
        self.assertTrue(df["close_pos"].isna().all())
        self.assertFalse(df["buying_climax"].any())
        self.assertFalse(df["selling_climax"].any())


if __name__ == "__main__":
    unittest.main()
