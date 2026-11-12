"""Price channel breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.price_channel_breakout import indicators, risk, signals
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


def _base_30(hi=101.0, lo=99.0, close=100.0):
    """31 flat base bars; the caller appends probe bars. 31 (not 30)
    so the probe bar has a defined channel value on the prior bar too
    -- the cross test compares against the previous bar's channel."""
    return _frame([close] * 31, highs=[hi] * 31, lows=[lo] * 31)


class TestPriceChannelBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("price_channel_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_channel_values_hand_computed(self):
        # 30 flat bars h=101/l=99: on bar 30 the channel is 101/99
        # and the midline is exactly 100.
        df = _base_30()
        probe = _frame([100.0], highs=[101.0], lows=[99.0])
        df = pd.concat([df, probe], ignore_index=True)
        df = indicators.add_indicators(df)
        self.assertAlmostEqual(df["channel_high"].iloc[30], 101.0)
        self.assertAlmostEqual(df["channel_low"].iloc[30], 99.0)
        self.assertAlmostEqual(df["channel_mid"].iloc[30], 100.0)
        # Before bar 30 there are not enough prior bars: NaN.
        self.assertTrue(np.isnan(df["channel_high"].iloc[29]))
        self.assertTrue(np.isfinite(df["channel_high"].iloc[30]))

    def test_long_entry_on_breakout(self):
        # Flat at 100, then a bar closing at 102: breaks above the
        # 30-bar channel high (101).
        df = _base_30()
        probe = _frame([102.0], highs=[102.5], lows=[101.5])
        df = pd.concat([df, probe], ignore_index=True)
        df = _run(df)
        self.assertTrue(df["long_entry"].iloc[31])
        self.assertFalse(df["short_entry"].iloc[31])
        self.assertFalse(df["long_entry"].iloc[:31].any())
        # Mirror: a close at 98 breaks below the channel low (99).
        df = _base_30()
        probe = _frame([98.0], highs=[98.5], lows=[97.5])
        df = pd.concat([df, probe], ignore_index=True)
        df = _run(df)
        self.assertTrue(df["short_entry"].iloc[31])
        self.assertFalse(df["long_entry"].iloc[31])

    def test_no_entry_on_small_move(self):
        # A close at 100.5 stays inside the 101/99 channel: no entry.
        df = _base_30()
        probe = _frame([100.5], highs=[101.0], lows=[100.0])
        df = pd.concat([df, probe], ignore_index=True)
        df = _run(df)
        self.assertFalse(df["long_entry"].iloc[31])
        self.assertFalse(df["short_entry"].iloc[31])

    def test_close_exactly_on_band_is_not_breakout(self):
        # Close exactly equal to the channel high is not a break
        # (strict >).
        df = _base_30()
        probe = _frame([101.0], highs=[101.5], lows=[100.5])
        df = pd.concat([df, probe], ignore_index=True)
        df = _run(df)
        self.assertFalse(df["long_entry"].iloc[31])

    def test_long_exit_on_midline_cross(self):
        # Break out long at bar 31 (close 102), hold at 101 on bar 32,
        # then close 99.5 on bar 33: crosses below the midline
        # (102.5 + 99) / 2 = 100.75, so long_exit fires on bar 33.
        df = _base_30()
        probes = _frame([102.0, 101.0, 99.5],
                        highs=[102.5, 101.5, 100.0],
                        lows=[101.5, 100.5, 99.0])
        df = pd.concat([df, probes], ignore_index=True)
        df = _run(df)
        self.assertTrue(df["long_entry"].iloc[31])
        self.assertFalse(df["long_exit"].iloc[31])
        self.assertFalse(df["long_exit"].iloc[32])
        self.assertTrue(df["long_exit"].iloc[33])

    def test_short_exit_on_midline_cross(self):
        # Break out short at bar 31 (close 98), hold at 99 on bar 32,
        # then close 101 on bar 33: crosses above the midline
        # (101 + 97.5) / 2 = 99.25, so short_exit fires on bar 33.
        df = _base_30()
        probes = _frame([98.0, 99.0, 101.0],
                        highs=[98.5, 99.5, 101.5],
                        lows=[97.5, 98.5, 100.5])
        df = pd.concat([df, probes], ignore_index=True)
        df = _run(df)
        self.assertTrue(df["short_entry"].iloc[31])
        self.assertFalse(df["short_exit"].iloc[31])
        self.assertFalse(df["short_exit"].iloc[32])
        self.assertTrue(df["short_exit"].iloc[33])

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
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("channel_high", "channel_low", "channel_mid",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): the channel collapses onto
        # the price, so no close can break it.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
