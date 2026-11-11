"""Early Onset Trend tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_early_onset_trend import indicators, risk, signals
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


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(rows):
    """Direct signal unit-test frame from explicit per-bar dicts."""
    return pd.DataFrame(rows)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _sine_frame(n=600, period=40, amp=5.0, base=100.0):
    closes = base + amp * np.sin(2 * np.pi * np.arange(n) / period)
    return _frame(closes)


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


class TestEarlyOnsetTrend(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ehlers_early_onset_trend", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_coefs_hand_computed(self):
        k = indicators.eot_coefs()
        alpha1 = (math.cos(math.radians(0.707 * 360 / 100))
                  + math.sin(math.radians(0.707 * 360 / 100)) - 1) / \
            math.cos(math.radians(0.707 * 360 / 100))
        self.assertAlmostEqual(k["alpha1"], alpha1, places=12)
        self.assertAlmostEqual(k["a1"], math.exp(-1.414 * math.pi / 30), places=12)
        self.assertAlmostEqual(k["c1"], 1 - k["c2"] - k["c3"], places=12)
        self.assertAlmostEqual(k["c3"], -k["a1"] ** 2, places=12)
        self.assertEqual(k["k1"], 0.85)
        self.assertEqual(k["k2"], 0.40)
        self.assertEqual(k["peak_decay"], 0.991)

    def test_indicator_values_flat(self):
        # Flat closes: the second difference is 0 every bar, so HP and
        # Filt stay 0, Peak stays 0, X stays 0, and the quotients sit at
        # their X=0 values: Q1 = 0.85, Q2 = 0.40. No zero crossing.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue((df["hp"] == 0.0).all())
        self.assertTrue((df["filt"] == 0.0).all())
        self.assertTrue((df["peak"] == 0.0).all())
        self.assertTrue((df["x"] == 0.0).all())
        self.assertTrue((df["q1"] == 0.85).all())
        self.assertTrue((df["q2"] == 0.40).all())

    def test_indicator_hand_computed_step(self):
        # Step: closes 100 for bars 0..9, then 110. At bar 10 the second
        # difference is 110 - 2*100 + 100 = 10, so
        #   HP[10] = (1-alpha1/2)^2 * 10
        #   Filt[10] = c1 * HP[10] / 2   (HP[9] = Filt[9] = Filt[8] = 0)
        #   Peak[10] = |Filt[10]|, X[10] = 1, Q1[10] = 1, Q2[10] = 1.
        closes = [100.0] * 10 + [110.0] * 10
        df = indicators.add_indicators(_frame(closes))
        k = indicators.eot_coefs()
        expect_hp10 = (1 - k["alpha1"] / 2) ** 2 * 10.0
        expect_f10 = k["c1"] * expect_hp10 / 2
        self.assertAlmostEqual(df["hp"].iloc[10], expect_hp10, places=9)
        self.assertAlmostEqual(df["filt"].iloc[10], expect_f10, places=9)
        self.assertAlmostEqual(df["peak"].iloc[10], abs(expect_f10), places=9)
        self.assertAlmostEqual(df["x"].iloc[10], 1.0, places=9)
        self.assertAlmostEqual(df["q1"].iloc[10], 1.0, places=9)
        self.assertAlmostEqual(df["q2"].iloc[10], 1.0, places=9)
        # Before the step everything is at the flat values.
        self.assertTrue((df["q1"].iloc[:10] == 0.85).all())
        self.assertTrue((df["q2"].iloc[:10] == 0.40).all())

    def test_x_bounded_by_one(self):
        # The peak tracker normalises Filt, so |X| <= 1 on any series
        # (up to the 0.991 decay letting a stale peak linger, which can
        # only shrink |X| further once Filt falls).
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue((df["x"].abs() <= 1.0 + 1e-9).all())
        self.assertTrue((df["q1"].abs() <= 1.0 + 1e-9).all())
        self.assertTrue((df["q2"].abs() <= 1.0 + 1e-9).all())

    def test_crosses_on_sine_wave(self):
        # A clean 40-bar sine cycle must drive X through -0.85 and back,
        # producing repeated Q1-up and Q2-down zero crossings in both
        # directions (verified by prototype: 15 each over 600 bars).
        df = indicators.add_indicators(_sine_frame())
        q1_up = ((df["q1"] > 0) & (df["q1"].shift(1) <= 0)).sum()
        q2_down = ((df["q2"] < 0) & (df["q2"].shift(1) >= 0)).sum()
        self.assertGreater(q1_up, 5)
        self.assertGreater(q2_down, 5)

    def test_signal_logic_crafted_rows(self):
        base = dict(q1=0.5, q2=0.5)
        # Q1 crosses above 0: long entry + short exit.
        rows = [dict(base, q1=-0.2), dict(base, q1=0.3)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[0])
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["short_exit"].iloc[1])
        self.assertFalse(out["long_exit"].iloc[1])
        # Q2 crosses below 0: short entry + long exit.
        rows = [dict(base, q2=0.2), dict(base, q2=-0.3)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertTrue(out["short_entry"].iloc[1])
        self.assertTrue(out["long_exit"].iloc[1])
        self.assertFalse(out["short_entry"].iloc[0])
        # At exactly 0 there is no cross (strict > / <).
        rows = [dict(base, q1=-0.2), dict(base, q1=0.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[1])
        # NaN quotients: no signal, no crash.
        rows = [dict(q1=np.nan, q2=np.nan)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[0])
        self.assertFalse(out["short_entry"].iloc[0])

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
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("hp", "filt", "peak", "x", "q1", "q2",
                    "long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars: closes flat, quotients sit at 0.85/0.40.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
