"""WaveTrend Oscillator tests — formula hand-check, cross-in-zone logic, guards.

Synthetic network-free data only. Run from the repo root:
    python3 -m pytest strategies/wave_trend/ -q
"""

import sys
from os.path import dirname, join

import numpy as np
import pandas as pd
import unittest

sys.path.insert(0, join(dirname(__file__), "..", ".."))

from strategies.wave_trend import indicators, signals, risk  # noqa: E402
from strategies import base as B  # noqa: E402


def _ohlcv(n, seed=42, flat=None):
    rng = np.random.default_rng(seed)
    if flat is not None:
        px = np.full(n, float(flat))
    else:
        px = 100.0 + np.cumsum(rng.standard_normal(n)) * 0.5
    c = px.astype(float)
    o = np.roll(c, 1)
    o[0] = c[0]
    return pd.DataFrame(
        {
            "t": np.arange(n) * 3_600_000,
            "o": o,
            "h": c + 0.3,
            "l": c - 0.3,
            "c": c,
            "v": np.full(n, 1000.0),
        }
    )


def _sig_df(wt1, wt2):
    return pd.DataFrame({"wt1": pd.Series(wt1), "wt2": pd.Series(wt2)})


def _manual_ema(x, n):
    """Plain-Python EMA matching pandas ewm(span=n, adjust=False, min_periods=n).

    Seeds on the first valid observation, skips NaN inputs, and requires n
    valid observations before emitting (pandas' min_periods semantics).
    """
    x = np.asarray(x, dtype=float)
    alpha = 2.0 / (n + 1.0)
    out = np.full_like(x, np.nan)
    y = np.nan
    valid = 0
    for i, xi in enumerate(x):
        if np.isnan(xi):
            continue
        valid += 1
        y = xi if valid == 1 else alpha * xi + (1.0 - alpha) * y
        if valid >= n:
            out[i] = y
    return out


class TestWaveTrendIndicators(unittest.TestCase):
    def test_formula_hand_check(self):
        """Hand-computed EMA chain matches wavetrend() on non-flat data."""
        df = _ohlcv(120, seed=7)
        wt = indicators.wavetrend(df["h"], df["l"], df["c"])
        ap = (df["h"] + df["l"] + df["c"]) / 3.0
        esa = _manual_ema(ap, 10)
        d = _manual_ema(np.abs(ap.to_numpy() - esa), 10)
        raw = (ap.to_numpy() - esa) / (0.015 * d)
        ci = np.where(d == 0, 0.0, raw)
        tci = _manual_ema(ci, 21)
        w1 = pd.Series(tci)
        w2 = w1.rolling(4, min_periods=4).mean()
        np.testing.assert_allclose(wt["wt1"].to_numpy(), w1.to_numpy(), rtol=1e-10)
        np.testing.assert_allclose(wt["wt2"].to_numpy(), w2.to_numpy(), rtol=1e-10)
        np.testing.assert_allclose(wt["ci"].to_numpy(), ci, rtol=1e-10)

    def test_wt2_is_sma_of_wt1(self):
        """wt2 == SMA(wt1, 4) identity (post-warmup)."""
        df = indicators.add_indicators(_ohlcv(300, seed=3))
        expect = B.sma(df["wt1"], 4)
        valid = df["wt2"].notna()
        self.assertTrue(valid.any())
        np.testing.assert_allclose(df.loc[valid, "wt2"], expect[valid])

    def test_zero_division_guard(self):
        """Perfectly flat price -> d == 0, ci guarded to 0 (never NaN/divide-by-zero)."""
        df = indicators.add_indicators(_ohlcv(200, flat=100.0))
        post = df.iloc[risk.WARMUP:]
        self.assertTrue((post["d"] == 0.0).all())
        self.assertTrue((post["ci"] == 0.0).all())
        self.assertTrue(post["ci"].notna().all())
        self.assertEqual(post["wt1"].iloc[-1], 0.0)
        self.assertEqual(post["wt2"].iloc[-1], 0.0)

    def test_warmup_nan(self):
        """First bars are NaN; the chain resolves after the WARMUP window."""
        df = indicators.add_indicators(_ohlcv(300, seed=5))
        for col in ("wt1", "wt2", "ci", "d", "esa"):
            self.assertTrue(np.isnan(df[col].iloc[0]), col)
            self.assertTrue(df[col].iloc[-1] is not np.nan and not np.isnan(df[col].iloc[-1]), col)

    def test_add_indicators_contract(self):
        """Input OHLCV preserved; all strategy columns added."""
        src = _ohlcv(200, seed=9)
        df = indicators.add_indicators(src)
        self.assertTrue((df[["t", "o", "h", "l", "c", "v"]] == src).all().all())
        for col in ("ap", "esa", "d", "ci", "wt1", "wt2", "atr"):
            self.assertIn(col, df.columns, col)

    def test_no_lookahead(self):
        """Bar-j indicators identical on the full series vs data truncated at j."""
        src = _ohlcv(300, seed=11)
        full = indicators.add_indicators(src)
        trunc = indicators.add_indicators(src.iloc[:200])
        for col in ("wt1", "wt2", "ci", "d", "esa"):
            self.assertEqual(full[col].iloc[199], trunc[col].iloc[199], col)


