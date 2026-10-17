"""Market-structure tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.market_structure import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.2):
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


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestMarketStructure(unittest.TestCase):
    def test_swing_high_is_local_max(self):
        c = np.array([1, 2, 3, 2, 1, 2, 3, 4, 3, 2, 1], dtype=float)
        df = indicators.add_indicators(_frame(c, spread=0.0))
        # local max at index 7 must be flagged as a swing high
        self.assertTrue(bool(df["swing_high"].iloc[7]))

    def test_bos_fires_on_close_through_level(self):
        # oscillating range, then a decisive close above the last swing high
        t = np.arange(60)
        rnge = 100 + 0.4 * np.sin(t / 3.0)
        c = np.concatenate([rnge, [101.5] * 8])
        df = _run(_frame(c, spread=0.05))
        self.assertTrue(bool(df["bos_up"].any()))
        # the BOS bar's close really is above a confirmed swing high
        bos_idx = int(np.where(df["bos_up"])[0][0])
        sh = df.loc[df["swing_high"], "h"]
        self.assertLess(float(sh[sh.index < bos_idx - 2].iloc[-1]), float(df["c"].iloc[bos_idx]))

    def test_choch_after_reversal(self):
        # up leg with pullbacks (swing lows form), then a sharp down leg
        # breaking the last swing low: choch_dn + short entry
        t = np.arange(80)
        up = 100 + 0.3 * t + 1.5 * np.sin(t / 2.0)
        dn = up[-1] - 1.2 * np.arange(60)
        df = _run(_frame(np.concatenate([up, dn]), spread=0.05))
        self.assertTrue(bool(df["choch_dn"].any()))
        self.assertTrue(bool(df["short_entry"].any()))
        self.assertEqual(int(df["ms_direction"].iloc[-1]), -1)

    def test_direction_persistence(self):
        # direction stays +1 through a shallow pullback that holds structure
        t = np.arange(80)
        up = 100 + 0.3 * t + 1.5 * np.sin(t / 2.0)
        pb = up[-1] - 0.05 * np.arange(25)  # shallow drift, no BOS down
        df = indicators.add_indicators(_frame(np.concatenate([up, pb]), spread=0.05))
        self.assertFalse(bool(df["bos_dn"].any()))
        tail = df["ms_direction"].iloc[-5:]
        self.assertTrue(bool((tail == 1.0).all()))

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(71)
        c = 100 + np.cumsum(rng.normal(0, 0.8, 300))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        # pivot confirmation lag: truncating must not change BOS flags at
        # bar 199 beyond what the RIGHT=2 lag allows
        trunc = _run(_frame(c[:200]))
        self.assertEqual(bool(df["bos_up"].iloc[197]), bool(trunc["bos_up"].iloc[197]))


if __name__ == "__main__":
    unittest.main()
