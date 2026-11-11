"""Ehlers RSI tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ehlers_rsi import indicators, risk, signals
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


class TestEhlersRSI(unittest.TestCase):
    def test_registered(self):
        self.assertIn("ehlers_rsi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_coefs_hand_computed(self):
        k = indicators.supersmoother_coefs(10)
        self.assertAlmostEqual(k["a1"], math.exp(-1.414 * math.pi / 10), places=12)
        self.assertAlmostEqual(k["b1"], 2 * k["a1"] * math.cos(math.radians(1.414 * 180 / 10)), places=12)
        self.assertAlmostEqual(k["c1"], 1 - k["c2"] - k["c3"], places=12)
        self.assertAlmostEqual(k["c3"], -k["a1"] ** 2, places=12)
        # Unity gain at DC: c1 / (1 - c2 - c3) == 1.
        self.assertAlmostEqual(k["c1"] / (1 - k["c2"] - k["c3"]), 1.0, places=12)

    def test_indicator_values_flat(self):
        # Flat closes: the SuperSmoother sits exactly on the price and
        # Wilder RSI on a zero-change series is 0 (no gains, no losses).
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(df["ss_close"], 100.0, atol=1e-9))
        self.assertTrue((df["rsi_ss"].iloc[14:] == 0.0).all())

    def test_supersmoother_hand_computed(self):
        # Step: closes 100 for bars 0..9, then 110. Seeds f[0]=f[1]=100.
        # f[10] = c1*(110+100)/2 + c2*100 + c3*100
        #       = 100 + c1*5   (since c1 + c2 + c3 == 1).
        closes = [100.0] * 10 + [110.0] * 10
        df = indicators.add_indicators(_frame(closes))
        k = indicators.supersmoother_coefs(10)
        self.assertAlmostEqual(df["ss_close"].iloc[10], 100.0 + 5.0 * k["c1"], places=9)
        # f[11] = c1*(110+110)/2 + c2*f[10] + c3*100.
        expect_f11 = k["c1"] * 110.0 + k["c2"] * df["ss_close"].iloc[10] + k["c3"] * 100.0
        self.assertAlmostEqual(df["ss_close"].iloc[11], expect_f11, places=9)

    def test_rsi_rising_and_falling(self):
        # Steadily rising closes: smoothed RSI converges to 100 and
        # crosses above 70 (long_exit fires, short_entry does not).
        closes = list(100.0 + np.arange(300, dtype=float) * 0.5)
        df = _run(_frame(closes))
        self.assertAlmostEqual(df["rsi_ss"].iloc[-1], 100.0, places=6)
        self.assertTrue(df["long_exit"].any())
        self.assertFalse(df["short_entry"].any())
        # Steadily falling closes: smoothed RSI converges to 0. It starts
        # at 0 (no gains on a zero-change/falling series), so it never
        # crosses below 30 — no short_exit and no long_entry can fire;
        # the below-30 exit is covered by the rise-then-fall case below.
        closes = list(250.0 - np.arange(300, dtype=float) * 0.5)
        df = _run(_frame(closes))
        self.assertAlmostEqual(df["rsi_ss"].iloc[-1], 0.0, places=6)
        self.assertFalse(df["short_exit"].any())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["long_exit"].any())

    def test_rsi_bounce_crosses(self):
        # Fall hard (RSI -> 0), then rise hard (RSI crosses back above 30):
        # a long_entry must fire on the recovery.
        closes = list(200.0 - np.arange(100, dtype=float)) + \
            list(100.0 + np.arange(100, dtype=float))
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].any())
        # Rise hard (RSI -> 100), then fall hard (RSI crosses below 70
        # and then below 30): a short_entry and a short_exit must fire.
        closes = list(100.0 + np.arange(100, dtype=float)) + \
            list(200.0 - np.arange(100, dtype=float))
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue(df["short_exit"].any())

    def test_signal_logic_crafted_rows(self):
        base = dict(rsi_ss=50.0)
        # RSI crosses above 30: long entry.
        rows = [dict(base, rsi_ss=25.0), dict(base, rsi_ss=35.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertFalse(out["short_exit"].iloc[1])
        # RSI crosses below 30: short exit.
        rows = [dict(base, rsi_ss=35.0), dict(base, rsi_ss=25.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertTrue(out["short_exit"].iloc[1])
        self.assertFalse(out["long_entry"].iloc[1])
        # RSI crosses below 70: short entry.
        rows = [dict(base, rsi_ss=75.0), dict(base, rsi_ss=65.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertTrue(out["short_entry"].iloc[1])
        # RSI crosses above 70: long exit.
        rows = [dict(base, rsi_ss=65.0), dict(base, rsi_ss=75.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertTrue(out["long_exit"].iloc[1])
        self.assertFalse(out["short_entry"].iloc[1])
        # At exactly 30 / 70 there is no cross (strict > / <).
        rows = [dict(base, rsi_ss=25.0), dict(base, rsi_ss=30.0)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[1])
        # NaN RSI: no signal, no crash.
        rows = [dict(rsi_ss=np.nan)]
        out = signals.add_signals(_signal_frame(rows))
        self.assertFalse(out["long_entry"].iloc[0])
        self.assertFalse(out["short_entry"].iloc[0])
        self.assertFalse(out["long_exit"].iloc[0])
        self.assertFalse(out["short_exit"].iloc[0])

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
        # Flat data: RSI sits at 0, never crosses 30 or 70.
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
        for col in ("ss_close", "rsi_ss",
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
        # Zero-range bars: closes flat, RSI 0, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
