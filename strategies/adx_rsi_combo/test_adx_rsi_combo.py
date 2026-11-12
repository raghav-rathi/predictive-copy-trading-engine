"""ADX + RSI combo tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adx_rsi_combo import indicators, risk, signals
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


class TestAdxRsiCombo(unittest.TestCase):
    def test_registered(self):
        self.assertIn("adx_rsi_combo", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_rsi_all_gains_is_100(self):
        # Steadily rising closes: every delta is a gain, so Wilder
        # RSI(14) converges to 100 after warmup.
        closes = 100.0 + np.arange(200, dtype=float)
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(np.allclose(df["rsi"].iloc[risk.WARMUP:], 100.0,
                                    atol=1e-9))

    def test_rsi_hand_computed(self):
        # Manual Wilder RSI(14) on a random series: gains/losses
        # smoothed with alpha = 1/14, seeded at the first smoothed
        # value (pandas ewm adjust=False, min_periods=14).
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        df = indicators.add_indicators(_frame(closes))
        # np.diff gives the 199 real deltas (pandas diff() has a leading
        # NaN that ewm skips); seed the Wilder recursion at the first
        # real delta, then apply alpha = 1/14 to the remaining 198.
        delta = np.diff(closes)
        gain = np.clip(delta, 0, None)
        loss = -np.clip(delta, None, 0)
        ag = gain[0]
        al = loss[0]
        for g, l in zip(gain[1:], loss[1:]):
            ag = (g + 13.0 * ag) / 14.0
            al = (l + 13.0 * al) / 14.0
        rs = ag / al if al != 0 else float("inf")
        expected = 100 - 100 / (1 + rs)
        self.assertAlmostEqual(df["rsi"].iloc[199], expected, places=6)
        # B.rsi fillna's warmup NaNs with 0.0 (ag is NaN, so ag > 0 is
        # False); the first genuine Wilder RSI value lands at bar 13.
        self.assertEqual(df["rsi"].iloc[12], 0.0)
        self.assertTrue(np.isfinite(df["rsi"].iloc[13]))

    def test_adx_strong_uptrend_above_25(self):
        # Steady +1/bar uptrend with a 1-point range: +DI dominates,
        # DX -> 100, so ADX(14) converges well above 25 after warmup.
        closes = 100.0 + np.arange(200, dtype=float)
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue((df["adx"].iloc[risk.WARMUP:] > 25).all())
        self.assertTrue(np.allclose(df["adx"].iloc[-1], 100.0, atol=1e-6))

    def test_adx_flat_is_nan_no_entries(self):
        # Flat bars: +DM = -DM = 0 and ATR = 0, so ADX is NaN and the
        # trend filter is False everywhere.
        df = _run(_flat_frame())
        self.assertTrue(df["adx"].iloc[risk.WARMUP:].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_long_entry_cross_above_30_with_adx(self):
        # Two-row crafted frame: RSI crosses 30 -> 35 with ADX 30.
        rows = pd.DataFrame({
            "rsi": [25.0, 35.0],
            "adx": [30.0, 30.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Same cross with ADX 20 (below the 25 filter): no entry.
        rows = pd.DataFrame({
            "rsi": [25.0, 35.0],
            "adx": [20.0, 20.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])
        # Same cross with ADX exactly 25: strict > 25, no entry.
        rows = pd.DataFrame({
            "rsi": [25.0, 35.0],
            "adx": [25.0, 25.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])

    def test_short_entry_cross_below_70_with_adx(self):
        rows = pd.DataFrame({
            "rsi": [75.0, 65.0],
            "adx": [40.0, 40.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        # ADX below 25 blocks the short too.
        rows = pd.DataFrame({
            "rsi": [75.0, 65.0],
            "adx": [10.0, 10.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["short_entry"].iloc[1])

    def test_exits_at_rsi_50_cross(self):
        # Long exit: RSI crosses below 50 (55 -> 45), no ADX needed.
        rows = pd.DataFrame({
            "rsi": [55.0, 45.0],
            "adx": [10.0, 10.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # Short exit: RSI crosses above 50 (45 -> 55).
        rows = pd.DataFrame({
            "rsi": [45.0, 55.0],
            "adx": [10.0, 10.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # RSI exactly on 50 is not a cross.
        rows = pd.DataFrame({
            "rsi": [45.0, 50.0],
            "adx": [30.0, 30.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])

    def test_no_entry_without_cross(self):
        # RSI sitting above 30 the whole time (no cross) never fires a
        # long entry even with a strong ADX.
        rows = pd.DataFrame({
            "rsi": [35.0, 40.0, 45.0, 60.0],
            "adx": [30.0, 30.0, 30.0, 30.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # NaN RSI/ADX (warmup): no entry, no exit.
        rows = pd.DataFrame({
            "rsi": [np.nan, np.nan],
            "adx": [np.nan, np.nan],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

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
        self.assertEqual(risk.WARMUP, 30)

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
        for col in ("adx", "rsi", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): no crash, no entries.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
