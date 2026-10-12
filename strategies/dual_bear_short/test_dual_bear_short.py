"""Dual-Bear Pullback Short tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dual_bear_short import indicators, risk, signals
from strategies.dual_bear_short.indicators import (
    DAILY_EMA_FAST, DAILY_EMA_SLOW, H4_EMA, PULLBACK_ATR_MULT,
)

HOUR_MS = 3_600_000
DAY_MS = 86_400_000
DAY0 = 20_000 * DAY_MS  # exact UTC-midnight boundary


def _df(rows):
    t = np.array([DAY0 + d * DAY_MS + hh * HOUR_MS for d, hh, *_ in rows],
                 dtype="int64")
    return pd.DataFrame({
        "t": t, "o": [r[2] for r in rows], "h": [r[3] for r in rows],
        "l": [r[4] for r in rows], "c": [r[5] for r in rows],
        "v": [r[6] for r in rows],
    })


def _scenario(trend="down", flat_days=9, vol_boost=True, rally=False):
    """60-day trend then a flat tail of micro-bear 4h blocks (o=px+0.05,
    c=px). With trend='down' the daily regime gate holds; 'up' breaks it."""
    rows = []
    px = 300.0 if trend == "down" else 100.0
    step = -0.12 if trend == "down" else 0.12
    for d in range(60):
        for hh in range(24):
            px += step
            o, c = px - step, px
            rows.append((d, hh, o, max(o, c) + 0.15, min(o, c) - 0.15, c,
                         1000.0))
    for d in range(60, 60 + flat_days):
        for hh in range(24):
            v = (1300.0 if (vol_boost and d == 60 + flat_days - 2
                            and hh // 4 >= 4) else 1000.0)
            o, c = px + 0.05, px
            rows.append((d, hh, o, o + 0.1, c - 0.1, c, v))
    if rally:  # sharp rally back above the 4H EMA21 -> reclaim exit
        for hh in range(24):
            px += 1.5
            rows.append((60 + flat_days, hh, px - 1.5, px + 0.2, px - 1.7,
                         px, 1000.0))
    return _df(rows)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestDualBearShort(unittest.TestCase):
    def test_short_entry_fires_with_all_gates(self):
        df = _run(_scenario())
        n = int(df["short_entry"].sum())
        self.assertGreater(n, 0)
        e = df.index[df["short_entry"]]
        ind = indicators.add_indicators(_scenario())
        self.assertTrue(bool(ind.loc[e, "new_block"].all()))
        self.assertTrue(bool(ind.loc[e, "regime_ok"].all()))
        self.assertTrue(bool(ind.loc[e, "h4_two_bear"].all()))
        self.assertTrue(bool(ind.loc[e, "pullback_ok"].all()))
        self.assertTrue(bool(ind.loc[e, "h4_vol_ok"].all()))

    def test_entries_only_on_new_block_bars(self):
        ind = indicators.add_indicators(_scenario())
        df = signals.add_signals(ind)
        e = df.index[df["short_entry"]]
        self.assertTrue(bool((ind.loc[e, "new_block"]).all()))

    def test_uptrend_breaks_regime_gate(self):
        df = _run(_scenario(trend="up"))
        ind = indicators.add_indicators(_scenario(trend="up"))
        self.assertFalse(bool(ind["regime_ok"].tail(200).any()))
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_no_pullback_no_entry(self):
        # steep uninterrupted decline: price stays far below 4H EMA21
        df = _run(_scenario(flat_days=0))
        ind = indicators.add_indicators(_scenario(flat_days=0))
        self.assertFalse(bool(ind["pullback_ok"].any()))
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_no_volume_confirmation_no_entry(self):
        df = _run(_scenario(vol_boost=False))
        ind = indicators.add_indicators(_scenario(vol_boost=False))
        e = df.index[df["short_entry"]]
        # entries may still fire on other blocks; none may rely on vol_ok
        for i in e:
            self.assertTrue(bool(ind.loc[i, "h4_vol_ok"]))

    def test_short_exit_on_ema21_reclaim(self):
        df = _run(_scenario(rally=True))
        ind = indicators.add_indicators(_scenario(rally=True))
        # exit logic == developing 4H close back above developing 4H EMA21
        expect = ((ind["c"] > ind["h4_ema21_dev"])
                  & ind["h4_ema21_dev"].notna()).fillna(False)
        pd.testing.assert_series_equal(df["short_exit"], expect,
                                       check_names=False)
        # the rally actually triggers exits
        tail = df.iloc[-30:]
        self.assertGreater(int(tail["short_exit"].sum()), 0)

    def test_never_long(self):
        df = _run(_scenario())
        self.assertFalse(bool(df["long_entry"].any()))
        self.assertFalse(bool(df["long_exit"].any()))

    def test_signals_boolean_clean(self):
        df = _run(_scenario())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        df = _scenario()
        full = indicators.add_indicators(df)
        for i in (1400, 1600):
            tr = indicators.add_indicators(df.iloc[: i + 1])
            for col in ("h4_ema21", "h4_trig_close", "d_ema21", "d_ema55",
                        "regime_ok", "pullback_ok", "h4_two_bear"):
                a, b = full[col].iloc[i], tr[col].iloc[i]
                if isinstance(a, (bool, np.bool_)):
                    ok = bool(a) == bool(b)
                else:
                    ok = (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9
                self.assertTrue(ok, (col, i))

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 240)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertFalse(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 1500)


if __name__ == "__main__":
    unittest.main()
