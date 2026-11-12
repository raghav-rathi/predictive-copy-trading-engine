"""Donchian + RSI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian_rsi import indicators, risk, signals
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


class TestDonchianRsi(unittest.TestCase):
    def test_registered(self):
        self.assertIn("donchian_rsi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_donchian_levels_hand_computed(self):
        # Flat bars with h=101, l=99: after 20 bars the channel is
        # exactly 101/99 (prior 20 bars, current bar excluded).
        df = indicators.add_indicators(_flat_frame(n=100))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["don_high20"], 101.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["don_low20"], 99.0, atol=1e-9))
        # NaN before 20 prior bars exist.
        self.assertTrue(df["don_high20"].iloc[:20].isna().all())
        self.assertTrue(np.isfinite(df["don_high20"].iloc[20]))

    def test_donchian_excludes_current_bar(self):
        # A single spike bar must NOT raise the channel on its own bar:
        # the level on the spike bar still reflects the prior 20 bars.
        n = 100
        closes = np.full(n, 100.0)
        highs = np.full(n, 101.0)
        highs[60] = 130.0
        closes[60] = 115.0
        df = indicators.add_indicators(
            _frame(closes, highs=highs, lows=np.full(n, 99.0)))
        self.assertEqual(df["don_high20"].iloc[60], 101.0)
        # But the NEXT bar sees the spike in its lookback window, and
        # it stays in the window through bar 80 (window 60..79).
        self.assertEqual(df["don_high20"].iloc[61], 130.0)
        self.assertEqual(df["don_high20"].iloc[80], 130.0)
        # At bar 81 the window is 61..80 and the spike drops out.
        self.assertEqual(df["don_high20"].iloc[81], 101.0)

    def test_long_entry_on_breakout_with_rsi(self):
        # Flat at 100, then a jump to 115: close clears the prior
        # 20-bar high (101) and RSI(14) jumps above 55 on the gains.
        n = 80
        closes = np.full(n, 100.0)
        closes[60] = 115.0
        closes[61:] = 115.0
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[60])
        self.assertFalse(df["long_entry"].iloc[:60].any())
        self.assertFalse(df["short_entry"].iloc[60])
        # Mirror: a jump down to 85 fires a short entry.
        closes = np.full(n, 100.0)
        closes[60] = 85.0
        closes[61:] = 85.0
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].iloc[60])
        self.assertFalse(df["long_entry"].iloc[60])

    def test_rsi_confirmation_blocks_breakout(self):
        # Crafted rows: a breakout with RSI 50 (below 55) is NOT a
        # long; with RSI 55 exactly it is not either (strict >).
        rows = pd.DataFrame({
            "c": [105.0, 105.0, 105.0],
            "don_high20": [100.0, 100.0, 100.0],
            "don_low20": [90.0, 90.0, 90.0],
            "rsi": [50.0, 55.0, 56.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertTrue(df["long_entry"].iloc[2])
        # Mirror on the short side: RSI 50 / 45 / 44.
        rows = pd.DataFrame({
            "c": [85.0, 85.0, 85.0],
            "don_high20": [100.0, 100.0, 100.0],
            "don_low20": [90.0, 90.0, 90.0],
            "rsi": [50.0, 45.0, 44.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertTrue(df["short_entry"].iloc[2])

    def test_exits_on_opposite_breakout(self):
        # A close below the prior 20-bar low exits a long (and is a
        # short entry only if RSI < 45 — here RSI 50, so exit only).
        rows = pd.DataFrame({
            "c": [95.0, 85.0, 105.0],
            "don_high20": [100.0, 100.0, 100.0],
            "don_low20": [90.0, 90.0, 90.0],
            "rsi": [50.0, 50.0, 50.0],
        })
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[2])
        # Close exactly on the channel edge is not a breakout.
        rows = pd.DataFrame({
            "c": [100.0, 90.0],
            "don_high20": [100.0, 100.0],
            "don_low20": [90.0, 90.0],
            "rsi": [60.0, 40.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[1])
        # NaN channel levels (warmup): no entry, no exit.
        rows = pd.DataFrame({
            "c": [105.0, 85.0],
            "don_high20": [np.nan, np.nan],
            "don_low20": [np.nan, np.nan],
            "rsi": [60.0, 40.0],
        })
        df = signals.add_signals(rows)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_entry_on_small_move(self):
        # A +0.5 move off a flat base does not clear the 101 high.
        n = 80
        closes = np.full(n, 100.0)
        closes[60] = 100.5
        closes[61:] = 100.5
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].iloc[60])
        self.assertFalse(df["short_entry"].iloc[60])

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
        for col in ("don_high20", "don_low20", "rsi",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): channel equals the close, so
        # no strict breakout is possible.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
