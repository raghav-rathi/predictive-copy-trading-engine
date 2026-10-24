"""TTM-style squeeze breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.keltner_squeeze import indicators, risk, signals


def _frame_from_parts(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _flat_frame(n=200, close=100.0, vol=100.0):
    c = np.full(n, close)
    h = c * 1.001
    l = c * 0.999
    return _frame_from_parts(c, h, l, c, np.full(n, vol))


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("bb_mid", "bb_upper", "bb_lower", "bb_width",
                    "kc_mid", "kc_upper", "kc_lower", "kc_width",
                    "squeeze_on", "atr"):
            self.assertIn(col, ind.columns)

    def test_squeeze_on_in_flat_market(self):
        # Flat closes -> Bollinger width ~0, Keltner width > 0 (the
        # h/l spread keeps ATR positive) -> squeeze must be ON.
        ind = indicators.add_indicators(_flat_frame(200, close=100.0))
        self.assertTrue(bool(ind["squeeze_on"].iloc[-1]))
        self.assertAlmostEqual(float(ind["bb_width"].iloc[-1]), 0.0, places=9)
        self.assertGreater(float(ind["kc_width"].iloc[-1]), 0.0)

    def test_squeeze_flag_matches_width_comparison(self):
        # Wiring: squeeze_on is exactly bb_width < kc_width wherever
        # both widths are defined.
        ind = indicators.add_indicators(_random_walk_frame())
        valid = ind["bb_width"].notna() & ind["kc_width"].notna()
        expected = ind.loc[valid, "bb_width"] < ind.loc[valid, "kc_width"]
        pd.testing.assert_series_equal(
            ind.loc[valid, "squeeze_on"].reset_index(drop=True),
            expected.reset_index(drop=True),
            check_names=False,
        )

    def test_kc_width_is_three_atr10(self):
        # Keltner width = 2 * 1.5 * ATR(10) by construction.
        from strategies import base as B
        df = _random_walk_frame()
        ind = indicators.add_indicators(df)
        atr10 = B.atr(df["h"], df["l"], df["c"], 10)
        expected = 2 * 1.5 * atr10
        # Both series must be defined: the Keltner mid (EMA20) spins
        # up later than ATR(10), so mask on the intersection.
        valid = expected.notna() & ind["kc_width"].notna()
        pd.testing.assert_series_equal(
            ind.loc[valid, "kc_width"].reset_index(drop=True),
            expected[valid].reset_index(drop=True),
            check_names=False, check_exact=False, rtol=1e-9,
        )

    def test_no_lookahead(self):
        # Squeeze flag at bar j must not change when later bars append.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["squeeze_on"].iloc[:200].reset_index(drop=True),
            ind_short["squeeze_on"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _direct_frame(self, close, upper, lower, squeeze):
        df = _frame_from_close(close, seed=9)
        df["bb_upper"] = np.asarray(upper, dtype=float)
        df["bb_lower"] = np.asarray(lower, dtype=float)
        df["squeeze_on"] = np.asarray(squeeze, dtype=bool)
        return df

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_breakout_after_squeeze(self):
        # Close rides 99, breaks to 101 above the 100 upper band at
        # bar 50; squeeze was ON at bars 48-50 -> entry fires at 50.
        close = np.full(100, 99.0)
        close[50:] = 101.0
        squeeze = np.zeros(100, dtype=bool)
        squeeze[48:51] = True
        sig = signals.add_signals(self._direct_frame(
            close, np.full(100, 100.0), np.full(100, 90.0), squeeze))
        self.assertTrue(sig["long_entry"].iloc[50])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_breakout_without_squeeze_blocked(self):
        # Same breakout, squeeze never ON -> no entry.
        close = np.full(100, 99.0)
        close[50:] = 101.0
        sig = signals.add_signals(self._direct_frame(
            close, np.full(100, 100.0), np.full(100, 90.0),
            np.zeros(100, dtype=bool)))
        self.assertFalse(sig["long_entry"].any())

    def test_squeeze_two_bars_ago_still_counts(self):
        # Squeeze ON only at bar 48, breakout at 50: bar 48 is inside
        # the j-2..j window -> entry fires.
        close = np.full(100, 99.0)
        close[50:] = 101.0
        squeeze = np.zeros(100, dtype=bool)
        squeeze[48] = True
        sig = signals.add_signals(self._direct_frame(
            close, np.full(100, 100.0), np.full(100, 90.0), squeeze))
        self.assertTrue(sig["long_entry"].iloc[50])

    def test_squeeze_three_bars_ago_does_not_count(self):
        # Squeeze ON only at bar 47, breakout at 50: bar 47 is outside
        # the j-2..j window -> entry blocked.
        close = np.full(100, 99.0)
        close[50:] = 101.0
        squeeze = np.zeros(100, dtype=bool)
        squeeze[47] = True
        sig = signals.add_signals(self._direct_frame(
            close, np.full(100, 100.0), np.full(100, 90.0), squeeze))
        self.assertFalse(sig["long_entry"].any())

    def test_short_entry_symmetry(self):
        # Close rides 91, drops to 89 below the 90 lower band at bar
        # 50; squeeze ON at 48-50 -> short entry fires at 50.
        close = np.full(100, 91.0)
        close[50:] = 89.0
        squeeze = np.zeros(100, dtype=bool)
        squeeze[48:51] = True
        sig = signals.add_signals(self._direct_frame(
            close, np.full(100, 100.0), np.full(100, 90.0), squeeze))
        self.assertTrue(sig["short_entry"].iloc[50])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_long_exit_on_opposite_band_cross(self):
        # After the long breakout at 50, close drops below the 90
        # lower band at bar 70 -> long_exit fires exactly there.
        close = np.full(100, 99.0)
        close[50:70] = 101.0
        close[70:] = 89.0
        squeeze = np.zeros(100, dtype=bool)
        squeeze[48:51] = True
        sig = signals.add_signals(self._direct_frame(
            close, np.full(100, 100.0), np.full(100, 90.0), squeeze))
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["long_exit"].iloc[50])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.5)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 96)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 60)

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
