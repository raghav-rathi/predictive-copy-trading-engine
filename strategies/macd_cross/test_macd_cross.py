"""MACD signal-line crossover tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_cross import indicators, risk, signals
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


class TestMacdCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("macd_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_macd_flat_zero(self):
        # Flat close: both EMAs equal the close, so MACD, signal and
        # histogram are all exactly 0 after warmup.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["macd"], 0.0, atol=1e-12))
        self.assertTrue(np.allclose(tail["macd_signal"], 0.0, atol=1e-12))
        self.assertTrue(np.allclose(tail["macd_hist"], 0.0, atol=1e-12))

    def test_macd_hand_computed(self):
        # Independent EMA computation of the MACD line and signal line
        # on random data, compared against the indicator columns.
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        df = indicators.add_indicators(_frame(closes))
        c = pd.Series(closes)
        ema12 = c.ewm(span=12, adjust=False, min_periods=12).mean()
        ema26 = c.ewm(span=26, adjust=False, min_periods=26).mean()
        macd_manual = ema12 - ema26
        sig_manual = macd_manual.ewm(span=9, adjust=False,
                                     min_periods=9).mean()
        pd.testing.assert_series_equal(
            df["macd"].reset_index(drop=True),
            macd_manual.reset_index(drop=True),
            check_names=False, atol=1e-9)
        pd.testing.assert_series_equal(
            df["macd_signal"].reset_index(drop=True),
            sig_manual.reset_index(drop=True),
            check_names=False, atol=1e-9)
        pd.testing.assert_series_equal(
            df["macd_hist"].reset_index(drop=True),
            (macd_manual - sig_manual).reset_index(drop=True),
            check_names=False, atol=1e-9)

    def test_macd_positive_after_sustained_rise(self):
        # After a long sustained rise the fast EMA sits above the slow
        # EMA, so the MACD line is positive and above its signal line.
        n = 200
        closes = list(np.linspace(100.0, 200.0, n))
        df = indicators.add_indicators(_frame(closes))
        self.assertGreater(df["macd"].iloc[-1], 0.0)
        self.assertGreater(df["macd_hist"].iloc[-1], 0.0)

    def test_long_entry_cross_above_signal(self):
        # Sustained fall (MACD below signal) then a sharp rise: the
        # MACD line crosses up through its signal line and a long
        # entry fires on the crossing bar.
        n = 200
        closes = list(np.linspace(200.0, 100.0, 100)) + [200.0] * 100
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[100:140].any())
        first = df.index[df["long_entry"]].min()
        self.assertTrue(df["macd"].iloc[first] > df["macd_signal"].iloc[first])
        self.assertTrue(df["macd"].iloc[first - 1] <= df["macd_signal"].iloc[first - 1])
        # The opposite cross is the long exit on the same bar.
        self.assertTrue(df["short_exit"].iloc[first])

    def test_short_entry_cross_below_signal(self):
        # Mirror: sustained rise then a sharp fall.
        n = 200
        closes = list(np.linspace(100.0, 200.0, 100)) + [100.0] * 100
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].iloc[100:140].any())
        first = df.index[df["short_entry"]].min()
        self.assertTrue(df["macd"].iloc[first] < df["macd_signal"].iloc[first])
        self.assertTrue(df["macd"].iloc[first - 1] >= df["macd_signal"].iloc[first - 1])
        self.assertTrue(df["long_exit"].iloc[first])

    def test_signal_logic_crafted_rows(self):
        # MACD crossing above signal: long entry + short exit.
        rows = [dict(macd=-1.0, macd_signal=0.0),
                dict(macd=1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # MACD crossing below signal: short entry + long exit.
        rows = [dict(macd=1.0, macd_signal=0.0),
                dict(macd=-1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # Touching the signal line exactly is not a cross (strict >).
        rows = [dict(macd=-1.0, macd_signal=0.0),
                dict(macd=0.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # NaN MACD (warmup): no entry, no exit.
        rows = [dict(macd=np.nan, macd_signal=np.nan),
                dict(macd=1.0, macd_signal=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

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
        # Flat close: MACD = signal = 0, no crossings.
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
        for col in ("macd", "macd_signal", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
