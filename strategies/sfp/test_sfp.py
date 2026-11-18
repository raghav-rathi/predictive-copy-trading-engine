"""Swing Failure Pattern (SFP) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sfp import indicators, risk, signals
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


def _sfp_bull_frame():
    """20 flat bars, swing low 97 at centre 22 (confirms bar 24),
    then bar 25 sweeps to 96 and closes back at 98 on a volume
    spike -> bullish SFP."""
    closes = [100.0] * 25 + [98.0]
    highs = [101.0] * 25 + [100.0]
    lows = [99.0] * 20 + [99.0, 98.0, 97.0, 98.0, 99.0] + [96.0]
    vols = [100.0] * 25 + [300.0]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


def _sfp_bear_frame():
    """Mirror: swing high 103 at centre 22 (confirms bar 24), then
    bar 25 sweeps to 104 and closes back at 102 on a volume spike
    -> bearish SFP."""
    closes = [100.0] * 25 + [102.0]
    highs = [101.0] * 20 + [101.0, 102.0, 103.0, 102.0, 101.0] + [104.0]
    lows = [99.0] * 25 + [100.0]
    vols = [100.0] * 25 + [300.0]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


class TestSfp(unittest.TestCase):
    def test_registered(self):
        self.assertIn("sfp", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_swing_low_confirms_at_centre_plus_two(self):
        df = indicators.add_indicators(_sfp_bull_frame())
        # Not recorded at the centre bar (22) nor the bar after (23).
        self.assertTrue(np.isnan(df["swing_low"].iloc[22]))
        self.assertTrue(np.isnan(df["swing_low"].iloc[23]))
        # Recorded at the confirmation bar (24) and forward-filled.
        self.assertAlmostEqual(df["swing_low"].iloc[24], 97.0)
        self.assertAlmostEqual(df["swing_low"].iloc[25], 97.0)

    def test_swing_high_confirms_at_centre_plus_two(self):
        df = indicators.add_indicators(_sfp_bear_frame())
        self.assertTrue(np.isnan(df["swing_high"].iloc[22]))
        self.assertTrue(np.isnan(df["swing_high"].iloc[23]))
        self.assertAlmostEqual(df["swing_high"].iloc[24], 103.0)
        self.assertAlmostEqual(df["swing_high"].iloc[25], 103.0)

    def test_bullish_sfp_long_entry(self):
        df = _run(_sfp_bull_frame())
        self.assertTrue(df["long_entry"].iloc[25])
        self.assertFalse(df["short_entry"].iloc[25])
        self.assertFalse(df["long_entry"].iloc[24])

    def test_bearish_sfp_short_entry(self):
        df = _run(_sfp_bear_frame())
        self.assertTrue(df["short_entry"].iloc[25])
        self.assertFalse(df["long_entry"].iloc[25])

    def test_no_entry_without_volume_spike(self):
        df = _sfp_bull_frame()
        df.loc[25, "v"] = 100.0
        out = _run(df)
        self.assertFalse(out["long_entry"].iloc[25])

    def test_no_entry_without_reclaim(self):
        # Sweeps below 97 but closes below it too -> no reclaim.
        df = _sfp_bull_frame()
        df.loc[25, "c"] = 96.0
        df.loc[25, "l"] = 95.0
        out = _run(df)
        self.assertFalse(out["long_entry"].iloc[25])

    def test_no_entry_without_sweep(self):
        # Low stays above the swing low -> no sweep.
        df = _sfp_bull_frame()
        df.loc[25, "l"] = 98.0
        df.loc[25, "c"] = 100.0
        out = _run(df)
        self.assertFalse(out["long_entry"].iloc[25])

    def test_signal_logic_crafted_rows(self):
        # Two rows: row 0 carries the level, row 1 is the signal bar
        # (signals read the level as of bar i-1).
        base = dict(l=100.0, c=100.0, h=101.0, v=100.0, vol_ma20=100.0,
                    swing_low=97.0, swing_high=103.0)
        rows = pd.DataFrame([
            base,
            dict(l=96.0, c=98.0, h=100.0, v=300.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        rows = pd.DataFrame([
            base,
            dict(l=100.0, c=102.0, h=104.0, v=300.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])

    def test_exit_long_on_close_below_swept_level(self):
        rows = pd.DataFrame([
            dict(l=100.0, c=100.0, h=101.0, v=100.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
            dict(l=95.0, c=96.0, h=97.0, v=100.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])

    def test_exit_long_on_bearish_sfp(self):
        rows = pd.DataFrame([
            dict(l=100.0, c=100.0, h=101.0, v=100.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
            dict(l=100.0, c=102.0, h=104.0, v=300.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[1])   # bearish SFP prints
        self.assertTrue(df["short_entry"].iloc[1])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([
            dict(l=100.0, c=100.0, h=101.0, v=100.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
            dict(l=96.0, c=98.0, h=100.0, v=300.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
        ])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[1])  # bullish SFP prints
        rows2 = pd.DataFrame([
            dict(l=100.0, c=100.0, h=101.0, v=100.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
            dict(l=100.0, c=104.0, h=105.0, v=100.0, vol_ma20=100.0,
                 swing_low=97.0, swing_high=103.0),
        ])
        df2 = signals.add_signals(rows2)
        self.assertTrue(df2["short_exit"].iloc[1])  # close above high
        self.assertFalse(df2["long_exit"].iloc[1])

    def test_vol_ma20_value(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertTrue(df["vol_ma20"].iloc[:19].isna().all())
        self.assertAlmostEqual(df["vol_ma20"].iloc[25], 100.0)

    def test_atr_positive(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue((df["atr"].dropna() > 0).all())

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
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("swing_high", "swing_low", "vol_ma20",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["swing_low"].isna().all())


if __name__ == "__main__":
    unittest.main()
