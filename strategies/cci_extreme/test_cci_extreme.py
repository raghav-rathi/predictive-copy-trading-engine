"""CCI extreme tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cci_extreme import indicators, risk, signals
from strategies.cci_extreme.indicators import CCI_N, LONG_LEVEL, SHORT_LEVEL, SCALE


def _frame_from_parts(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


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
        for col in ("cci", "atr"):
            self.assertIn(col, ind.columns)

    def test_no_nan_after_warmup(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(ind["cci"].isna().any())

    def test_cci_hand_computation(self):
        # 20 bars, tp rising linearly 100..119 (h=l=c=tp). Mean =
        # 109.5; mean deviation = mean(|tp - 109.5|) = 5.0; last
        # CCI = (119 - 109.5) / (0.015 * 5) = 126.666...
        n = 20
        tp = np.arange(100.0, 100.0 + n)
        df = _frame_from_parts(tp, tp, tp, tp, np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["cci"].iloc[-1]), 9.5 / (0.015 * 5.0),
                               places=6)

    def test_cci_flat_window_is_zero(self):
        # Dead-flat window: mean deviation = 0 -> CCI = 0, not
        # NaN or inf.
        n = 30
        df = _frame_from_parts(
            np.full(n, 100.0), np.full(n, 100.0), np.full(n, 100.0),
            np.full(n, 100.0), np.ones(n))
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["cci"].iloc[-1]), 0.0, places=9)
        self.assertFalse(ind["cci"].isna().any())

    def test_cci_sign_symmetry(self):
        # Mirror the linear ramp (tp falling 119..100): last CCI
        # must be the exact negative of the rising case.
        n = 20
        tp_up = np.arange(100.0, 100.0 + n)
        tp_dn = tp_up[::-1].copy()
        df_up = _frame_from_parts(tp_up, tp_up, tp_up, tp_up, np.ones(n))
        df_dn = _frame_from_parts(tp_dn, tp_dn, tp_dn, tp_dn, np.ones(n))
        c_up = float(indicators.add_indicators(df_up)["cci"].iloc[-1])
        c_dn = float(indicators.add_indicators(df_dn)["cci"].iloc[-1])
        self.assertAlmostEqual(c_up, -c_dn, places=6)

    def test_cci_bounded_on_random_walk(self):
        # On ordinary data CCI stays in a sane band (no blow-ups
        # from tiny mean deviations on noisy but non-flat data).
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertTrue((ind["cci"].abs() < 1000).all())

    def test_no_lookahead(self):
        # CCI at bar j must not change when later bars are appended.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["cci"].iloc[:200].reset_index(drop=True),
            ind_short["cci"].reset_index(drop=True),
            check_names=False,
        )

    def test_cci_uses_current_window_mean(self):
        # A single spike bar inside an otherwise flat window: the
        # spike's CCI must be positive and large (mean deviation
        # is small relative to the spike's distance from the mean).
        n = 20
        tp = np.full(n, 100.0)
        tp[-1] = 110.0
        df = _frame_from_parts(tp, tp, tp, tp, np.ones(n))
        ind = indicators.add_indicators(df)
        cci = float(ind["cci"].iloc[-1])
        # mean = 100.5, md = (19*0.5 + 9.5)/20 = 0.95,
        # CCI = 9.5 / (0.015*0.95) = 666.67
        self.assertAlmostEqual(cci, 9.5 / (0.015 * 0.95), places=4)


class TestSignals(unittest.TestCase):
    def _direct_frame(self, cci_path):
        n = len(cci_path)
        df = _frame_from_close(np.full(n, 100.0), seed=9)
        df["cci"] = np.asarray(cci_path, dtype=float)
        return df

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_cross_above_minus_100(self):
        # CCI climbs -120 -> -90 at bar 10 (cross above -100 from
        # below) -> fires exactly there.
        cci = [-120.0] * 10 + [-90.0, -50.0, 0.0]
        sig = signals.add_signals(self._direct_frame(cci))
        self.assertTrue(sig["long_entry"].iloc[10])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_touch_without_cross_does_not_fire(self):
        # CCI sits below -100 the whole path (never crosses up) ->
        # no long entry even though it is deeply oversold.
        cci = [-150.0, -140.0, -130.0, -120.0, -110.0, -105.0]
        sig = signals.add_signals(self._direct_frame(cci))
        self.assertFalse(sig["long_entry"].any())

    def test_short_entry_cross_below_plus_100(self):
        # CCI drops 120 -> 90 at bar 10 (cross below +100 from
        # above) -> fires exactly there.
        cci = [120.0] * 10 + [90.0, 50.0, 0.0]
        sig = signals.add_signals(self._direct_frame(cci))
        self.assertTrue(sig["short_entry"].iloc[10])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_long_exit_cross_below_zero(self):
        # Long entry at bar 10 (-120 -> -90), then CCI falls back
        # through 0 at bar 12 (10 -> -10) -> long_exit fires there.
        cci = [-120.0] * 10 + [-90.0, 10.0, -10.0, -50.0]
        sig = signals.add_signals(self._direct_frame(cci))
        self.assertTrue(sig["long_entry"].iloc[10])
        self.assertTrue(sig["long_exit"].iloc[12])
        self.assertFalse(sig["long_exit"].iloc[10])

    def test_short_exit_cross_above_zero(self):
        # Short entry at bar 10 (120 -> 90), then CCI climbs back
        # through 0 at bar 12 (-10 -> 10) -> short_exit fires there.
        cci = [120.0] * 10 + [90.0, -10.0, 10.0, 50.0]
        sig = signals.add_signals(self._direct_frame(cci))
        self.assertTrue(sig["short_entry"].iloc[10])
        self.assertTrue(sig["short_exit"].iloc[12])


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
