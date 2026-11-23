"""Wilder ADX/DMI trend-system tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adx_dmi_trend import indicators, risk, signals


def _frame(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _flat_frame(n=100, price=100.0, vol=100.0):
    c = np.full(n, price)
    return _frame(c, c + 0.1, c - 0.1, c, np.full(n, vol))


def _trend_frame(direction=1, n_flat=60, n_trend=40, step=1.0, price=100.0):
    """Flat bars, then closes moving `step` per bar, h/l straddle c by 0.1."""
    c_flat = np.full(n_flat, price)
    c_trend = price + direction * step * np.arange(1, n_trend + 1)
    c = np.concatenate([c_flat, c_trend])
    o = np.concatenate([[c[0]], c[:-1]])
    h = c + 0.1
    l = c - 0.1
    return _frame(o, h, l, c, np.full(len(c), 100.0))


def _zigzag_frame():
    """Flat, up 40, down 20, up 40: DI crosses happen in both
    directions while ADX is already built up, so both setups fire."""
    c_flat = np.full(60, 100.0)
    c_up1 = 100.0 + np.arange(1, 41)
    c_dn = 140.0 - np.arange(1, 21)
    c_up2 = 120.0 + np.arange(1, 41)
    c = np.concatenate([c_flat, c_up1, c_dn, c_up2])
    o = np.concatenate([[c[0]], c[:-1]])
    h = c + 0.1
    l = c - 0.1
    return _frame(o, h, l, c, np.full(len(c), 100.0))


def _random_walk_frame(n=1500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("adx", "plus_di", "minus_di", "atr", "long_setup", "short_setup"):
            self.assertIn(col, ind.columns)

    def test_uptrend_di_values(self):
        # Sustained +1/bar rise: +DM = 1, -DM = 0 every bar, TR ~ 1.1,
        # so +DI -> ~100*1/1.1 = 90.9, -DI -> 0, DX -> 100, ADX -> ~95.
        ind = indicators.add_indicators(_trend_frame(direction=1))
        self.assertGreater(ind["plus_di"].iloc[-1], 80.0)
        self.assertLess(ind["minus_di"].iloc[-1], 1.0)
        self.assertGreater(ind["adx"].iloc[-1], 25.0)

    def test_downtrend_di_values_mirror(self):
        ind = indicators.add_indicators(_trend_frame(direction=-1))
        self.assertGreater(ind["minus_di"].iloc[-1], 80.0)
        self.assertLess(ind["plus_di"].iloc[-1], 1.0)
        self.assertGreater(ind["adx"].iloc[-1], 25.0)

    def test_flat_series_di_zero_adx_undefined(self):
        # No directional movement: both DIs are 0 and DX is 0/0, so
        # ADX stays NaN and no setup can fire.
        ind = indicators.add_indicators(_flat_frame(100))
        self.assertAlmostEqual(ind["plus_di"].iloc[-1], 0.0, places=9)
        self.assertAlmostEqual(ind["minus_di"].iloc[-1], 0.0, places=9)
        self.assertTrue(ind["adx"].isna().all())
        self.assertFalse(ind["long_setup"].any())
        self.assertFalse(ind["short_setup"].any())

    def test_both_setups_fire_on_zigzag(self):
        # A single ramp cannot fire a setup: its DI cross happens
        # before ADX has built above 25. The zigzag's second leg
        # crosses while ADX is already high, so both sides fire.
        ind = indicators.add_indicators(_zigzag_frame())
        self.assertGreater(int(ind["long_setup"].sum()), 0)
        self.assertGreater(int(ind["short_setup"].sum()), 0)

    def test_setup_implies_adx_gate(self):
        # Wherever a setup fires, ADX must be above Wilder's 25.
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("long_setup", "short_setup"):
            fired = ind[col].to_numpy(dtype=bool)
            self.assertTrue((ind["adx"].to_numpy()[fired] > 25.0).all())

    def test_no_setup_before_warmup(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(ind["long_setup"].iloc[:40].any())
        self.assertFalse(ind["short_setup"].iloc[:40].any())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:1300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("long_setup", "short_setup", "adx", "plus_di", "minus_di"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:1300].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, long_setup, short_setup, adx, plus_di, minus_di):
        n = len(adx)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        c = np.full(n, 100.0)
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "adx": adx, "plus_di": plus_di, "minus_di": minus_di,
            "long_setup": long_setup, "short_setup": short_setup,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_zigzag_enters_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_zigzag_frame()))
        self.assertGreaterEqual(int(sig["long_entry"].sum()), 1)
        self.assertGreaterEqual(int(sig["short_entry"].sum()), 1)

    def test_exit_long_on_opposite_cross(self):
        # Long at bar 1 (+DI above -DI); at bar 3 -DI crosses above
        # +DI -> exit long. ADX stays above 20 throughout.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.zeros(4, dtype=bool),
            adx=np.array([30.0, 30.0, 30.0, 30.0]),
            plus_di=np.array([10.0, 30.0, 30.0, 20.0]),
            minus_di=np.array([10.0, 10.0, 10.0, 25.0]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_exit_long_on_adx_below_20(self):
        # No opposite cross, but ADX falls below 20 at bar 3 -> exit.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.zeros(4, dtype=bool),
            adx=np.array([30.0, 30.0, 30.0, 19.0]),
            plus_di=np.array([10.0, 30.0, 30.0, 30.0]),
            minus_di=np.array([10.0, 10.0, 10.0, 10.0]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_exit_short_on_opposite_cross(self):
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.zeros(4, dtype=bool),
            short_setup=np.array([False, True, False, False]),
            adx=np.array([30.0, 30.0, 30.0, 30.0]),
            plus_di=np.array([10.0, 10.0, 10.0, 25.0]),
            minus_di=np.array([10.0, 30.0, 30.0, 20.0]),
        ))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertFalse(sig["short_exit"].iloc[2])
        self.assertTrue(sig["short_exit"].iloc[3])

    def test_opposite_setup_flips_position(self):
        # Long at bar 1; bar 3 is a short setup (-DI crossed above
        # +DI, ADX > 25) -> exit long + enter short.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.array([False, False, False, True]),
            adx=np.array([30.0, 30.0, 30.0, 30.0]),
            plus_di=np.array([10.0, 30.0, 30.0, 20.0]),
            minus_di=np.array([10.0, 10.0, 10.0, 25.0]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_no_reentry_while_holding(self):
        # Setup repeats on bars 1-3 while long; only one entry.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, True, True]),
            short_setup=np.zeros(4, dtype=bool),
            adx=np.array([30.0, 30.0, 30.0, 30.0]),
            plus_di=np.array([10.0, 30.0, 30.0, 30.0]),
            minus_di=np.array([10.0, 10.0, 10.0, 10.0]),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 168)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 40)

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
