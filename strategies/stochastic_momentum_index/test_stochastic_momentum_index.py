"""Stochastic Momentum Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.stochastic_momentum_index import indicators, risk, signals
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


class TestStochasticMomentumIndex(unittest.TestCase):
    def test_registered(self):
        self.assertIn("stochastic_momentum_index", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_smi_top_of_range(self):
        # Close pinned at the top of a fixed 110/90 range: D = +10,
        # half-range = 10, so SMI converges to +100.
        n = 200
        df = indicators.add_indicators(_frame(
            [110.0] * n, highs=[110.0] * n, lows=[90.0] * n))
        tail = df["smi"].iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail, 100.0, atol=1e-6))

    def test_smi_bottom_of_range(self):
        # Close pinned at the bottom of the same range: SMI -> -100.
        n = 200
        df = indicators.add_indicators(_frame(
            [90.0] * n, highs=[110.0] * n, lows=[90.0] * n))
        tail = df["smi"].iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail, -100.0, atol=1e-6))

    def test_smi_midpoint_zero(self):
        # Close at the range midpoint: D = 0, so SMI = 0.
        n = 200
        df = indicators.add_indicators(_frame(
            [100.0] * n, highs=[110.0] * n, lows=[90.0] * n))
        tail = df["smi"].iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail, 0.0, atol=1e-9))

    def test_smi_hand_computed(self):
        # Independent double-EMA computation of DS and DHL on random
        # data, compared against the indicator columns.
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        highs = closes + rng.uniform(0.1, 1.0, 200)
        lows = closes - rng.uniform(0.1, 1.0, 200)
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        hh = pd.Series(highs).rolling(13, min_periods=13).max()
        ll = pd.Series(lows).rolling(13, min_periods=13).min()
        d = pd.Series(closes) - (hh + ll) / 2
        rng_range = hh - ll
        ds = d.ewm(span=25, adjust=False, min_periods=25).mean()
        ds = ds.ewm(span=2, adjust=False, min_periods=2).mean()
        dhl = rng_range.ewm(span=25, adjust=False, min_periods=25).mean()
        dhl = dhl.ewm(span=2, adjust=False, min_periods=2).mean()
        smi_manual = (100.0 * ds / (0.5 * dhl)).clip(-100, 100).fillna(0.0)
        pd.testing.assert_series_equal(
            df["smi"].reset_index(drop=True), smi_manual.reset_index(drop=True),
            check_names=False, atol=1e-9)
        # SMI stays inside [-100, 100] everywhere.
        self.assertTrue(((df["smi"] >= -100.0) & (df["smi"] <= 100.0)).all())

    def test_long_entry_cross_above_minus40(self):
        # 60 bars pinned at the range bottom (SMI -> -100), then the
        # close jumps to the top of the range: SMI climbs through -40
        # and a long entry fires on the crossing bar.
        n = 200
        closes = [90.0] * 60 + [110.0] * 140
        highs = [110.0] * n
        lows = [90.0] * n
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["smi"].iloc[59] < -40.0)
        self.assertTrue(df["long_entry"].iloc[60:80].any())
        first = df.index[df["long_entry"]].min()
        self.assertTrue(df["smi"].iloc[first] > -40.0)
        self.assertTrue(df["smi"].iloc[first - 1] <= -40.0)

    def test_short_entry_cross_below_plus40(self):
        # Mirror: 60 bars at the range top (SMI -> +100), then the
        # close drops to the bottom: SMI falls through +40.
        n = 200
        closes = [110.0] * 60 + [90.0] * 140
        highs = [110.0] * n
        lows = [90.0] * n
        df = _run(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(df["smi"].iloc[59] > 40.0)
        self.assertTrue(df["short_entry"].iloc[60:80].any())
        first = df.index[df["short_entry"]].min()
        self.assertTrue(df["smi"].iloc[first] < 40.0)
        self.assertTrue(df["smi"].iloc[first - 1] >= 40.0)

    def test_signal_logic_crafted_rows(self):
        # SMI crossing -40 up: long entry, no short entry.
        rows = [dict(smi=-50.0), dict(smi=-30.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # SMI crossing +40 down: short entry.
        rows = [dict(smi=50.0), dict(smi=30.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        # SMI crossing 0 down: long exit.
        rows = [dict(smi=5.0), dict(smi=-5.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # SMI crossing 0 up: short exit.
        rows = [dict(smi=-5.0), dict(smi=5.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Touching -40 exactly is not a cross (strict >).
        rows = [dict(smi=-50.0), dict(smi=-40.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # NaN SMI (warmup): no entry, no exit.
        rows = [dict(smi=np.nan), dict(smi=-30.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

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
        # Flat close at the range midpoint: SMI = 0, no crossings.
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
        for col in ("smi", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): DHL = 0, SMI is defined as 0.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["smi"], 0.0, atol=1e-12))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
