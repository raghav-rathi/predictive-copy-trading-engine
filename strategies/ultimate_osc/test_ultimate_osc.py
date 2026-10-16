"""Ultimate Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ultimate_osc import indicators, risk, signals
from strategies.ultimate_osc.signals import (
    _bull_divergence, _bear_divergence, _fractal_pivots)


def _frame(n, c):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


class TestUltimateOsc(unittest.TestCase):
    def test_uo_bounded_zero_100(self):
        n = 300
        rng = np.random.default_rng(13)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        df = indicators.add_indicators(_frame(n, c))
        uo = df["uo"].dropna()
        self.assertTrue(((uo >= 0.0) & (uo <= 100.0)).all())
        self.assertFalse(uo.empty)

    def test_uo_matches_manual_formula(self):
        n = 60
        rng = np.random.default_rng(17)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        frame = _frame(n, c)
        df = indicators.add_indicators(frame)
        prev_c = frame["c"].shift(1)
        bp = frame["c"] - pd.concat([frame["l"], prev_c], axis=1).min(axis=1)
        tr = (pd.concat([frame["h"], prev_c], axis=1).max(axis=1)
              - pd.concat([frame["l"], prev_c], axis=1).min(axis=1))
        manual = 100.0 * (4 * bp.rolling(7).sum() / tr.rolling(7).sum()
                          + 2 * bp.rolling(14).sum() / tr.rolling(14).sum()
                          + bp.rolling(28).sum() / tr.rolling(28).sum()) / 7.0
        pd.testing.assert_series_equal(df["uo"], manual.clip(0, 100),
                                       check_names=False)

    def test_fractal_pivot_detects_center_extreme(self):
        l = np.full(50, 10.0)
        l[25] = 5.0  # unique minimum centred at 25
        piv = _fractal_pivots(l, 3, "low")
        self.assertIn(25, piv)
        # flat runs manufacture nothing
        self.assertEqual(_fractal_pivots(np.full(50, 10.0), 3, "low"), [])

    def test_bull_divergence_detected(self):
        lows = [50, 100]
        closes = np.full(150, 100.0)
        closes[50], closes[100] = 100.0, 98.0   # lower low
        uo = np.full(150, 45.0)
        uo[50], uo[100], uo[75] = 40.0, 44.0, 25.0  # higher low, dip < 30
        self.assertTrue(_bull_divergence(lows, closes, uo, 100))

    def test_bull_divergence_rejected_cases(self):
        lows = [50, 100]
        closes = np.full(150, 100.0)
        uo = np.full(150, 45.0)
        # no lower low in price
        c2 = closes.copy(); c2[100] = 101.0
        self.assertFalse(_bull_divergence(lows, c2, uo, 100))
        # no higher low in the oscillator
        u2 = uo.copy(); u2[50], u2[100], u2[75] = 44.0, 40.0, 25.0
        self.assertFalse(_bull_divergence(lows, closes, u2, 100))
        # oscillator never dipped under 30
        u3 = uo.copy(); u3[50], u3[100] = 40.0, 44.0
        self.assertFalse(_bull_divergence(lows, closes, u3, 100))

    def test_bear_divergence_detected_and_placed_at_confirmation(self):
        n = 150
        closes = np.full(n, 100.0)
        closes[50], closes[100] = 100.0, 102.0  # higher high
        uo = np.full(n, 55.0)
        uo[50], uo[100], uo[75] = 60.0, 56.0, 65.0  # lower high, peak > 50
        self.assertTrue(
            signals._bear_divergence([50, 100], closes, uo, 100))

    def test_no_lookahead_pivot_uses_future_bars(self):
        # a pivot centred at j is invisible before bar j+k
        l = np.full(100, 10.0)
        l[50] = 5.0
        piv_full = _fractal_pivots(l, 3, "low")
        # with only bars 0..52 visible the pivot at 50 (needs 47..53)
        # cannot exist
        piv_early = _fractal_pivots(l[:53], 3, "low")
        self.assertIn(50, piv_full)
        self.assertNotIn(50, piv_early)

    def test_signal_columns_bool_no_nan(self):
        n = 300
        rng = np.random.default_rng(19)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 120)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.max_hold_bars, 96)

    def test_registration(self):
        import strategies.ultimate_osc as m
        from strategies.registry import REGISTRY
        self.assertIn("ultimate_osc", REGISTRY)
        self.assertIs(REGISTRY["ultimate_osc"], m.SPEC)


if __name__ == "__main__":
    unittest.main()
