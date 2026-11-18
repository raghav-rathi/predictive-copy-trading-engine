"""ATR expansion breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.atr_breakout import indicators, risk, signals
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


def _row(c, rh, rl, atr, atr_ma, ok):
    return pd.DataFrame([dict(c=c, range_high_20=rh, range_low_20=rl,
                              atr=atr, atr_ma20=atr_ma, range_ok=ok)])


class TestAtrBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("atr_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_range_high_excludes_current_bar(self):
        closes = [100.0] * 20 + [111.0]
        df = indicators.add_indicators(_frame(closes))
        last = df.iloc[-1]
        self.assertAlmostEqual(last["range_high_20"], 100.0)
        self.assertAlmostEqual(last["range_low_20"], 100.0)

    def test_range_low_excludes_current_bar(self):
        closes = [100.0] * 20 + [89.0]
        df = indicators.add_indicators(_frame(closes))
        last = df.iloc[-1]
        self.assertAlmostEqual(last["range_low_20"], 100.0)
        self.assertLess(last["c"], last["range_low_20"] - 0.25 * last["atr"])

    def test_range_not_yet_seeded(self):
        df = indicators.add_indicators(_frame([100.0] * 10))
        self.assertTrue(df["range_high_20"].isna().all())
        self.assertTrue(df["range_low_20"].isna().all())

    def test_range_ok_consistent_with_width_and_atr(self):
        df = indicators.add_indicators(_random_walk_frame())
        width = df["range_high_20"] - df["range_low_20"]
        expect = (width <= 2.0 * df["atr"]).fillna(False)
        pd.testing.assert_series_equal(df["range_ok"], expect,
                                       check_names=False)

    def test_atr_ma20_is_sma20_of_atr(self):
        df = indicators.add_indicators(_random_walk_frame())
        expect = df["atr"].rolling(20, min_periods=20).mean()
        pd.testing.assert_series_equal(df["atr_ma20"], expect,
                                       check_names=False)

    def test_long_entry_all_conditions(self):
        df = signals.add_signals(_row(111.0, 100.0, 90.0, 5.0, 4.0, True))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])

    def test_no_long_entry_without_buffer(self):
        # Close above the level but not by 0.25*ATR (needs > 101.25).
        df = signals.add_signals(_row(101.0, 100.0, 90.0, 5.0, 4.0, True))
        self.assertFalse(df["long_entry"].iloc[0])

    def test_no_long_entry_without_expansion(self):
        df = signals.add_signals(_row(111.0, 100.0, 90.0, 3.0, 4.0, True))
        self.assertFalse(df["long_entry"].iloc[0])

    def test_no_long_entry_when_range_too_wide(self):
        df = signals.add_signals(_row(111.0, 100.0, 90.0, 5.0, 4.0, False))
        self.assertFalse(df["long_entry"].iloc[0])

    def test_short_entry_all_conditions(self):
        df = signals.add_signals(_row(88.0, 100.0, 90.0, 5.0, 4.0, True))
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])

    def test_no_short_entry_without_buffer(self):
        df = signals.add_signals(_row(89.0, 100.0, 90.0, 5.0, 4.0, True))
        self.assertFalse(df["short_entry"].iloc[0])

    def test_long_exit_back_inside_range(self):
        df = signals.add_signals(_row(99.0, 100.0, 90.0, 5.0, 6.0, True))
        self.assertTrue(df["long_exit"].iloc[0])

    def test_long_exit_on_regime_fade(self):
        # Close still above the level, but ATR faded below its average.
        df = signals.add_signals(_row(105.0, 100.0, 90.0, 3.0, 4.0, True))
        self.assertTrue(df["long_exit"].iloc[0])
        # Note: short_exit is also True here (close > range_low), which
        # is inherent to the symmetric range exits — the harness only
        # applies the exit matching the open position.

    def test_no_long_exit_while_break_holds(self):
        df = signals.add_signals(_row(105.0, 100.0, 90.0, 5.0, 4.0, True))
        self.assertFalse(df["long_exit"].iloc[0])

    def test_short_exit_mirror(self):
        df = signals.add_signals(_row(91.0, 100.0, 90.0, 5.0, 6.0, True))
        self.assertTrue(df["short_exit"].iloc[0])
        # Note: long_exit is also True here (close < range_high) — see
        # test_long_exit_on_regime_fade; the harness applies only the
        # exit matching the open position.

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
        for col in ("range_high_20", "atr", "atr_ma20",
                    "long_entry", "long_exit"):
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
