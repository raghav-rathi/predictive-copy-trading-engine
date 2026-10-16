"""Key-reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.key_reversal import indicators, risk, signals


def _frame(n, o, h, l, c, v=100.0):
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, float),
                         "h": np.asarray(h, float), "l": np.asarray(l, float),
                         "c": np.asarray(c, float),
                         "v": np.full(n, v)})


def _reversal_frame(n=60, direction="bear", vol=300.0):
    # flat base, then a key-reversal bar at index n-1
    o = np.full(n, 100.0)
    h = np.full(n, 101.0)
    l = np.full(n, 99.0)
    c = np.full(n, 100.0)
    v = np.full(n, 100.0)
    if direction == "bear":
        h[-1] = 105.0          # new 20-bar high
        l[-1] = 99.5
        c[-1] = 98.0           # closes below prior bar's low (99.0)
    else:
        l[-1] = 95.0           # new 20-bar low
        h[-1] = 100.5
        c[-1] = 102.0          # closes above prior bar's high (101.0)
    v[-1] = vol                # 3x average -> volume-confirmed
    return _frame(n, o, h, l, c, v)


class TestKeyReversal(unittest.TestCase):
    def test_bearish_reversal_detected(self):
        df = indicators.add_indicators(_reversal_frame(direction="bear"))
        self.assertTrue(df["kr_bear"].iloc[-1])
        self.assertFalse(df["kr_bear"].iloc[:-1].any())

    def test_bullish_reversal_detected(self):
        df = indicators.add_indicators(_reversal_frame(direction="bull"))
        self.assertTrue(df["kr_bull"].iloc[-1])
        self.assertFalse(df["kr_bull"].iloc[:-1].any())

    def test_near_miss_new_high_but_no_close_through(self):
        # new 20-bar high but close stays inside the prior bar's range
        df0 = _reversal_frame(direction="bear")
        df0.loc[df0.index[-1], "c"] = 100.0  # inside prior bar [99, 101]
        df = indicators.add_indicators(df0)
        self.assertFalse(df["kr_bear"].iloc[-1])

    def test_volume_filter_gates_signals(self):
        low_vol = _reversal_frame(direction="bull", vol=100.0)  # = average
        ind = indicators.add_indicators(low_vol)
        self.assertTrue(ind["kr_bull"].iloc[-1])  # pattern present...
        with_f = signals.add_signals(ind, use_volume_filter=True)
        without_f = signals.add_signals(ind, use_volume_filter=False)
        self.assertFalse(with_f["long_entry"].iloc[-1])   # ...but filtered
        self.assertTrue(without_f["long_entry"].iloc[-1])  # unfiltered fires

    def test_confirmed_reversal_fires_with_default(self):
        df = indicators.add_indicators(_reversal_frame(direction="bull"))
        sig = signals.add_signals(df)  # default = volume filter
        self.assertTrue(sig["long_entry"].iloc[-1])

    def test_signal_columns_bool_no_nan(self):
        n = 300
        rng = np.random.default_rng(31)
        c = 100 + np.cumsum(rng.normal(0, 0.7, n))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.05
        l = np.minimum(o, c) - 0.05
        sig = signals.add_signals(
            indicators.add_indicators(_frame(n, o, h, l, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_no_lookahead(self):
        n = 200
        rng = np.random.default_rng(37)
        c = 100 + np.cumsum(rng.normal(0, 0.7, n))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.05
        l = np.minimum(o, c) - 0.05
        base = _frame(n, o, h, l, c)
        full = indicators.add_indicators(base)
        for k in (100, 199):
            trunc = indicators.add_indicators(base[:k + 1])
            self.assertEqual(full["kr_bull"].iloc[k], trunc["kr_bull"].iloc[k])
            self.assertEqual(full["kr_bear"].iloc[k], trunc["kr_bear"].iloc[k])

    def test_registration_and_risk(self):
        import strategies.key_reversal as K
        self.assertEqual(K.SPEC.slug, "key_reversal")
        self.assertEqual(risk.WARMUP, 120)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)


if __name__ == "__main__":
    unittest.main()
