"""Heikin-Ashi trend tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.heikin_ashi import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _trend(n=400, drift=0.15, seed=31):
    rng = np.random.default_rng(seed)
    c = 100 + drift * np.arange(n) + rng.normal(0, 0.2, n).cumsum() * 0.2
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.2
    return _ohlcv(o, h, l, c)


def _trend_with_turn(n=400, seed=33):
    """Downtrend first, then an uptrend: the Heikin-Ashi red->green flip at
    the turn is what fires a long entry (Valcu rule: color change)."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:150] = 130 - 0.20 * np.arange(150) + rng.normal(0, 0.15, 150)
    # violent V-turn: +3.0 gap at bar 150 so the HA flip bar has a real body
    c[150:] = c[149] + 3.0 + 0.70 * np.arange(n - 150) + rng.normal(0, 0.15, n - 150)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.2
    return _ohlcv(o, h, l, c)


def _trend_with_turn_dn(n=400, seed=37):
    """Uptrend first, then a downtrend: green->red flip fires a short."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:150] = 70 + 0.20 * np.arange(150) + rng.normal(0, 0.15, 150)
    c[150:] = c[149] - 3.0 - 0.70 * np.arange(n - 150) + rng.normal(0, 0.15, n - 150)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.2
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.2
    return _ohlcv(o, h, l, c)


class TestHeikinAshi(unittest.TestCase):
    def test_uptrend_generates_long_only(self):
        df = signals.add_signals(indicators.add_indicators(_trend_with_turn()))
        self.assertGreater(int(df["long_entry"].sum()), 0)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_downtrend_generates_short_only(self):
        df = signals.add_signals(indicators.add_indicators(_trend_with_turn_dn()))
        self.assertGreater(int(df["short_entry"].sum()), 0)
        self.assertEqual(int(df["long_entry"].sum()), 0)

    def test_no_entries_during_consolidation(self):
        ind = indicators.add_indicators(_trend())
        df = signals.add_signals(ind)
        for i in df.index[df["long_entry"] | df["short_entry"]]:
            self.assertFalse(ind["ha_consol"].iloc[i])

    def test_entry_requires_color_flip(self):
        ind = indicators.add_indicators(_trend_with_turn())
        df = signals.add_signals(ind)
        idx = df.index[df["long_entry"]]
        self.assertGreater(len(idx), 0)
        for i in idx:
            self.assertTrue(ind["ha_red"].iloc[i - 1])
            self.assertTrue(ind["ha_green"].iloc[i])

    def test_reversal_exits_fire(self):
        ind = indicators.add_indicators(_trend_with_turn())
        df = signals.add_signals(ind)
        self.assertGreater(int(df["long_exit"].sum()), 0)
        ind2 = indicators.add_indicators(_trend_with_turn_dn())
        df2 = signals.add_signals(ind2)
        self.assertGreater(int(df2["short_exit"].sum()), 0)

    def test_no_lookahead_truncation(self):
        full = _trend()
        ind_full = indicators.add_indicators(full)
        for i in (100, 300):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("ha_open", "ha_close", "ha_high", "ha_low", "ha_consol"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                if isinstance(a, (bool, np.bool_)):
                    self.assertEqual(bool(a), bool(b))
                else:
                    self.assertTrue((pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_trend()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertGreaterEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
