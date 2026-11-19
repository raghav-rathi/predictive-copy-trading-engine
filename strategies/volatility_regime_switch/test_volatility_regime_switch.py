"""ATR-percentile volatility regime switch tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.volatility_regime_switch import indicators, risk, signals
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


def _signal_frame(atr_pct, closes, prev_high, prev_low, mid,
                  bb_mid, bb_upper, bb_lower):
    n = len(atr_pct)
    return pd.DataFrame({
        "atr_pct": np.array(atr_pct, dtype=float),
        "c": np.array(closes, dtype=float),
        "prev_high": np.array(prev_high, dtype=float),
        "prev_low": np.array(prev_low, dtype=float),
        "donchian_mid": np.array(mid, dtype=float),
        "bb_mid": np.array(bb_mid, dtype=float),
        "bb_upper": np.array(bb_upper, dtype=float),
        "bb_lower": np.array(bb_lower, dtype=float),
    })


def _expansion_breakout_frame():
    """100 flat bars (ATR ~1), then 25 rising bars with wide range
    (ATR rising -> high percentile), then a close jumping above the
    prior 20-bar high at bar 125."""
    n = 126
    closes = np.full(n, 100.0)
    highs = np.full(n, 100.5)
    lows = np.full(n, 99.5)
    for i in range(100, 125):
        closes[i] = 100.0 + 0.5 * (i - 99)
        highs[i] = closes[i] + 2.5
        lows[i] = closes[i] - 2.5
    closes[125] = 120.0
    highs[125] = 122.5
    lows[125] = 117.5
    return _frame(closes, highs=highs, lows=lows)


class TestVolatilityRegimeSwitch(unittest.TestCase):
    def test_registered(self):
        self.assertIn("volatility_regime_switch", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)
            self.assertFalse(df[col].isna().any())

    def test_prev_high_excludes_current_bar(self):
        # 20 bars at high 100, then one bar at high 110: the Donchian
        # level including the current bar is 110, but prev_high must
        # still read 100 (the prior 20-bar high excluding this bar).
        highs = [100.0] * 20 + [110.0]
        lows = [99.0] * 21
        closes = [100.0] * 20 + [110.0]
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertAlmostEqual(df["donchian_high_20"].iloc[-1], 110.0)
        self.assertAlmostEqual(df["prev_high"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["prev_low"].iloc[-1], 99.0)

    def test_expansion_breakout_long_fires(self):
        df = _run(_expansion_breakout_frame())
        self.assertGreater(df["atr_pct"].iloc[125], 0.60)
        self.assertFalse(df["long_entry"].iloc[:125].any())
        self.assertTrue(df["long_entry"].iloc[125])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].any())

    def test_no_breakout_entry_in_middle_regime(self):
        # Same close above the prior high, but ATR percentile 0.50:
        # middle regime, no entries.
        df = signals.add_signals(_signal_frame(
            atr_pct=[0.50] * 5, closes=[98, 99, 100, 101, 102],
            prev_high=[100] * 5, prev_low=[90] * 5, mid=[95] * 5,
            bb_mid=[100] * 5, bb_upper=[105] * 5, bb_lower=[95] * 5))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_compression_fade_long_fires(self):
        df = signals.add_signals(_signal_frame(
            atr_pct=[0.20] * 5, closes=[98, 97, 96, 94, 96],
            prev_high=[110] * 5, prev_low=[80] * 5, mid=[95] * 5,
            bb_mid=[100] * 5, bb_upper=[105] * 5, bb_lower=[95] * 5))
        self.assertFalse(df["long_entry"].iloc[:3].any())
        self.assertTrue(df["long_entry"].iloc[3])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_compression_fade_short_fires(self):
        df = signals.add_signals(_signal_frame(
            atr_pct=[0.20] * 5, closes=[102, 103, 104, 106, 104],
            prev_high=[110] * 5, prev_low=[80] * 5, mid=[95] * 5,
            bb_mid=[100] * 5, bb_upper=[105] * 5, bb_lower=[95] * 5))
        self.assertTrue(df["short_entry"].iloc[3])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_no_fade_entry_in_expansion(self):
        # Close below the lower Bollinger band in EXPANSION is not a
        # fade entry (and not below the prior Donchian low either).
        df = signals.add_signals(_signal_frame(
            atr_pct=[0.80] * 5, closes=[98, 97, 96, 94, 93],
            prev_high=[110] * 5, prev_low=[85] * 5, mid=[97.5] * 5,
            bb_mid=[100] * 5, bb_upper=[105] * 5, bb_lower=[95] * 5))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_expansion_long_exit_below_midpoint(self):
        df = signals.add_signals(_signal_frame(
            atr_pct=[0.80] * 5, closes=[100, 99, 96, 94, 93],
            prev_high=[110] * 5, prev_low=[90] * 5, mid=[95] * 5,
            bb_mid=[100] * 5, bb_upper=[105] * 5, bb_lower=[95] * 5))
        self.assertFalse(df["long_exit"].iloc[:3].any())
        self.assertTrue(df["long_exit"].iloc[3])

    def test_compression_long_exit_above_bb_mid(self):
        df = signals.add_signals(_signal_frame(
            atr_pct=[0.20] * 5, closes=[96, 97, 99, 101, 102],
            prev_high=[110] * 5, prev_low=[80] * 5, mid=[95] * 5,
            bb_mid=[100] * 5, bb_upper=[105] * 5, bb_lower=[95] * 5))
        self.assertFalse(df["long_exit"].iloc[:3].any())
        self.assertTrue(df["long_exit"].iloc[3])

    def test_no_signal_exit_in_middle_regime(self):
        # Close below the Donchian midpoint in the middle regime:
        # no signal exit (harness stop/trail still applies).
        df = signals.add_signals(_signal_frame(
            atr_pct=[0.50] * 5, closes=[100, 99, 96, 94, 93],
            prev_high=[110] * 5, prev_low=[90] * 5, mid=[95] * 5,
            bb_mid=[100] * 5, bb_upper=[105] * 5, bb_lower=[95] * 5))
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_atr_pct_range_and_monotone(self):
        df = indicators.add_indicators(_random_walk_frame())
        # atr_pct is NaN until the 100-bar window sits fully on valid
        # ATR values (ATR itself needs 14 bars, so first valid is
        # bar 112); warmup 120 covers it.
        self.assertEqual(df["atr_pct"].first_valid_index(), 112)
        pct = df["atr_pct"].dropna()
        self.assertTrue(pct.between(0.0, 1.0).all())

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
        self.assertEqual(risk.WARMUP, 120)

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
        # Constant ATR ties rank at 1.0 (all 100 values equal the
        # current one); entries still need a real breakout, which
        # flat prices never print.
        self.assertTrue((df["atr_pct"].iloc[120:] == 1.0).all())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("atr_pct", "prev_high", "long_entry",
                    "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
