"""GMMA tests. Network-free, synthetic series only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.gmma import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _trend_up(n=400, seed=3):
    """Persistent uptrend: GMMA groups should fully align bullish."""
    rng = np.random.default_rng(seed)
    c = 100 + 0.20 * np.arange(n) + rng.normal(0, 0.15, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.05, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.05, n)) - 0.2
    return _ohlcv(o, h, l, c)


def _reversal(n=600, seed=7):
    """Long downtrend then sharp reversal up: must fire a fresh long entry."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:300] = 200 - 0.25 * np.arange(300) + rng.normal(0, 0.2, 300)
    c[300:] = c[299] + 0.45 * np.arange(1, n - 300 + 1) + rng.normal(0, 0.2, n - 300)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.4
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.4
    return _ohlcv(o, h, l, c)


def _chop(n=600, seed=21):
    """Whipsaw chop: the groups interpenetrate on most bars."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[0] = 100.0
    for i in range(1, n):  # OU process: fast mean reversion, no trend
        c[i] = c[i - 1] + 0.6 * (100 - c[i - 1]) + rng.normal(0, 0.12)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.15
    l = np.minimum(o, c) - 0.15
    return _ohlcv(o, h, l, c)


class TestGMMA(unittest.TestCase):
    def test_12_ema_columns_present(self):
        df = indicators.add_indicators(_trend_up())
        for n in (3, 5, 8, 10, 12, 15):
            self.assertIn(f"ema_s_{n}", df.columns)
        for n in (30, 35, 40, 45, 50, 60):
            self.assertIn(f"ema_l_{n}", df.columns)
        for col in ("short_min", "short_max", "long_min", "long_max",
                    "gmma_sep", "gmma_bull_gap", "gmma_bear_gap", "atr"):
            self.assertIn(col, df.columns)

    def test_ramp_orders_short_above_long(self):
        df = indicators.add_indicators(_trend_up())
        tail = df.iloc[-1]
        # in a clean uptrend every short-group EMA sits above every long-group EMA
        for n in (3, 5, 8, 10, 12, 15):
            self.assertGreater(tail[f"ema_s_{n}"], tail["long_max"], n)
        self.assertGreater(tail["gmma_bull_gap"], 0)
        self.assertGreater(tail["gmma_sep"], 0)

    def test_crossover_fires_long_on_reversal_up(self):
        df = signals.add_signals(indicators.add_indicators(_reversal()))
        entries = df.index[df["long_entry"]]
        self.assertGreater(len(entries), 0)
        i = entries[0]
        # the crossover bar: groups cross fully, previous bar not crossed
        self.assertGreater(df["short_min"].iloc[i], df["long_max"].iloc[i])
        self.assertLessEqual(df["short_min"].iloc[i - 1], df["long_max"].iloc[i - 1])

    def test_chop_no_entries_while_groups_intertwined(self):
        # Entry must require FULL group separation: on bars where the
        # groups interpenetrate (neither side fully separated), no entry
        # may fire. This is the exact Guppy rule vs a naive partial cross.
        df = signals.add_signals(indicators.add_indicators(_chop()))
        intertwined = (~(df["short_min"] > df["long_max"])) & (
            ~(df["short_max"] < df["long_min"])
        )
        self.assertGreater(int(intertwined.sum()), 50)  # chop really is choppy
        self.assertEqual(int((df["long_entry"] & intertwined).sum()), 0)
        self.assertEqual(int((df["short_entry"] & intertwined).sum()), 0)

    def test_exit_fires_on_recross(self):
        df = signals.add_signals(indicators.add_indicators(_reversal()))
        self.assertGreater(int(df["long_exit"].sum()), 0)
        idx = df.index[df["long_exit"]]
        for i in idx[:10]:
            self.assertLess(df["short_min"].iloc[i], df["long_max"].iloc[i])

    def test_no_lookahead_truncation(self):
        full = _trend_up()
        ind_full = indicators.add_indicators(full)
        for i in (150, 350):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("ema_s_3", "ema_l_60", "short_min", "long_max", "gmma_bull_gap"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_trend_up()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 100)

    def test_short_crossover_fires_on_reversal_down(self):
        rng = np.random.default_rng(9)
        n = 600
        c = np.empty(n)
        c[:300] = 100 + 0.25 * np.arange(300) + rng.normal(0, 0.2, 300)
        c[300:] = c[299] - 0.45 * np.arange(1, n - 300 + 1) + rng.normal(0, 0.2, n - 300)
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.4
        l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.4
        df = signals.add_signals(indicators.add_indicators(_ohlcv(o, h, l, c)))
        entries = df.index[df["short_entry"]]
        self.assertGreater(len(entries), 0)
        i = entries[0]
        self.assertLess(df["short_max"].iloc[i], df["long_min"].iloc[i])
        self.assertGreaterEqual(df["short_max"].iloc[i - 1], df["long_min"].iloc[i - 1])


if __name__ == "__main__":
    unittest.main()
