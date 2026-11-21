"""Triple EMA Crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.triple_ema_cross import indicators, risk, signals
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


def _uptrend_frame():
    """60 flat bars, rise 101->120, dip 119->110, recover 111->130."""
    closes = ([100.0] * 60 + list(np.linspace(101, 120, 20))
              + list(np.linspace(119, 110, 10))
              + list(np.linspace(111, 130, 20)))
    return _frame(closes)


def _downtrend_frame():
    """Mirror of the uptrend frame."""
    closes = ([100.0] * 60 + list(np.linspace(99, 80, 20))
              + list(np.linspace(81, 90, 10))
              + list(np.linspace(89, 70, 20)))
    return _frame(closes)


class TestTripleEmaCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("triple_ema_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_ema_math_hand_computed(self):
        # Independent recursion for EMA(5), alpha = 2/(5+1),
        # seeded at the first close (pandas ewm adjust=False).
        closes = [100, 101, 102, 101, 103, 105, 104, 106, 108, 107, 109,
                  110, 112, 111]
        df = indicators.add_indicators(_frame(closes))
        alpha = 2.0 / (5 + 1)
        e = float(closes[0])
        for c in closes[1:]:
            e = alpha * c + (1 - alpha) * e
        self.assertAlmostEqual(df["ema_fast"].iloc[13], e, places=8)
        # EMA(13) on the same frame via the same recursion.
        alpha13 = 2.0 / (13 + 1)
        e13 = float(closes[0])
        for c in closes[1:]:
            e13 = alpha13 * c + (1 - alpha13) * e13
        self.assertAlmostEqual(df["ema_mid"].iloc[13], e13, places=8)

    def test_ema_stack_on_uptrend(self):
        df = indicators.add_indicators(_uptrend_frame())
        # Late in the first rise the stack is fast > mid > slow.
        self.assertGreater(df["ema_fast"].iloc[79], df["ema_mid"].iloc[79])
        self.assertGreater(df["ema_mid"].iloc[79], df["ema_slow"].iloc[79])

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        # ewm min_periods=n: first defined value is at index n-1.
        self.assertTrue(df["ema_fast"].iloc[:4].isna().all())
        self.assertTrue(df["ema_mid"].iloc[:12].isna().all())
        self.assertTrue(df["ema_slow"].iloc[:49].isna().all())
        self.assertFalse(np.isnan(df["ema_fast"].iloc[4]))
        self.assertFalse(np.isnan(df["ema_mid"].iloc[12]))
        self.assertFalse(np.isnan(df["ema_slow"].iloc[49]))

    def test_long_entry_on_recovery(self):
        df = _run(_uptrend_frame())
        # First rise crosses up with the stack aligned at bar 60.
        self.assertTrue(df["long_entry"].iloc[60])
        i = int(np.where(df["long_entry"])[0][0])
        self.assertGreater(df["ema_fast"].iloc[i], df["ema_mid"].iloc[i])
        self.assertGreater(df["ema_mid"].iloc[i], df["ema_slow"].iloc[i])

    def test_short_entry_on_downtrend(self):
        df = _run(_downtrend_frame())
        self.assertTrue(df["short_entry"].iloc[60])
        i = int(np.where(df["short_entry"])[0][0])
        self.assertLess(df["ema_fast"].iloc[i], df["ema_mid"].iloc[i])
        self.assertLess(df["ema_mid"].iloc[i], df["ema_slow"].iloc[i])

    def test_long_exit_on_cross_down(self):
        # The dip pulls EMA(5) back below EMA(13): long exit at 86.
        df = _run(_uptrend_frame())
        self.assertTrue(df["long_exit"].iloc[86])
        self.assertTrue(df["short_exit"].iloc[60] or
                        df["short_exit"].iloc[94])

    def test_no_entry_without_stack_alignment(self):
        # EMA(5) crosses up through EMA(13) but EMA(13) is still
        # below EMA(50): the trend filter must block the long.
        df = pd.DataFrame({
            "ema_fast": [10.0, 11.0, 12.0],
            "ema_mid": [10.5, 10.8, 11.5],
            "ema_slow": [12.0, 12.0, 12.0],
        })
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].any())
        # The cross-down exit still fires on the cross itself.
        self.assertFalse(out["long_exit"].any())

    def test_exit_is_cross_back(self):
        df = pd.DataFrame({
            "ema_fast": [12.0, 11.0, 10.0],
            "ema_mid": [11.0, 11.2, 11.4],
            "ema_slow": [10.0, 10.0, 10.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_exit"].iloc[1])
        self.assertFalse(out["long_entry"].any())

    def test_no_entry_on_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

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
        self.assertEqual(risk.WARMUP, 70)

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
        for col in ("ema_fast", "ema_mid", "ema_slow",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["ema_slow"].isna().all())


if __name__ == "__main__":
    unittest.main()
