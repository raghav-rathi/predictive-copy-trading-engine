"""Judas swing tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.judas_swing import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

BASE_MS = int(pd.Timestamp("2026-01-04 20:00", tz="UTC").timestamp() * 1000)


def _bars(specs):
    """specs: list of (o, h, l, c) in hourly order from BASE_MS."""
    n = len(specs)
    arr = np.array(specs, dtype=float)
    return pd.DataFrame({
        "t": (BASE_MS + np.arange(n) * 3_600_000).astype("int64"),
        "o": arr[:, 0], "h": arr[:, 1], "l": arr[:, 2], "c": arr[:, 3],
        "v": np.full(n, 100.0),
    })


def _evening():
    """Four evening bars (20:00-23:00 Jan 4): Asian range 110 / 100."""
    return [(105, 110, 100, 105)] * 4


def _flat_night(n=7):
    return [(105, 106, 104, 105)] * n


def _bull_frame():
    """Bullish Judas: sweep 98 below Asian low 100 at 07:00 with a
    reclaim close 102 the same bar; 08:00 high 108; 09:00 close 109
    above it -> long trigger at 09:00 (bar index 13)."""
    return _bars(_evening() + _flat_night(7) + [
        (102, 106, 98, 102),    # 07:00 sweep + reclaim
        (107, 108, 101, 107),   # 08:00
        (109, 110, 106, 109),   # 09:00 trigger
        (115, 116, 110, 115),   # 10:00 (must not re-fire)
        (115, 116, 112, 115),   # 11:00
        (115, 116, 112, 115),   # 12:00
    ])


def _bear_frame():
    """Mirror of _bull_frame reflected about 200: short trigger at 09:00."""
    df = _bull_frame()
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


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


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": close, "h": hi, "l": lo,
                         "c": close, "v": np.full(n, vol)})


class TestJudasSwing(unittest.TestCase):
    def test_registered(self):
        self.assertIn("judas_swing", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_asian_range_from_prior_evening(self):
        df = indicators.add_indicators(_bull_frame())
        # No range on the evening bars themselves (prior evening unknown).
        self.assertTrue(np.isnan(df["asian_low"].iloc[0]))
        # From 00:00 Jan 5 the prior evening's range is known.
        self.assertAlmostEqual(df["asian_low"].iloc[4], 100.0)
        self.assertAlmostEqual(df["asian_high"].iloc[4], 110.0)

    def test_bull_long_trigger(self):
        df = _run(_bull_frame())
        self.assertFalse(df["long_entry"].iloc[:13].any())
        self.assertTrue(df["long_entry"].iloc[13])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].any())
        self.assertEqual(df["judas_state"].iloc[11], 1)  # swept (reclaim checked from next bar)
        self.assertEqual(df["judas_state"].iloc[12], 2)  # reclaimed

    def test_bear_short_trigger_on_mirrored_frame(self):
        df = _run(_bear_frame())
        self.assertFalse(df["short_entry"].iloc[:13].any())
        self.assertTrue(df["short_entry"].iloc[13])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_without_sweep(self):
        # 07:00 low 101 never goes below the Asian low 100.
        df = _run(_bars(_evening() + _flat_night(7) + [
            (105, 106, 101, 105),
            (107, 108, 101, 107),
            (109, 110, 106, 109),
            (115, 116, 110, 115),
        ]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_reclaim(self):
        # Sweep below 100 at 07:00 but closes stay below 100: no reclaim.
        df = _run(_bars(_evening() + _flat_night(7) + [
            (99, 101, 98, 99),    # 07:00 sweep, close 99 < 100
            (99, 100, 97, 99),    # 08:00 still below
            (101, 102, 98, 99),   # 09:00 close still below 100
            (102, 108, 99, 102),  # 10:00 reclaim, but no later shift bar
            (102, 103, 100, 102), # 11:00 close 102 < 108 since-high
        ]))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_after_noon_deadline(self):
        # Sweep + reclaim early, but the shift close only comes at 12:00.
        df = _run(_bars(_evening() + _flat_night(7) + [
            (102, 106, 98, 102),   # 07:00 sweep + reclaim
            (107, 108, 101, 107),  # 08:00 sets since-high 108
            (107, 108, 104, 107),  # 09:00 close 107 <= 108
            (107, 108, 104, 107),  # 10:00
            (108, 108, 104, 108),  # 11:00 close 108, not above 108
            (109, 110, 106, 109),  # 12:00 shift, but past the deadline
        ]))
        self.assertFalse(df["long_entry"].any())

    def test_exit_long_on_sweep_invalidation(self):
        rows = pd.DataFrame([dict(
            c=97.0, long_trigger=False, short_trigger=False,
            last_bull_sweep_low=98.0, last_bear_sweep_high=112.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=105.0, long_trigger=False, short_trigger=True,
            last_bull_sweep_low=98.0, last_bear_sweep_high=112.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(
            c=113.0, long_trigger=False, short_trigger=False,
            last_bull_sweep_low=98.0, last_bear_sweep_high=112.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
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
        df1 = _run(_bars([(c, c + 0.5, c - 0.5, c) for c in closes]))
        df2 = _run(_bars([(c, c + 0.5, c - 0.5, c) for c in closes]
                         + [(c + 300.0, c + 300.5, c + 299.5, c + 300.0)
                            for c in closes[-50:]]))
        for col in ("asian_low", "judas_state", "long_entry",
                    "short_entry", "long_exit"):
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
