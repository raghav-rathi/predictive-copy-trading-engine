"""Supertrend Parabolic tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.supertrend_parabolic import indicators, risk, signals
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


def _risk_checks(tc):
    tc.assertEqual(risk.RISK.atr_window, 14)
    tc.assertEqual(risk.RISK.stop_atr_mult, 2.0)
    tc.assertEqual(risk.RISK.trail_atr_mult, 2.5)
    tc.assertIsNone(risk.RISK.target_atr_mult)
    tc.assertEqual(risk.RISK.max_hold_bars, 120)
    tc.assertEqual(risk.RISK.risk_frac, 0.01)
    tc.assertEqual(risk.RISK.max_leverage, 3.0)
    tc.assertEqual(risk.RISK.fee_rate, 0.00045)
    tc.assertEqual(risk.RISK.slippage_rate, 0.0001)
    tc.assertTrue(risk.RISK.allow_longs)
    tc.assertTrue(risk.RISK.allow_shorts)
    tc.assertEqual(risk.WARMUP, 60)


class TestSupertrendParabolic(unittest.TestCase):
    def test_registered(self):
        self.assertIn("supertrend_parabolic", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_psar_below_price_in_rising_series(self):
        closes = [100.0 + i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertLess(df["psar"].iloc[-1], df["c"].iloc[-1])
        # PSAR rises with price in an uptrend.
        self.assertGreater(df["psar"].iloc[-1], df["psar"].iloc[20])

    def test_psar_above_price_in_falling_series(self):
        closes = [200.0 - i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertGreater(df["psar"].iloc[-1], df["c"].iloc[-1])

    def test_psar_starts_below_price(self):
        closes = [100.0 + i * 0.5 for i in range(50)]
        df = indicators.add_indicators(_frame(closes))
        self.assertLess(df["psar"].iloc[0], df["c"].iloc[0])

    def test_supertrend_dir_up_on_rise(self):
        closes = [100.0 + i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertEqual(df["supertrend_dir"].iloc[-1], 1.0)

    def test_supertrend_dir_down_on_fall(self):
        closes = [200.0 - i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertEqual(df["supertrend_dir"].iloc[-1], -1.0)

    def test_signal_logic_crafted_rows(self):
        # Agreement turns on long: prior bar not above both, now above both.
        rows = pd.DataFrame([
            dict(c=99.0, supertrend=100.0, psar=101.0),
            dict(c=102.0, supertrend=100.0, psar=101.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Agreement turns on short.
        rows = pd.DataFrame([
            dict(c=101.0, supertrend=100.0, psar=99.0),
            dict(c=98.0, supertrend=100.0, psar=99.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_no_entry_when_already_above_both(self):
        rows = pd.DataFrame([
            dict(c=102.0, supertrend=100.0, psar=101.0),
            dict(c=103.0, supertrend=100.0, psar=101.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])

    def test_no_entry_when_only_one_line_agrees(self):
        rows = pd.DataFrame([
            dict(c=99.0, supertrend=100.0, psar=98.0),
            dict(c=101.0, supertrend=102.0, psar=98.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_exit_long_on_either_line_flip(self):
        # Price below the Supertrend line alone exits a long, even
        # though it is still above the PSAR.
        rows = pd.DataFrame([dict(c=99.0, supertrend=100.0, psar=98.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        # Price below the PSAR alone also exits a long.
        rows = pd.DataFrame([dict(c=97.0, supertrend=100.0, psar=98.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        # Price above the PSAR alone exits a short, even though it
        # is still below the Supertrend line.
        rows = pd.DataFrame([dict(c=101.0, supertrend=100.0, psar=98.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_risk_config_sane(self):
        _risk_checks(self)

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
        # Flat price sits above both trend lines once they seed, so
        # the agreement turn-on fires exactly once; it never sits
        # below both lines, so no short entry ever fires.
        df = _run(_flat_frame())
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("supertrend", "psar", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # 5 bars: Supertrend (ATR 10) has not seeded yet, so no
        # agreement can turn on.
        df = _run(_flat_frame(n=5))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
