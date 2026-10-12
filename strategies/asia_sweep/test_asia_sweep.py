"""Asia Sweep tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.asia_sweep import indicators, risk, signals
from strategies.asia_sweep.signals import DEPTH_ATR_MULT

HOUR_MS = 3_600_000
DAY_MS = 86_400_000
DAY0 = 20_000 * DAY_MS  # exact UTC-midnight boundary


def _bars(rows):
    """rows: list of (day, hour, o, h, l, c, v)."""
    t = np.array([DAY0 + d * DAY_MS + hh * HOUR_MS for d, hh, *_ in rows],
                 dtype="int64")
    return pd.DataFrame({
        "t": t,
        "o": [r[2] for r in rows], "h": [r[3] for r in rows],
        "l": [r[4] for r in rows], "c": [r[5] for r in rows],
        "v": [r[6] for r in rows],
    })


def _flat_day(d, px=100.0, spread=0.2, n=24):
    return [(d, hh, px, px + spread, px - spread, px, 100.0)
            for hh in range(n)]


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestAsiaSweep(unittest.TestCase):
    def _sweep_setup(self, d=2, hour=7, ref=200.0, depth=0.7, long=True):
        """Two quiet uptrend days (bias +1), then day `d` Asia 00-06 with
        exact low=ref, then a sweep bar at `hour`."""
        rows = []
        px = 190.0
        for dd in range(2):
            for hh in range(24):
                px += 0.25
                if dd == 1 and hh == 16:
                    px += 2.5  # acceleration -> close breaks 30-bar high
                rows.append((dd, hh, px - 0.25, px + 0.3, px - 0.3, px, 100.0))
        for hh in range(0, 7):  # Asia session, low exactly ref
            rows.append((d, hh, ref + 0.2, ref + 0.6, ref, ref + 0.3, 100.0))
        if long:
            rows.append((d, hour, ref + 0.4, ref + 0.9, ref - depth,
                         ref + 0.8, 100.0))
        else:
            rows.append((d, hour, ref - 0.4, ref + depth, ref - 0.9,
                         ref - 0.8, 100.0))
        return _bars(rows)

    def test_ref_levels_hand_built(self):
        df = indicators.add_indicators(self._sweep_setup())
        bar = df.iloc[-1]
        self.assertEqual(int(bar["hour"]), 7)
        self.assertAlmostEqual(bar["ref_low"], 200.0)
        self.assertAlmostEqual(bar["ref_high"], 200.6)

    def test_long_entry_on_sweep_and_reclaim(self):
        df = _run(self._sweep_setup())
        bar = df.iloc[-1]
        self.assertEqual(bar["bias"], 1.0)
        self.assertTrue(bool(bar["long_entry"]))
        self.assertFalse(bool(bar["short_entry"]))
        self.assertGreaterEqual(200.0 - bar["l"], DEPTH_ATR_MULT * bar["atr"])

    def test_short_entry_mirror(self):
        # bearish backdrop: downtrend days give bias -1, Asia high exact
        rows = []
        px = 210.0
        for dd in range(2):
            for hh in range(24):
                px -= 0.25
                if dd == 1 and hh == 16:
                    px -= 2.5  # acceleration -> close breaks 30-bar low
                rows.append((dd, hh, px + 0.25, px + 0.3, px - 0.3, px, 100.0))
        ref = 200.0
        for hh in range(0, 7):
            rows.append((2, hh, ref - 0.2, ref, ref - 0.6, ref - 0.3, 100.0))
        for hh in range(7, 12):  # London session, high exactly ref
            rows.append((2, hh, ref - 0.2, ref, ref - 0.6, ref - 0.3, 100.0))
        rows.append((2, 12, ref - 0.4, ref + 0.7, ref - 0.9, ref - 0.8, 100.0))
        df = _run(_bars(rows))
        bar = df.iloc[-1]
        self.assertEqual(bar["bias"], -1.0)
        self.assertAlmostEqual(bar["ref_high"], 200.0)
        self.assertTrue(bool(bar["short_entry"]))
        self.assertFalse(bool(bar["long_entry"]))

    def test_no_entry_outside_window(self):
        df = _run(self._sweep_setup(hour=11))  # 11:00 not a window hour
        self.assertFalse(bool(df.iloc[-1]["long_entry"]))

    def test_skip_1400_utc(self):
        df = _run(self._sweep_setup(hour=14))
        self.assertFalse(bool(df.iloc[-1]["long_entry"]))
        self.assertFalse(bool(df.iloc[-1]["short_entry"]))

    def test_wrong_bias_blocks(self):
        df = _run(self._sweep_setup(long=False))  # bearish candle, bias +1
        self.assertFalse(bool(df.iloc[-1]["short_entry"]))
        self.assertFalse(bool(df.iloc[-1]["long_entry"]))

    def test_shallow_sweep_blocked(self):
        df = _run(self._sweep_setup(depth=0.001))
        self.assertFalse(bool(df.iloc[-1]["long_entry"]))

    def test_kill_at_2000_utc(self):
        rows = _flat_day(0) + _flat_day(1)
        rows.append((2, 20, 100.0, 100.2, 99.8, 100.0, 100.0))
        df = _run(_bars(rows))
        self.assertTrue(bool(df.iloc[-1]["long_exit"]))
        self.assertTrue(bool(df.iloc[-1]["short_exit"]))

    def test_bias_persistence_and_flip(self):
        rows = [(0, hh, 100.0, 100.2, 99.8, 100.0, 100.0) for hh in range(24)]
        rows += [(1, hh, 100.0, 100.2, 99.8, 100.0, 100.0) for hh in range(6)]
        rows.append((1, 6, 100.0, 110.5, 100.0, 110.0, 100.0))   # BOS up
        rows += [(1, hh, 110.0, 110.2, 109.8, 110.0, 100.0) for hh in range(7, 24)]
        rows += [(2, hh, 110.0, 110.2, 109.8, 110.0, 100.0) for hh in range(6)]
        rows.append((2, 6, 110.0, 110.2, 49.0, 50.0, 100.0))     # BOS down
        df = indicators.add_indicators(_bars(rows))
        self.assertEqual(df["bias"].iloc[29], 0.0)    # no break yet
        self.assertEqual(df["bias"].iloc[30], 1.0)    # breakout bar
        self.assertEqual(df["bias"].iloc[45], 1.0)    # persists
        self.assertEqual(df["bias"].iloc[-1], -1.0)   # flipped

    def test_incomplete_session_poisons_ref(self):
        rows = _flat_day(0)
        rows += [(1, hh, 100.0, 100.2, 99.8, 100.0, 100.0) for hh in range(3)]
        rows.append((1, 7, 100.4, 100.9, 99.3, 100.8, 100.0))  # sweep bar
        df = _run(_bars(rows))
        self.assertTrue(pd.isna(df.iloc[-1]["ref_low"]))
        self.assertFalse(bool(df.iloc[-1]["long_entry"]))

    def test_no_lookahead_truncation(self):
        rng = np.random.default_rng(21)
        n = 200
        t = DAY0 + np.arange(n, dtype="int64") * HOUR_MS
        rets = rng.normal(0, 0.003, n)
        c = 100 * np.exp(np.cumsum(rets))
        o = np.concatenate([[100.0], c[:-1]])
        df = pd.DataFrame({"t": t, "o": o,
                           "h": np.maximum(o, c) * 1.002,
                           "l": np.minimum(o, c) * 0.998,
                           "c": c, "v": np.abs(rng.normal(100, 20, n))})
        full = indicators.add_indicators(df)
        for i in (100, 150):
            tr = indicators.add_indicators(df.iloc[: i + 1])
            for col in ("ref_low", "ref_high", "bias", "atr", "hour"):
                a, b = full[col].iloc[i], tr[col].iloc[i]
                ok = (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9
                self.assertTrue(ok, (col, i))

    def test_signals_boolean_clean_and_reversing(self):
        df = _run(self._sweep_setup())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.0)
        self.assertEqual(risk.RISK.target_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
