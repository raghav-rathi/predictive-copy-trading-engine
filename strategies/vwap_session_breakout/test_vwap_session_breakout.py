"""VWAP session breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vwap_session_breakout import indicators, risk, signals

# 2026-01-01 00:00 UTC in ms — a UTC-midnight session anchor.
DAY0 = 1_767_225_600_000


def _frame(o, h, l, c, v, t0=DAY0):
    n = len(c)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _session_frame():
    """Three bars in one UTC session, hand-computable VWAP/SD:
    bar0: tp=100, v=10 -> VWAP 100, SD 0
    bar1: tp=102, v=10 -> VWAP 101, SD 1
    bar2: tp=104, v=30 -> VWAP 102.8, SD 1.6 (Var = 2.56)."""
    return _frame(
        o=[100.0, 102.0, 104.0],
        h=[102.0, 104.0, 106.0],
        l=[98.0, 100.0, 102.0],
        c=[100.0, 102.0, 104.0],
        v=[10.0, 10.0, 30.0],
    )


def _random_walk_frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (DAY0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("vwap", "vwap_sd", "vwap_upper", "vwap_lower",
                    "session_bar", "session_avg_vol", "vol_above_avg", "atr"):
            self.assertIn(col, ind.columns)

    def test_vwap_and_sd_golden_values(self):
        ind = indicators.add_indicators(_session_frame())
        self.assertAlmostEqual(ind["vwap"].iloc[0], 100.0, places=6)
        self.assertAlmostEqual(ind["vwap_sd"].iloc[0], 0.0, places=6)
        self.assertAlmostEqual(ind["vwap"].iloc[1], 101.0, places=6)
        self.assertAlmostEqual(ind["vwap_sd"].iloc[1], 1.0, places=6)
        self.assertAlmostEqual(ind["vwap"].iloc[2], 102.8, places=6)
        self.assertAlmostEqual(ind["vwap_sd"].iloc[2], 1.6, places=6)
        self.assertAlmostEqual(ind["vwap_upper"].iloc[2], 104.4, places=6)
        self.assertAlmostEqual(ind["vwap_lower"].iloc[2], 101.2, places=6)

    def test_session_avg_vol_and_gate(self):
        ind = indicators.add_indicators(_session_frame())
        # avg bar volume: 10, 10, 50/3 = 16.667
        self.assertAlmostEqual(ind["session_avg_vol"].iloc[0], 10.0, places=6)
        self.assertAlmostEqual(ind["session_avg_vol"].iloc[1], 10.0, places=6)
        self.assertAlmostEqual(ind["session_avg_vol"].iloc[2], 50.0 / 3.0, places=6)
        self.assertFalse(bool(ind["vol_above_avg"].iloc[0]))
        self.assertFalse(bool(ind["vol_above_avg"].iloc[1]))
        self.assertTrue(bool(ind["vol_above_avg"].iloc[2]))
        self.assertEqual(list(ind["session_bar"]), [1, 2, 3])

    def test_session_resets_at_utc_midnight(self):
        # Bar 0 in session 1, bar 1 at the next UTC midnight:
        # cumulative sums restart, so VWAP/SD reset exactly.
        df = _frame(
            o=[100.0, 100.0], h=[102.0, 102.0], l=[98.0, 98.0],
            c=[100.0, 100.0], v=[10.0, 10.0],
            t0=DAY0,
        )
        df.loc[1, "t"] = DAY0 + 24 * 3_600_000
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["vwap"].iloc[1], 100.0, places=6)
        self.assertAlmostEqual(ind["vwap_sd"].iloc[1], 0.0, places=6)
        self.assertEqual(int(ind["session_bar"].iloc[1]), 1)

    def test_no_nan_on_random_walk(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("vwap", "vwap_sd", "vwap_upper", "vwap_lower",
                    "session_avg_vol"):
            self.assertFalse(ind[col].isna().any(), col)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("vwap", "vwap_sd", "vwap_upper", "session_avg_vol"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:300].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )

    def test_zero_volume_session_does_not_break_signals(self):
        # All-zero volume: VWAP is undefined (NaN), but the signal
        # layer must still emit clean boolean columns.
        n = 50
        df = _frame(np.full(n, 100.0), np.full(n, 101.0), np.full(n, 99.0),
                    np.full(n, 100.0), np.zeros(n))
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)


class TestSignals(unittest.TestCase):
    def _signal_frame(self, c, upper, lower, vwap, session_bar, vol):
        n = len(c)
        t = (DAY0 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": np.asarray(c, dtype=float),
            "h": np.asarray(c, dtype=float) + 1.0,
            "l": np.asarray(c, dtype=float) - 1.0,
            "c": np.asarray(c, dtype=float),
            "v": np.full(n, 100.0),
            "vwap": np.asarray(vwap, dtype=float),
            "vwap_upper": np.asarray(upper, dtype=float),
            "vwap_lower": np.asarray(lower, dtype=float),
            "session_bar": np.asarray(session_bar, dtype=float),
            "vol_above_avg": np.asarray(vol, dtype=bool),
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_breakout_with_volume(self):
        # Close crosses above the upper band at bar 3
        # (100 -> 105 vs upper 104) with above-average volume.
        sig = signals.add_signals(self._signal_frame(
            c=[100.0, 100.0, 100.0, 105.0, 106.0],
            upper=[101.0, 101.0, 101.0, 104.0, 104.0],
            lower=[99.0, 99.0, 99.0, 96.0, 96.0],
            vwap=[100.0] * 5,
            session_bar=[1, 2, 3, 4, 5],
            vol=[True] * 5,
        ))
        self.assertTrue(sig["long_entry"].iloc[3])
        # No re-entry while held: bar 4 stays above the band.
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_long_entry_blocked_without_volume(self):
        sig = signals.add_signals(self._signal_frame(
            c=[100.0, 100.0, 100.0, 105.0, 106.0],
            upper=[101.0, 101.0, 101.0, 104.0, 104.0],
            lower=[99.0, 99.0, 99.0, 96.0, 96.0],
            vwap=[100.0] * 5,
            session_bar=[1, 2, 3, 4, 5],
            vol=[True, True, True, False, True],
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_long_entry_blocked_in_first_two_session_bars(self):
        # A cross on session bar 1 is ignored (degenerate band);
        # bar 2 has no fresh cross, so nothing fires at all.
        sig = signals.add_signals(self._signal_frame(
            c=[100.0, 105.0, 106.0],
            upper=[101.0, 104.0, 104.0],
            lower=[99.0, 96.0, 96.0],
            vwap=[100.0] * 3,
            session_bar=[1, 2, 3],
            vol=[True] * 3,
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_long_exit_on_close_below_vwap(self):
        sig = signals.add_signals(self._signal_frame(
            c=[100.0, 100.0, 100.0, 105.0, 99.0],
            upper=[101.0, 101.0, 101.0, 104.0, 104.0],
            lower=[99.0, 99.0, 99.0, 96.0, 96.0],
            vwap=[100.0] * 5,
            session_bar=[1, 2, 3, 4, 5],
            vol=[True] * 5,
        ))
        self.assertTrue(sig["long_entry"].iloc[3])
        self.assertTrue(sig["long_exit"].iloc[4])

    def test_short_mirror_entry_and_exit(self):
        # Close crosses below the lower band at bar 3
        # (100 -> 95 vs lower 96); exit at bar 4 on a close
        # back above VWAP.
        sig = signals.add_signals(self._signal_frame(
            c=[100.0, 100.0, 100.0, 95.0, 101.0],
            upper=[101.0, 101.0, 101.0, 104.0, 104.0],
            lower=[99.0, 99.0, 99.0, 96.0, 96.0],
            vwap=[100.0] * 5,
            session_bar=[1, 2, 3, 4, 5],
            vol=[True] * 5,
        ))
        self.assertTrue(sig["short_entry"].iloc[3])
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertTrue(sig["short_exit"].iloc[4])

    def test_opposite_setup_flips_position(self):
        # Long at bar 3; at bar 5 the close breaks below the
        # lower band (106 -> 90 vs lower 96) -> exit + flip.
        sig = signals.add_signals(self._signal_frame(
            c=[100.0, 100.0, 100.0, 105.0, 106.0, 90.0],
            upper=[101.0, 101.0, 101.0, 104.0, 104.0, 104.0],
            lower=[99.0, 99.0, 99.0, 96.0, 96.0, 96.0],
            vwap=[100.0] * 6,
            session_bar=[1, 2, 3, 4, 5, 6],
            vol=[True] * 6,
        ))
        self.assertTrue(sig["long_entry"].iloc[3])
        self.assertTrue(sig["long_exit"].iloc[5])
        self.assertTrue(sig["short_entry"].iloc[5])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 24)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 24)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
