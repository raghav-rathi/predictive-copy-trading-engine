"""Awesome Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.awesome_oscillator import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _df_from_c(c):
    """Degenerate bars with fixed 0.05 spread so median == close."""
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    return _ohlcv(o, h, l, c)


class TestAwesomeOscillator(unittest.TestCase):
    def test_ao_formula_hand_computed(self):
        # median = (h+l)/2; AO = SMA5 - SMA34, hand-computed at the end
        n = 40
        med = np.linspace(100.0, 120.0, n)
        h = med + 1.0
        l = med - 1.0
        o = np.concatenate([[med[0]], med[:-1]])
        df = indicators.add_indicators(_ohlcv(o, h, l, med))
        got = df["ao"].iloc[-1]
        exp = med[-5:].mean() - med[-34:].mean()
        self.assertAlmostEqual(got, exp, places=9)

    def test_zero_cross_fires_long(self):
        n = 120
        i = np.arange(n)
        a = np.where(i < 80, -0.05 * i, -4.0 + 0.25 * (i - 80))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(100.0 + a)))
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        j = idx[0]
        ao = indicators.add_indicators(_df_from_c(100.0 + a))["ao"]
        self.assertLessEqual(ao.iloc[j - 1], 0)
        self.assertGreater(ao.iloc[j], 0)

    def test_zero_cross_fires_short_mirror(self):
        n = 120
        i = np.arange(n)
        a = np.where(i < 80, 0.05 * i, 4.0 - 0.25 * (i - 80))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(100.0 + a)))
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        j = idx[0]
        ao = indicators.add_indicators(_df_from_c(100.0 + a))["ao"]
        self.assertGreaterEqual(ao.iloc[j - 1], 0)
        self.assertLess(ao.iloc[j], 0)

    def test_saucer_requires_three_bars_above_zero_middle_lowest(self):
        n = 200
        i = np.arange(n)
        a = 0.10 * i + 0.25 * np.sin(i / 2.2)
        ind = indicators.add_indicators(_df_from_c(100.0 + a))
        sig = signals.add_signals(ind)
        idx = sig.index[sig["bull_saucer"]]
        self.assertGreater(len(idx), 0)
        for j in idx:
            trip = ind["ao"].to_numpy()[j - 2 : j + 1]
            self.assertTrue(bool((trip > 0).all()))
            self.assertGreater(trip[0], trip[1])
            self.assertLess(trip[1], trip[2])

    def test_saucer_rejects_bar_below_zero(self):
        # hand-set a fake AO triple: one bar below zero must not fire
        n = 50
        df = indicators.add_indicators(
            _df_from_c(100.0 + np.zeros(n))
        ).copy()
        ao = np.full(n, 1.0)
        ao[20], ao[21], ao[22] = 1.3, -0.5, 1.4
        df["ao"] = ao
        df["bull_saucer"] = (
            (df["ao"] > 0)
            & (df["ao"].shift(1) > 0)
            & (df["ao"].shift(2) > 0)
            & (df["ao"].shift(2) > df["ao"].shift(1))
            & (df["ao"].shift(1) < df["ao"])
        ).fillna(False)
        self.assertFalse(bool(df["bull_saucer"].iloc[22]))

    def test_twin_peaks_fires_on_rising_troughs_below_zero(self):
        n = 140
        i = np.arange(n)
        a = -0.05 * i
        a[88:93] -= 3.0 * np.exp(-0.5 * ((np.arange(88, 93) - 90) / 1.2) ** 2)
        a[113:118] -= 1.6 * np.exp(-0.5 * ((np.arange(113, 118) - 115) / 1.2) ** 2)
        ind = indicators.add_indicators(_df_from_c(100.0 + a))
        idx = ind.index[ind["bull_twin_peaks"]]
        self.assertGreater(len(idx), 0)
        # every firing bar: AO rising, and the two troughs in-window
        # are below zero with the second higher
        for j in idx:
            ao = ind["ao"].to_numpy()
            self.assertGreater(ao[j], ao[j - 1])
            self.assertLessEqual(ao[j - 29 : j + 1].max(), 0)

    def test_twin_peaks_blocked_by_zero_cross_between_troughs(self):
        n = 140
        i = np.arange(n)
        a = -0.05 * i
        a[88:93] -= 3.0 * np.exp(-0.5 * ((np.arange(88, 93) - 90) / 1.2) ** 2)
        # strong up-leg between the troughs pushes AO above zero
        a[100:110] += 6.0
        a[113:118] -= 1.6 * np.exp(-0.5 * ((np.arange(113, 118) - 115) / 1.2) ** 2)
        ind = indicators.add_indicators(_df_from_c(100.0 + a))
        self.assertEqual(int(ind["bull_twin_peaks"].sum()), 0)

    def test_exit_on_opposite_cross(self):
        n = 120
        i = np.arange(n)
        a = np.where(i < 80, -0.05 * i, -4.0 + 0.25 * (i - 80))
        ind = indicators.add_indicators(_df_from_c(100.0 + a))
        sig = signals.add_signals(ind)
        # long_entry on cross up, long_exit exactly on cross down
        self.assertTrue(
            bool((sig["long_exit"] == ((ind["ao"].shift(1) >= 0) & (ind["ao"] < 0)).fillna(False)).all())
        )
        self.assertGreater(int(sig["long_exit"].sum()) + int(sig["short_exit"].sum()), -1)

    def test_no_lookahead_truncation(self):
        n = 300
        i = np.arange(n)
        a = 0.10 * i + 0.25 * np.sin(i / 2.2)
        full = _df_from_c(100.0 + a)
        ind_full = indicators.add_indicators(full)
        for j in (150, 250):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("ao", "bull_saucer", "bull_twin_peaks"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                if isinstance(av, (bool, np.bool_)):
                    self.assertEqual(bool(av), bool(bv), (col, j))
                else:
                    self.assertTrue(
                        (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                    )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        n = 200
        i = np.arange(n)
        a = 0.10 * i + 0.25 * np.sin(i / 2.2)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(100.0 + a)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "bull_saucer", "bear_saucer", "bull_twin_peaks", "bear_twin_peaks"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 70)


if __name__ == "__main__":
    unittest.main()
