"""RSI hidden-divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.hidden_divergence import indicators, risk, signals
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


class TestHiddenDivergence(unittest.TestCase):
    def test_registered(self):
        self.assertIn("hidden_divergence", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_rsi_all_gains_is_100(self):
        # Every bar gains: average loss is 0, so Wilder RSI is 100.
        n = 200
        closes = list(np.arange(100.0, 100.0 + n))
        df = indicators.add_indicators(_frame(closes))
        tail = df["rsi"].iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail, 100.0, atol=1e-9))

    def test_rsi_all_losses_is_0(self):
        # Every bar loses: average gain is 0, so Wilder RSI is 0.
        n = 200
        closes = list(np.arange(300.0, 300.0 - n, -1.0))
        df = indicators.add_indicators(_frame(closes))
        tail = df["rsi"].iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail, 0.0, atol=1e-9))

    def test_rsi_hand_computed(self):
        # Independent Wilder-RSI computation on random data.
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        df = indicators.add_indicators(_frame(closes))
        c = pd.Series(closes)
        delta = c.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        ag = gain.ewm(alpha=1.0 / 14, adjust=False, min_periods=14).mean()
        al = loss.ewm(alpha=1.0 / 14, adjust=False, min_periods=14).mean()
        rs = ag / al.replace(0, float("nan"))
        manual = (100 - 100 / (1 + rs)).fillna(100.0 * (ag > 0).astype(float))
        pd.testing.assert_series_equal(
            df["rsi"].reset_index(drop=True),
            manual.reset_index(drop=True),
            check_names=False, atol=1e-9)

    def test_pivot_low_detection(self):
        # A clean V in the lows: the bottom bar is the swing low.
        n = 20
        lows = [100.0, 99.0, 98.0, 97.0, 98.0, 99.0, 100.0] + [100.0] * 13
        closes = [l + 1.0 for l in lows]
        df = indicators.add_indicators(_frame(closes, lows=lows))
        self.assertTrue(df["pivot_low"].iloc[3])
        self.assertFalse(df["pivot_low"].iloc[:3].any())
        self.assertFalse(df["pivot_low"].iloc[4:].any())

    def test_pivot_high_detection(self):
        # A clean inverted V in the highs: the top bar is the swing high.
        n = 20
        highs = [100.0, 101.0, 102.0, 103.0, 102.0, 101.0, 100.0] + [100.0] * 13
        closes = [h - 1.0 for h in highs]
        df = indicators.add_indicators(_frame(closes, highs=highs))
        self.assertTrue(df["pivot_high"].iloc[3])
        self.assertFalse(df["pivot_high"].iloc[:3].any())
        self.assertFalse(df["pivot_high"].iloc[4:].any())

    def test_bullish_hidden_divergence_crafted(self):
        # Two swing lows: price higher low (90 -> 92), RSI lower low
        # (30 -> 25). The second pivot is at bar 5, confirmed at bar 7,
        # so the long entry fires on bar 7 and not before.
        rows = []
        for i in range(10):
            rows.append(dict(rsi=50.0, pivot_low=False, pivot_high=False,
                             l=100.0, h=101.0))
        rows[0] = dict(rows[0], pivot_low=True, l=90.0, rsi=30.0)
        rows[5] = dict(rows[5], pivot_low=True, l=92.0, rsi=25.0)
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[:7].any())
        self.assertTrue(df["long_entry"].iloc[7])
        self.assertFalse(df["short_entry"].any())

    def test_bearish_hidden_divergence_crafted(self):
        # Two swing highs: price lower high (110 -> 108), RSI higher
        # high (70 -> 75). Short entry fires on the confirmation bar 7.
        rows = []
        for i in range(10):
            rows.append(dict(rsi=50.0, pivot_low=False, pivot_high=False,
                             l=100.0, h=101.0))
        rows[0] = dict(rows[0], pivot_high=True, h=110.0, rsi=70.0)
        rows[5] = dict(rows[5], pivot_high=True, h=108.0, rsi=75.0)
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["short_entry"].iloc[:7].any())
        self.assertTrue(df["short_entry"].iloc[7])
        self.assertFalse(df["long_entry"].any())

    def test_regular_divergence_is_not_traded(self):
        # Regular bullish divergence (lower price low 90 -> 88, higher
        # RSI low 25 -> 30) is a reversal setup, not hidden divergence:
        # no long entry.
        rows = []
        for i in range(10):
            rows.append(dict(rsi=50.0, pivot_low=False, pivot_high=False,
                             l=100.0, h=101.0))
        rows[0] = dict(rows[0], pivot_low=True, l=90.0, rsi=25.0)
        rows[5] = dict(rows[5], pivot_low=True, l=88.0, rsi=30.0)
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        # Same-direction moves (higher low AND higher RSI) also no entry.
        rows[5] = dict(rows[5], l=92.0, rsi=35.0)
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())

    def test_first_pivot_never_signals(self):
        # A single pivot has nothing to compare against: no entry.
        rows = [dict(rsi=50.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0) for _ in range(10)]
        rows[3] = dict(rows[3], pivot_low=True, l=90.0, rsi=30.0)
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_rsi_50_exit_crafted(self):
        # RSI crossing 50 down: long exit. Crossing 50 up: short exit.
        rows = [dict(rsi=55.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0),
                dict(rsi=45.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        rows = [dict(rsi=45.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0),
                dict(rsi=55.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Touching 50 exactly is not a cross (strict < / >).
        rows = [dict(rsi=55.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0),
                dict(rsi=50.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_exit"].iloc[1])
        # NaN RSI (warmup): no exit.
        rows = [dict(rsi=np.nan, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0),
                dict(rsi=45.0, pivot_low=False, pivot_high=False,
                     l=100.0, h=101.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_exit"].iloc[1])

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
        self.assertEqual(risk.WARMUP, 100)

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
        # Flat close: no pivots (equal lows never form a strict swing
        # low), RSI is 50-ish flat, no entries.
        df = _run(_flat_frame())
        self.assertFalse(df["pivot_low"].any())
        self.assertFalse(df["pivot_high"].any())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any RSI or signal
        # value on the bars before the jump. Pivot columns may change
        # only on the last two bars before the jump (their confirmation
        # bars i+1/i+2 did not exist yet), so they are compared on a
        # shorter prefix.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("rsi", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)
        for col in ("pivot_low", "pivot_high"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1298].reset_index(drop=True),
                df2[col].iloc[:1298].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
