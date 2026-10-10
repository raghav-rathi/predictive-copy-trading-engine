"""NR7 tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.nr7 import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _nr7_setup():
    """10 bars; ranges hand-built so bar 7 is the unique NR7 bar."""
    rngs = np.array([5.0, 4.0, 3.0, 2.0, 6.0, 7.0, 8.0, 1.0, 9.0, 9.0])
    c = np.array([100, 101, 102, 103, 102, 101, 100, 100.5, 101, 102], dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + rngs / 2
    l = np.minimum(o, c) - rngs / 2
    # pin bar 7's extremes so the test can break them precisely
    l[7] = 99.5
    h[7] = 100.5  # range stays 1.0
    c[7] = 100.0
    return _ohlcv(o, h, l, c)


def _random_walk(n=500, seed=3):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0, 0.002, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    sp = np.abs(rng.normal(0, 0.0015, n))
    h = np.maximum(o, c) * (1 + sp)
    l = np.minimum(o, c) * (1 - sp)
    return _ohlcv(o, h, l, c)


class TestNR7(unittest.TestCase):
    def test_is_nr7_flags_exactly_narrowest_bar(self):
        df = indicators.add_indicators(_nr7_setup())
        self.assertFalse(df["is_nr7"].iloc[:7].any())
        self.assertTrue(df["is_nr7"].iloc[7])
        self.assertFalse(df["is_nr7"].iloc[8:].any())

    def test_tied_ranges_all_flag(self):
        n = 12
        c = np.full(n, 100.0)
        o = np.full(n, 100.0)
        h = np.full(n, 102.0)
        l = np.full(n, 98.0)  # every range exactly 4.0
        df = indicators.add_indicators(_ohlcv(o, h, l, c))
        self.assertFalse(df["is_nr7"].iloc[:6].any())
        self.assertTrue(df["is_nr7"].iloc[6:].all())

    def test_entry_fires_only_after_nr7_and_break(self):
        raw = _nr7_setup()
        # bar 8 breaks bar 7's high (100.5) with its close
        raw.loc[8, "c"] = 101.0
        df = signals.add_signals(indicators.add_indicators(raw))
        self.assertTrue(df["long_entry"].iloc[8])
        self.assertFalse(df["short_entry"].iloc[8])
        # exits mirror the opposite entry condition: a long break closes shorts
        self.assertFalse(df["long_exit"].iloc[8])
        self.assertTrue(df["short_exit"].iloc[8])

    def test_short_entry_on_low_break(self):
        raw = _nr7_setup()
        raw.loc[8, "c"] = 99.0  # below bar 7's low (99.5)
        df = signals.add_signals(indicators.add_indicators(raw))
        self.assertTrue(df["short_entry"].iloc[8])
        self.assertFalse(df["long_entry"].iloc[8])

    def test_no_entry_on_non_nr7_breakout(self):
        raw = _nr7_setup()
        raw.loc[5, "c"] = raw["h"].iloc[4] + 5.0  # break of a non-NR7 bar's high
        df = signals.add_signals(indicators.add_indicators(raw))
        self.assertFalse(df["long_entry"].iloc[5])
        self.assertFalse(df["short_entry"].iloc[5])
        # close touches but does not break the NR7 high -> no entry
        raw2 = _nr7_setup()
        raw2.loc[8, "c"] = raw2["h"].iloc[7]
        df2 = signals.add_signals(indicators.add_indicators(raw2))
        self.assertFalse(df2["long_entry"].iloc[8])

    def test_both_sides_cannot_trigger(self):
        df = signals.add_signals(indicators.add_indicators(_random_walk()))
        self.assertEqual(int((df["long_entry"] & df["short_entry"]).sum()), 0)
        self.assertEqual(int((df["long_exit"] & df["short_exit"]).sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _random_walk()
        ind_full = indicators.add_indicators(full)
        for i in (120, 400):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("rng", "is_nr7", "nr7_high", "nr7_low", "atr"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b))
                    or (a == b if isinstance(a, (bool, np.bool_)) else abs(a - b) < 1e-9),
                    (col, i),
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_random_walk()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})
            self.assertTrue(df[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
