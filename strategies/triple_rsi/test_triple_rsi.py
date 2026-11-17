"""Triple RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.triple_rsi import indicators, risk, signals
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


def _trend_frame():
    # 30 flat bars, 60 rising, 60 falling.
    closes = ([100.0] * 30 + list(np.linspace(100, 160, 60))
              + list(np.linspace(160, 90, 60)))
    return _frame(closes)


class TestTripleRsi(unittest.TestCase):
    def test_registered(self):
        self.assertIn("triple_rsi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)
            self.assertFalse(df[col].isna().any())

    def test_rsi_all_gains_is_100(self):
        # Strictly rising closes: every RSI is 100 once warmed up.
        closes = list(np.linspace(100, 200, 100))
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["rsi7"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["rsi14"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["rsi21"].iloc[-1], 100.0)

    def test_rsi_all_losses_is_0(self):
        # Strictly falling closes: every RSI is 0 once warmed up.
        closes = list(np.linspace(200, 100, 100))
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["rsi7"].iloc[-1], 0.0)
        self.assertAlmostEqual(df["rsi14"].iloc[-1], 0.0)
        self.assertAlmostEqual(df["rsi21"].iloc[-1], 0.0)

    def test_rsi_bounds(self):
        df = indicators.add_indicators(_random_walk_frame())
        for col in ("rsi7", "rsi14", "rsi21"):
            s = df[col].iloc[60:]
            self.assertTrue(((s >= 0) & (s <= 100)).all())

    def test_rsi_faster_reacts_first(self):
        # On a fresh sustained rise, RSI(7) exceeds 55 before RSI(21).
        df = indicators.add_indicators(_trend_frame())
        first7 = int(df.index[df["rsi7"] > 55][0])
        first21 = int(df.index[df["rsi21"] > 55][0])
        self.assertLessEqual(first7, first21)

    def test_signal_logic_crafted_rows(self):
        # Two RSIs already > 55, the third crosses above 55 on bar 1:
        # long entry fires on bar 1 (the bar the last one crosses).
        rows = [dict(rsi7=60.0, rsi14=60.0, rsi21=50.0),
                dict(rsi7=60.0, rsi14=60.0, rsi21=56.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertTrue(df["long_entry"].iloc[1])
        # Mirror: short entry when the last RSI crosses below 45.
        rows = [dict(rsi7=40.0, rsi14=40.0, rsi21=50.0),
                dict(rsi7=40.0, rsi14=40.0, rsi21=44.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertTrue(df["short_entry"].iloc[1])

    def test_entry_fires_once_per_alignment(self):
        # All three stay above 55 for two bars: entry fires only on the
        # first bar of the alignment, not on every bar.
        rows = [dict(rsi7=50.0, rsi14=60.0, rsi21=60.0),
                dict(rsi7=60.0, rsi14=60.0, rsi21=60.0),
                dict(rsi7=61.0, rsi14=61.0, rsi21=61.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_long_entry_needs_all_three(self):
        # Two RSIs above 55, the third stuck below: no long entry.
        rows = [dict(rsi7=60.0, rsi14=60.0, rsi21=50.0),
                dict(rsi7=61.0, rsi14=61.0, rsi21=51.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        # Two below 45, the third stuck above: no short entry.
        rows = [dict(rsi7=40.0, rsi14=40.0, rsi21=50.0),
                dict(rsi7=39.0, rsi14=39.0, rsi21=49.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["short_entry"].any())

    def test_exit_on_any_rsi_crossing_50(self):
        # Long exit: only RSI(7) crosses below 50, the others stay high.
        rows = [dict(rsi7=55.0, rsi14=70.0, rsi21=70.0),
                dict(rsi7=49.0, rsi14=70.0, rsi21=70.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # Short exit: only RSI(21) crosses above 50.
        rows = [dict(rsi7=30.0, rsi14=30.0, rsi21=45.0),
                dict(rsi7=30.0, rsi14=30.0, rsi21=51.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])

    def test_no_exit_without_50_cross(self):
        # All RSIs drift but none crosses 50: no exits.
        rows = [dict(rsi7=60.0, rsi14=60.0, rsi21=60.0),
                dict(rsi7=61.0, rsi14=61.0, rsi21=61.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_entries_fire_on_trend_frame(self):
        df = _run(_trend_frame())
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
        # Flat closes: RSI is 0 for all three (no gains ever) -> all
        # three are below 45 from the start, but the entry requires a
        # fresh crossing into the all-below state, and the flat series
        # starts there, so no entry fires.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("rsi7", "rsi14", "rsi21", "long_entry", "short_entry",
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
