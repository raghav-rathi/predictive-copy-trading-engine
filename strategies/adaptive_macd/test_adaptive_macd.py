"""Adaptive MACD tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adaptive_macd import indicators, risk, signals
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


def _v_frame():
    """80 bars falling 120 -> 90, then 80 bars rising 90 -> 130."""
    return _frame(list(np.linspace(120, 90, 80))
                  + list(np.linspace(90, 130, 80)))


class TestAdaptiveMacd(unittest.TestCase):
    def test_registered(self):
        self.assertIn("adaptive_macd", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_er_is_one_on_straight_line(self):
        # +1 every bar: |c - c[10]| = 10, sum of 10 |diffs| = 10.
        df = indicators.add_indicators(_frame(list(np.arange(100, 200, dtype=float))))
        self.assertTrue(np.allclose(df["er"].iloc[10:], 1.0))

    def test_er_is_zero_on_zigzag(self):
        # Alternating +1/-1: c[i] == c[i-10], so numerator 0.
        closes = [100.0 + (1.0 if i % 2 == 0 else 0.0) for i in range(200)]
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(np.allclose(df["er"].iloc[10:], 0.0))

    def test_er_bounded_zero_one(self):
        df = indicators.add_indicators(_random_walk_frame())
        er = df["er"].dropna()
        self.assertTrue(((er >= 0) & (er <= 1)).all())

    def test_sc_bounds(self):
        df = indicators.add_indicators(_random_walk_frame())
        scf = df["sc_fast"].dropna()
        scs = df["sc_slow"].dropna()
        self.assertTrue(((scf >= (2 / 13) ** 2) & (scf <= (2 / 3) ** 2)).all())
        self.assertTrue(((scs >= (2 / 27) ** 2) & (scs <= (2 / 6) ** 2)).all())

    def test_sc_formula_spot_check(self):
        # ER = 1 -> SC_fast = (2/3)^2, SC_slow = (2/6)^2.
        df = indicators.add_indicators(_frame(list(np.arange(100, 200, dtype=float))))
        self.assertAlmostEqual(df["sc_fast"].iloc[50], (2 / 3) ** 2)
        self.assertAlmostEqual(df["sc_slow"].iloc[50], (2 / 6) ** 2)
        # ER = 0 -> SC_fast = (2/13)^2, SC_slow = (2/27)^2.
        closes = [100.0 + (1.0 if i % 2 == 0 else 0.0) for i in range(200)]
        df2 = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df2["sc_fast"].iloc[50], (2 / 13) ** 2)
        self.assertAlmostEqual(df2["sc_slow"].iloc[50], (2 / 27) ** 2)

    def test_flat_series_macd_zero(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertTrue(np.allclose(df["ama_fast"].iloc[10:], 100.0))
        self.assertTrue(np.allclose(df["ama_slow"].iloc[10:], 100.0))
        self.assertTrue(np.allclose(df["macd"].iloc[10:], 0.0))
        self.assertTrue(np.allclose(df["macd_signal"].iloc[10:], 0.0))

    def test_signal_seeded_with_first_macd(self):
        df = indicators.add_indicators(_v_frame())
        self.assertAlmostEqual(df["macd_signal"].iloc[10], df["macd"].iloc[10])

    def test_v_frame_crosses(self):
        df = _run(_v_frame())
        # Falling leg: MACD crosses below signal early; rising leg:
        # MACD crosses above signal exactly at the turn bar 80.
        self.assertTrue(df["short_entry"].iloc[11])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[80])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_macd_hist_is_line_minus_signal(self):
        df = indicators.add_indicators(_random_walk_frame())
        pd.testing.assert_series_equal(
            df["macd_hist"], df["macd"] - df["macd_signal"],
            check_names=False)

    def test_adaptive_ema_recursion_spot_check(self):
        # Recompute the fast AMA by hand on the V frame.
        df0 = _v_frame()
        df = indicators.add_indicators(df0)
        c = df0["c"].to_numpy(float)
        sc = df["sc_fast"].to_numpy(float)
        ema = c[10]
        for i in range(11, 80):
            ema = ema + sc[i] * (c[i] - ema)
        self.assertAlmostEqual(df["ama_fast"].iloc[79], ema, places=8)

    def test_exit_is_opposite_cross(self):
        df = pd.DataFrame({
            "macd": [1.0, 2.0, 1.8, 0.5],
            "macd_signal": [1.5, 1.5, 1.5, 1.5],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])   # cross above
        self.assertTrue(out["short_entry"].iloc[3])  # cross below
        self.assertTrue(out["long_exit"].iloc[3])
        self.assertTrue(out["short_exit"].iloc[1])

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["er"].iloc[:10].isna().all())
        self.assertTrue(df["macd"].iloc[:10].isna().all())
        self.assertTrue(df["macd_signal"].iloc[:10].isna().all())
        self.assertFalse(np.isnan(df["macd"].iloc[10]))

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
        for col in ("er", "ama_fast", "macd", "macd_signal",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["macd"].isna().all())


if __name__ == "__main__":
    unittest.main()
