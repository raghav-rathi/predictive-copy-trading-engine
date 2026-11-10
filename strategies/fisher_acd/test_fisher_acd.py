"""Fisher ACD opening-range system tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fisher_acd import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

# 2026-01-01 00:00 UTC, so hourly bars align exactly to UTC days.
MIDNIGHT_MS = 1_767_225_600_000


def _frame(closes, highs=None, lows=None, vols=None, opens=None,
           start=MIDNIGHT_MS):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (start + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=48, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(closes, a_up=102.0, a_down=98.0, c_up=104.0, c_down=96.0,
                  or_high=101.0, or_low=99.0, pivot=100.0, day_index=1):
    n = len(closes)
    di = [day_index] * n if isinstance(day_index, int) else list(day_index)
    return pd.DataFrame({
        "c": np.array(closes, dtype=float),
        "a_up": np.full(n, float(a_up)),
        "a_down": np.full(n, float(a_down)),
        "c_up": np.full(n, float(c_up)),
        "c_down": np.full(n, float(c_down)),
        "or_high": np.full(n, float(or_high)),
        "or_low": np.full(n, float(or_low)),
        "pivot_prev_day": np.full(n, float(pivot)),
        "day_index": np.array(di, dtype=int),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (MIDNIGHT_MS + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestFisherAcd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("fisher_acd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat_hand_computed(self):
        # Every bar: o=100, h=101, l=99, c=100. True range is 2 on every
        # bar, so Wilder ATR(14) is exactly 2.0 once valid (bar 13).
        # Day 1 = bars 0-23, day 2 = bars 24-47; both days share the same
        # OR (101/99) and the previous-day pivot (101+99+100)/3 = 100.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(df["atr14"].iloc[:13].isna().all())
        self.assertTrue(np.allclose(df["atr14"].iloc[13:], 2.0))
        self.assertTrue((df["or_high"] == 101.0).all())
        self.assertTrue((df["or_low"] == 99.0).all())
        # A = OR edge +/- 0.5*ATR = +/- 1.0; C = OR edge +/- 1.5*ATR = +/- 3.0.
        self.assertTrue(np.allclose(df["a_up"].iloc[13:], 102.0))
        self.assertTrue(np.allclose(df["a_down"].iloc[13:], 98.0))
        self.assertTrue(np.allclose(df["c_up"].iloc[13:], 104.0))
        self.assertTrue(np.allclose(df["c_down"].iloc[13:], 96.0))
        # No previous-day pivot on day 1; exactly 100.0 on day 2.
        self.assertTrue(df["pivot_prev_day"].iloc[:24].isna().all())
        self.assertTrue(np.allclose(df["pivot_prev_day"].iloc[24:], 100.0))
        # day_index restarts at each UTC midnight.
        self.assertEqual(df["day_index"].iloc[0], 0)
        self.assertEqual(df["day_index"].iloc[23], 23)
        self.assertEqual(df["day_index"].iloc[24], 0)
        self.assertEqual(df["day_index"].iloc[47], 23)

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.isfinite(tail["atr14"]).all())
        self.assertTrue((tail["a_up"] > tail["or_high"]).all())
        self.assertTrue((tail["a_down"] < tail["or_low"]).all())
        self.assertTrue((tail["c_up"] > tail["a_up"]).all())
        self.assertTrue((tail["c_down"] < tail["a_down"]).all())
        self.assertTrue(np.isfinite(tail["pivot_prev_day"]).all())
        # OR levels are constant within each UTC day.
        self.assertTrue(
            (df.groupby(df["t"] // 86_400_000)["or_high"].nunique() == 1).all())
        self.assertTrue(
            (df.groupby(df["t"] // 86_400_000)["or_low"].nunique() == 1).all())

    def test_or_uses_first_bar_only(self):
        # Day 2 opens with a wide first bar (h=110, l=90), then trades
        # tight: the OR must stay 110/90 all day, not track later bars.
        closes = [100.0] * 48
        highs = [101.0] * 48
        lows = [99.0] * 48
        highs[24] = 110.0
        lows[24] = 90.0
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertTrue((df["or_high"].iloc[24:] == 110.0).all())
        self.assertTrue((df["or_low"].iloc[24:] == 90.0).all())
        self.assertTrue((df["or_high"].iloc[:24] == 101.0).all())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 48)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertIn("net_pnl_usd", m)
        self.assertIn("sharpe", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_a_up_cross_above_pivot(self):
        # Close crosses above A-up (102) at index 2, above pivot 100.
        df = signals.add_signals(_signal_frame([100, 101, 103, 103]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_a_down_cross_below_pivot(self):
        # Close crosses below A-down (98) at index 2, below pivot 100.
        df = signals.add_signals(_signal_frame([100, 99, 97, 97]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_pivot_filter_blocks_entry(self):
        # Same A-up cross, but close is below the pivot: no long entry.
        df = signals.add_signals(_signal_frame([100, 101, 103, 103], pivot=105.0))
        self.assertFalse(df["long_entry"].any())
        # Same A-down cross, but close is above the pivot: no short entry.
        df = signals.add_signals(_signal_frame([100, 99, 97, 97], pivot=95.0))
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_on_first_bar_of_day(self):
        # A-up cross on a day_index==0 bar must not fire an entry.
        df = signals.add_signals(_signal_frame(
            [100, 101, 103, 103], day_index=[0, 0, 0, 1]))
        self.assertFalse(df["long_entry"].iloc[2])
        df = signals.add_signals(_signal_frame(
            [100, 99, 97, 97], day_index=[0, 0, 0, 1]))
        self.assertFalse(df["short_entry"].iloc[2])

    def test_b_exits_at_or_edges(self):
        # Close below OR low exits a long; close above OR high exits a short.
        df = signals.add_signals(_signal_frame([100, 98.5]))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        df = signals.add_signals(_signal_frame([100, 101.5]))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])

    def test_failed_a_up_reverses_to_short(self):
        # Prev close already below A-down (no A-down cross), but close
        # breaks below C-down (96): long exit AND short entry on that bar.
        df = signals.add_signals(_signal_frame([97, 95]))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_failed_a_down_reverses_to_long(self):
        # Prev close already above A-up (no A-up cross), but close breaks
        # above C-up (104): short exit AND long entry on that bar.
        df = signals.add_signals(_signal_frame([103, 105]))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

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
        for col in ("atr14", "or_high", "or_low", "a_up", "a_down",
                    "c_up", "c_down", "pivot_prev_day",
                    "long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_no_lookahead_future_alteration(self):
        # Changing closes after bar 200 must not change signals on bars < 200.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(5).normal(0.0005, 0.01, 300))))
        df1 = _run(_frame(closes))
        altered = closes[:200] + [50.0] * 100
        df2 = _run(_frame(altered))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than warmup: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): ATR is 0, A/C levels collapse
        # onto the OR edges, close never strictly crosses: no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        self.assertTrue((df["atr14"].iloc[13:] == 0.0).all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
