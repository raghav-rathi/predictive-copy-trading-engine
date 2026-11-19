"""Balanced Price Range tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.balanced_price_range import indicators, risk, signals
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


def _bear_bpr_frame():
    """Bearish BPR: bull FVG [100,102] confirmed bar 2 (l2=102 > h0=100),
    refreshed to [100.5,102] at bar 3; bear FVG [100,103] confirmed bar 5
    (h5=101 < l3=102) -> overlap zone [100.5,102], bearish (later gap).
    Bar 6 closes 99 (below the zone: traded beyond it) and refreshes
    the BPR to the same zone; bar 7 closes 101 (inside) -> short."""
    highs = [100, 100.5, 103, 103, 103, 101, 100, 102]
    lows = [99, 99.5, 102, 102, 101, 100, 98, 100]
    closes = [99.5, 100, 102.5, 102.5, 102, 100.5, 99, 101]
    return _frame(closes, highs=highs, lows=lows)


def _bull_bpr_frame():
    """Mirror of _bear_bpr_frame (prices reflected about 100):
    bullish BPR, long trigger on the final bar."""
    df = _bear_bpr_frame()
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


class TestBalancedPriceRange(unittest.TestCase):
    def test_registered(self):
        self.assertIn("balanced_price_range", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_bear_bpr_zone_is_overlap(self):
        df = indicators.add_indicators(_bear_bpr_frame())
        self.assertTrue(np.isnan(df["bear_bpr_bottom"].iloc[4]))
        self.assertAlmostEqual(df["bear_bpr_bottom"].iloc[5], 100.5)
        self.assertAlmostEqual(df["bear_bpr_top"].iloc[5], 102.0)
        self.assertEqual(int(df["bpr_side"].iloc[5]), -1)

    def test_bear_short_trigger_on_return_into_zone(self):
        df = _run(_bear_bpr_frame())
        self.assertFalse(df["short_entry"].iloc[:7].any())
        self.assertTrue(df["short_entry"].iloc[7])
        self.assertFalse(df["long_entry"].iloc[7])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_bull_long_trigger_on_mirrored_frame(self):
        df = _run(_bull_bpr_frame())
        self.assertFalse(df["long_entry"].iloc[:7].any())
        self.assertTrue(df["long_entry"].iloc[7])
        self.assertFalse(df["short_entry"].iloc[7])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        # Note: FVG gaps are NOT reflection-symmetric (a bull gap is
        # [high[i-2], low[i]] while a bear gap is [low[i], high[i-2]]),
        # so the mirrored zone is [98,99], not [98,99.5].
        self.assertAlmostEqual(df["bull_bpr_bottom"].iloc[5], 98.0)
        self.assertAlmostEqual(df["bull_bpr_top"].iloc[5], 99.0)

    def test_no_entry_without_trading_beyond_first(self):
        # BPR forms at bar 5; bar 6 closes INSIDE the zone without ever
        # trading beyond it -> no entry. Bar 7 trades below, bar 8
        # returns inside -> short on bar 8.
        df0 = _bear_bpr_frame()
        highs = list(df0["h"]) + [102.0]
        lows = list(df0["l"]) + [100.0]
        closes = list(df0["c"])
        closes[6] = 101.0
        highs[6] = 101.5
        lows[6] = 100.8
        closes[7] = 99.0
        highs[7] = 100.0
        lows[7] = 98.0
        closes = closes + [101.0]
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].iloc[:8].any())
        self.assertTrue(df["short_entry"].iloc[8])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_no_bpr_from_same_direction_gaps_only(self):
        # Bullish FVGs only, never a bearish one -> no BPR, no entry.
        df = _run(_bear_bpr_frame().iloc[:4])
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())
        self.assertTrue((df["bpr_side"] == 0).all())

    def test_no_bpr_when_second_gap_over_60_bars_later(self):
        # Bull FVG [100,102] at bar 2, then flat bars, then a bear FVG
        # overlapping in price but confirmed at bar 75 (73 bars after
        # the bull FVG) -> too late, no BPR.
        highs = [100, 100.5, 103] + [102.5] * 70 + [103, 103, 100.5]
        lows = [99, 99.5, 102] + [101.5] * 70 + [101, 101.5, 100]
        closes = [99.5, 100, 102.5] + [102.0] * 70 + [102, 102.5, 100.2]
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())
        self.assertTrue((df["bpr_side"] == 0).all())

    def test_no_bpr_when_gaps_do_not_overlap(self):
        # Bull FVG [100,102] at bar 2, then a slow drift down in 0.3
        # steps (h[i] == l[i-2] exactly, so no FVG forms on the way),
        # then a bear FVG [95.5,98] confirmed at bar 21, disjoint
        # from [100,102] -> no BPR.
        highs = [100, 100.5, 103]
        lows = [99, 99.5, 102]
        closes = [99.5, 100, 102.5]
        for k in range(18):  # bars 3..20, drifting 102.8 -> 97.7
            # Round to 1 decimal: the drift is built so h[i] == l[i-2]
            # exactly, so no FVG forms on the way down.
            highs.append(round(102.8 - 0.3 * k, 1))
            lows.append(round(102.2 - 0.3 * k, 1))
            closes.append(round(102.5 - 0.3 * k, 1))
        highs += [96.5, 96.0]
        lows += [95.5, 95.0]
        closes += [96.0, 95.5]
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_entry"].any())
        self.assertTrue((df["bpr_side"] == 0).all())

    def test_zone_expires_after_100_bars(self):
        # BPR formed bar 6; price then closes inside the zone (101)
        # for 100+ bars without ever closing through it: zone alive
        # at bar 106 (100 bars after formation) and gone at bar 107.
        df0 = _bear_bpr_frame()
        n_extra = 115
        highs = list(df0["h"]) + [101.5] * n_extra
        lows = list(df0["l"]) + [100.8] * n_extra
        closes = list(df0["c"]) + [101.0] * n_extra
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertAlmostEqual(df["bear_bpr_bottom"].iloc[106], 100.5)
        self.assertTrue(np.isnan(df["bear_bpr_bottom"].iloc[107]))

    def test_zone_invalidated_by_close_through(self):
        # After the BPR forms, a close above the bearish zone top
        # invalidates it before any entry.
        df0 = _bear_bpr_frame()
        highs = list(df0["h"])
        lows = list(df0["l"])
        closes = list(df0["c"])
        closes[6] = 103.0
        highs[6] = 103.5
        lows[6] = 102.5
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(np.isnan(df["bear_bpr_top"].iloc[7]))
        self.assertFalse(df["short_entry"].any())

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=101.0, long_trigger=False, short_trigger=True,
            bull_bpr_bottom=98.0, bear_bpr_top=102.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_on_close_above_zone_top(self):
        rows = pd.DataFrame([dict(
            c=103.0, long_trigger=False, short_trigger=False,
            bull_bpr_bottom=98.0, bear_bpr_top=99.5)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_exit_long_on_close_below_zone_bottom(self):
        rows = pd.DataFrame([dict(
            c=97.0, long_trigger=False, short_trigger=False,
            bull_bpr_bottom=98.0, bear_bpr_top=99.5)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

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
        for col in ("bull_bpr_bottom", "bear_bpr_bottom", "bpr_side",
                    "long_entry", "short_entry", "long_exit"):
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
