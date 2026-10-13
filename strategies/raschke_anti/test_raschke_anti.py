"""Network-free unit tests for Raschke Anti."""

import unittest

import numpy as np
import pandas as pd

from strategies.raschke_anti import indicators, risk, signals


def _candles(o, h, l, c) -> pd.DataFrame:
    n = len(c)
    return pd.DataFrame(
        {
            "t": np.arange(n, dtype=np.int64) * 3600_000,
            "o": np.asarray(o, dtype=float),
            "h": np.asarray(h, dtype=float),
            "l": np.asarray(l, dtype=float),
            "c": np.asarray(c, dtype=float),
            "v": np.full(n, 100.0),
        }
    )


class TestRaschkeIndicators(unittest.TestCase):
    def test_fastk_math_on_known_values(self):
        # 7 bars: high=110, low=100 constant, close ramps 101..107 -> last %K = 70
        c = np.arange(101.0, 108.0)
        df = indicators.add_indicators(
            _candles(c, np.full(7, 110.0), np.full(7, 100.0), c)
        )
        self.assertAlmostEqual(df["fastK"].iloc[6], 70.0, places=6)

    def test_slowd_is_sma_of_fastk(self):
        c = 100.0 + np.cumsum(np.random.RandomState(0).randn(60))
        df = indicators.add_indicators(_candles(c, c + 1, c - 1, c))
        expect = df["fastK"].rolling(10, min_periods=10).mean()
        pd.testing.assert_series_equal(df["slowD"], expect, check_names=False)

    def test_inside2_detection(self):
        # bars 0,1 set 2-bar range [90,110]; bar 2 inside -> True
        h = [110, 105, 104]
        l = [90, 95, 96]
        c = [100, 100, 100]
        df = indicators.add_indicators(_candles(c, h, l, c))
        self.assertTrue(df["inside2"].iloc[2])
        self.assertFalse(df["inside2"].iloc[:2].any())

    def test_no_lookahead(self):
        c = 100.0 + np.cumsum(np.random.RandomState(1).randn(120))
        df = _candles(c, c + 1, c - 1, c)
        full = indicators.add_indicators(df)
        trunc = indicators.add_indicators(df.iloc[:-1])
        for col in ("fastK", "slowD", "osc310", "osc310_sig", "inside2"):
            pd.testing.assert_series_equal(
                full[col].iloc[:-1], trunc[col], check_names=False
            )


class TestRaschkeSignals(unittest.TestCase):
    def _frame(self, n=8, **over):
        base = {
            "uptrend": np.zeros(n, dtype=bool),
            "downtrend": np.zeros(n, dtype=bool),
            "hook_dn": np.zeros(n, dtype=bool),
            "hook_up": np.zeros(n, dtype=bool),
            "inside2": np.zeros(n, dtype=bool),
            "fastK": np.full(n, 50.0),
            "slowD": np.full(n, 50.0),
            "osc310": np.full(n, 0.0),
            "osc310_sig": np.full(n, 0.0),
        }
        base.update(over)
        return pd.DataFrame(base)

    def test_hook_then_realign_triggers_long(self):
        # %K crosses below %D at i=1 (hook), back above at i=3; uptrend throughout
        n = 8
        fastK = np.array([60, 55, 52, 58, 62, 63, 64, 65.0])
        slowD = np.array([58, 57, 56, 56, 57, 58, 59, 60.0])
        hook_dn = np.zeros(n, dtype=bool)
        hook_dn[1] = True  # %K hooks down through %D at i=1
        df = signals.add_signals(
            self._frame(
                n,
                uptrend=np.ones(n, dtype=bool),
                fastK=fastK,
                slowD=slowD,
                hook_dn=hook_dn,
            ),
            arm_window=5,
        )
        # crossed_below at i=1 (55<57 after 60>=58); crossed_above at i=3 (58>56 after 52<=56)
        self.assertTrue(df["long_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[[0, 1, 2]].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_arm_no_entry(self):
        # %K re-aligns but no prior hook/inside day -> no entry
        n = 8
        fastK = np.array([55, 56, 57, 58, 59, 60, 61, 62.0])
        slowD = np.array([58, 58, 58, 57, 57, 57, 57, 57.0])
        df = signals.add_signals(
            self._frame(n, uptrend=np.ones(n, dtype=bool), fastK=fastK, slowD=slowD)
        )
        self.assertFalse(df[["long_entry", "short_entry"]].any().any())

    def test_osc310_cross_triggers_in_trend(self):
        # inside day at i=2 arms; 3/10 crosses up at i=4 while %K still below %D
        n = 10
        inside = np.zeros(n, dtype=bool)
        inside[2] = True
        osc = np.array([-2, -2.5, -3, -2, 1, 2, 3, 4, 5, 6.0])
        sig = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0])
        df = signals.add_signals(
            self._frame(
                n,
                uptrend=np.ones(n, dtype=bool),
                inside2=inside,
                osc310=osc,
                osc310_sig=sig,
            ),
            arm_window=5,
        )
        # crossed_above(osc, sig) at i=4 (1>0 after -2<=0)
        self.assertTrue(df["long_entry"].iloc[4])

    def test_opposite_osc_cross_exits(self):
        n = 6
        osc = np.array([3, 2, 1, -1, -2, -3.0])
        sig = np.zeros(n)
        df = signals.add_signals(self._frame(n, osc310=osc, osc310_sig=sig))
        self.assertTrue(df["long_exit"].iloc[3])
        self.assertFalse(df["short_exit"].iloc[3])

    def test_boolean_columns(self):
        c = 100.0 + np.cumsum(np.random.RandomState(2).randn(300))
        df = signals.add_signals(indicators.add_indicators(_candles(c, c + 1, c - 1, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)


class TestRaschkeRisk(unittest.TestCase):
    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 90)


if __name__ == "__main__":
    unittest.main()
