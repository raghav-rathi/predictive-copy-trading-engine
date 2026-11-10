"""Intraday Momentum Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.intraday_momentum_index import indicators, risk, signals
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


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n, opens=[close] * n)


def _signal_frame(imi):
    n = len(imi)
    return pd.DataFrame({
        "c": np.full(n, 100.0),
        "imi": np.array(imi, dtype=float),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestIntradayMomentumIndex(unittest.TestCase):
    def test_registered(self):
        self.assertIn("intraday_momentum_index", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_all_gains(self):
        # 14 bars, each gain 2, loss 0: IMI = 100 * 28 / 28 = 100.
        df = indicators.add_indicators(
            _frame([102.0] * 14, opens=[100.0] * 14))
        self.assertTrue(df["imi"].iloc[:13].isna().all())
        self.assertAlmostEqual(df["imi"].iloc[13], 100.0)

    def test_indicator_all_losses(self):
        # 14 bars, each loss 2, gain 0: IMI = 100 * 0 / 28 = 0.
        df = indicators.add_indicators(
            _frame([100.0] * 14, opens=[102.0] * 14))
        self.assertAlmostEqual(df["imi"].iloc[13], 0.0)

    def test_indicator_mixed_hand_computed(self):
        # 3 bars gain 10 (sum 30), 1 bar loss 10 (sum 10), 10 flat bars:
        # IMI = 100 * 30 / (30 + 10) = 75.
        opens = [100.0] * 3 + [110.0] + [100.0] * 10
        closes = [110.0] * 3 + [100.0] + [100.0] * 10
        df = indicators.add_indicators(_frame(closes, opens=opens))
        self.assertAlmostEqual(df["imi"].iloc[13], 75.0)
        # 7 bars gain 2 (sum 14), 7 bars loss 2 (sum 14): IMI = 50.
        opens = [100.0] * 7 + [102.0] * 7
        closes = [102.0] * 7 + [100.0] * 7
        df = indicators.add_indicators(_frame(closes, opens=opens))
        self.assertAlmostEqual(df["imi"].iloc[13], 50.0)

    def test_indicator_flat_is_fifty(self):
        # No intraday movement at all: total == 0 -> IMI = 50, not NaN.
        df = indicators.add_indicators(_flat_frame(n=30))
        self.assertTrue(df["imi"].iloc[:13].isna().all())
        self.assertTrue((df["imi"].iloc[13:] == 50.0).all())

    def test_indicator_bounded_and_rolling(self):
        # 14 gain bars then 14 loss bars: IMI 100 at bar 13, 0 at bar 27
        # once the window holds only losses.
        opens = [100.0] * 14 + [102.0] * 14
        closes = [102.0] * 14 + [100.0] * 14
        df = indicators.add_indicators(_frame(closes, opens=opens))
        self.assertAlmostEqual(df["imi"].iloc[13], 100.0)
        self.assertAlmostEqual(df["imi"].iloc[27], 0.0)
        # Midway (7 gains + 7 losses in window) it is exactly 50.
        self.assertAlmostEqual(df["imi"].iloc[20], 50.0)
        # Bounded [0, 100] on a random walk.
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[indicators.IMI_PERIOD:]
        self.assertTrue(np.isfinite(tail["imi"]).all())
        self.assertTrue(((tail["imi"] >= 0.0) & (tail["imi"] <= 100.0)).all())

    def test_indicator_uses_open_to_close_not_close_to_close(self):
        # Close-to-close is flat (c == 100 every bar) but each bar moves
        # intraday: gains of 2 on every bar -> IMI must be 100, while a
        # close-to-close RSI-style measure would see no movement at all.
        df = indicators.add_indicators(
            _frame([100.0] * 14, opens=[98.0] * 14))
        self.assertAlmostEqual(df["imi"].iloc[13], 100.0)

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
        self.assertEqual(risk.WARMUP, 30)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("net_pnl_usd", m)
        self.assertIn("sharpe", m)

    def test_long_entry_on_cross_up_30(self):
        # IMI crosses up through 30 at index 2.
        df = signals.add_signals(_signal_frame([25, 28, 31, 35]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])

    def test_short_entry_on_cross_down_70(self):
        # IMI crosses down through 70 at index 2.
        df = signals.add_signals(_signal_frame([75, 72, 68, 65]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_exits(self):
        # Crossing above 70 exits a long.
        df = signals.add_signals(_signal_frame([65, 68, 72, 75]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        # Crossing below 30 exits a short.
        df = signals.add_signals(_signal_frame([35, 32, 28, 25]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_cross_no_signal(self):
        # IMI pinned at 50 the whole time: no entries, no exits.
        df = signals.add_signals(_signal_frame([50.0] * 20))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("imi", "long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the 14-bar window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertTrue(df["imi"].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c == o): IMI 50, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200, opens=[100.0] * 200))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue((tail["imi"] == 50.0).all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
