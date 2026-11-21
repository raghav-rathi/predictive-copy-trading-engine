"""Chande Momentum Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chande_momentum import indicators, risk, signals
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


def _cmo_expected(closes, n=14):
    """Independent loop recomputation of CMO(14)."""
    closes = np.asarray(closes, dtype=float)
    out = np.full(len(closes), np.nan)
    for i in range(len(closes)):
        if i < n:
            continue
        su = sd = 0.0
        for j in range(i - n + 1, i + 1):
            d = closes[j] - closes[j - 1]
            if d > 0:
                su += d
            else:
                sd += -d
        out[i] = 0.0 if su + sd == 0 else 100.0 * (su - sd) / (su + sd)
    return out


class TestChandeMomentum(unittest.TestCase):
    def test_registered(self):
        self.assertIn("chande_momentum", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_cmo_all_up_is_100(self):
        # 14 consecutive +1 moves: Su=14, Sd=0 -> CMO=100 at index 14.
        closes = [100 + i for i in range(20)]
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["cmo"].iloc[14], 100.0)
        self.assertAlmostEqual(df["cmo"].iloc[19], 100.0)

    def test_cmo_all_down_is_minus_100(self):
        closes = [100 - i for i in range(20)]
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["cmo"].iloc[14], -100.0)

    def test_cmo_hand_computed_mixed(self):
        # Moves: +1,-1,+2,-1,+2,-1,+2,-1,+2,-1,+2,-1,+2,-1
        # Su = 13, Sd = 7 -> CMO = 100*(13-7)/20 = 30.0 at index 14.
        closes = [100, 101, 100, 102, 101, 103, 102, 104, 103, 105,
                  104, 106, 105, 107, 106]
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["cmo"].iloc[14], 30.0)

    def test_cmo_matches_loop_recomputation(self):
        df0 = _random_walk_frame()
        df = indicators.add_indicators(df0)
        expected = _cmo_expected(df0["c"].to_numpy(float))
        for i in (14, 50, 500, 1499):
            self.assertAlmostEqual(df["cmo"].iloc[i], expected[i], places=8)

    def test_cmo_flat_window_is_zero(self):
        # Zero denominator guard: flat closes -> CMO 0 once defined.
        df = indicators.add_indicators(_frame([100.0] * 60))
        self.assertTrue(df["cmo"].iloc[:14].isna().all())
        self.assertAlmostEqual(df["cmo"].iloc[14], 0.0)
        self.assertAlmostEqual(df["cmo"].iloc[59], 0.0)

    def test_cmo_bounds(self):
        df = indicators.add_indicators(_random_walk_frame())
        valid = df["cmo"].dropna()
        self.assertTrue(((valid >= -100.0) & (valid <= 100.0)).all())

    def test_cmo_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["cmo"].iloc[:14].isna().all())
        self.assertFalse(np.isnan(df["cmo"].iloc[14]))

    def test_long_entry_cross_up_minus_50(self):
        # 20 down moves (CMO -> -100), then 20 up moves: CMO must
        # cross up through -50 exactly once in the rise.
        closes = [100 - i for i in range(20)] + \
            [80 + i for i in range(1, 21)]
        df = _run(_frame(closes))
        exp = _cmo_expected(closes)
        expected_idx = [i for i in range(1, len(closes))
                        if not np.isnan(exp[i]) and not np.isnan(exp[i - 1])
                        and exp[i] > -50 and exp[i - 1] <= -50]
        self.assertEqual(len(expected_idx), 1)
        self.assertTrue(df["long_entry"].iloc[expected_idx[0]])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_short_entry_cross_down_plus_50(self):
        closes = [100 + i for i in range(20)] + \
            [120 - i for i in range(1, 21)]
        df = _run(_frame(closes))
        exp = _cmo_expected(closes)
        expected_idx = [i for i in range(1, len(closes))
                        if not np.isnan(exp[i]) and not np.isnan(exp[i - 1])
                        and exp[i] < 50 and exp[i - 1] >= 50]
        self.assertEqual(len(expected_idx), 1)
        self.assertTrue(df["short_entry"].iloc[expected_idx[0]])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_exit_is_opposite_cross(self):
        df = pd.DataFrame({"cmo": [-60.0, -40.0, 60.0, 40.0]})
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["short_entry"].iloc[3])
        self.assertTrue(out["long_exit"].iloc[3])   # short fires -> long exits
        self.assertTrue(out["short_exit"].iloc[1])  # long fires -> short exits

    def test_no_entry_while_cmo_inside_band(self):
        # Flat series: CMO 0, never crosses +/-50.
        df = _run(_frame([100.0] * 200))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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
        self.assertEqual(risk.WARMUP, 40)

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
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("cmo", "atr", "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 5))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["cmo"].isna().all())


if __name__ == "__main__":
    unittest.main()
