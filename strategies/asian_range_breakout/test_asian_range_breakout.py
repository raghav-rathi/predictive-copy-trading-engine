"""Asian-range breakout tests. Network-free, synthetic data only.

Timestamps are aligned to UTC hours, starting at 2026-01-01
00:00 UTC (1767225600000 ms), so hour/day derivation in the
strategy matches the constructed session layout.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.asian_range_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

BASE_MS = 1_767_225_600_000  # 2026-01-01 00:00 UTC


def _day_frame(days):
    """days: list of per-day bar dicts; each day is 24 hourly bars
    given as (close, high, low, volume) for hours 0..23, or a
    callable hour -> tuple. Returns a DataFrame."""
    rows = []
    for d, day in enumerate(days):
        for hr in range(24):
            c, h, l, v = day(hr) if callable(day) else day[hr]
            rows.append((BASE_MS + (d * 24 + hr) * 3_600_000, c, c, h, l, c, v))
    arr_t = np.array([r[0] for r in rows], dtype=np.int64)
    return pd.DataFrame({
        "t": arr_t,
        "o": np.array([r[1] for r in rows], dtype=float),
        "h": np.array([r[3] for r in rows], dtype=float),
        "l": np.array([r[4] for r in rows], dtype=float),
        "c": np.array([r[5] for r in rows], dtype=float),
        "v": np.array([r[6] for r in rows], dtype=float),
    })


def _flat_day():
    # Asian range 99-101, rest of day flat at 100, volume 100.
    return lambda hr: (100, 101, 99, 100.0) if hr < 8 else (100, 101, 99, 100.0)


def _breakout_day(direction):
    def day(hr):
        if hr < 8:
            return (100, 101, 99, 100.0)
        if hr == 8:
            if direction == "long":
                return (103, 103, 102, 200.0)  # close > 101, vol > avg
            return (97, 98, 97, 200.0)  # close < 99, vol > avg
        if hr < 16:
            return (103, 104, 102, 200.0) if direction == "long" else (97, 98, 96, 200.0)
        return (100, 101, 99, 100.0)
    return day


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (BASE_MS + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


class TestAsianRangeBreakout(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("asian_high", "asian_low", "vol_avg20", "atr"):
            self.assertIn(col, df.columns)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["asian_high"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["asian_low"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["breakout_dir"].isna().any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_breakout(self):
        df = _run(_day_frame([_flat_day(), _breakout_day("long")]))
        idx = 24 + 8  # day 2, 08:00 UTC bar
        self.assertEqual(df["asian_high"].iloc[idx], 101)
        self.assertEqual(df["breakout_dir"].iloc[idx], 1)
        self.assertTrue(df["long_entry"].iloc[idx])
        self.assertFalse(df["short_entry"].any())

    def test_short_breakout(self):
        df = _run(_day_frame([_flat_day(), _breakout_day("short")]))
        idx = 24 + 8
        self.assertEqual(df["asian_low"].iloc[idx], 99)
        self.assertEqual(df["breakout_dir"].iloc[idx], -1)
        self.assertTrue(df["short_entry"].iloc[idx])
        self.assertFalse(df["long_entry"].any())

    def test_low_volume_blocks_breakout(self):
        def day(hr):
            if hr < 8:
                return (100, 101, 99, 100.0)
            if hr == 8:
                return (103, 103, 102, 50.0)  # breaks range, vol < avg
            return (100, 101, 99, 100.0)
        df = _run(_day_frame([_flat_day(), day]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_time_exit_at_16(self):
        df = _run(_day_frame([_flat_day(), _breakout_day("long")]))
        self.assertTrue(df["long_entry"].iloc[24 + 8])
        self.assertTrue(df["long_exit"].iloc[24 + 16])
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_one_entry_per_day_next_day_reenters(self):
        df = _run(_day_frame([_flat_day(), _breakout_day("long"),
                              _breakout_day("long")]))
        # One entry on day 2 (bar 32) and one on day 3 (bar 56),
        # despite breakout bars also at hours 9-15 each day.
        self.assertEqual(int(df["long_entry"].sum()), 2)
        self.assertTrue(df["long_entry"].iloc[24 + 8])
        self.assertTrue(df["long_entry"].iloc[48 + 8])

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:50])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:50].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        import strategies.asian_range_breakout  # noqa: F401
        self.assertIn("asian_range_breakout", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["asian_range_breakout"].slug,
                         "asian_range_breakout")

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 25)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
