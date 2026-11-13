"""Markov Regime Switching tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.markov_regime import indicators, risk, signals
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


def _signal_frame(rows):
    return pd.DataFrame(rows)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _two_regime_frame(n_calm=600, n_turb=600, seed=7):
    """Prices from log returns: calm N(0, 0.002), then turbulent
    N(0, 0.02). The regime switch is at bar n_calm."""
    rng = np.random.default_rng(seed)
    rets = np.concatenate([
        rng.normal(0.0, 0.002, n_calm),
        rng.normal(0.0, 0.02, n_turb),
    ])
    c = 100 * np.exp(np.cumsum(rets))
    return _frame(c), rets


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


class TestMarkovRegime(unittest.TestCase):
    def test_registered(self):
        self.assertIn("markov_regime", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_hmm_recovers_high_vol_state(self):
        # Fit directly on two-regime returns: the smoothed posterior
        # of the high-vol state must average > 0.6 on the volatile
        # segment and < 0.4 on the calm segment.
        _, rets = _two_regime_frame()
        fit = indicators.fit_hmm_2state(rets)
        high = int(np.argmax(fit["sigma"]))
        self.assertGreater(fit["sigma"][high], 2.0 * fit["sigma"][1 - high])
        gamma_high = fit["gamma"][:, high]
        self.assertGreater(gamma_high[600:].mean(), 0.6)
        self.assertLess(gamma_high[:600].mean(), 0.4)

    def test_hmm_regime_column_on_prices(self):
        # End-to-end: indicators on two-regime prices. The calibration
        # window (first 1000 returns) spans both regimes, and the
        # forward filter must still flag the volatile segment.
        df, _ = _two_regime_frame()
        out = indicators.add_indicators(df)
        self.assertGreater(out["turb_prob"].iloc[600:1000].mean(), 0.6)
        self.assertLess(out["turb_prob"].iloc[100:500].mean(), 0.4)
        self.assertTrue(set(out["regime"].unique()) <= {0, 1})
        self.assertTrue(((out["turb_prob"] >= 0.0)
                         & (out["turb_prob"] <= 1.0)).all())

    def test_logret_exact_value(self):
        # Close doubles in one bar: log return = log(2).
        closes = [100.0] * 50 + [200.0] * 50
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["logret"].iloc[50], np.log(2.0), places=12)
        self.assertTrue(np.isnan(df["logret"].iloc[0]))

    def test_ema_rsi_exact_columns(self):
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 300)))
        df = indicators.add_indicators(_frame(closes))
        c = pd.Series(closes)
        pd.testing.assert_series_equal(
            df["ema_fast"].reset_index(drop=True),
            c.ewm(span=12, adjust=False, min_periods=12).mean().reset_index(drop=True),
            check_names=False, atol=1e-12)
        pd.testing.assert_series_equal(
            df["ema_slow"].reset_index(drop=True),
            c.ewm(span=26, adjust=False, min_periods=26).mean().reset_index(drop=True),
            check_names=False, atol=1e-12)

    def test_calm_ema_cross_long(self):
        # Calm regime, EMA fast crosses above slow: long entry.
        rows = [
            dict(regime=0, ema_fast=99.0, ema_slow=100.0, rsi=50.0),
            dict(regime=0, ema_fast=101.0, ema_slow=100.0, rsi=50.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_calm_ema_cross_short(self):
        rows = [
            dict(regime=0, ema_fast=101.0, ema_slow=100.0, rsi=50.0),
            dict(regime=0, ema_fast=99.0, ema_slow=100.0, rsi=50.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_turbulent_rsi_mean_reversion(self):
        # Turbulent regime, RSI crosses up through 30: long entry.
        rows = [
            dict(regime=1, ema_fast=99.0, ema_slow=100.0, rsi=25.0),
            dict(regime=1, ema_fast=99.0, ema_slow=100.0, rsi=35.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Turbulent regime, RSI crosses down through 70: short entry.
        rows = [
            dict(regime=1, ema_fast=101.0, ema_slow=100.0, rsi=75.0),
            dict(regime=1, ema_fast=101.0, ema_slow=100.0, rsi=65.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        # RSI cross does NOT enter in the calm regime.
        rows = [
            dict(regime=0, ema_fast=99.0, ema_slow=100.0, rsi=25.0),
            dict(regime=0, ema_fast=99.0, ema_slow=100.0, rsi=35.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # EMA cross does NOT enter in the turbulent regime.
        rows = [
            dict(regime=1, ema_fast=99.0, ema_slow=100.0, rsi=50.0),
            dict(regime=1, ema_fast=101.0, ema_slow=100.0, rsi=50.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])

    def test_exits_either_system(self):
        # Long exits on RSI crossing down through 50 even in calm.
        rows = [
            dict(regime=0, ema_fast=101.0, ema_slow=100.0, rsi=55.0),
            dict(regime=0, ema_fast=101.0, ema_slow=100.0, rsi=45.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        # Short exits on EMA crossing up even in turbulent.
        rows = [
            dict(regime=1, ema_fast=99.0, ema_slow=100.0, rsi=50.0),
            dict(regime=1, ema_fast=101.0, ema_slow=100.0, rsi=50.0),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])

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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("turb_prob", "regime", "long_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_flat(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Flat prices: zero returns, HMM must not crash.
        df = indicators.add_indicators(_frame([100.0] * 1200))
        self.assertTrue(np.isfinite(df["turb_prob"]).all())


if __name__ == "__main__":
    unittest.main()
