"""Support Resistance Flip tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.support_resistance_flip import indicators, risk, signals
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


def _base_arrays(n=60):
    return [100.0] * n, [101.0] * n, [99.0] * n


def _bull_frame():
    """Resistance 110: swing high centre 10 (confirmed 12); touches
    at bars 14-15 (low 109.5, within 0.5x ATR of 110); break bar 20
    (close 112); bar 21 no retest (low 112, too far); retest-hold
    bar 22 (low 109.5, close 111) -> long entry; bars 23-24 hold
    above; bar 25 closes 108, below the flipped level -> exit."""
    closes, highs, lows = _base_arrays()
    highs[10] = 110.0
    for i in (14, 15):
        lows[i] = 109.5
        highs[i] = 110.5
        closes[i] = 110.0
    closes[20] = 112.0
    highs[20] = 113.0
    lows[20] = 112.0
    closes[21] = 112.0
    highs[21] = 113.0
    lows[21] = 112.0
    closes[22] = 111.0
    highs[22] = 111.5
    lows[22] = 109.5
    for i in (23, 24):
        closes[i] = 111.0
        highs[i] = 112.0
        lows[i] = 110.5
    closes[25] = 108.0
    highs[25] = 109.0
    lows[25] = 107.0
    return _frame(closes, highs=highs, lows=lows)


def _bear_frame():
    """Support 90: swing low centre 10 (confirmed 12); touches at
    bars 14-15 (low 90.5); break bar 20 (close 88); bar 21 no
    retest (low 88, too far); retest-hold bar 22 (low 90.5,
    close 89) -> short entry; bars 23-24 hold below; bar 25
    closes 92, above the flipped level -> exit."""
    closes, highs, lows = _base_arrays()
    lows[10] = 90.0
    for i in (14, 15):
        lows[i] = 90.5
        highs[i] = 91.5
        closes[i] = 90.0
    closes[20] = 88.0
    highs[20] = 89.0
    lows[20] = 87.0
    closes[21] = 88.0
    highs[21] = 89.0
    lows[21] = 88.0
    closes[22] = 89.0
    highs[22] = 91.0
    lows[22] = 90.5
    for i in (23, 24):
        closes[i] = 89.0
        highs[i] = 90.0
        lows[i] = 89.5
    closes[25] = 92.0
    highs[25] = 93.0
    lows[25] = 91.0
    return _frame(closes, highs=highs, lows=lows)


class TestSupportResistanceFlip(unittest.TestCase):
    def test_registered(self):
        self.assertIn("support_resistance_flip", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_bull_break_retest_entry_exact(self):
        df = _run(_bull_frame())
        # Pivot confirmed at 12; no pending before the break.
        self.assertTrue(df["is_swing_high"].iloc[12])
        self.assertAlmostEqual(df["swing_high"].iloc[12], 110.0)
        self.assertTrue(pd.isna(df["pending_bull_level"].iloc[19]))
        # Break bar 20 opens the pending setup; no entry on the break.
        self.assertAlmostEqual(df["pending_bull_level"].iloc[20], 110.0)
        self.assertFalse(df["long_entry"].iloc[20])
        # Bar 21: low too far from the level, no retest.
        self.assertFalse(df["retest_bull"].iloc[21])
        self.assertAlmostEqual(df["pending_bull_level"].iloc[21], 110.0)
        # Retest-hold bar 22: entry, pending consumed, level flips.
        self.assertTrue(df["retest_bull"].iloc[22])
        self.assertTrue(df["long_entry"].iloc[22])
        self.assertTrue(pd.isna(df["pending_bull_level"].iloc[22]))
        self.assertAlmostEqual(df["flip_long_level"].iloc[22], 110.0)
        self.assertFalse(df["long_entry"].iloc[:22].any())
        # No short side anywhere in the bull frame.
        self.assertFalse(df["short_entry"].any())

    def test_bull_exit_exact(self):
        df = _run(_bull_frame())
        self.assertAlmostEqual(df["flip_long_level"].iloc[24], 110.0)
        self.assertFalse(df["long_exit"].iloc[24])
        self.assertTrue(df["long_exit"].iloc[25])
        self.assertAlmostEqual(df["flip_long_level"].iloc[25], 110.0)
        self.assertTrue(pd.isna(df["flip_long_level"].iloc[26]))

    def test_bear_break_retest_entry_exact(self):
        df = _run(_bear_frame())
        self.assertTrue(df["is_swing_low"].iloc[12])
        self.assertAlmostEqual(df["swing_low"].iloc[12], 90.0)
        self.assertAlmostEqual(df["pending_bear_level"].iloc[20], 90.0)
        self.assertFalse(df["short_entry"].iloc[20])
        self.assertFalse(df["retest_bear"].iloc[21])
        self.assertTrue(df["retest_bear"].iloc[22])
        self.assertTrue(df["short_entry"].iloc[22])
        self.assertAlmostEqual(df["flip_short_level"].iloc[22], 90.0)
        self.assertFalse(df["short_entry"].iloc[:22].any())
        self.assertFalse(df["long_entry"].any())

    def test_bear_exit_exact(self):
        df = _run(_bear_frame())
        self.assertFalse(df["short_exit"].iloc[24])
        self.assertTrue(df["short_exit"].iloc[25])
        self.assertAlmostEqual(df["flip_short_level"].iloc[25], 90.0)
        self.assertTrue(pd.isna(df["flip_short_level"].iloc[26]))

    def test_no_pending_without_two_touches(self):
        # Swing high 110 breaks at bar 20, but the level was never
        # touched (lows are 99 or 112): no pending setup, no entry.
        closes, highs, lows = _base_arrays()
        highs[10] = 110.0
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 112.0
        for i in range(21, 30):
            closes[i] = 112.0
            highs[i] = 113.0
            lows[i] = 112.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(pd.isna(df["pending_bull_level"].iloc[20]))
        self.assertFalse(df["long_entry"].any())

    def test_one_touch_is_not_enough(self):
        # Only one touch bar (14): the level does not qualify.
        # Bar 15 shares bar 14's high (110.5) with a base low, so
        # neither bar forms a second pivot level of its own.
        closes, highs, lows = _base_arrays()
        highs[10] = 110.0
        lows[14] = 109.5
        highs[14] = 110.5
        closes[14] = 110.0
        highs[15] = 110.5
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 112.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(pd.isna(df["pending_bull_level"].iloc[20]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_without_close_back_above_level(self):
        # Bar 21 dips to the level (low 109.5) but closes at 109,
        # below it: not a hold, no entry. Bar 22 stays far away.
        closes, highs, lows = _base_arrays()
        highs[10] = 110.0
        for i in (14, 15):
            lows[i] = 109.5
            highs[i] = 110.5
            closes[i] = 110.0
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 112.0
        closes[21] = 109.0
        highs[21] = 112.0
        lows[21] = 109.5
        closes[22] = 112.0
        highs[22] = 113.0
        lows[22] = 112.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["retest_bull"].iloc[21])
        self.assertFalse(df["long_entry"].iloc[21])
        self.assertFalse(df["long_entry"].iloc[22])
        # Setup still pending (a close back across does not kill it).
        self.assertAlmostEqual(df["pending_bull_level"].iloc[21], 110.0)

    def test_setup_expires_after_20_bars(self):
        # Break at 20, then 25 bars holding far above the level
        # (low 112) with no retest: pending expires at bar 41.
        closes, highs, lows = _base_arrays()
        highs[10] = 110.0
        for i in (14, 15):
            lows[i] = 109.5
            highs[i] = 110.5
            closes[i] = 110.0
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 112.0
        for i in range(21, 50):
            closes[i] = 112.0
            highs[i] = 113.0
            lows[i] = 112.0
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertAlmostEqual(df["pending_bull_level"].iloc[40], 110.0)
        self.assertTrue(pd.isna(df["pending_bull_level"].iloc[41]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_on_break_without_retest_window(self):
        # A retest 25 bars after the break is too late: the setup
        # has expired, so the dip-and-hold at bar 45 is not an entry.
        closes, highs, lows = _base_arrays()
        highs[10] = 110.0
        for i in (14, 15):
            lows[i] = 109.5
            highs[i] = 110.5
            closes[i] = 110.0
        closes[20] = 112.0
        highs[20] = 113.0
        lows[20] = 112.0
        for i in range(21, 45):
            closes[i] = 112.0
            highs[i] = 113.0
            lows[i] = 112.0
        closes[45] = 111.0
        highs[45] = 111.5
        lows[45] = 109.5
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["long_entry"].iloc[45])
        self.assertFalse(df["long_entry"].any())

    def test_pivot_confirmed_at_center_plus_two(self):
        df = indicators.add_indicators(_bull_frame())
        self.assertFalse(df["is_swing_high"].iloc[10])
        self.assertTrue(df["is_swing_high"].iloc[12])

    def test_signal_logic_crafted_rows(self):
        rows = [dict(retest_bull=True, retest_bear=False,
                     flip_long_level=110.0, flip_short_level=np.nan,
                     c=111.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        rows = [dict(retest_bull=False, retest_bear=False,
                     flip_long_level=110.0, flip_short_level=np.nan,
                     c=108.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])
        rows = [dict(retest_bull=False, retest_bear=True,
                     flip_long_level=np.nan, flip_short_level=90.0,
                     c=89.0)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_entry"].iloc[0])
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
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("retest_bull", "retest_bear", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["pending_bull_level"].isna().all())
        self.assertTrue(df["flip_long_level"].isna().all())


if __name__ == "__main__":
    unittest.main()
