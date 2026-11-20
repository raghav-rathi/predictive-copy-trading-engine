"""Bollinger Bands %b mean-reversion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_reversion import indicators, risk, signals
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


def _dip_frame():
    """Flat 100 for 25 bars, dip to 90 for 3 bars, back to 100."""
    closes = [100.0] * 25 + [90.0] * 3 + [100.0] * 5
    return _frame(closes)


def _spike_frame():
    """Flat 100 for 25 bars, spike to 110 for 3 bars, back to 100."""
    closes = [100.0] * 25 + [110.0] * 3 + [100.0] * 5
    return _frame(closes)


class TestBollingerReversion(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bollinger_reversion", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_band_math_on_known_series(self):
        # Closes 100..119: SMA(20) = 109.5, sample std = sqrt(665/19).
        closes = list(range(100, 120))
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["bb_mid"].iloc[19], 109.5)
        self.assertAlmostEqual(df["bb_upper"].iloc[19],
                               109.5 + 2 * float(np.std(closes, ddof=1)))
        self.assertAlmostEqual(df["bb_lower"].iloc[19],
                               109.5 - 2 * float(np.std(closes, ddof=1)))
        self.assertAlmostEqual(df["bb_width"].iloc[19],
                               df["bb_upper"].iloc[19] - df["bb_lower"].iloc[19])

    def test_warmup_nans(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertTrue(df["bb_mid"].iloc[:19].isna().all())
        self.assertFalse(np.isnan(df["bb_mid"].iloc[19]))
        self.assertTrue(df["pct_b"].iloc[:19].isna().all())

    def test_flat_price_zero_width(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["bb_mid"].iloc[19], 100.0)
        self.assertAlmostEqual(df["bb_width"].iloc[19], 0.0)
        self.assertTrue(np.isnan(df["pct_b"].iloc[19]))

    def test_pct_b_formula(self):
        df = indicators.add_indicators(_random_walk_frame())
        valid = df["bb_width"] > 0
        expect = (df["c"] - df["bb_lower"]) / df["bb_width"]
        pd.testing.assert_series_equal(
            df.loc[valid, "pct_b"], expect[valid], check_names=False)

    def test_long_entry_on_lower_band_tag(self):
        df = _run(_dip_frame())
        self.assertFalse(df["long_entry"].iloc[:25].any())
        self.assertTrue(df["long_entry"].iloc[25])
        self.assertTrue(df["long_entry"].iloc[26])
        self.assertTrue(df["long_entry"].iloc[27])
        # %b <= 0 on the tag bars.
        self.assertTrue((df["pct_b"].iloc[25:28] <= 0).all())

    def test_short_entry_on_upper_band_tag(self):
        df = _run(_spike_frame())
        self.assertFalse(df["short_entry"].iloc[:25].any())
        self.assertTrue(df["short_entry"].iloc[25])
        self.assertTrue((df["pct_b"].iloc[25:28] >= 1).all())

    def test_long_exit_on_close_back_to_mid(self):
        df = _run(_dip_frame())
        # Close returns to 100 at bar 28; mid is ~98.5 there, so the
        # exit fires on bar 28.
        self.assertTrue(df["long_exit"].iloc[28])
        self.assertFalse(df["long_exit"].iloc[25])

    def test_short_exit_on_close_back_to_mid(self):
        df = _run(_spike_frame())
        self.assertTrue(df["short_exit"].iloc[28])
        self.assertFalse(df["short_exit"].iloc[25])

    def test_no_entry_on_flat_frame(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_entry_and_exit_never_coincide(self):
        df = _run(_random_walk_frame())
        self.assertFalse((df["long_entry"] & df["long_exit"]).any())
        self.assertFalse((df["short_entry"] & df["short_exit"]).any())

    def test_exit_columns_direct(self):
        rows = pd.DataFrame([dict(c=100.0, bb_mid=99.0, bb_lower=97.0, bb_upper=101.0),
                             dict(c=98.0, bb_mid=99.0, bb_lower=97.0, bb_upper=101.0),
                             dict(c=102.0, bb_mid=99.0, bb_lower=97.0, bb_upper=101.0)])
        df = signals.add_signals(rows)
        # c == mid is not a tag, but it IS the long exit (c >= mid).
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertTrue(df["short_entry"].iloc[2])

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
        self.assertEqual(risk.WARMUP, 40)

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
        self.assertGreater(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("bb_mid", "bb_upper", "bb_lower", "pct_b",
                    "long_entry", "short_entry", "long_exit"):
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
