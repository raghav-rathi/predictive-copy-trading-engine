"""ABCD pattern tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.abcd_pattern import indicators, risk, signals
from strategies.abcd_pattern.indicators import classify_abcd


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


# Bullish ABCD: A=120, B=100, C=112, D=96.
# AB=20, BC=12 (60% of AB), CD=16 (133% of BC, 80% of AB).
BULL_PATH = [100.0, 120.0, 100.0, 112.0, 96.0]
# Bearish mirror: A=80, B=100, C=88, D=104 (same ratios).
BEAR_PATH = [100.0, 80.0, 100.0, 88.0, 104.0]


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("abcd_dir", "abcd_d_price", "abcd_cd", "atr"):
            self.assertIn(col, ind.columns)

    def test_bullish_abcd_fires_once(self):
        ind = indicators.add_indicators(_frame_from_close_path(BULL_PATH))
        fires = np.where(ind["abcd_dir"] == 1)[0]
        self.assertEqual(len(fires), 1)
        # D pivot is at bar 40 (4 legs x 10 bars); it confirms at 45.
        # D price is the pivot extreme (the bar's low), not the close:
        # low = min(o, c) - 0.05 = 95.95; C extreme is the bar's high
        # 112.05, so CD = 112.05 - 95.95 = 16.10.
        self.assertEqual(int(fires[0]), 45)
        self.assertAlmostEqual(float(ind["abcd_d_price"].iloc[45]), 95.95,
                               places=6)
        self.assertAlmostEqual(float(ind["abcd_cd"].iloc[45]), 16.10, places=6)

    def test_bearish_abcd_fires_once(self):
        ind = indicators.add_indicators(_frame_from_close_path(BEAR_PATH))
        fires = np.where(ind["abcd_dir"] == -1)[0]
        self.assertEqual(len(fires), 1)
        self.assertEqual(int(fires[0]), 45)
        # D price is the pivot extreme (the bar's high): 104.05.
        self.assertAlmostEqual(float(ind["abcd_d_price"].iloc[45]), 104.05,
                               places=6)
        self.assertAlmostEqual(float(ind["abcd_cd"].iloc[45]), 16.10, places=6)

    def test_bc_outside_band_rejected(self):
        # BC = 19 = 95% of AB=20: above the 88.6% cap -> no fire.
        ind = indicators.add_indicators(
            _frame_from_close_path([100.0, 120.0, 100.0, 119.0, 96.0]))
        self.assertFalse((ind["abcd_dir"] != 0).any())

    def test_cd_extension_too_short_rejected(self):
        # CD = 14 = 117% of BC=12: below the 127.2% floor, with D < B
        # still satisfied (D=98 < B=100) so the CD band is the cause.
        ind = indicators.add_indicators(
            _frame_from_close_path([100.0, 120.0, 100.0, 112.0, 98.0]))
        self.assertFalse((ind["abcd_dir"] != 0).any())

    def test_cd_ab_ratio_outside_20pct_rejected(self):
        # AB=20, BC=17 (85%), CD=26: CD/BC=153% (in band) but
        # CD/AB=130% (outside the +-20% band) -> no fire.
        ind = indicators.add_indicators(
            _frame_from_close_path([100.0, 120.0, 100.0, 117.0, 91.0]))
        self.assertFalse((ind["abcd_dir"] != 0).any())

    def test_classify_rejects_wrong_pivot_order(self):
        # Kinds must alternate high/low in the ABCD order.
        four = [(0, 120.0, 1), (10, 100.0, 1), (20, 112.0, 1),
                (30, 96.0, -1)]
        self.assertIsNone(classify_abcd(four))

    def test_random_walks_fire_rarely(self):
        # The three ratio bands are tight: on noise, a 500-bar walk
        # should average ~1 completion, not a stream of them. Bound
        # is generous (<= 20 across 10 walks) so the test asserts
        # rarity, not an exact count.
        total = 0
        for seed in range(10):
            ind = indicators.add_indicators(_random_walk_frame(seed=seed))
            total += int((ind["abcd_dir"] != 0).sum())
        self.assertLessEqual(total, 20)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["abcd_dir"].iloc[:200].reset_index(drop=True),
            ind_short["abcd_dir"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, c, direction, d_price, cd):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "abcd_dir": direction, "abcd_d_price": d_price, "abcd_cd": cd,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_bullish_completion_enters_long(self):
        ind = indicators.add_indicators(_frame_from_close_path(BULL_PATH))
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[45])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_bearish_completion_enters_short(self):
        ind = indicators.add_indicators(_frame_from_close_path(BEAR_PATH))
        sig = signals.add_signals(ind)
        self.assertTrue(sig["short_entry"].iloc[45])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_exit_on_50pct_cd_move_past_d(self):
        # Long at D=96, CD=16: failure level is 96 - 8 = 88.
        # Close 97 holds, close 87 fails.
        c = np.array([96.0, 96.0, 97.0, 87.0])
        d = np.array([0, 1, 0, 0])
        dp = np.array([np.nan, 96.0, np.nan, np.nan])
        cd = np.array([np.nan, 16.0, np.nan, np.nan])
        sig = signals.add_signals(self._signal_frame(c, d, dp, cd))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_exit_on_opposite_completion(self):
        # Long at bar 1, bearish completion at bar 3 -> long exit.
        c = np.array([96.0, 96.0, 96.0, 96.0])
        d = np.array([0, 1, 0, -1])
        dp = np.array([np.nan, 96.0, np.nan, 104.0])
        cd = np.array([np.nan, 16.0, np.nan, 16.0])
        sig = signals.add_signals(self._signal_frame(c, d, dp, cd))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        # The bearish completion also opens the short (harness flips).
        self.assertTrue(sig["short_entry"].iloc[3])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.5)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 96)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 80)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
