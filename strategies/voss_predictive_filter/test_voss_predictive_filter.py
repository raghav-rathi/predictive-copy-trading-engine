"""Voss Predictive Filter tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.voss_predictive_filter import indicators, risk, signals
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


class TestVossPredictiveFilter(unittest.TestCase):
    def test_registered(self):
        self.assertIn("voss_predictive_filter", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_coefs_hand_computed(self):
        k = indicators.voss_coefs()
        self.assertAlmostEqual(k["f1"], math.cos(2 * math.pi / 20), places=12)
        self.assertAlmostEqual(k["g1"], math.cos(0.25 * 2 * math.pi / 20), places=12)
        # S1 = 1/G1 - sqrt(1/G1^2 - 1) ~= 0.92439 for the shipped parameters.
        self.assertAlmostEqual(k["s1"], 0.9243904916582067, places=9)
        self.assertEqual(k["order"], 9)

    def test_indicator_values_flat(self):
        # Flat closes: Close[i] - Close[i-2] is 0 every bar, so Filt and
        # Voss stay exactly 0; no cross can fire.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue((df["bandpass"] == 0.0).all())
        self.assertTrue((df["voss"] == 0.0).all())
        self.assertTrue(np.isfinite(df["bandpass"]).all())
        self.assertTrue(np.isfinite(df["voss"]).all())

    def test_indicator_hand_computed_step(self):
        # Step: closes 100 for bars 0..9, then 110. The first six Filt
        # values are 0 by construction; at bar 10:
        #   Filt[10] = 0.5*(1-S1)*(110-100) = 0.3780475...
        #   Voss[10] = 6*Filt[10] - SumC(0) = 2.2682852...
        # (SumC is 0 because every earlier Voss value is 0.)
        closes = [100.0] * 10 + [110.0] * 10
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue((df["bandpass"].iloc[:6] == 0.0).all())
        self.assertTrue((df["voss"].iloc[:6] == 0.0).all())
        self.assertAlmostEqual(df["bandpass"].iloc[10], 0.37804754170896626, places=9)
        self.assertAlmostEqual(df["voss"].iloc[10], 2.268285250253798, places=9)
        # Bar 11: Filt[11] = 0.5*(1-S1)*(110-100) + F1*(1+S1)*Filt[10].
        s1 = indicators.voss_coefs()["s1"]
        f1 = indicators.voss_coefs()["f1"]
        expect_f11 = 0.5 * (1 - s1) * 10 + f1 * (1 + s1) * df["bandpass"].iloc[10]
        self.assertAlmostEqual(df["bandpass"].iloc[11], expect_f11, places=9)
        # Voss[11] = 6*Filt[11] - SumC; SumC uses only Voss[10] at lag 1
        # with weight 9/9 (all earlier Voss are 0): SumC = Voss[10].
        self.assertAlmostEqual(
            df["voss"].iloc[11], 6 * df["bandpass"].iloc[11] - df["voss"].iloc[10],
            places=9)

    def test_crosses_on_sine_wave(self):
        # A clean 40-bar sine cycle must produce repeated Voss/bandpass
        # crosses in both directions (verified by prototype: 16 up, 15 down).
        df = indicators.add_indicators(_sine_frame())
        cross_up = ((df["voss"] > df["bandpass"])
                    & (df["voss"].shift(1) <= df["bandpass"].shift(1))).sum()
        cross_down = ((df["voss"] < df["bandpass"])
                      & (df["voss"].shift(1) >= df["bandpass"].shift(1))).sum()
        self.assertGreater(cross_up, 5)
        self.assertGreater(cross_down, 5)

    def test_signal_logic_crafted_rows(self):
        base = dict(voss=0.0, bandpass=0.0, adx=20.0)
        # Voss crosses above bandpass with ADX 20 (< 25): long entry.
        rows = [dict(base, voss=-1.0, bandpass=0.0),
                dict(base, voss=1.0, bandpass=0.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[0])
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["short_exit"].iloc[1])
        self.assertFalse(out["long_exit"].iloc[1])
        # Voss crosses below bandpass: short entry + long exit.
        rows = [dict(base, voss=1.0, bandpass=0.0),
                dict(base, voss=-1.0, bandpass=0.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertTrue(out["short_entry"].iloc[1])
        self.assertTrue(out["long_exit"].iloc[1])
        # ADX gate blocks entries at 25+ but not exits.
        rows = [dict(base, voss=-1.0, bandpass=0.0, adx=30.0),
                dict(base, voss=1.0, bandpass=0.0, adx=30.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[1])
        self.assertTrue(out["short_exit"].iloc[1])
        # NaN ADX blocks the entry (gate cannot pass on unknown trend).
        rows = [dict(base, voss=-1.0, bandpass=0.0, adx=np.nan),
                dict(base, voss=1.0, bandpass=0.0, adx=np.nan)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[1])

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
        for col in ("bandpass", "voss", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars: closes flat, so Filt/Voss are 0, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
