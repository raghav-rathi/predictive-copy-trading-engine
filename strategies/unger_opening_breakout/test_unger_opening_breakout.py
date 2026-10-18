"""Unger opening-breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.unger_opening_breakout import indicators, risk, signals

T0 = int(datetime(2023, 11, 14, tzinfo=timezone.utc).timestamp() * 1000)  # UTC midnight
DAY_MS = 86_400_000


def _ohlcv(o, h, l, c, t0=T0, v=100.0):
    n = len(c)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _range_day(extra_closes=(), short_break=False):
    """Two UTC days: day 0 range [100, 101] on bars 0-2, then extra bars."""
    n = 48
    c = np.full(n, 100.5)
    o = c.copy()
    h = np.full(n, 101.0)
    l = np.full(n, 100.0)
    for k, px in enumerate(extra_closes):
        j = 3 + k
        o[j] = 100.5
        c[j] = px
        h[j] = max(100.5, px) + 0.05
        l[j] = min(100.5, px) - 0.05
    if short_break:  # day 1 (bars 24-26) range [200, 201], break below
        o[24:27] = 200.5
        h[24:27] = 201.0
        l[24:27] = 200.0
        c[24:27] = 200.5
        o[27] = 200.5
        c[27] = 199.2
        h[27] = 200.6
        l[27] = 199.1
    return _ohlcv(o, h, l, c)


class TestUngerOpeningBreakout(unittest.TestCase):
    def test_range_hand_computed(self):
        ind = indicators.add_indicators(_range_day())
        d0 = ind["utc_day"].iloc[0]
        m = ind["utc_day"] == d0
        self.assertTrue((ind["range_high"][m] == 101.0).all())
        self.assertTrue((ind["range_low"][m] == 100.0).all())
        # day positions: bars 0,1,2 form the range, bar 3 is eligible
        self.assertEqual(list(ind["day_pos"].iloc[:4]), [0, 1, 2, 3])

    def test_long_trigger_on_first_close_above_range(self):
        ind = indicators.add_indicators(_range_day(extra_closes=(101.5, 102.0)))
        self.assertTrue(bool(ind["long_trigger"].iloc[3]))
        # second close beyond the range same day is masked: one per side/day
        self.assertFalse(bool(ind["long_trigger"].iloc[4]))
        self.assertEqual(int(ind["long_trigger"].sum()), 1)

    def test_no_trigger_inside_range(self):
        ind = indicators.add_indicators(_range_day(extra_closes=(100.8, 100.2)))
        self.assertEqual(int(ind["long_trigger"].sum()), 0)
        self.assertEqual(int(ind["short_trigger"].sum()), 0)

    def test_short_trigger_mirror(self):
        ind = indicators.add_indicators(_range_day(short_break=True))
        self.assertTrue(bool(ind["short_trigger"].iloc[27]))
        self.assertEqual(int(ind["short_trigger"].sum()), 1)

    def test_range_bars_themselves_cannot_trigger(self):
        # even if bar 2 closes above the eventual range high, ineligible
        n = 48
        c = np.full(n, 100.5)
        o = c.copy()
        h = np.full(n, 101.0)
        l = np.full(n, 100.0)
        c[2] = 101.8
        h[2] = 101.9
        ind = indicators.add_indicators(_ohlcv(o, h, l, c))
        self.assertFalse(bool(ind["long_trigger"].iloc[2]))

    def test_partial_day_has_no_range(self):
        # frame ending mid-day-1: last day has < 3 bars -> NaN, no triggers
        df = _range_day().iloc[:26]
        ind = indicators.add_indicators(df)
        last_day = ind["utc_day"].iloc[-1]
        m = ind["utc_day"] == last_day
        self.assertTrue(ind["range_high"][m].isna().all())
        self.assertEqual(int(ind.loc[m, "long_trigger"].sum()), 0)

    def test_no_lookahead_truncation(self):
        n = 10 * 24
        rng = np.random.default_rng(3)
        rets = rng.normal(0, 0.003, n)
        c = 100.0 * np.exp(np.cumsum(rets))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
        full = _ohlcv(o, h, l, c)
        ind_full = indicators.add_indicators(full)
        for j in (100, 200):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("range_high", "range_low", "long_trigger",
                        "short_trigger", "atr"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                if isinstance(av, (bool, np.bool_)):
                    self.assertEqual(bool(av), bool(bv), (col, j))
                else:
                    self.assertTrue(
                        (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9,
                        (col, j),
                    )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_exits_are_always_false(self):
        # Unger runs no signal exits: stop/trail/max-hold do the work
        ind = indicators.add_indicators(_range_day(extra_closes=(101.5,)))
        sig = signals.add_signals(ind)
        self.assertEqual(int(sig["long_exit"].sum()), 0)
        self.assertEqual(int(sig["short_exit"].sum()), 0)

    def test_registration_imports_cleanly(self):
        import strategies.unger_opening_breakout as mod
        self.assertEqual(mod.SPEC.slug, "unger_opening_breakout")
        self.assertEqual(mod.SPEC.warmup_bars, 48)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 21)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 48)


if __name__ == "__main__":
    unittest.main()
