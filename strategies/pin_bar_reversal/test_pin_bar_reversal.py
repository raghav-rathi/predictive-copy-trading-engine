"""Pin bar reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pin_bar_reversal import indicators, risk, signals


def _bar(o, h, l, c):
    return (o, h, l, c)


def _frame(bars, start_t=1_700_000_000_000):
    n = len(bars)
    arr = np.asarray(bars, dtype=float)
    t = (start_t + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {
            "t": t,
            "o": arr[:, 0],
            "h": arr[:, 1],
            "l": arr[:, 2],
            "c": arr[:, 3],
            "v": np.full(n, 100.0),
        }
    )


def _benign(center, spread=0.5, low_offset=2.0):
    """A non-pin candle: small body, small wicks, no dominant tail."""
    o = center
    c = center + spread * 0.2
    h = center + low_offset * 0.4
    l = center - low_offset
    return _bar(o, h, l, c)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        df = _frame([_benign(100 + i) for i in range(20)])
        ind = indicators.add_indicators(df)
        for col in ("rng", "body", "upper_wick", "lower_wick",
                    "bullish_pin", "bearish_pin", "atr"):
            self.assertIn(col, ind.columns)

    def test_hand_built_bullish_pin_detected(self):
        # rng=12: lower_wick=8 >= 8, body=3 <= 4, upper_wick=1 <= 2.4,
        # l=88 is the 5-bar swing low.
        bars = [
            _benign(98, low_offset=6.0),  # l ~ 92
            _benign(97, low_offset=6.0),  # l ~ 91
            _benign(99, low_offset=6.0),  # l ~ 93
            _benign(96, low_offset=6.0),  # l ~ 90
            _benign(95, low_offset=3.0),  # l ~ 92
            _benign(96, low_offset=5.0),  # l ~ 91
            _benign(97, low_offset=4.0),  # l ~ 93
            _benign(95, low_offset=5.0),  # l ~ 90
            _bar(96.0, 100.0, 88.0, 99.0),  # pin bar
            _benign(99, low_offset=4.0),
        ]
        ind = indicators.add_indicators(_frame(bars))
        self.assertTrue(ind["bullish_pin"].iloc[8])
        self.assertFalse(ind["bearish_pin"].iloc[8])
        self.assertTrue(ind["bullish_pin"].sum() >= 1)

    def test_hand_built_bearish_pin_detected(self):
        # Mirror image: rng=12, upper_wick=8 >= 8, body=3 <= 4,
        # lower_wick=1 <= 2.4, h=112 is the 5-bar swing high.
        bars = [
            _benign(105, low_offset=4.0),
            _benign(106, low_offset=4.0),
            _benign(104, low_offset=4.0),
            _benign(108, low_offset=4.0),
            _benign(105, low_offset=4.0),
            _benign(106, low_offset=4.0),
            _benign(104, low_offset=4.0),
            _benign(107, low_offset=4.0),
            _bar(104.0, 112.0, 100.0, 101.0),  # pin bar
            _benign(101, low_offset=4.0),
        ]
        ind = indicators.add_indicators(_frame(bars))
        self.assertTrue(ind["bearish_pin"].iloc[8])
        self.assertFalse(ind["bullish_pin"].iloc[8])

    def test_tail_boundary_just_under_two_thirds_rejected(self):
        # lower_wick=7.9/12 = 0.658 < 2/3 -> not a pin (everything else ok).
        bars = [_benign(95, low_offset=5.0) for _ in range(8)]
        bars.append(_bar(95.9, 100.0, 88.0, 99.0))
        ind = indicators.add_indicators(_frame(bars))
        self.assertFalse(ind["bullish_pin"].iloc[8])

    def test_body_over_one_third_rejected(self):
        # body=5/12 rng > 1/3 -> not a pin.
        bars = [_benign(95, low_offset=5.0) for _ in range(8)]
        bars.append(_bar(93.0, 100.0, 88.0, 98.0))
        ind = indicators.add_indicators(_frame(bars))
        self.assertFalse(ind["bullish_pin"].iloc[8])

    def test_opposite_wick_over_limit_rejected(self):
        # upper_wick=3/12 = 0.25 > 0.2 -> not a bullish pin.
        bars = [_benign(95, low_offset=5.0) for _ in range(8)]
        bars.append(_bar(96.0, 100.0, 88.0, 97.0))
        ind = indicators.add_indicators(_frame(bars))
        self.assertFalse(ind["bullish_pin"].iloc[8])

    def test_location_filter_pin_not_at_swing_low_rejected(self):
        # Identical pin shape, but a lower low 3 bars earlier -> rejected.
        bars = [
            _benign(95, low_offset=5.0),
            _benign(94, low_offset=5.0),
            _benign(95, low_offset=5.0),
            _benign(96, low_offset=5.0),
            _bar(90.0, 96.0, 80.0, 92.0),  # deeper low INSIDE the 5-bar window
            _benign(95, low_offset=5.0),
            _benign(96, low_offset=5.0),
            _benign(95, low_offset=5.0),
            _bar(96.0, 100.0, 88.0, 99.0),  # pin shape, not swing low
        ]
        ind = indicators.add_indicators(_frame(bars))
        self.assertFalse(ind["bullish_pin"].iloc[8])

    def test_location_filter_bearish_not_at_swing_high_rejected(self):
        bars = [
            _benign(105, low_offset=4.0),
            _benign(106, low_offset=4.0),
            _benign(105, low_offset=4.0),
            _benign(106, low_offset=4.0),
            _bar(108.0, 120.0, 104.0, 110.0),  # higher high INSIDE window
            _benign(105, low_offset=4.0),
            _benign(106, low_offset=4.0),
            _benign(105, low_offset=4.0),
            _bar(104.0, 112.0, 100.0, 101.0),  # pin shape, not swing high
        ]
        ind = indicators.add_indicators(_frame(bars))
        self.assertFalse(ind["bearish_pin"].iloc[8])

    def test_mirror_symmetry(self):
        # Vertically mirroring the price flips bullish pins to bearish pins.
        bars = [_benign(95 + i, low_offset=5.0) for i in range(8)]
        bars.append(_bar(96.0, 100.0, 88.0, 99.0))
        df = _frame(bars)
        ind = indicators.add_indicators(df)
        mir = df.copy()
        mir["o"], mir["c"], mir["h"], mir["l"] = -df["o"], -df["c"], -df["l"], -df["h"]
        mir_ind = indicators.add_indicators(mir)
        pd.testing.assert_series_equal(
            mir_ind["bearish_pin"].reset_index(drop=True),
            ind["bullish_pin"].reset_index(drop=True),
            check_names=False,
        )
        pd.testing.assert_series_equal(
            mir_ind["bullish_pin"].reset_index(drop=True),
            ind["bearish_pin"].reset_index(drop=True),
            check_names=False,
        )

    def test_nan_warmup_first_four_bars_never_pins(self):
        bars = [_bar(96.0, 100.0, 88.0, 99.0)] * 8  # pin shape everywhere
        ind = indicators.add_indicators(_frame(bars))
        self.assertFalse(ind["bullish_pin"].iloc[:4].any())
        self.assertFalse(ind["bearish_pin"].iloc[:4].any())
        # ...but the 5-bar window is complete from bar 4 on
        self.assertTrue(ind["bullish_pin"].iloc[4:].any())

    def test_boolean_no_nan_outputs(self):
        rng = np.random.default_rng(3)
        n = 300
        c = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.01, n)))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.02, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.02, n))
        df = _frame(list(zip(o, h, l, c)))
        ind = indicators.add_indicators(df)
        for col in ("bullish_pin", "bearish_pin"):
            self.assertFalse(ind[col].isna().any(), col)
            self.assertTrue(ind[col].dtype == bool, col)

    def test_flat_bars_never_pins(self):
        bars = [_bar(100.0, 100.0, 100.0, 100.0)] * 12
        ind = indicators.add_indicators(_frame(bars))
        self.assertFalse(ind["bullish_pin"].any())
        self.assertFalse(ind["bearish_pin"].any())

    def test_no_lookahead(self):
        bars = [_benign(95 + (i % 7), low_offset=5.0) for i in range(40)]
        bars[20] = _bar(96.0, 100.0, 88.0, 99.0)
        df = _frame(bars)
        short = indicators.add_indicators(df.iloc[:25].copy())
        long = indicators.add_indicators(df.copy())
        pd.testing.assert_series_equal(
            short["bullish_pin"].reset_index(drop=True),
            long["bullish_pin"].iloc[:25].reset_index(drop=True),
            check_names=False,
        )

    def test_does_not_mutate_input(self):
        df = _frame([_benign(95 + i) for i in range(20)])
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def _sig(self, n=60, seed=11):
        rng = np.random.default_rng(seed)
        c = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.01, n)))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.02, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.02, n))
        df = _frame(list(zip(o, h, l, c)))
        return signals.add_signals(indicators.add_indicators(df))

    def test_entry_exit_mapping(self):
        sig = self._sig()
        pd.testing.assert_series_equal(sig["long_entry"], sig["bullish_pin"],
                                       check_names=False)
        pd.testing.assert_series_equal(sig["short_entry"], sig["bearish_pin"],
                                       check_names=False)
        pd.testing.assert_series_equal(sig["long_exit"], sig["bearish_pin"],
                                       check_names=False)
        pd.testing.assert_series_equal(sig["short_exit"], sig["bullish_pin"],
                                       check_names=False)

    def test_signal_columns_boolean_no_nan(self):
        sig = self._sig()
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(sig[col].dtype == bool, col)

    def test_hand_built_pin_produces_entry(self):
        bars = [_benign(95 + (i % 5), low_offset=5.0) for i in range(8)]
        bars.append(_bar(96.0, 100.0, 88.0, 99.0))   # bullish pin
        bars.append(_bar(104.0, 112.0, 100.0, 101.0))  # bearish pin
        sig = signals.add_signals(indicators.add_indicators(_frame(bars)))
        self.assertTrue(sig["long_entry"].iloc[8])
        self.assertTrue(sig["short_entry"].iloc[9])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertEqual(r.target_atr_mult, 2.0)
        self.assertEqual(r.max_hold_bars, 48)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
