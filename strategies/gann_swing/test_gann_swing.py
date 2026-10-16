"""Gann swing tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.gann_swing import indicators, risk, signals


def _frame(n, c, v=100.0):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, v)})


def _hl_frame(h, l):
    h = pd.Series(np.asarray(h, float))
    l = pd.Series(np.asarray(l, float))
    c = (h + l) / 2
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    t = (1_700_000_000_000 + np.arange(len(h)) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(len(h), 100.0)})


def _pullback_series():
    # 60 bars of steady rise, 2-bar shallow pullback, resume.
    # The pullback must not break the 3-bar low, so the main trend stays up.
    c = [100.0 + 0.5 * i for i in range(60)]
    c += [129.3, 129.1]
    c += [129.1 + 0.8 * i for i in range(1, 40)]
    h = [x + 0.5 for x in c]
    l = [x - 0.5 for x in c]
    return _hl_frame(h, l)


class TestGannSwing(unittest.TestCase):
    def test_swing_direction_up_down_and_hold(self):
        h = [10, 11, 12, 12, 11, 10]
        l = [9, 10, 11, 11, 10, 9]
        sw = indicators._swing_direction(pd.Series(h, dtype=float),
                                         pd.Series(l, dtype=float))
        self.assertListEqual(sw.tolist(), [0, 1, 1, 1, -1, -1])

    def test_main_trend_flips_on_3bar_break(self):
        # flat, then a 3-bar-high break, then a 3-bar-low break
        h = [10.0] * 10 + [10.1, 10.2, 10.3, 10.4] + [10.4] * 4 + [10.0, 9.9, 9.8, 9.7]
        l = [9.0] * 10 + [9.1, 9.2, 9.3, 9.4] + [9.4] * 4 + [9.0, 8.9, 8.8, 8.7]
        tr = indicators._main_trend(pd.Series(h), pd.Series(l))
        self.assertEqual(tr[13], 1)   # h=10.4 breaks max of prior 3
        self.assertEqual(tr[17], 1)   # holds through the flat top
        self.assertEqual(tr[21], -1)  # l=8.7 breaks min of prior 3

    def test_pullback_long_entry(self):
        df = _pullback_series()
        sig = signals.add_signals(indicators.add_indicators(df))
        longs = sig.index[sig["long_entry"]].tolist()
        self.assertEqual(longs, [62])
        # verify the entry bar's microstructure
        self.assertEqual(sig["gann_trend3"].iloc[62], 1)
        self.assertEqual(sig["gann_swing1"].iloc[62], 1)
        self.assertEqual(sig["gann_swing1"].iloc[61], -1)

    def test_pullback_short_entry_mirror(self):
        df = _pullback_series()
        # invert: negated closes keep h/l structure mirrored
        df2 = df.copy()
        mid = (df["h"] + df["l"]) / 2
        rng = (df["h"] - df["l"]) / 2
        df2["c"] = 2 * mid.iloc[0] - mid
        df2["h"] = df2["c"] + rng
        df2["l"] = df2["c"] - rng
        df2["o"] = pd.Series(np.concatenate(
            [[df2["c"].iloc[0]], df2["c"].iloc[:-1].to_numpy()]))
        sig = signals.add_signals(indicators.add_indicators(df2))
        self.assertTrue(sig["short_entry"].any())
        self.assertFalse(sig["long_entry"].any())

    def test_exits_follow_trend_flip(self):
        df = _pullback_series()
        sig = signals.add_signals(indicators.add_indicators(df))
        # long_exit is exactly the bars where the main trend is down
        pd.testing.assert_series_equal(
            sig["long_exit"], sig["gann_trend3"] == -1, check_names=False)
        pd.testing.assert_series_equal(
            sig["short_exit"], sig["gann_trend3"] == 1, check_names=False)

    def test_signal_columns_bool_no_nan(self):
        n = 400
        rng = np.random.default_rng(21)
        c = 100 + np.cumsum(rng.normal(0, 0.7, n))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_no_lookahead(self):
        n = 400
        rng = np.random.default_rng(23)
        c = 100 + np.cumsum(rng.normal(0, 0.7, n))
        full = indicators.add_indicators(_frame(n, c))
        for k in (200, 399):
            trunc = indicators.add_indicators(_frame(n, c)[:k + 1])
            self.assertEqual(full["gann_swing1"].iloc[k],
                             trunc["gann_swing1"].iloc[k])
            self.assertEqual(full["gann_trend3"].iloc[k],
                             trunc["gann_trend3"].iloc[k])

    def test_registration_and_risk(self):
        import strategies.gann_swing as G
        self.assertEqual(G.SPEC.slug, "gann_swing")
        self.assertEqual(risk.WARMUP, 120)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)


if __name__ == "__main__":
    unittest.main()
