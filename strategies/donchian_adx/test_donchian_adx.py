"""Donchian ADX tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian_adx import indicators, risk, signals
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

class TestDonchianAdx(unittest.TestCase):
    def test_registered(self):
        self.assertIn("donchian_adx", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_donchian_hand_computed(self):
        # Hand-built highs/lows: the 20-bar high at bar 19 is the max
        # of h[0..19] and the 20-bar low is the min of l[0..19].
        rng = np.random.default_rng(5)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 60)))
        highs = closes + rng.uniform(0.1, 1.0, 60)
        lows = closes - rng.uniform(0.1, 1.0, 60)
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertTrue(np.isnan(df["donchian_high_20"].iloc[18]))
        self.assertAlmostEqual(df["donchian_high_20"].iloc[19],
                               highs[:20].max(), places=9)
        self.assertAlmostEqual(df["donchian_low_20"].iloc[19],
                               lows[:20].min(), places=9)
        self.assertAlmostEqual(df["donchian_mid_20"].iloc[19],
                               (highs[:20].max() + lows[:20].min()) / 2,
                               places=9)
        # Window slides: at bar 20 the window is bars 1..20.
        self.assertAlmostEqual(df["donchian_high_20"].iloc[20],
                               highs[1:21].max(), places=9)

    def test_adx_flat_nan_and_trend_strong(self):
        # Flat price: no directional movement, ATR is zero, so ADX is
        # NaN everywhere (0/0 in the DI computation).
        df = indicators.add_indicators(_flat_frame(n=300))
        self.assertTrue(df["adx"].iloc[risk.WARMUP:].isna().all())
        # Steady +1%/bar trend: directional movement dominates, ADX
        # climbs well above 25 and +DI stays above -DI.
        n = 300
        closes = 100.0 * 1.01 ** np.arange(n)
        df = indicators.add_indicators(_frame(closes))
        self.assertGreater(df["adx"].iloc[-1], 25.0)
        self.assertTrue((df["plus_di"].iloc[-50:] > df["minus_di"].iloc[-50:]).all())

    def test_long_entry_on_breakout_with_trend(self):
        # Flat base, then a steady +1%/bar rise: the Donchian breakout
        # fires while ADX is above 25, so a long entry must appear.
        n_flat, n_rise = 40, 150
        closes = np.concatenate([np.full(n_flat, 100.0),
                                 100.0 * 1.01 ** np.arange(1, n_rise + 1)])
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[n_flat:].any())
        self.assertFalse(df["short_entry"].iloc[n_flat:n_flat + n_rise].any())

    def test_signal_logic_crafted_rows(self):
        # Two-row frames: row 0 sets the prior channel, row 1 is the
        # breakout bar. ADX 30 clears the entry filter.
        rows = [dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=30.0),
                dict(c=111.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=30.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        rows = [dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=30.0),
                dict(c=89.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=30.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        # Breakout up but ADX 20 (no trend): no entry.
        rows = [dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=20.0),
                dict(c=111.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=20.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # No breakout even with strong ADX: no entry.
        rows = [dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=30.0),
                dict(c=105.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=30.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # ADX below 20 with no breakout: both exits fire (trend death).
        rows = [dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=15.0),
                dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=15.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        # ADX exactly 25 is not > 25: no entry.
        rows = [dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=25.0),
                dict(c=111.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=25.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # NaN ADX (warmup): no entry, no exit.
        rows = [dict(c=100.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=np.nan),
                dict(c=111.0, donchian_high_20=110.0, donchian_low_20=90.0, adx=np.nan)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
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
        for col in ("donchian_high_20", "donchian_low_20", "adx",
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
        # Zero-range bars (h == l == c): channel equals the price,
        # ADX is NaN, no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["donchian_high_20"], 100.0, atol=1e-9))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
