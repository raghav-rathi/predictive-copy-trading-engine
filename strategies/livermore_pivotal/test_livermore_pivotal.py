"""Livermore pivotal-point tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.livermore_pivotal import indicators, risk, signals
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


def _livermore_frame(break_vol=200.0, reaction_vol=50.0,
                     reaction_low=102.2, resume_close=104.5):
    """Full bullish Livermore sequence.

    Bars 0-119: flat 100 (h 105 / l 95, range 10).
    Bars 120-139: narrow consolidation (h 102 / l 98, range 4 < 0.6*10);
        the 20-bar window completes at bar 139 -> bull pivot 102,
        bear pivot 98.
    Bar 140: break close 103.5 > 102 on volume 200 (> 1.25x mean 105).
    Bar 141: natural reaction — close 102.8 below the break close,
        low 102.2 above the pivot, volume 50 below the mean.
        Reaction high = 104 (the break bar's high).
    Bar 142: resumption close 104.5 > 104 on volume 150 -> long entry.
    Bars 143-147: flat at 104.5.
    """
    closes, highs, lows, vols = [], [], [], []
    for _ in range(120):
        closes.append(100.0)
        highs.append(105.0)
        lows.append(95.0)
        vols.append(100.0)
    for _ in range(20):
        closes.append(100.0)
        highs.append(102.0)
        lows.append(98.0)
        vols.append(100.0)
    closes.append(103.5)
    highs.append(104.0)
    lows.append(102.5)
    vols.append(break_vol)
    closes.append(102.8)
    highs.append(103.0)
    lows.append(reaction_low)
    vols.append(reaction_vol)
    closes.append(resume_close)
    highs.append(105.0)
    lows.append(104.0)
    vols.append(150.0)
    for _ in range(5):
        closes.append(104.5)
        highs.append(105.0)
        lows.append(104.0)
        vols.append(100.0)
    return _frame(closes, highs=highs, lows=lows, vols=vols)


def _mirror_frame(df):
    """Reflect prices about 100: bullish sequence becomes bearish."""
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


class TestLivermorePivotal(unittest.TestCase):
    def test_registered(self):
        self.assertIn("livermore_pivotal", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_pivot_frozen_when_window_completes(self):
        df = indicators.add_indicators(_livermore_frame())
        # No pivot before the narrow window completes at bar 139.
        self.assertTrue(np.isnan(df["bull_pivot"].iloc[138]))
        self.assertAlmostEqual(df["bull_pivot"].iloc[139], 102.0)
        self.assertAlmostEqual(df["bear_pivot"].iloc[139], 98.0)
        self.assertTrue(df["narrow"].iloc[139])
        self.assertFalse(df["narrow"].iloc[138])

    def test_state_progression(self):
        df = indicators.add_indicators(_livermore_frame())
        self.assertEqual(df["liv_state"].iloc[139], 0)  # pivot armed
        self.assertEqual(df["liv_state"].iloc[140], 1)  # break confirmed
        self.assertEqual(df["liv_state"].iloc[141], 2)  # reaction armed
        self.assertEqual(df["liv_side"].iloc[141], 1)

    def test_long_trigger_on_resumption(self):
        df = _run(_livermore_frame())
        self.assertFalse(df["long_entry"].iloc[:142].any())
        self.assertTrue(df["long_entry"].iloc[142])
        self.assertFalse(df["short_entry"].iloc[142])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_bear_short_trigger_on_mirrored_frame(self):
        df = _run(_mirror_frame(_livermore_frame()))
        self.assertFalse(df["short_entry"].iloc[:142].any())
        self.assertTrue(df["short_entry"].iloc[142])
        self.assertFalse(df["long_entry"].iloc[142])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_no_entry_without_expanding_break_volume(self):
        # Break close is above the pivot but volume 110 is not
        # > 1.25x the 20-bar mean (~105) -> no break, no entry.
        df = _run(_livermore_frame(break_vol=110.0))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_when_reaction_volume_not_contracting(self):
        # Reaction bar volume 300 is above the 20-bar mean, so the
        # pullback is not a contracting-volume natural reaction.
        df = _run(_livermore_frame(reaction_vol=300.0))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_when_reaction_violates_pivot(self):
        # Reaction bar low 101.0 is below the bull pivot 102.
        df = _run(_livermore_frame(reaction_low=101.0))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_without_resumption(self):
        # Resumption close 103.5 stays below the reaction high 104.
        df = _run(_livermore_frame(resume_close=103.5))
        self.assertFalse(df["long_entry"].any())

    def test_exit_long_on_pivot_violation(self):
        # No bear pivot yet (NaN) so only the long exit can fire.
        rows = pd.DataFrame([dict(
            c=101.0, long_trigger=False, short_trigger=False,
            bull_pivot=102.0, bear_pivot=np.nan)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=104.0, long_trigger=False, short_trigger=True,
            bull_pivot=102.0, bear_pivot=np.nan)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        # No bull pivot yet (NaN) so only the short exit can fire.
        rows = pd.DataFrame([dict(
            c=99.0, long_trigger=True, short_trigger=False,
            bull_pivot=np.nan, bear_pivot=98.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

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
        self.assertEqual(risk.WARMUP, 120)

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
        for col in ("bull_pivot", "bear_pivot", "liv_state", "long_entry",
                    "short_entry", "long_exit"):
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
