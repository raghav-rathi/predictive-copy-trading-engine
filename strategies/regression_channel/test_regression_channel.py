"""Linear regression channel tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.regression_channel import indicators, risk, signals
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


class TestRegressionChannel(unittest.TestCase):
    def test_registered(self):
        self.assertIn("regression_channel", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_regression_exact_line(self):
        # Perfect line y = 2x + 10: slope is exactly 2, the midline
        # equals the close, and the residual std is 0.
        closes = 2.0 * np.arange(300, dtype=float) + 10.0
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["reg_slope"], 2.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["reg_mid"], tail["c"], atol=1e-6))
        self.assertTrue(np.allclose(tail["reg_std"], 0.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["reg_upper"], tail["reg_mid"], atol=1e-6))
        self.assertTrue(np.allclose(tail["reg_lower"], tail["reg_mid"], atol=1e-6))

    def test_regression_hand_computed_polyfit(self):
        # Independent OLS check with np.polyfit on the last 100 closes:
        # slope, midline value at the last bar, and residual std must
        # match the vectorized rolling computation.
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 300)))
        df = indicators.add_indicators(_frame(closes))
        x = np.arange(100, dtype=float)
        y = closes[-100:]
        slope, intercept = np.polyfit(x, y, 1)
        fitted = slope * x + intercept
        self.assertAlmostEqual(df["reg_slope"].iloc[-1], slope, places=6)
        self.assertAlmostEqual(df["reg_mid"].iloc[-1], fitted[-1], places=4)
        self.assertAlmostEqual(df["reg_std"].iloc[-1],
                               np.std(y - fitted, ddof=1), places=6)
        # NaN before 100 bars of history exist.
        self.assertTrue(df["reg_mid"].iloc[:99].isna().all())
        self.assertTrue(np.isfinite(df["reg_mid"].iloc[99]))

    def test_bands_symmetric_two_sigma(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["reg_upper"] - tail["reg_mid"],
                                    2.0 * tail["reg_std"], atol=1e-9))
        self.assertTrue(np.allclose(tail["reg_mid"] - tail["reg_lower"],
                                    2.0 * tail["reg_std"], atol=1e-9))

    def test_long_entry_cross_back_above_lower_band(self):
        # Close crosses from below/at the lower band to above it.
        rows = pd.DataFrame({
            "c": [90.0, 96.0],
            "reg_lower": [95.0, 95.0],
            "reg_upper": [105.0, 105.0],
            "reg_mid": [100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Already above the band (no cross): no entry.
        rows = pd.DataFrame({
            "c": [96.0, 97.0],
            "reg_lower": [95.0, 95.0],
            "reg_upper": [105.0, 105.0],
            "reg_mid": [100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        # Mirror: close crosses back below the upper band -> short.
        rows = pd.DataFrame({
            "c": [110.0, 104.0],
            "reg_lower": [95.0, 95.0],
            "reg_upper": [105.0, 105.0],
            "reg_mid": [100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_exits_at_midline_cross(self):
        # Long exit: close crosses above the midline.
        rows = pd.DataFrame({
            "c": [90.0, 101.0],
            "reg_lower": [80.0, 80.0],
            "reg_upper": [120.0, 120.0],
            "reg_mid": [100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # Short exit: close crosses below the midline.
        rows = pd.DataFrame({
            "c": [110.0, 99.0],
            "reg_lower": [80.0, 80.0],
            "reg_upper": [120.0, 120.0],
            "reg_mid": [100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Close exactly on the midline is not a cross.
        rows = pd.DataFrame({
            "c": [90.0, 100.0],
            "reg_lower": [80.0, 80.0],
            "reg_upper": [120.0, 120.0],
            "reg_mid": [100.0, 100.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # NaN bands (warmup): no entry, no exit.
        rows = pd.DataFrame({
            "c": [90.0, 110.0],
            "reg_lower": [np.nan, np.nan],
            "reg_upper": [np.nan, np.nan],
            "reg_mid": [np.nan, np.nan],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_long_entry_on_dip_and_revert(self):
        # End-to-end: flat at 100, a dip to 80 (below the lower band),
        # then a revert to 99 — the revert bar crosses back above the
        # lower band and fires a long entry.
        n = 200
        closes = np.full(n, 100.0)
        closes[150:160] = 80.0
        closes[160:] = 99.0
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[160])
        self.assertFalse(df["long_entry"].iloc[:160].any())

    def test_no_signal_on_flat(self):
        # Flat closes: regression line is flat, residual std is 0, so
        # the bands coincide with the close and no cross can fire.
        df = _run(_flat_frame())
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

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("reg_mid", "reg_upper", "reg_lower", "reg_slope",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the 100-bar lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): no crash, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
