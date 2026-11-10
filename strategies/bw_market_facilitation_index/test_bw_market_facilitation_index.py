"""Bill Williams Market Facilitation Index squat breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bw_market_facilitation_index import indicators, risk, signals
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


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(closes, highs, lows, bar_types, ema20):
    """Frame with precomputed indicator columns, for pure signal tests."""
    n = len(closes)
    return pd.DataFrame({
        "c": np.array(closes, dtype=float),
        "h": np.array(highs, dtype=float),
        "l": np.array(lows, dtype=float),
        "bar_type": np.array(bar_types, dtype=object),
        "ema20": np.array(ema20, dtype=float),
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestBwMarketFacilitationIndex(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bw_market_facilitation_index", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_mfi_hand_computed(self):
        # bar0: (110-100)/10 = 1.0, no previous bar -> "none"
        # bar1: (112-100)/20 = 0.6 (MFI down), vol 10->20 up -> "squat"
        # bar2: (105-100)/5  = 1.0 (MFI up),   vol 20->5 down -> "fake"
        # bar3: (104-100)/4  = 1.0 (MFI flat -> not up), vol down -> "fade"
        # bar4: (110-100)/10 = 1.0 (MFI flat -> not up), vol 4->10 up -> "squat"
        df = indicators.add_indicators(_frame(
            [105, 106, 103, 102, 108],
            highs=[110, 112, 105, 104, 110],
            lows=[100, 100, 100, 100, 100],
            vols=[10, 20, 5, 4, 10],
        ))
        self.assertTrue(np.allclose(df["bw_mfi"], [1.0, 0.6, 1.0, 1.0, 1.0]))
        self.assertEqual(list(df["bar_type"]),
                         ["none", "squat", "fake", "fade", "squat"])

    def test_mfi_green_and_zero_volume(self):
        # bar1: MFI (112-100)/11 = 1.0909 up from 1.0, vol 10->11 up -> "green"
        # bar2: volume 0 -> MFI guarded to 0.0 (no inf/nan)
        df = indicators.add_indicators(_frame(
            [105, 106, 107],
            highs=[110, 112, 112],
            lows=[100, 100, 100],
            vols=[10, 11, 0],
        ))
        # bar0 MFI = 10/10 = 1.0; bar1 = 12/11
        self.assertAlmostEqual(df["bw_mfi"].iloc[0], 1.0)
        self.assertAlmostEqual(df["bw_mfi"].iloc[1], 12 / 11)
        self.assertEqual(df["bar_type"].iloc[1], "green")
        self.assertEqual(df["bw_mfi"].iloc[2], 0.0)
        self.assertTrue(np.isfinite(df["bw_mfi"]).all())

    def test_ema20_flat(self):
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["ema20"], 100.0, atol=1e-9))
        self.assertTrue(np.isfinite(tail["ema20"]).all())
        # First 19 bars are NaN (min_periods=20).
        self.assertTrue(df["ema20"].iloc[:19].isna().all())

    def test_long_entry_squat_breakout(self):
        # Squat at bar 2 (high 110, low 100). Bar 3 closes 105 (no
        # breakout), bar 4 closes 111 above the squat high and above
        # EMA(20)=100 -> long entry at bar 4 only.
        df = signals.add_signals(_signal_frame(
            closes=[100, 100, 105, 105, 111, 112],
            highs=[101, 101, 110, 106, 112, 113],
            lows=[99, 99, 100, 104, 110, 111],
            bar_types=["none", "none", "squat", "none", "none", "none"],
            ema20=[100.0] * 6,
        ))
        self.assertFalse(df["long_entry"].iloc[:4].any())
        self.assertTrue(df["long_entry"].iloc[4])
        # Bar 5 is still inside the 5-bar window and still breaks the
        # squat high, so the signal stays on; the harness takes only
        # the first while flat (one position at a time).
        self.assertTrue(df["long_entry"].iloc[5])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_squat_breakout(self):
        # Squat at bar 2 (high 110, low 100). Bar 4 closes 99 below the
        # squat low and below EMA(20)=100 -> short entry at bar 4.
        df = signals.add_signals(_signal_frame(
            closes=[100, 100, 105, 101, 99, 98],
            highs=[101, 101, 110, 102, 100, 99],
            lows=[99, 99, 100, 100, 98, 97],
            bar_types=["none", "none", "squat", "none", "none", "none"],
            ema20=[100.0] * 6,
        ))
        self.assertTrue(df["short_entry"].iloc[4])
        self.assertFalse(df["short_entry"].iloc[:4].any())
        self.assertFalse(df["long_entry"].any())

    def test_ema_filter_blocks_entry(self):
        # Close 111 breaks the squat high (110) but sits below
        # EMA(20)=115 -> no long entry. Same bar below EMA would
        # not be a short either (close is above the squat low).
        df = signals.add_signals(_signal_frame(
            closes=[100, 100, 105, 111],
            highs=[101, 101, 110, 112],
            lows=[99, 99, 100, 110],
            bar_types=["none", "none", "squat", "none"],
            ema20=[115.0] * 4,
        ))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_squat_window_expiry(self):
        # Squat at bar 2; breakout close arrives at bar 8 (age 6,
        # outside the 5-bar window) -> no entry.
        df = signals.add_signals(_signal_frame(
            closes=[100, 100, 105, 105, 105, 105, 105, 105, 111],
            highs=[101, 101, 110, 106, 106, 106, 106, 106, 112],
            lows=[99, 99, 100, 104, 104, 104, 104, 104, 110],
            bar_types=["none", "none", "squat", "none", "none",
                       "none", "none", "none", "none"],
            ema20=[100.0] * 9,
        ))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_newer_squat_replaces(self):
        # Squat A at bar 2 (high 110), squat B at bar 4 (high 120,
        # low 105). Bar 5 closes 115: above A's high but below B's
        # high -> no entry. Bar 6 closes 121 above B's high -> entry.
        df = signals.add_signals(_signal_frame(
            closes=[100, 100, 105, 106, 108, 115, 121],
            highs=[101, 101, 110, 107, 120, 116, 122],
            lows=[99, 99, 100, 105, 105, 114, 120],
            bar_types=["none", "none", "squat", "none", "squat",
                       "none", "none"],
            ema20=[100.0] * 7,
        ))
        self.assertFalse(df["long_entry"].iloc[:6].any())
        self.assertTrue(df["long_entry"].iloc[6])

    def test_exits(self):
        # FADE bar exits both sides; a close below EMA(20) exits a
        # long but not a short; a close above EMA(20) exits a short.
        df = signals.add_signals(_signal_frame(
            closes=[100, 100, 100, 99, 101],
            highs=[101, 101, 101, 100, 102],
            lows=[99, 99, 99, 98, 100],
            bar_types=["none", "none", "fade", "none", "none"],
            ema20=[100.0, 100.0, 100.0, 100.0, 100.0],
        ))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[3])   # close 99 < EMA 100
        self.assertFalse(df["short_exit"].iloc[3])
        self.assertTrue(df["short_exit"].iloc[4])  # close 101 > EMA 100
        self.assertFalse(df["long_exit"].iloc[4])

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
        self.assertEqual(signals.SQUAT_WINDOW, 5)
        self.assertEqual(indicators.EMA_PERIOD, 20)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("net_pnl_usd", m)
        self.assertIn("sharpe", m)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("bw_mfi", "bar_type", "ema20", "long_entry", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the EMA warmup: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c, volume 0): MFI is 0, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200, vols=[0.0] * 200))
        self.assertTrue((df["bw_mfi"] == 0.0).all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
