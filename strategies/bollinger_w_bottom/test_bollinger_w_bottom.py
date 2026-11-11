"""Bollinger W-bottom / M-top tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_w_bottom import indicators, risk, signals
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


def _flat_frame(n=300, close=100.0):
    return _frame([close] * n)


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


def _pattern_rows(pctb, closes, mid=100.0):
    """Direct signal unit-test frame from explicit per-bar values."""
    return pd.DataFrame({"pctb": pctb, "c": closes,
                         "bb_mid": [mid] * len(pctb)})


class TestBollingerWBottom(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bollinger_w_bottom", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_pctb_hand_computed(self):
        # 20 closes 100..119, then a 120 close: mid = mean of the last
        # 20 closes, sd = sample std (ddof=1); %B = (c - lower) /
        # (upper - lower) with bands mid +/- 2*sd.
        closes = list(range(100, 121))
        df = indicators.add_indicators(_frame(closes))
        window = np.array(closes[-20:], dtype=float)
        mid = window.mean()
        sd = window.std(ddof=1)
        upper, lower = mid + 2 * sd, mid - 2 * sd
        self.assertAlmostEqual(df["bb_mid"].iloc[-1], mid, places=8)
        self.assertAlmostEqual(df["bb_upper"].iloc[-1], upper, places=8)
        self.assertAlmostEqual(df["bb_lower"].iloc[-1], lower, places=8)
        self.assertAlmostEqual(df["pctb"].iloc[-1],
                               (120.0 - lower) / (upper - lower), places=8)
        # BB needs 20 bars: NaN before bar 19.
        self.assertTrue(np.isnan(df["bb_mid"].iloc[18]))
        self.assertFalse(np.isnan(df["bb_mid"].iloc[19]))

    def test_indicator_pctb_flat_zero_width(self):
        # Flat closes: zero-width band -> %B defined as 0.5.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[20:]
        self.assertTrue(np.allclose(tail["pctb"], 0.5))
        self.assertTrue(np.allclose(tail["bb_width"], 0.0))

    def test_w_bottom_full_pattern_enters(self):
        # Bar 0: first low %B -0.2 at 90. Bar 2: rally close 105 above
        # mid. Bar 4: second low 89.5 (within 1% of 90) with %B -0.1
        # (higher than -0.2). Bar 5: close 102 above mid -> entry.
        rows = _pattern_rows(
            pctb=[-0.2, 0.1, 0.6, 0.3, -0.1, 0.55],
            closes=[90.0, 95.0, 105.0, 98.0, 89.5, 102.0])
        df = signals.add_signals(rows)
        self.assertEqual(list(df["long_entry"]),
                         [False, False, False, False, False, True])
        self.assertFalse(df["short_entry"].any())

    def test_w_bottom_no_divergence_no_entry(self):
        # Second low at 89.5 with %B -0.2, exactly the first low's %B:
        # no divergence, so no pattern completes even when price
        # closes back above the middle band.
        rows = _pattern_rows(
            pctb=[-0.2, 0.1, 0.6, 0.3, -0.2, 0.55],
            closes=[90.0, 95.0, 105.0, 98.0, 89.5, 102.0])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())

    def test_w_bottom_second_low_too_high_no_entry(self):
        # Second-low candidate at 92 is more than 1% above the first
        # low's 90, so it does not count; the later close above mid
        # is not a confirmation.
        rows = _pattern_rows(
            pctb=[-0.2, 0.1, 0.6, 0.3, 0.0, 0.55],
            closes=[90.0, 95.0, 105.0, 98.0, 92.0, 102.0])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())

    def test_w_bottom_stale_pattern_expires(self):
        # First low at bar 0, rally at bar 2, then 41 bars with no
        # second low (price stays above 1.01 * 90): the pattern
        # expires, so a late second low + close above mid is ignored.
        pctb = [-0.2, 0.1, 0.6] + [0.3] * 41 + [-0.1, 0.55]
        closes = [90.0, 95.0, 105.0] + [95.0] * 41 + [89.5, 102.0]
        df = signals.add_signals(_pattern_rows(pctb, closes))
        self.assertFalse(df["long_entry"].any())

    def test_w_bottom_new_extreme_restarts_pattern(self):
        # First low -0.2 at 90, then a deeper low -0.4 at 88 before
        # any rally: the deeper low becomes the first low. Rally at
        # 105, second low 87.5 (within 1% of 88) with %B -0.3
        # (higher than -0.4), close above mid -> entry.
        rows = _pattern_rows(
            pctb=[-0.2, -0.4, 0.1, 0.6, 0.3, -0.3, 0.55],
            closes=[90.0, 88.0, 92.0, 105.0, 98.0, 87.5, 102.0])
        df = signals.add_signals(rows)
        self.assertEqual(list(df["long_entry"]),
                         [False, False, False, False, False, False, True])

    def test_m_top_full_pattern_enters(self):
        # Mirror: first high %B 1.2 at 110, dip to 95 below mid, second
        # high 110.5 (within 1% of 110) with %B 1.1 (lower than 1.2),
        # close 98 below mid -> short entry.
        rows = _pattern_rows(
            pctb=[1.2, 0.9, 0.4, 0.7, 1.1, 0.45],
            closes=[110.0, 105.0, 95.0, 102.0, 110.5, 98.0])
        df = signals.add_signals(rows)
        self.assertEqual(list(df["short_entry"]),
                         [False, False, False, False, False, True])
        self.assertFalse(df["long_entry"].any())

    def test_exits_on_midband_cross(self):
        rows = _pattern_rows(pctb=[0.5, 0.5, 0.5],
                             closes=[99.0, 101.0, 100.0])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_full_pipeline_w_bottom_synthetic(self):
        # Build a price path that actually forms a W: 20 flat bars at
        # 100, a plunge to 85 (outside the lower band), a rally to
        # 102 (above the middle band), a retest at 84.5 (lower price
        # but a higher %B once the bands have widened), then a close
        # above the middle band. The pipeline must fire a long entry.
        closes = [100.0] * 20
        closes += [97.0, 93.0, 88.0, 85.0]          # plunge, first low
        closes += [90.0, 96.0, 102.0]              # rally above mid
        closes += [95.0, 88.0, 84.5]               # retest, lower price
        closes += [92.0, 100.0, 104.0]             # back above mid
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        entry_idx = int(np.where(df["long_entry"].to_numpy())[0][0])
        # Entry must come after the retest low (bar 29).
        self.assertGreaterEqual(entry_idx, 30)

    def test_no_signal_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("bb_mid", "pctb", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:300].reset_index(drop=True),
                df2[col].iloc[:300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
