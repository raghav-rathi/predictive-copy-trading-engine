"""CCI + MACD combo tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cci_macd_combo import indicators, risk, signals
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


class TestCciMacdCombo(unittest.TestCase):
    def test_registered(self):
        self.assertIn("cci_macd_combo", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)
            self.assertFalse(df[col].isna().any())

    def test_typical_price_exact(self):
        # h=110, l=90, c=100 -> TP = 100.
        df = indicators.add_indicators(_frame(
            [100.0], highs=[110.0], lows=[90.0]))
        self.assertAlmostEqual(df["tp"].iloc[0], 100.0)
        # h=120, l=90, c=105 -> TP = 105.
        df = indicators.add_indicators(_frame(
            [105.0], highs=[120.0], lows=[90.0]))
        self.assertAlmostEqual(df["tp"].iloc[0], 105.0)

    def test_cci_exact(self):
        # 13 bars TP=100, bar 13 TP=114, bars 14..26 TP=100.
        # At bar 26 the 14-bar window (bars 13..26) holds thirteen 100s
        # and one 114: SMA = 101, mean dev = (13*1 + 13)/14 = 26/14,
        # CCI = (100-101) / (0.015 * 26/14) = -35.897...
        # (CCI is first defined at bar 26: the SMA needs 14 bars and the
        # deviation mean needs 14 defined deviations.)
        closes = [100.0] * 13 + [114.0] + [100.0] * 13
        df = indicators.add_indicators(_frame(closes + [100.0] * 30))
        self.assertTrue(np.isnan(df["cci"].iloc[13]))
        self.assertAlmostEqual(df["cci"].iloc[26], -35.8974358974359)
        self.assertEqual(int(df["cci"].first_valid_index()), 26)

    def test_cci_flat_is_nan(self):
        # Flat typical price: mean deviation 0 -> CCI NaN, never a signal.
        df = indicators.add_indicators(_flat_frame())
        self.assertTrue(df["cci"].iloc[60:].isna().all())

    def test_macd_columns_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(np.isfinite(df["macd"].iloc[60:]).all())
        self.assertTrue(np.isfinite(df["macd_signal"].iloc[60:]).all())

    def test_signal_logic_crafted_rows(self):
        # CCI crosses up through -100 (prev -150 -> -50) with MACD
        # line above signal -> long entry.
        rows = [dict(cci=-150.0, macd=1.0, macd_signal=0.0),
                dict(cci=-50.0, macd=1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # CCI crosses down through +100 (prev 150 -> 50) with MACD
        # line below signal -> short entry.
        rows = [dict(cci=150.0, macd=-1.0, macd_signal=0.0),
                dict(cci=50.0, macd=-1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_long_entry_needs_macd_bullish(self):
        # CCI crosses up through -100 but MACD line is BELOW signal:
        # no long entry.
        rows = [dict(cci=-150.0, macd=-1.0, macd_signal=0.0),
                dict(cci=-50.0, macd=-1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])

    def test_short_entry_needs_macd_bearish(self):
        # CCI crosses down through +100 but MACD line is ABOVE signal:
        # no short entry.
        rows = [dict(cci=150.0, macd=1.0, macd_signal=0.0),
                dict(cci=50.0, macd=1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["short_entry"].iloc[1])

    def test_exit_on_cci_zero_cross(self):
        # Long exit: CCI crosses down through 0 (prev 10 -> -10).
        rows = [dict(cci=10.0, macd=1.0, macd_signal=0.0),
                dict(cci=-10.0, macd=1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # Short exit: CCI crosses up through 0 (prev -10 -> 10).
        rows = [dict(cci=-10.0, macd=-1.0, macd_signal=0.0),
                dict(cci=10.0, macd=-1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])

    def test_no_cross_no_entry(self):
        # CCI drifts inside (-100, +100): no threshold cross, no entries.
        rows = [dict(cci=-50.0, macd=1.0, macd_signal=0.0),
                dict(cci=-20.0, macd=1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_entries_fire_on_random_walk(self):
        df = _run(_random_walk_frame())
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertGreater(int(df["short_entry"].sum()), 0)

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
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("cci", "macd_hist", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertEqual(len(df), 10)


if __name__ == "__main__":
    unittest.main()
