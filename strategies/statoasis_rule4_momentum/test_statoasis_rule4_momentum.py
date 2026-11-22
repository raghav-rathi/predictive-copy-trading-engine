"""StatOasis Rule 4 tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.statoasis_rule4_momentum import indicators, risk, signals


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _signal_frame(n=30, rsi=None, k=None, wr=None, ret=None):
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": np.full(n, 100.0), "h": np.full(n, 100.1),
        "l": np.full(n, 99.9), "c": np.full(n, 100.0),
        "v": np.full(n, 100.0),
        "rsi": np.full(n, 50.0) if rsi is None else np.asarray(rsi, dtype=float),
        "stoch_k": np.full(n, 50.0) if k is None else np.asarray(k, dtype=float),
        "willr": np.full(n, -50.0) if wr is None else np.asarray(wr, dtype=float),
        "ret_120h": np.zeros(n) if ret is None else np.asarray(ret, dtype=float),
    })


def _long_on(frame, lo, hi):
    """Set all four long conditions true on bars [lo, hi)."""
    frame.loc[lo:hi - 1, "rsi"] = 60.0
    frame.loc[lo:hi - 1, "stoch_k"] = 60.0
    frame.loc[lo:hi - 1, "willr"] = -40.0
    frame.loc[lo:hi - 1, "ret_120h"] = 0.02


def _short_on(frame, lo, hi):
    frame.loc[lo:hi - 1, "rsi"] = 40.0
    frame.loc[lo:hi - 1, "stoch_k"] = 40.0
    frame.loc[lo:hi - 1, "willr"] = -60.0
    frame.loc[lo:hi - 1, "ret_120h"] = -0.02


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("rsi", "stoch_k", "willr", "ret_120h", "atr"):
            self.assertIn(col, ind.columns)

    def test_stochastic_and_williams_bounds(self):
        ind = indicators.add_indicators(_random_walk_frame())
        k = ind["stoch_k"].dropna()
        self.assertTrue(((k >= 0) & (k <= 100)).all())
        wr = ind["willr"].dropna()
        self.assertTrue(((wr >= -100) & (wr <= 0)).all())

    def test_stochastic_k_formula(self):
        # Flat range h=110, l=90, c=100 -> raw %K = 50, smoothed 50.
        n = 30
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0), "h": np.full(n, 110.0),
            "l": np.full(n, 90.0), "c": np.full(n, 100.0),
            "v": np.full(n, 100.0)})
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["stoch_k"].iloc[-1], 50.0, places=9)
        self.assertAlmostEqual(ind["willr"].iloc[-1], -50.0, places=9)

    def test_ret_120h_is_120_bar_return(self):
        c = np.concatenate([np.full(130, 100.0), np.full(20, 110.0)])
        ind = indicators.add_indicators(_frame_from_close(c))
        # c[130]/c[10] - 1 = 0.10; c[129]/c[9] - 1 = 0.
        self.assertAlmostEqual(ind["ret_120h"].iloc[130], 0.10, places=9)
        self.assertAlmostEqual(ind["ret_120h"].iloc[129], 0.0, places=9)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        full = indicators.add_indicators(df)
        part = indicators.add_indicators(short)
        for col in ("rsi", "stoch_k", "willr", "ret_120h"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                part[col].reset_index(drop=True), check_names=False)


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_and_10_bar_exit(self):
        f = _signal_frame()
        _long_on(f, 5, 15)  # conditions true bars 5..14 only
        sig = signals.add_signals(f)
        self.assertTrue(sig["long_entry"].iloc[5])
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        # Fixed 10-bar hold: exit exactly 10 bars after entry.
        self.assertTrue(sig["long_exit"].iloc[15])
        self.assertEqual(int(sig["long_exit"].sum()), 1)
        # No exit before bar 15, even though the condition holds.
        self.assertFalse(sig["long_exit"].iloc[:15].any())

    def test_no_reentry_while_in_position(self):
        f = _signal_frame()
        _long_on(f, 5, 25)
        sig = signals.add_signals(f)
        # After the bar-15 exit the condition still holds, so the
        # state machine re-enters at 15 — but never while holding.
        self.assertFalse(sig["long_entry"].iloc[6:15].any())

    def test_short_mirror_entry_and_exit(self):
        f = _signal_frame()
        _short_on(f, 5, 25)
        sig = signals.add_signals(f)
        self.assertTrue(sig["short_entry"].iloc[5])
        self.assertTrue(sig["short_exit"].iloc[15])

    def test_one_failed_leg_blocks_entry(self):
        # RSI, %K, %R all pass but the 120h return is only +0.5%.
        f = _signal_frame()
        _long_on(f, 5, 25)
        f.loc[5:24, "ret_120h"] = 0.005
        sig = signals.add_signals(f)
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_boundary_values_do_not_fire(self):
        # Strict inequalities: exactly 55 / 50 / -50 / 1% is not a buy.
        f = _signal_frame()
        f.loc[5:24, "rsi"] = 55.0
        f.loc[5:24, "stoch_k"] = 50.0
        f.loc[5:24, "willr"] = -50.0
        f.loc[5:24, "ret_120h"] = 0.01
        sig = signals.add_signals(f)
        self.assertFalse(sig["long_entry"].any())

    def test_no_lookahead_signals(self):
        df = _random_walk_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        part = signals.add_signals(
            indicators.add_indicators(df.iloc[:200]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                part[col].reset_index(drop=True), check_names=False)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 10)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 150)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        self.assertGreaterEqual(res.metrics()["trades"], 0)


if __name__ == "__main__":
    unittest.main()
