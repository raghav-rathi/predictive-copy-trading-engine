"""Waddah Attar Explosion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.waddah_attar import indicators, risk, signals


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=21):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _momentum_kick(n=400, down=False):
    # gentle drift, then an abrupt momentum leg: the histogram jumps and
    # the explosion line grows, which is exactly the WAE trigger regime
    k = np.arange(n)
    c = 100.0 + 0.05 * k
    c[200:] = c[200] + 1.5 * (k[200:] - 200)
    if down:
        c = 2 * 100.0 - c  # mirror: gentle decline, then sharp drop
    return _df_from_c(c)


def _manual_indicator_frame(n=60, long=True):
    """Hand-built indicators frame: entry conditions true from bar 30."""
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    hist = np.linspace(1.0, 6.0, n)
    if not long:
        hist = -hist
    df = pd.DataFrame({"t": t})
    df["wae_hist"] = hist
    df["wae_expl"] = np.linspace(0.2, 1.0, n)
    df["wae_dead"] = np.full(n, 0.1)
    df["wae_hist_rising"] = long  # shorts need a falling histogram
    df["wae_expl_rising"] = True
    return df


class TestWaddahAttar(unittest.TestCase):
    def test_hist_formula(self):
        df = indicators.add_indicators(_rand_df())
        macd = B.ema(df["c"], 20) - B.ema(df["c"], 40)
        expect = 150.0 * (macd - macd.shift(1))
        got = df["wae_hist"].dropna()
        exp = expect.dropna()
        pd.testing.assert_series_equal(got, exp, check_names=False)

    def test_explosion_formula(self):
        df = indicators.add_indicators(_rand_df())
        hist = df["wae_hist"]
        expect = 2.0 * hist.rolling(20, min_periods=20).std()
        pd.testing.assert_series_equal(
            df["wae_expl"].dropna(), expect.dropna(), check_names=False
        )

    def test_dead_zone_formula(self):
        df = indicators.add_indicators(_rand_df())
        expect = 3.7 * B.atr(df["h"], df["l"], df["c"], 100)
        pd.testing.assert_series_equal(
            df["wae_dead"].dropna(), expect.dropna(), check_names=False
        )

    def test_long_entry_predicate(self):
        df = _manual_indicator_frame(long=True)
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_entry"].iloc[40]))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_entry_predicate(self):
        df = _manual_indicator_frame(long=False)
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["short_entry"].iloc[40]))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_long_exit_on_cross(self):
        # hist above expl, then falls through it
        n = 40
        df = _manual_indicator_frame(n=n, long=True)
        df.loc[30:, "wae_hist"] = np.linspace(5.0, 0.3, n - 30)
        sig = signals.add_signals(df)
        exits = sig.index[sig["long_exit"]]
        self.assertTrue(bool((exits > 30).any()))

    def test_short_exit_on_cross(self):
        n = 40
        df = _manual_indicator_frame(n=n, long=False)
        df.loc[30:, "wae_hist"] = np.linspace(-5.0, -0.3, n - 30)
        sig = signals.add_signals(df)
        exits = sig.index[sig["short_exit"]]
        self.assertTrue(bool((exits > 30).any()))

    def test_dead_zone_blocks_weak_momentum(self):
        # identical rising hist but buried under the dead zone: no entry
        df = _manual_indicator_frame(long=True)
        df["wae_dead"] = 100.0
        sig = signals.add_signals(df)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_momentum_kick_fires_long(self):
        sig = signals.add_signals(indicators.add_indicators(_momentum_kick()))
        self.assertTrue(bool(sig["long_entry"].any()))

    def test_momentum_kick_fires_short(self):
        sig = signals.add_signals(indicators.add_indicators(_momentum_kick(down=True)))
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_flat_no_entries(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(np.full(200, 100.0))))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(bool(sig[col].isna().any()))
            self.assertTrue(bool(set(sig[col].unique()) <= {True, False}))

    def test_indicators_return_copy(self):
        df = _rand_df()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertAlmostEqual(risk.RISK.fee_rate, 0.00045)
        self.assertAlmostEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertAlmostEqual(risk.RISK.risk_frac, 0.01)
        self.assertAlmostEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 130)

    def test_spec_registers(self):
        from strategies.waddah_attar import SPEC
        self.assertEqual(SPEC.slug, "waddah_attar")
        self.assertEqual(SPEC.warmup_bars, risk.WARMUP)


if __name__ == "__main__":
    unittest.main()
