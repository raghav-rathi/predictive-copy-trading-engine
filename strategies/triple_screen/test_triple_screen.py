"""Triple Screen unit tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.triple_screen import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    vv = np.asarray(v, float)
    vv = vv if vv.ndim else np.full(n, float(v))
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float), "v": vv}
    )


def _accel(n=400, seed=5, sign=1.0):
    """200 flat bars, then exponential acceleration (sign flips it down).

    The 4h MACD-histogram slope is positive during the acceleration phase
    and ~zero/negative once the move is established (documented oscillator
    behavior, not a bug)."""
    rng = np.random.default_rng(seed)
    base = np.concatenate(
        [np.zeros(200), sign * 100.0 * (np.exp(0.0015 * np.arange(n - 200)) - 1.0)]
    )
    c = 100.0 + base + rng.normal(0, 0.02, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.02
    l = np.minimum(o, c) - 0.02
    return _ohlcv(o, h, l, c)


class TestTripleScreen(unittest.TestCase):
    def test_tide_nan_until_first_closed_4h_bar(self):
        df = indicators.add_indicators(_accel())
        self.assertTrue(df["tide_slope"].iloc[:8].isna().all())

    def test_tide_tracks_acceleration_phase(self):
        df = indicators.add_indicators(_accel())
        s = df["tide_slope"]
        # acceleration phase: tide overwhelmingly positive
        self.assertGreater((s.iloc[200:260] > 0).mean(), 0.9)
        # flat phase: tide not positive
        self.assertLess((s.iloc[40:120] > 0).mean(), 0.1)

    def test_tide_uses_closed_4h_bars_only(self):
        raw = _accel(300)
        df = indicators.add_indicators(raw)
        r4 = indicators._resample_4h(raw)
        m = B.macd(r4["c"], 12, 26, 9)
        slope = (m["macd_hist"] - m["macd_hist"].shift(1)).shift(1)
        i = 220
        closed = r4[r4["t"] <= raw["t"].iloc[i]]
        expect = slope.loc[closed.index[-1]]
        self.assertAlmostEqual(df["tide_slope"].iloc[i], expect, places=9)

    def test_no_long_when_tide_down(self):
        # inject an FI2 dip while the tide is forced down: no longs allowed
        df = indicators.add_indicators(_accel())
        df["fi2"] = pd.Series(np.where(np.arange(len(df)) == 250, -1.0, 0.5),
                              index=df.index)
        df["tide_slope"] = -0.01  # falling tide everywhere
        df["tide_up"] = df["tide_slope"] > 0
        df["tide_dn"] = df["tide_slope"] < 0
        df = signals.add_signals(df)
        self.assertFalse(df["long_entry"].any())

    def test_entry_logic_conjunction(self):
        # FI2 dips below zero during a rising tide and bar 51 takes out the
        # prior high -> exactly one long entry; mirror for shorts.
        n = 60
        df = _ohlcv(np.ones(n) * 100, np.ones(n) * 101, np.ones(n) * 99,
                    np.ones(n) * 100)
        df = indicators.add_indicators(df)
        df["fi2"] = pd.Series(np.where(np.arange(n) == 50, -1.0, 0.5),
                              index=df.index)
        df["fi13"] = 1.0
        df["tide_slope"] = 0.01
        df["tide_up"] = True
        df["tide_dn"] = False
        df.loc[50, "h"] = 101.5  # takes out bar 49's high on the dip bar
        df = signals.add_signals(df)
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertTrue(df["long_entry"].iloc[50])
        # short mirror
        df2 = indicators.add_indicators(
            _ohlcv(np.ones(n) * 100, np.ones(n) * 101, np.ones(n) * 99,
                   np.ones(n) * 100))
        df2["fi2"] = pd.Series(np.where(np.arange(n) == 50, 1.0, -0.5),
                               index=df2.index)
        df2["fi13"] = -1.0
        df2["tide_slope"] = -0.01
        df2["tide_up"] = False
        df2["tide_dn"] = True
        df2.loc[50, "l"] = 98.5  # undercuts bar 49's low on the pop bar
        df2 = signals.add_signals(df2)
        self.assertEqual(int(df2["short_entry"].sum()), 1)
        self.assertTrue(df2["short_entry"].iloc[50])

    def test_sparse_trades(self):
        df = signals.add_signals(indicators.add_indicators(_accel(800)))
        entries = int(df["long_entry"].sum() + df["short_entry"].sum())
        self.assertLess(entries, 60, f"too many entries: {entries}")

    def test_no_lookahead(self):
        raw = _accel(300)
        df_full = signals.add_signals(indicators.add_indicators(raw))
        df_tr = signals.add_signals(indicators.add_indicators(raw.iloc[:-1]))
        for col in ("tide_slope", "fi2", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            a = df_full[col].iloc[:-1].fillna(-999.0).to_numpy()
            b = df_tr[col].fillna(-999.0).to_numpy()
            self.assertTrue(np.allclose(a, b, equal_nan=True),
                            f"lookahead leak in {col}")

    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertGreaterEqual(risk.WARMUP, 150)
        self.assertEqual(risk.RISK.max_hold_bars, 336)


if __name__ == "__main__":
    unittest.main()
