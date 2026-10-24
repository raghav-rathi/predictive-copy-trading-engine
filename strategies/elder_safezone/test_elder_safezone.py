"""Elder SafeZone tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elder_safezone import indicators, risk, signals
from strategies.elder_safezone.indicators import EMA_N, SZ_N, PEN_MULT


def _frame_from_parts(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("ema22", "safezone_long", "safezone_short", "atr"):
            self.assertIn(col, ind.columns)

    def test_no_nan_after_warmup(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("ema22", "safezone_long", "safezone_short"):
            self.assertFalse(ind[col].isna().any(), col)

    def test_safezone_long_hand_computation(self):
        # 20 bars, lows falling 1/bar: 100..81. Last 10-bar window
        # lows 90..81: highest low = 90, penetration = 1 every bar,
        # avg = 1 -> safezone_long = 90 - 2.5*1 = 87.5.
        n = 20
        low = np.arange(100.0, 100.0 - n, -1.0)
        high = low + 2.0
        close = low + 1.0
        df = _frame_from_parts(close, high, low, close, np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["safezone_long"].iloc[-1]), 87.5, places=9)

    def test_safezone_short_hand_computation(self):
        # 20 bars, highs rising 1/bar: 100..119. Last 10-bar window
        # highs 110..119: lowest high = 110, penetration = 1 every
        # bar, avg = 1 -> safezone_short = 110 + 2.5*1 = 112.5.
        n = 20
        high = np.arange(100.0, 100.0 + n, 1.0)
        low = high - 2.0
        close = high - 1.0
        df = _frame_from_parts(close, high, low, close, np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["safezone_short"].iloc[-1]), 112.5, places=9)

    def test_zero_penetration_hugs_extreme(self):
        # Flat lows (no counter-trend penetration at all): avg pen = 0,
        # so safezone_long == highest low of the window.
        n = 20
        low = np.full(n, 100.0)
        high = np.full(n, 102.0)
        close = np.full(n, 101.0)
        df = _frame_from_parts(close, high, low, close, np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["safezone_long"].iloc[-1]), 100.0, places=9)

    def test_deep_penetration_pushes_line_down(self):
        # Same highest low as the flat case but with deep 4-point
        # penetrations: the line must sit strictly below 100.
        n = 20
        low = np.full(n, 100.0)
        low[1::2] = 96.0  # alternate bars dip 4 below the prior low
        high = low + 2.0
        close = low + 1.0
        df = _frame_from_parts(close, high, low, close, np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertLess(float(ind["safezone_long"].iloc[-1]), 100.0)

    def test_ema22_tracks_close(self):
        # Steadily rising closes -> ema22 below the last close but
        # above the start (a lagging average, not a lookahead).
        c = np.linspace(100.0, 150.0, 100)
        df = _frame_from_close(c)
        ind = indicators.add_indicators(df)
        self.assertLess(float(ind["ema22"].iloc[-1]), 150.0)
        self.assertGreater(float(ind["ema22"].iloc[-1]), 100.0)

    def test_no_lookahead(self):
        # safezone_long at bar j must not change when later bars
        # are appended.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["safezone_long"].iloc[:200].reset_index(drop=True),
            ind_short["safezone_long"].reset_index(drop=True),
            check_names=False,
        )

    def test_long_line_at_or_below_lows_in_uptrend(self):
        # In a clean uptrend the long line must trail at or below
        # the recent lows (it is a stop line, not a resistance
        # line). With zero counter-trend penetration it sits
        # exactly at the highest low of the window.
        c = np.linspace(100.0, 140.0, 100)
        df = _frame_from_close(c)
        ind = indicators.add_indicators(df)
        self.assertLessEqual(float(ind["safezone_long"].iloc[-1]),
                             float(df["l"].iloc[-1]))
        self.assertLess(float(ind["safezone_long"].iloc[-1]),
                        float(df["c"].iloc[-1]))


class TestSignals(unittest.TestCase):
    def _direct_frame(self, ema_slope=0.05, cross_bar=50, direction=1,
                      szl_offset=-2.0, szs_offset=2.0):
        """Deterministic frame: EMA is a straight ramp (no noise).

        direction=1: close rides 1 below ema, jumps 1 above at
        cross_bar (a clean cross_above on bar cross_bar).
        direction=-1: mirror.
        SafeZone lines sit szl_offset/szs_offset from the close path
        so the SafeZone condition can be toggled by the offsets.
        """
        n = 100
        ema = 100.0 + ema_slope * np.arange(n)
        close = np.empty(n)
        if direction == 1:
            close[:] = ema - 1.0
            close[cross_bar:] = ema[cross_bar:] + 1.0
        else:
            close[:] = ema + 1.0
            close[cross_bar:] = ema[cross_bar:] - 1.0
        df = _frame_from_close(close, seed=9)
        df["ema22"] = ema
        df["safezone_long"] = close + szl_offset
        df["safezone_short"] = close + szs_offset
        return df

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_cross_above_ema_while_above_line(self):
        # Clean cross above, close 2 above the long line -> fires
        # exactly at the cross bar.
        df = self._direct_frame(direction=1, szl_offset=-2.0)
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_entry"].iloc[50])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_long_entry_blocked_below_safezone_line(self):
        # Same cross, but the long line sits 2 ABOVE the close ->
        # the SafeZone condition blocks the entry.
        df = self._direct_frame(direction=1, szl_offset=2.0)
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())

    def test_short_entry_symmetry(self):
        # Mirror: cross below, close 2 below the short line -> fires
        # exactly at the cross bar.
        df = self._direct_frame(direction=-1, szs_offset=2.0)
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_entry"].iloc[50])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_short_entry_blocked_above_safezone_line(self):
        # Cross below, but the short line sits 2 BELOW the close ->
        # blocked.
        df = self._direct_frame(direction=-1, szs_offset=-2.0)
        sig = signals.add_signals(df)
        self.assertFalse(sig["short_entry"].any())

    def test_long_exit_on_close_below_line(self):
        # After entry, close drops 5 below the long line at bar 70
        # -> long_exit fires exactly there.
        df = self._direct_frame(direction=1, szl_offset=-2.0)
        close = df["c"].to_numpy().copy()
        close[70:] = df["safezone_long"].to_numpy()[70:] - 5.0
        df["c"] = close
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["long_exit"].iloc[50])

    def test_short_exit_on_close_above_line(self):
        df = self._direct_frame(direction=-1, szs_offset=2.0)
        close = df["c"].to_numpy().copy()
        close[70:] = df["safezone_short"].to_numpy()[70:] + 5.0
        df["c"] = close
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_exit"].iloc[70])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.5)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 96)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 60)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
