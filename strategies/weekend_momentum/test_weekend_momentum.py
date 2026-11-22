"""Weekend crypto momentum tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.weekend_momentum import indicators, risk, signals

# 2026-01-02 is a Friday. Bars 0-23 Fri, 24-47 Sat, 48-71 Sun,
# bar 72 Mon 00:00, bar 240 the next Mon 00:00.
T0 = int(pd.Timestamp("2026-01-02", tz="UTC").timestamp() * 1000)


def _frame(n=400, drift=0.0005, seed=7):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(drift, 0.003, n)))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _trend_frame(n=400, slope=0.02):
    """Deterministic linear uptrend (slope per bar) / downtrend if negative."""
    c = 100 + slope * np.arange(n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("mom168", "mom168_pct", "weekday", "hour",
                    "is_weekend", "is_monday_open", "atr"):
            self.assertIn(col, ind.columns)

    def test_weekday_hour_from_t(self):
        ind = indicators.add_indicators(_frame())
        # Bar 0: Friday 00:00 UTC. Bar 72: Monday 00:00 UTC.
        self.assertEqual(int(ind["weekday"].iloc[0]), 4)
        self.assertEqual(int(ind["hour"].iloc[0]), 0)
        self.assertEqual(int(ind["weekday"].iloc[72]), 0)
        self.assertEqual(int(ind["hour"].iloc[72]), 0)
        self.assertEqual(int(ind["weekday"].iloc[73]), 0)
        self.assertEqual(int(ind["hour"].iloc[73]), 1)

    def test_weekend_session_flags(self):
        ind = indicators.add_indicators(_frame())
        # Fri 00:00 .. Sun 23:59 = bars 0..71; Mon 00:00 = bar 72.
        self.assertTrue(ind["is_weekend"].iloc[:72].all())
        self.assertFalse(ind["is_weekend"].iloc[72])
        self.assertFalse(ind["is_weekend"].iloc[100])  # Tuesday
        # Next weekend: Fri 2026-01-09 00:00 = bar 168.
        self.assertTrue(ind["is_weekend"].iloc[168])
        self.assertTrue(ind["is_weekend"].iloc[239])
        self.assertFalse(ind["is_weekend"].iloc[240])

    def test_monday_open_flags(self):
        ind = indicators.add_indicators(_frame())
        self.assertTrue(ind["is_monday_open"].iloc[72])
        self.assertTrue(ind["is_monday_open"].iloc[240])
        self.assertFalse(ind["is_monday_open"].iloc[73])
        self.assertEqual(int(ind["is_monday_open"].sum()), 2)

    def test_momentum_168_lag(self):
        ind = indicators.add_indicators(_trend_frame(slope=0.02))
        # mom168 at bar 200 = c[200] - c[32] = 0.02 * 168.
        self.assertAlmostEqual(float(ind["mom168"].iloc[200]), 0.02 * 168,
                               places=6)
        self.assertTrue(np.isnan(ind["mom168"].iloc[:168]).all())

    def test_no_lookahead(self):
        df = _frame()
        full = indicators.add_indicators(df)
        short = indicators.add_indicators(df.iloc[:200])
        for col in ("mom168", "is_weekend", "is_monday_open"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def test_long_on_weekend_uptrend(self):
        sig = signals.add_signals(
            indicators.add_indicators(_trend_frame(slope=0.02)))
        # One entry per weekend, on the first weekend bar with valid
        # momentum: bar 168 (Fri 2026-01-09 00:00) and bar 336
        # (Fri 2026-01-16 00:00). No entries on weekday bars.
        self.assertTrue(sig["long_entry"].iloc[168])
        self.assertTrue(sig["long_entry"].iloc[336])
        self.assertEqual(int(sig["long_entry"].sum()), 2)
        self.assertFalse(sig["short_entry"].any())
        self.assertFalse(sig["long_entry"].iloc[100])
        self.assertFalse(sig["long_entry"].iloc[72])

    def test_short_on_weekend_downtrend(self):
        sig = signals.add_signals(
            indicators.add_indicators(_trend_frame(slope=-0.02)))
        self.assertTrue(sig["short_entry"].iloc[168])
        self.assertTrue(sig["short_entry"].iloc[336])
        self.assertEqual(int(sig["short_entry"].sum()), 2)
        self.assertFalse(sig["long_entry"].any())

    def test_exit_on_monday_open_only(self):
        sig = signals.add_signals(
            indicators.add_indicators(_trend_frame(slope=0.02)))
        # Long entered Fri bar 168 exits Mon bar 240; bar 72 is before
        # any entry (momentum not yet valid), so no exit there.
        self.assertTrue(sig["long_exit"].iloc[240])
        self.assertFalse(sig["long_exit"].iloc[72])
        self.assertFalse(sig["long_exit"].iloc[241])
        self.assertFalse(sig["long_exit"].iloc[239])  # Sunday 23:00: still in
        self.assertFalse(sig["short_exit"].any())

    def test_no_reentry_same_weekend(self):
        # Momentum stays positive all weekend: exactly one entry per
        # weekend session, not one per bar.
        sig = signals.add_signals(
            indicators.add_indicators(_trend_frame(slope=0.02)))
        self.assertEqual(int(sig["long_entry"].iloc[168:240].sum()), 1)

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_no_entry_before_momentum_warmup(self):
        # First 168 bars: mom168 is NaN -> treated as 0 -> no entries.
        sig = signals.add_signals(
            indicators.add_indicators(_trend_frame(slope=0.02)))
        self.assertFalse(sig["long_entry"].iloc[:168].any())


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 192)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