class TestWaveTrendSignals(unittest.TestCase):
    def test_long_entry_cross_in_oversold(self):
        """wt1 crosses above wt2 with prior wt1 < -53 -> long_entry fires."""
        df = signals.add_signals(
            _sig_df([-60.0, -54.0, -49.0, -40.0], [-50.0, -53.0, -52.0, -45.0])
        )
        self.assertEqual(df["long_entry"].tolist(), [False, False, True, False])

    def test_short_entry_cross_in_overbought(self):
        """wt1 crosses below wt2 with prior wt1 > +53 -> short_entry fires."""
        df = signals.add_signals(
            _sig_df([60.0, 54.0, 49.0, 45.0], [50.0, 53.0, 52.0, 48.0])
        )
        self.assertEqual(df["short_entry"].tolist(), [False, False, True, False])

    def test_cross_without_zone_no_entry(self):
        """Cross outside the zones is not an entry."""
        df = signals.add_signals(_sig_df([10.0, 0.0, 10.0], [0.0, 5.0, 8.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_long_exit_opposite_cross(self):
        """wt1 crossing back below wt2 exits a long."""
        df = signals.add_signals(_sig_df([10.0, 8.0, -5.0], [0.0, 6.0, 4.0]))
        self.assertEqual(df["long_exit"].tolist(), [False, False, True])

    def test_long_exit_extreme(self):
        """wt1 > +60 is a hard long exit even with no cross."""
        df = signals.add_signals(_sig_df([0.0, 65.0], [0.0, 0.0]))
        self.assertEqual(df["long_exit"].tolist(), [False, True])

    def test_short_exit_opposite_cross(self):
        """wt1 crossing back above wt2 exits a short."""
        df = signals.add_signals(_sig_df([-10.0, -8.0, 5.0], [0.0, -6.0, -4.0]))
        self.assertEqual(df["short_exit"].tolist(), [False, False, True])

    def test_short_exit_extreme(self):
        """wt1 < -60 is a hard short exit even with no cross."""
        df = signals.add_signals(_sig_df([0.0, -65.0], [0.0, 0.0]))
        self.assertEqual(df["short_exit"].tolist(), [False, True])

    def test_signals_boolean_no_nan(self):
        """Signal columns are boolean and NaN-free on real indicator output."""
        src = _ohlcv(500, seed=13)
        df = signals.add_signals(indicators.add_indicators(src))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool, col)
            self.assertTrue(df[col].notna().all(), col)


class TestWaveTrendRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.5)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertEqual(r.fee_rate, 0.00045)
        self.assertEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
