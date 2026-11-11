"""TEMA cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tema_cross import indicators, risk, signals
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

class TestTemaCross(unittest.TestCase):
    def test_registered(self):
        self.assertIn("tema_cross", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_tema_hand_computed(self):
        # Manual TEMA(9): EMA recursion with alpha = 2/(9+1), seeded at
        # the first close; nested EMAs skip leading NaNs the same way
        # pandas ewm does (a NaN observation leaves the state unchanged).
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        df = indicators.add_indicators(_frame(closes))

        def _ema_manual(vals, n):
            alpha = 2.0 / (n + 1)
            out = np.full(len(vals), np.nan)
            state = None
            for i, x in enumerate(vals):
                if np.isnan(x):
                    out[i] = state if state is not None else np.nan
                    continue
                state = x if state is None else alpha * x + (1.0 - alpha) * state
                out[i] = state
            return out

        e1 = _ema_manual(closes, 9)
        e2 = _ema_manual(e1, 9)
        e3 = _ema_manual(e2, 9)
        tema_manual = 3 * e1 - 3 * e2 + e3
        self.assertAlmostEqual(df["tema_fast"].iloc[199], tema_manual[199], places=8)
        # TEMA(21) still NaN at bar 10 (needs 21 bars for the first EMA).
        self.assertTrue(np.isnan(df["tema_slow"].iloc[10]))
        self.assertTrue(np.isfinite(df["tema_fast"].iloc[199]))

    def test_tema_flat(self):
        # Flat price: both TEMAs sit exactly on the price; no cross.
        df = indicators.add_indicators(_flat_frame(n=300))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["tema_fast"], 100.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["tema_slow"], 100.0, atol=1e-9))

    def test_cross_up_then_down_scenario(self):
        # Flat, then a steady rise, then a steady fall. TEMA(9) must
        # cross above TEMA(21) during the rise and below during the fall.
        n_flat, n_rise, n_fall, n_flat2 = 60, 80, 40, 60
        rise = np.linspace(100.0, 140.0, n_rise)
        fall = np.linspace(140.0, 100.0, n_fall)
        closes = np.concatenate([np.full(n_flat, 100.0), rise, fall,
                                 np.full(n_flat2, 100.0)])
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[n_flat:n_flat + n_rise].any())
        # TEMA tracks a linear move with near-zero lag, so fast and slow
        # sit almost on top of each other during the fall itself; the
        # cross below lands once price flattens at 100 and the fast
        # TEMA settles first.
        self.assertTrue(df["short_entry"].iloc[n_flat + n_rise:].any())
        # Entries and exits are mirror images: a long exit fires exactly
        # where a short entry fires, and vice versa.
        pd.testing.assert_series_equal(
            df["long_exit"].reset_index(drop=True),
            df["short_entry"].reset_index(drop=True), check_names=False)
        pd.testing.assert_series_equal(
            df["short_exit"].reset_index(drop=True),
            df["long_entry"].reset_index(drop=True), check_names=False)

    def test_signal_logic_crafted_rows(self):
        # Two-row frames: the cross is decided by the change from row 0
        # to row 1.
        rows = [dict(tema_fast=90.0, tema_slow=100.0),
                dict(tema_fast=101.0, tema_slow=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        rows = [dict(tema_fast=110.0, tema_slow=100.0),
                dict(tema_fast=99.0, tema_slow=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        # No cross (fast stays above slow): no entry.
        rows = [dict(tema_fast=110.0, tema_slow=100.0),
                dict(tema_fast=111.0, tema_slow=100.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # NaN TEMAs (warmup): no entry, no exit.
        rows = [dict(tema_fast=np.nan, tema_slow=np.nan),
                dict(tema_fast=np.nan, tema_slow=np.nan)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("tema_fast", "tema_slow", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): TEMAs converge to the price,
        # no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["tema_fast"], 100.0, atol=1e-9))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
