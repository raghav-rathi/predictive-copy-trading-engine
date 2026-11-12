"""Bull Power / Bear Power tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bull_bear_power import indicators, risk, signals
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


class TestBullBearPower(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bull_bear_power", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_powers_hand_computed(self):
        # Flat close 100, h=101, l=99: EMA(13) converges to 100, so
        # Bull Power -> +1 and Bear Power -> -1.
        df = indicators.add_indicators(_flat_frame(n=200))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["ema13"], 100.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["bull_power"], 1.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["bear_power"], -1.0, atol=1e-9))

    def test_powers_formula_on_random_data(self):
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        highs = closes + rng.uniform(0.1, 1.0, 200)
        lows = closes - rng.uniform(0.1, 1.0, 200)
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        ema13 = pd.Series(closes).ewm(span=13, adjust=False,
                                       min_periods=13).mean()
        pd.testing.assert_series_equal(
            df["ema13"].reset_index(drop=True),
            ema13.reset_index(drop=True), check_names=False, atol=1e-9)
        self.assertTrue(np.allclose(
            df["bull_power"].dropna(),
            (pd.Series(highs) - ema13).dropna(), atol=1e-9))
        self.assertTrue(np.allclose(
            df["bear_power"].dropna(),
            (pd.Series(lows) - ema13).dropna(), atol=1e-9))
        # Bull Power is always >= Bear Power (high >= low).
        valid = df["bull_power"].notna() & df["bear_power"].notna()
        self.assertTrue((df.loc[valid, "bull_power"]
                         >= df.loc[valid, "bear_power"]).all())

    def test_long_entry_bear_power_turns_up(self):
        # Flat at 100 (bear = -1), then the low lifts to 99.5 while the
        # close stays 100: Bear Power rises to -0.5, still below zero,
        # Bull Power stays +1 > 0 -> long entry on the lift bar.
        n = 100
        closes = np.full(n, 100.0)
        lows = np.full(n, 99.0)
        lows[60:] = 99.5
        df = _run(_frame(closes, lows=lows))
        self.assertTrue(df["long_entry"].iloc[60])
        self.assertFalse(df["long_entry"].iloc[:60].any())
        self.assertFalse(df["short_entry"].iloc[60])

    def test_short_entry_bull_power_turns_down(self):
        # Mirror: the high drops to 100.5 while the close stays 100:
        # Bull Power falls to +0.5, still above zero, Bear Power -1 < 0
        # -> short entry on the drop bar.
        n = 100
        closes = np.full(n, 100.0)
        highs = np.full(n, 101.0)
        highs[60:] = 100.5
        df = _run(_frame(closes, highs=highs))
        self.assertTrue(df["short_entry"].iloc[60])
        self.assertFalse(df["short_entry"].iloc[:60].any())
        self.assertFalse(df["long_entry"].iloc[60])

    def test_no_entry_when_bear_power_above_zero(self):
        # Bear Power rising but already above zero (low above the EMA)
        # is not a long: the "still below zero" condition blocks it.
        rows = [dict(bull_power=1.0, bear_power=0.5),
                dict(bull_power=1.0, bear_power=0.8)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # Bull Power falling but already below zero is not a short.
        rows = [dict(bull_power=-0.5, bear_power=-1.0),
                dict(bull_power=-0.8, bear_power=-1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["short_entry"].iloc[1])

    def test_signal_logic_crafted_rows(self):
        # Bear rising below zero + bull above zero: long entry, and it
        # is also the short exit (opposite turn).
        rows = [dict(bull_power=1.0, bear_power=-1.0),
                dict(bull_power=1.0, bear_power=-0.5)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Bull falling above zero + bear below zero: short entry, and
        # it is also the long exit.
        rows = [dict(bull_power=1.0, bear_power=-1.0),
                dict(bull_power=0.5, bear_power=-1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        # Bear falling (not turning up): no long entry.
        rows = [dict(bull_power=1.0, bear_power=-0.5),
                dict(bull_power=1.0, bear_power=-1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # NaN powers (warmup): no entry, no exit.
        rows = [dict(bull_power=np.nan, bear_power=np.nan),
                dict(bull_power=1.0, bear_power=-0.5)]
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
        # Flat bars: Bear Power is constant (-1), never "turns up", so
        # no entries fire.
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
        for col in ("bull_power", "bear_power", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): both powers are 0, no turns.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["bull_power"], 0.0, atol=1e-12))
        self.assertTrue(np.allclose(tail["bear_power"], 0.0, atol=1e-12))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
