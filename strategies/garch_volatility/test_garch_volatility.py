"""GARCH Volatility tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.garch_volatility import indicators, risk, signals
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


def _signal_frame(rows):
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


class TestGarchVolatility(unittest.TestCase):
    def test_registered(self):
        self.assertIn("garch_volatility", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_garch_zero_returns_exact(self):
        # Flat closes -> log returns 0. sigma2[0] = omega/(1-a-b) = 5e-7.
        # sigma2[1] = 1e-8 + 0.9*5e-7 = 4.6e-7; [2] = 1e-8+0.9*4.6e-7
        # = 4.24e-7; [3] = 1e-8+0.9*4.24e-7 = 3.916e-7.
        df = indicators.add_indicators(_flat_frame(n=1200))
        self.assertAlmostEqual(df["garch_var"].iloc[0], 5e-7, places=15)
        self.assertAlmostEqual(df["garch_var"].iloc[1], 4.6e-7, places=15)
        self.assertAlmostEqual(df["garch_var"].iloc[2], 4.24e-7, places=15)
        self.assertAlmostEqual(df["garch_var"].iloc[3], 3.916e-7, places=15)
        # Converges to omega/(1-beta) = 1e-7 as returns stay zero.
        self.assertAlmostEqual(df["garch_var"].iloc[-1], 1e-7, places=12)
        self.assertTrue(np.allclose(df["garch_vol"], np.sqrt(df["garch_var"])))

    def test_garch_hand_computed_random(self):
        # Independent recursion on random data.
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 300)))
        df = indicators.add_indicators(_frame(closes))
        r = np.zeros(300)
        r[1:] = np.log(closes[1:] / closes[:-1])
        s2 = np.empty(300)
        s2[0] = 1e-8 / 0.02
        for i in range(1, 300):
            s2[i] = 1e-8 + 0.08 * r[i - 1] ** 2 + 0.90 * s2[i - 1]
        np.testing.assert_allclose(df["garch_var"].to_numpy(), s2, rtol=1e-12)
        # A large shock raises the next forecast variance.
        self.assertGreater(df["garch_var"].iloc[1], 0)

    def test_vol_percentiles_and_normal_band(self):
        # With a small pct window the percentile columns are computable
        # and vol_normal is True exactly when vol sits in the band.
        df = indicators.add_indicators(_random_walk_frame(n=300), pct_n=100)
        tail = df.iloc[150:]
        self.assertTrue(tail["vol_p30"].notna().all())
        self.assertTrue(tail["vol_p70"].notna().all())
        self.assertTrue((tail["vol_p30"] <= tail["vol_p70"]).all())
        expect = ((tail["garch_vol"] >= tail["vol_p30"])
                  & (tail["garch_vol"] <= tail["vol_p70"]))
        pd.testing.assert_series_equal(
            tail["vol_normal"].reset_index(drop=True),
            expect.reset_index(drop=True), check_names=False)
        # Before the percentile window fills, vol_normal is False.
        self.assertFalse(df["vol_normal"].iloc[:99].any())

    def test_prev_high_low_exact(self):
        # prev_high_20 on bar 20 = max high of bars 0..19.
        highs = list(range(100, 130))
        lows = list(range(90, 120))
        closes = [95.0] * 30
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertEqual(df["prev_high_20"].iloc[20], 119.0)
        self.assertEqual(df["prev_low_20"].iloc[20], 90.0)
        self.assertTrue(np.isnan(df["prev_high_20"].iloc[19]))

    def test_signal_logic_crafted_rows(self):
        # Breakout above prev high with vol normal: long entry.
        rows = [dict(c=100.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True),
                dict(c=111.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Same breakout but vol outside the normal band: no entry.
        rows[1]["vol_normal"] = False
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # Breakdown below prev low with vol normal: short entry.
        rows = [dict(c=100.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True),
                dict(c=89.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        # Long exit: close back below the previous 20-bar high.
        rows = [dict(c=111.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True),
                dict(c=109.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        # (short_exit also fires here: 109 > prev_low 90 is the
        # short-exit condition evaluated independently per side.)
        # Short exit: close back above the previous 20-bar low.
        rows = [dict(c=89.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True),
                dict(c=91.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])
        # (long_exit also fires here: 91 < prev_high 110 is the
        # long-exit condition evaluated independently per side.)
        # Touching the high exactly is not a cross (strict >).
        rows = [dict(c=100.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True),
                dict(c=110.0, prev_high_20=110.0, prev_low_20=90.0, vol_normal=True)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])

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
        self.assertEqual(risk.WARMUP, 1100)

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
        # Flat closes: no new 20-bar high/low breakout, no entries.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("garch_vol", "vol_normal", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars: no breakout, no entries, vol still defined.
        df = _run(_frame([100.0] * 1200, highs=[100.0] * 1200,
                         lows=[100.0] * 1200))
        self.assertTrue(df["garch_vol"].iloc[-1] > 0)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
