"""Turn-of-the-month calendar effect tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.turn_of_month import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

MS_PER_HOUR = 3_600_000


def _dated_frame(start_ms, n, close=100.0, jump_close=None):
    """Hourly bars starting at start_ms (UTC). If jump_close is set,
    the last 50 bars close at that price (for the no-lookahead test
    the caller builds the extension separately)."""
    closes = np.full(n, close)
    t = (start_ms + np.arange(n) * MS_PER_HOUR).astype("int64")
    return pd.DataFrame({
        "t": t, "o": closes, "h": closes + 0.5, "l": closes - 0.5,
        "c": closes, "v": np.full(n, 100.0),
    })


def _ms(y, mo, d, h=0):
    import datetime
    return int(datetime.datetime(y, mo, d, h,
                                 tzinfo=datetime.timezone.utc).timestamp() * 1000)


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


class TestTurnOfMonth(unittest.TestCase):
    def test_registered(self):
        self.assertIn("turn_of_month", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_dated_frame(_ms(2026, 3, 28), 240))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)
            self.assertFalse(df[col].isna().any())

    def test_march_entry_and_april_exit_exact_bars(self):
        # Mar 28 00:00 UTC + 240 hourly bars. Last day of March is
        # the 31st; entry on Mar 31 00:00 (bar 72); exit on Apr 3
        # 23:00 (bar 167).
        df = _run(_dated_frame(_ms(2026, 3, 28), 240))
        self.assertEqual(int(df["tom_entry"].sum()), 1)
        self.assertTrue(df["tom_entry"].iloc[72])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[72])
        self.assertEqual(int(df["tom_exit"].sum()), 1)
        self.assertTrue(df["tom_exit"].iloc[167])
        self.assertEqual(int(df["long_exit"].sum()), 1)
        self.assertTrue(df["long_exit"].iloc[167])
        # Neighbours are NOT entry/exit bars.
        self.assertFalse(df["tom_entry"].iloc[48])   # Mar 30 00:00
        self.assertFalse(df["tom_entry"].iloc[73])   # Mar 31 01:00
        self.assertFalse(df["tom_exit"].iloc[144])   # Apr 3 00:00
        self.assertFalse(df["tom_exit"].iloc[168])   # Apr 4 00:00

    def test_january_31_day_month(self):
        # Jan 30 00:00 + 8 days: entry Jan 31 00:00 (bar 24),
        # exit Feb 3 23:00 (bar 119); January has 31 days.
        df = _run(_dated_frame(_ms(2026, 1, 30), 8 * 24))
        self.assertTrue((df["days_in_month"].iloc[:48] == 31).all())
        self.assertTrue(df["tom_entry"].iloc[24])
        self.assertEqual(int(df["tom_entry"].sum()), 1)
        self.assertTrue(df["tom_exit"].iloc[119])
        self.assertEqual(int(df["tom_exit"].sum()), 1)

    def test_february_28_day_month_not_leap(self):
        # Feb 26 00:00 + 8 days: 2026 is not a leap year, so the last
        # day of February is the 28th; entry Feb 28 00:00 (bar 48),
        # exit Mar 3 23:00 (bar 143).
        df = _run(_dated_frame(_ms(2026, 2, 26), 8 * 24))
        self.assertTrue((df["days_in_month"].iloc[:48] == 28).all())
        self.assertTrue(df["tom_entry"].iloc[48])
        self.assertEqual(int(df["tom_entry"].sum()), 1)
        self.assertTrue(df["tom_exit"].iloc[143])
        self.assertEqual(int(df["tom_exit"].sum()), 1)

    def test_missing_entry_bar_means_no_entry(self):
        # Same March window, but the Mar 31 00:00 bar is dropped:
        # no entry is manufactured from the 01:00 bar.
        df0 = _dated_frame(_ms(2026, 3, 28), 240)
        df0 = df0.drop(index=72).reset_index(drop=True)
        df = _run(df0)
        self.assertEqual(int(df["tom_entry"].sum()), 0)
        self.assertFalse(df["long_entry"].any())

    def test_never_shorts(self):
        df = _run(_dated_frame(_ms(2026, 3, 28), 240))
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["short_exit"].any())

    def test_flat_frame_only_calendar_entries(self):
        # Flat prices still produce the calendar long (the strategy
        # is price-blind by design); entries fire ONLY on the
        # last-day 00:00 bar, never on shorts.
        df = _run(_dated_frame(_ms(2026, 3, 28), 240))
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[72])
        self.assertFalse(df["short_entry"].any())

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
        self.assertFalse(risk.RISK.allow_shorts)
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

    def test_no_lookahead_future_jump(self):
        base = _dated_frame(_ms(2026, 3, 28), 240)
        ext = base.copy()
        tail = _dated_frame(_ms(2026, 4, 7), 50, close=300.0)
        df2_in = pd.concat([base, tail], ignore_index=True)
        df1 = _run(base)
        df2 = _run(df2_in)
        for col in ("tom_entry", "tom_exit", "long_entry",
                    "long_exit", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:240].reset_index(drop=True),
                df2[col].iloc[:240].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_dated_frame(_ms(2026, 3, 28), 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
