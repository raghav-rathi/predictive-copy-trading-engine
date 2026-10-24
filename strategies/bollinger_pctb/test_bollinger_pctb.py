"""Bollinger %B tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_pctb import indicators, risk, signals


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
        for col in ("bb_mid", "bb_upper", "bb_lower", "bb_width", "pctb", "atr"):
            self.assertIn(col, ind.columns)

    def test_pctb_hand_computation(self):
        # Last 20 closes: 19 bars at 100, final bar jumps to 130.
        c = np.concatenate([np.full(19, 100.0), [130.0]])
        df = _frame_from_close(c, seed=3)
        ind = indicators.add_indicators(df)
        window = c[-20:]
        mid = float(window.mean())
        sd = float(window.std(ddof=1))
        expected = (130.0 - (mid - 2.0 * sd)) / (4.0 * sd)
        self.assertAlmostEqual(float(ind["pctb"].iloc[-1]), expected, places=9)

    def test_pctb_zero_width_band_is_half(self):
        # All 20 closes identical -> band width 0 -> %B defined as 0.5.
        ind = indicators.add_indicators(_flat_frame(60, close=100.0))
        self.assertAlmostEqual(float(ind["pctb"].iloc[-1]), 0.5, places=9)
        self.assertAlmostEqual(float(ind["bb_width"].iloc[-1]), 0.0, places=9)

    def test_pctb_above_one_on_upward_jump(self):
        c = np.concatenate([np.full(60, 100.0), [130.0]])
        ind = indicators.add_indicators(_frame_from_close(c, seed=3))
        self.assertGreater(float(ind["pctb"].iloc[-1]), 1.0)

    def test_pctb_below_zero_on_downward_jump(self):
        c = np.concatenate([np.full(60, 100.0), [70.0]])
        ind = indicators.add_indicators(_frame_from_close(c, seed=3))
        self.assertLess(float(ind["pctb"].iloc[-1]), 0.0)

    def test_no_lookahead(self):
        # %B at bar j must not change when later bars are appended.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["pctb"].iloc[:200].reset_index(drop=True),
            ind_short["pctb"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _direct_frame(self, pctb):
        df = _frame_from_close(np.full(len(pctb), 100.0), seed=9)
        df["pctb"] = np.asarray(pctb, dtype=float)
        return df

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_reclaim_of_zero(self):
        # %B sits at -0.1, jumps to +0.1 at bar 50 -> cross above 0.
        pctb = np.full(100, -0.1)
        pctb[50:] = 0.1
        sig = signals.add_signals(self._direct_frame(pctb))
        self.assertTrue(sig["long_entry"].iloc[50])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_no_long_entry_while_stuck_below_zero(self):
        # %B pinned at -0.1 never crosses above 0 -> no entry.
        sig = signals.add_signals(self._direct_frame(np.full(100, -0.1)))
        self.assertFalse(sig["long_entry"].any())

    def test_short_entry_on_loss_of_one(self):
        # %B sits at 1.1, drops to 0.9 at bar 50 -> cross below 1.
        pctb = np.full(100, 1.1)
        pctb[50:] = 0.9
        sig = signals.add_signals(self._direct_frame(pctb))
        self.assertTrue(sig["short_entry"].iloc[50])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_long_exit_on_cross_below_half(self):
        # Reclaim at 50, %B runs to 0.8, drops to 0.4 at bar 70.
        pctb = np.full(100, -0.1)
        pctb[50:70] = 0.8
        pctb[70:] = 0.4
        sig = signals.add_signals(self._direct_frame(pctb))
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["long_exit"].iloc[50])

    def test_short_exit_on_cross_above_half(self):
        # Loss of 1 at 50, %B runs to 0.2, rises to 0.6 at bar 70.
        pctb = np.full(100, 1.1)
        pctb[50:70] = 0.2
        pctb[70:] = 0.6
        sig = signals.add_signals(self._direct_frame(pctb))
        self.assertTrue(sig["short_exit"].iloc[70])
        self.assertFalse(sig["short_exit"].iloc[50])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.5)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 50)

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
