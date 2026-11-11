"""Random Walk Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rwi import indicators, risk, signals
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
                  vols=[vol] * n)


def _signal_frame(rows):
    """Direct signal unit-test frame from explicit per-bar dicts."""
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


class TestRWI(unittest.TestCase):
    def test_registered(self):
        self.assertIn("rwi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat_range(self):
        # Constant 10-point range: TR = 10 every bar, so Wilder ATR(14)
        # converges to exactly 10; RWI-high = RWI-low = (110-100)/10 = 1.0
        # once the ATR has converged (bar 14+).
        df = indicators.add_indicators(
            _frame([105.0] * 200, highs=[110.0] * 200, lows=[100.0] * 200))
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertAlmostEqual(df["atr_14"].iloc[30], 10.0, places=9)
        self.assertAlmostEqual(df["rwi_high"].iloc[30], 1.0, places=9)
        self.assertAlmostEqual(df["rwi_low"].iloc[30], 1.0, places=9)
        self.assertAlmostEqual(df["rwi_high"].iloc[100], 1.0, places=9)

    def test_indicator_hand_computed_spike(self):
        # 100 flat bars (h=110, l=100, c=105, ATR=10), then bar 100
        # spikes high to 120. TR[100] = max(20, |120-105|, |100-105|) = 20,
        # so ATR[100] = 10 + (20-10)/14 = 10.7142857 and
        # RWI-high[100] = (120-100)/10.7142857 = 1.8666667.
        n = 120
        closes = [105.0] * n
        highs = [110.0] * n
        lows = [100.0] * n
        highs[100] = 120.0
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertAlmostEqual(df["atr_14"].iloc[100], 10.0 + 10.0 / 14.0, places=9)
        self.assertAlmostEqual(df["rwi_high"].iloc[100], 20.0 / (10.0 + 10.0 / 14.0), places=9)
        # RWI-low is unchanged by the high spike: (110-100)/ATR.
        self.assertAlmostEqual(
            df["rwi_low"].iloc[100], 10.0 / (10.0 + 10.0 / 14.0), places=9)

    def test_long_entry_on_high_spike(self):
        # Full pipeline: flat range, then a high spike pushes RWI-high
        # from 1.0 to ~1.87 -> long_entry on the spike bar, and the
        # short_exit fires on the same bar (opposite RWI rule).
        n = 120
        closes = [105.0] * n
        highs = [110.0] * n
        lows = [100.0] * n
        highs[100] = 120.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["long_entry"].iloc[100])
        self.assertTrue(df["short_exit"].iloc[100])
        self.assertFalse(df["short_entry"].iloc[100])

    def test_short_entry_on_low_spike(self):
        # Mirror image: a low spike to 90 pushes RWI-low above 1.0.
        n = 120
        closes = [105.0] * n
        highs = [110.0] * n
        lows = [100.0] * n
        lows[100] = 90.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["short_entry"].iloc[100])
        self.assertTrue(df["long_exit"].iloc[100])
        self.assertFalse(df["long_entry"].iloc[100])

    def test_signal_logic_crafted_rows(self):
        base = dict(rwi_high=0.9, rwi_low=0.9)
        # RWI-high crosses above 1.0: long entry + short exit.
        rows = [dict(base, rwi_high=0.9), dict(base, rwi_high=1.2)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[0])
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["short_exit"].iloc[1])
        # RWI-low crosses above 1.0: short entry + long exit.
        rows = [dict(base, rwi_low=0.8), dict(base, rwi_low=1.5)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertTrue(out["short_entry"].iloc[1])
        self.assertTrue(out["long_exit"].iloc[1])
        self.assertFalse(out["long_entry"].iloc[1])
        # At exactly 1.0 there is no cross (strict >).
        rows = [dict(base, rwi_high=0.9), dict(base, rwi_high=1.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[1])
        # NaN RWI (warmup / zero ATR): no signal, no crash.
        rows = [dict(rwi_high=np.nan, rwi_low=np.nan)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[0])
        self.assertFalse(out["short_entry"].iloc[0])
        self.assertFalse(out["long_exit"].iloc[0])
        self.assertFalse(out["short_exit"].iloc[0])

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
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        # Constant 2-point range: RWI sits exactly at 1.0, never crosses.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("atr_14", "rwi_high", "rwi_low",
                    "long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): ATR is 0, RWI is NaN, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
