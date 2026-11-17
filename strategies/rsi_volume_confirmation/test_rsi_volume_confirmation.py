"""RSI Volume Confirmation tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_volume_confirmation import indicators, risk, signals
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


def _rsi_cross_frame():
    """Falling closes then rising closes: RSI crosses below 50 on the
    way down and above 50 on the way up. Volume spikes on the cross bars."""
    downs = [100.0 - i for i in range(30)]          # 100 .. 71
    ups = [71.0 + i for i in range(30)]             # 71 .. 100
    closes = downs + ups
    vols = [100.0] * len(closes)
    vols[30:] = [200.0] * (len(closes) - 30)  # spikes on all rising bars,
    # so whichever bar RSI crosses 50 on carries volume confirmation
    return _frame(closes, vols=vols)


class TestRsiVolumeConfirmation(unittest.TestCase):
    def test_registered(self):
        self.assertIn("rsi_volume_confirmation", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_rsi_flat_is_zero(self):
        # No gains and no losses: Wilder RSI resolves to 0 in base.rsi.
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["rsi"].iloc[-1], 0.0)

    def test_rsi_rising_above_50(self):
        closes = [100.0 + i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertGreater(df["rsi"].iloc[-1], 50.0)

    def test_rsi_falling_below_50(self):
        closes = [200.0 - i for i in range(100)]
        df = indicators.add_indicators(_frame(closes))
        self.assertLess(df["rsi"].iloc[-1], 50.0)

    def test_vol_ratio_exact(self):
        # 20 bars vol 100, then a 150-vol bar: ratio 1.5 vs prev-20 mean.
        df = indicators.add_indicators(_frame(
            [100.0] * 21, vols=[100.0] * 20 + [150.0]))
        self.assertAlmostEqual(df["vol_mean_20"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 1.5)

    def test_vol_mean_excludes_current_bar(self):
        # A 1000-vol bar must not raise its own comparison mean.
        df = indicators.add_indicators(_frame(
            [100.0] * 21, vols=[100.0] * 20 + [1000.0]))
        self.assertAlmostEqual(df["vol_mean_20"].iloc[-1], 100.0)
        self.assertAlmostEqual(df["vol_ratio"].iloc[-1], 10.0)

    def test_signal_logic_crafted_rows(self):
        # RSI cross above 50 + volume spike -> long entry only.
        rows = pd.DataFrame([
            dict(rsi=49.0, vol_ratio=1.5),
            dict(rsi=51.0, vol_ratio=1.5),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # RSI cross below 50 + volume spike -> short entry only.
        rows = pd.DataFrame([
            dict(rsi=51.0, vol_ratio=1.5),
            dict(rsi=49.0, vol_ratio=1.5),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_volume_threshold_strict(self):
        # RSI cross above 50 but vol ratio exactly 1.25: no entry.
        rows = pd.DataFrame([
            dict(rsi=49.0, vol_ratio=1.25),
            dict(rsi=51.0, vol_ratio=1.25),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])

    def test_no_entry_without_volume(self):
        rows = pd.DataFrame([
            dict(rsi=49.0, vol_ratio=1.0),
            dict(rsi=51.0, vol_ratio=1.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])

    def test_no_entry_without_cross(self):
        # RSI already above 50 and rising: no cross, no entry.
        rows = pd.DataFrame([
            dict(rsi=51.0, vol_ratio=2.0),
            dict(rsi=52.0, vol_ratio=2.0),
        ])
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_exit_on_reverse_cross(self):
        rows = pd.DataFrame([
            dict(rsi=51.0, vol_ratio=1.5),
            dict(rsi=49.0, vol_ratio=1.5),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertTrue(df["short_entry"].iloc[1])
        rows = pd.DataFrame([
            dict(rsi=49.0, vol_ratio=1.0),
            dict(rsi=51.0, vol_ratio=1.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[1])

    def test_entries_fire_on_v_shape(self):
        # V-shaped closes: RSI crosses below 50 on the fall and above
        # 50 on the rise; at least one of the two crossings carries a
        # volume spike in the crafted frame.
        df = _run(_rsi_cross_frame())
        self.assertTrue(df["long_entry"].any() or df["short_entry"].any())

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
        # Flat closes: RSI 0, never crosses 50; no entries.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("rsi", "vol_ratio", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
