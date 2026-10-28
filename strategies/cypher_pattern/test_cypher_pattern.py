"""Cypher pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cypher_pattern import indicators, risk, signals
from strategies.cypher_pattern.indicators import classify_cypher
from strategies.registry import REGISTRY


def _frame_from_close_path(pivots, leg_bars=10, tail_bars=10):
    """Piecewise-linear closes through pivot values (first = start).

    Each leg is monotonic, so each pivot bar is the window extreme
    over +-5 bars and no interior bar becomes a pivot.
    """
    closes = []
    for a, b in zip(pivots[:-1], pivots[1:]):
        seg = np.linspace(a, b, leg_bars + 1)
        closes.extend(seg[:-1].tolist())
    closes.append(pivots[-1])
    tail_end = pivots[-1] + (2.0 if pivots[-1] < pivots[-2] else -2.0)
    closes.extend(np.linspace(pivots[-1], tail_end, tail_bars + 1)[1:].tolist())
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


# Bullish Cypher: X=100, A=120, B=108, C=123.2, D=104.96.
# AB/XA = 12/20 = 60%, BC/AB = 15.2/12 = 126.7%, CD/XC = 18.24/23.2 = 78.6%.
# A lead-in bar (110) makes X a detectable swing low at bar 10.
BULL_PATH = [110.0, 100.0, 120.0, 108.0, 123.2, 104.96]
# Bearish mirror: X=120, A=100, B=112, C=96.8, D=115.04 (same ratios).
BEAR_PATH = [110.0, 120.0, 100.0, 112.0, 96.8, 115.04]


class TestClassify(unittest.TestCase):
    def test_bullish_valid(self):
        five = [(0, 100.0, -1), (10, 120.0, 1), (20, 108.0, -1),
                (30, 123.2, 1), (40, 104.96, -1)]
        res = classify_cypher(five)
        self.assertIsNotNone(res)
        self.assertEqual(res[0], "bull")
        self.assertAlmostEqual(res[1], 104.96)

    def test_bearish_valid(self):
        five = [(0, 120.0, 1), (10, 100.0, -1), (20, 112.0, 1),
                (30, 96.8, -1), (40, 115.04, 1)]
        res = classify_cypher(five)
        self.assertIsNotNone(res)
        self.assertEqual(res[0], "bear")

    def test_ab_xa_outside_band_rejected(self):
        # AB = 16 = 80% of XA = 20: above the 69.8% cap; the other
        # bands and the structure still hold (D = 103.5 < B = 104,
        # BC/AB = 19.2/16 = 120%, CD/XC = 19.7/23.2 = 84.9%).
        five = [(0, 100.0, -1), (10, 120.0, 1), (20, 104.0, -1),
                (30, 123.2, 1), (40, 103.5, -1)]
        self.assertIsNone(classify_cypher(five))

    def test_bc_ab_outside_band_rejected(self):
        # BC = 12.5 = 104.2% of AB = 12: below the 105% floor; the
        # other bands and the structure still hold (C = 120.5 > A,
        # CD/XC = 16.5/20.5 = 80.5%).
        five = [(0, 100.0, -1), (10, 120.0, 1), (20, 108.0, -1),
                (30, 120.5, 1), (40, 104.0, -1)]
        self.assertIsNone(classify_cypher(five))

    def test_cd_xc_outside_band_rejected(self):
        # CD = 15.7 = 67.7% of XC = 23.2: below the 70.6% floor; the
        # other bands and the structure still hold (D = 107.5 < B).
        five = [(0, 100.0, -1), (10, 120.0, 1), (20, 108.0, -1),
                (30, 123.2, 1), (40, 107.5, -1)]
        self.assertIsNone(classify_cypher(five))

    def test_span_over_60_rejected(self):
        five = [(0, 100.0, -1), (10, 120.0, 1), (20, 108.0, -1),
                (30, 123.2, 1), (61, 104.96, -1)]
        self.assertIsNone(classify_cypher(five))

    def test_wrong_pivot_order_rejected(self):
        five = [(0, 100.0, -1), (10, 120.0, 1), (20, 108.0, 1),
                (30, 123.2, 1), (40, 104.96, -1)]
        self.assertIsNone(classify_cypher(five))


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("cypher_dir", "cypher_d_price", "atr"):
            self.assertIn(col, ind.columns)

    def test_bullish_cypher_fires_once(self):
        ind = indicators.add_indicators(_frame_from_close_path(BULL_PATH))
        fires = np.where(ind["cypher_dir"] == 1)[0]
        self.assertEqual(len(fires), 1)
        # Pivots at bars 10/20/30/40/50; D confirms at 55.
        # D price is the pivot extreme (the bar's low):
        # min(o, c) - 0.05 = 104.91.
        self.assertEqual(int(fires[0]), 55)
        self.assertAlmostEqual(float(ind["cypher_d_price"].iloc[55]), 104.91,
                               places=6)

    def test_bearish_cypher_fires_once(self):
        ind = indicators.add_indicators(_frame_from_close_path(BEAR_PATH))
        fires = np.where(ind["cypher_dir"] == -1)[0]
        self.assertEqual(len(fires), 1)
        self.assertEqual(int(fires[0]), 55)
        # D price is the pivot extreme (the bar's high): 115.09.
        self.assertAlmostEqual(float(ind["cypher_d_price"].iloc[55]), 115.09,
                               places=6)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["cypher_dir"].iloc[:200].reset_index(drop=True),
            ind_short["cypher_dir"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, c, direction):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "cypher_dir": direction,
            "cypher_d_price": np.full(n, np.nan),
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_flat_data_no_entries(self):
        n = 200
        flat = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0), "h": np.full(n, 100.0),
            "l": np.full(n, 100.0), "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
        })
        sig = signals.add_signals(indicators.add_indicators(flat))
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_bullish_completion_enters_long(self):
        ind = indicators.add_indicators(_frame_from_close_path(BULL_PATH))
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[55])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_bearish_completion_enters_short(self):
        ind = indicators.add_indicators(_frame_from_close_path(BEAR_PATH))
        sig = signals.add_signals(ind)
        self.assertTrue(sig["short_entry"].iloc[55])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_exit_on_opposite_completion(self):
        c = np.array([100.0, 100.0, 100.0, 100.0])
        d = np.array([0, 1, 0, -1])
        sig = signals.add_signals(self._signal_frame(c, d))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        # The bearish completion also opens the short (harness flips).
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_no_lookahead_signals(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        full = signals.add_signals(indicators.add_indicators(df))
        trunc = signals.add_signals(indicators.add_indicators(short))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )


class TestRiskAndRegistry(unittest.TestCase):
    def test_registered(self):
        self.assertIn("cypher_pattern", REGISTRY)
        self.assertEqual(REGISTRY["cypher_pattern"].warmup_bars, risk.WARMUP)

    def test_risk_config_sane(self):
        r = risk.RISK
        self.assertGreater(r.stop_atr_mult, 0)
        self.assertGreater(r.risk_frac, 0)
        self.assertLessEqual(r.max_leverage, 3.0)
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.5)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 168)
        self.assertTrue(r.allow_longs and r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 70)

    def test_backtest_smoke(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)
        self.assertIn("net_pnl_usd", m)


if __name__ == "__main__":
    unittest.main()
