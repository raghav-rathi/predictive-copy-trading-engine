"""Relative Vigor Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.relative_vigor_index import indicators, risk, signals
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


def _flip_frame():
    """10 bars closing 1 below open (c-o = -1, h-l = 2), then 10 bars
    closing 1 above open (c-o = +1, h-l = 2)."""
    o, c, h, l = [], [], [], []
    price = 100.0
    for i in range(20):
        o.append(price)
        if i < 10:
            price -= 1.0
        else:
            price += 1.0
        c.append(price)
        h.append(max(o[-1], price) + 0.5)
        l.append(min(o[-1], price) - 0.5)
    return _frame(c, highs=h, lows=l, opens=o)


class TestRelativeVigorIndex(unittest.TestCase):
    def test_registered(self):
        self.assertIn("relative_vigor_index", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_rvi_hand_computed(self):
        # 4 bars, each c-o = +1 and h-l = 2.
        # num = 1 + 2*1 + 2*1 + 1 = 6; den = 2 + 4 + 4 + 2 = 12; RVI = 0.5.
        o = [100.0, 101.0, 102.0, 103.0]
        c = [101.0, 102.0, 103.0, 104.0]
        h = [102.0, 103.0, 104.0, 105.0]
        l = [100.0, 101.0, 102.0, 103.0]
        df = indicators.add_indicators(_frame(c, highs=h, lows=l, opens=o))
        self.assertAlmostEqual(df["rvi_num"].iloc[3], 6.0, places=9)
        self.assertAlmostEqual(df["rvi_den"].iloc[3], 12.0, places=9)
        self.assertAlmostEqual(df["rvi"].iloc[3], 0.5, places=9)

    def test_signal_hand_computed(self):
        # 7 bars, each c-o = +1 and h-l = 2, so RVI = 0.5 from bar 3 on.
        # Signal at bar 6 = (0.5 + 2*0.5 + 2*0.5 + 0.5)/6 = 0.5.
        n = 7
        o = [100.0 + i for i in range(n)]
        c = [101.0 + i for i in range(n)]
        h = [102.0 + i for i in range(n)]
        l = [100.0 + i for i in range(n)]
        df = indicators.add_indicators(_frame(c, highs=h, lows=l, opens=o))
        self.assertTrue(df["rvi"].iloc[3:].eq(0.5).all())
        self.assertAlmostEqual(df["rvi_signal"].iloc[6], 0.5, places=9)

    def test_zero_denominator_is_zero(self):
        # Doji bars with h == l == o == c: numerator and denominator are
        # both 0, so RVI must be 0, not NaN or inf.
        df = indicators.add_indicators(_flat_frame(n=20, hi=100.0, lo=100.0))
        self.assertTrue(df["rvi"].iloc[3:].eq(0.0).all())
        self.assertTrue(df["rvi_signal"].iloc[6:].eq(0.0).all())

    def test_rvi_bounded_by_one(self):
        # |c-o| <= 0.3 and h-l = 1 on every bar, so |RVI| <= 1.
        rng = np.random.default_rng(11)
        steps = rng.uniform(-0.3, 0.3, 200)
        c = 100 + np.cumsum(steps)
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(
            _frame(c, highs=c + 0.5, lows=c - 0.5, opens=o))
        self.assertLessEqual(df["rvi"].iloc[3:].abs().max(), 1.0 + 1e-9)

    def test_cross_up_is_long_entry(self):
        df = pd.DataFrame({
            "rvi": [-0.2, -0.1, 0.1, 0.2, 0.1],
            "rvi_signal": [0.0, 0.0, 0.0, 0.0, 0.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[2])
        self.assertEqual(int(out["long_entry"].sum()), 1)
        self.assertFalse(out["short_entry"].any())
        self.assertTrue(out["short_exit"].iloc[2])

    def test_cross_down_is_short_entry(self):
        df = pd.DataFrame({
            "rvi": [0.2, 0.1, -0.1, -0.2, -0.1],
            "rvi_signal": [0.0, 0.0, 0.0, 0.0, 0.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["short_entry"].iloc[2])
        self.assertEqual(int(out["short_entry"].sum()), 1)
        self.assertFalse(out["long_entry"].any())
        self.assertTrue(out["long_exit"].iloc[2])

    def test_no_cross_no_entry(self):
        df = pd.DataFrame({
            "rvi": [0.1, 0.1, 0.1, 0.1],
            "rvi_signal": [0.0, 0.0, 0.0, 0.0],
        })
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].any())

    def test_exit_is_opposite_cross(self):
        df = pd.DataFrame({
            "rvi": [-0.2, 0.1, -0.1],
            "rvi_signal": [0.0, 0.0, 0.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["long_exit"].iloc[2])
        self.assertTrue(out["short_entry"].iloc[2])

    def test_flip_frame_gives_long_entry(self):
        # Ten down bars (RVI negative) then ten up bars (RVI positive):
        # RVI must cross up through its signal line.
        df = _run(_flip_frame())
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["rvi"].iloc[:3].isna().all())
        self.assertFalse(np.isnan(df["rvi"].iloc[3]))
        self.assertTrue(df["rvi_signal"].iloc[:6].isna().all())
        self.assertFalse(np.isnan(df["rvi_signal"].iloc[6]))

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
        for col in ("rvi", "rvi_signal", "long_entry", "short_entry",
                    "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["rvi"].iloc[:3].isna().all())


if __name__ == "__main__":
    unittest.main()
