"""Woodies CCI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.cci_woodies import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.3):
    c = np.asarray(c, dtype=float)
    n = len(c)
    prev = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": prev,
            "h": np.maximum(c, prev) + spread,
            "l": np.minimum(c, prev) - spread,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


def _v_bottom(n_drop=60):
    """Sharp V: flat, -25 over 5 bars, +25 back over 5 bars. CCI must hook
    below -100 on the drop leg and cross back above 0 -> long entry."""
    c = np.concatenate(
        [
            np.full(n_drop, 100.0),
            100.0 - 5.0 * np.arange(1, 6),
            75.0 + 5.0 * np.arange(1, 6),
            np.full(40, 100.0),
        ]
    )
    return _frame(c)


def _v_top(n_flat=60):
    """Mirror of _v_bottom: +25 spike then back -> short entry."""
    c = np.concatenate(
        [
            np.full(n_flat, 100.0),
            100.0 + 5.0 * np.arange(1, 6),
            125.0 - 5.0 * np.arange(1, 6),
            np.full(40, 100.0),
        ]
    )
    return _frame(c)


def _flat(n=120):
    return _frame(np.full(n, 100.0) + 0.01 * np.arange(n) % 0.0)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestCciWoodies(unittest.TestCase):
    def test_cci_formula_independent_loop(self):
        # Independent pure-Python recomputation of the documented formula:
        # CCI = (TP - SMA14(TP)) / (0.015 * mean14(|TP - SMA14(TP)|)).
        c = np.concatenate([np.full(60, 100.0), [103.0], np.full(30, 103.0)])
        df = indicators.add_indicators(_frame(c, spread=0.2))
        h = df["h"].to_numpy(); l = df["l"].to_numpy(); cc = df["c"].to_numpy()
        tp = (h + l + cc) / 3.0
        last = 60  # the bar of the +3 step
        sma = [sum(tp[i - 13 : i + 1]) / 14.0 for i in range(last - 13, last + 1)]
        devs = [abs(tp[i] - s) for i, s in zip(range(last - 13, last + 1), sma)]
        md = sum(devs) / 14.0
        sma_last = sum(tp[last - 13 : last + 1]) / 14.0
        expect = (tp[last] - sma_last) / (0.015 * md)
        self.assertAlmostEqual(df["cci"].iloc[last], expect, places=6)
        self.assertGreater(df["cci"].iloc[last], 100.0)  # up-step -> extreme +

    def test_long_entry_on_v_bottom(self):
        df = _run(_v_bottom())
        self.assertLess(df["cci_min20"].min(), -100.0)  # hook happened
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        self.assertLessEqual(df["cci"].iloc[i - 1], 0.0)
        self.assertGreater(df["cci"].iloc[i], 0.0)
        self.assertLess(df["cci_min20"].iloc[i], -100.0)

    def test_short_entry_on_inverted_v(self):
        df = _run(_v_top())
        self.assertGreater(df["cci_max20"].max(), 100.0)
        self.assertGreater(int(df["short_entry"].sum()), 0)
        j = int(df.index[df["short_entry"]][0])
        self.assertGreaterEqual(df["cci"].iloc[j - 1], 0.0)
        self.assertLess(df["cci"].iloc[j], 0.0)

    def test_no_entry_without_hook(self):
        # Gentle sine wiggle: CCI crosses 0 but never prints extremes.
        i = np.arange(200)
        c = 100.0 + 0.4 * np.sin(2 * np.pi * i / 25.0)
        df = _run(_frame(c, spread=0.2))
        self.assertGreater((df["cci"] > 0).sum(), 50)  # crosses happened
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_flat_series_no_signals(self):
        df = _run(_flat())
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_exits_follow_zero_line(self):
        # V-bottom (long entry) followed by a slow bleed that pushes CCI
        # back below 0: the long_exit must fire after the entry.
        c = np.concatenate(
            [
                np.full(60, 100.0),
                100.0 - 5.0 * np.arange(1, 6),
                75.0 + 5.0 * np.arange(1, 6),
                100.0 - 0.8 * np.arange(1, 31),
            ]
        )
        df = _run(_frame(c))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        i = int(df.index[df["long_entry"]][0])
        exits = df.index[df["long_exit"]]
        self.assertTrue((exits > i).any())
        j = int(exits[exits > i][0])
        self.assertGreaterEqual(df["cci"].iloc[j - 1], 0.0)
        self.assertLess(df["cci"].iloc[j], 0.0)

    def test_no_lookahead_truncation(self):
        full = _v_bottom()
        ind_full = indicators.add_indicators(full)
        for i in (70, 100):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("cci", "cci_min20", "cci_max20"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )

    def test_signals_boolean_clean(self):
        df = _run(_v_bottom())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)
        self.assertEqual(indicators.N, 14)
        self.assertEqual(indicators.HOOK, 100.0)


if __name__ == "__main__":
    unittest.main()
