"""Fibonacci pullback tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fibonacci_pullback import indicators, risk, signals


def _ohlc(h):
    h = np.asarray(h, dtype=float)
    n = len(h)
    l = h - 1.0
    c = h - 0.2
    o = h - 0.5
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


class TestFibonacciPullback(unittest.TestCase):
    def _series(self, c):
        c = np.asarray(c, dtype=float)
        n = len(c)
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.5
        l = np.minimum(o, c) - 0.5
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame(
            {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
        )

    def test_retracement_levels_hand_computed(self):
        # 12-bar rising series, swing_window=6
        h = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 18]
        df = indicators.add_indicators(_ohlc(h), swing_window=6, sma_n=10)
        # bar 11: swingH = max(h[6..11]) = 20, swingL = min(l[6..11]) = 15
        self.assertAlmostEqual(df["swingH"].iloc[11], 20.0)
        self.assertAlmostEqual(df["swingL"].iloc[11], 15.0)
        self.assertAlmostEqual(df["lretr50"].iloc[11], 17.5)
        self.assertAlmostEqual(df["lretr618"].iloc[11], 20 - 0.618 * 5)
        self.assertAlmostEqual(df["lretr786"].iloc[11], 20 - 0.786 * 5)
        self.assertAlmostEqual(df["sretr382"].iloc[11], 15 + 0.382 * 5)
        self.assertAlmostEqual(df["sretr50"].iloc[11], 17.5)
        # undefined before the window fills
        self.assertTrue(df["swingH"].iloc[:5].isna().all())

    def test_long_entry_fires_on_pullback_reclaim(self):
        # bar 11 above: low 17 dips below lretr50=17.5, holds above
        # lretr786=16.07, closes 17.8 back above lretr618=16.91, and
        # close > 10-bar SMA -> long_entry must fire at bar 11 only
        h = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 18]
        ind = indicators.add_indicators(_ohlc(h), swing_window=6, sma_n=10)
        sig = signals.add_signals(ind)
        self.assertTrue(bool(sig["long_entry"].iloc[11]))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(bool(ind["in_zone_long"].iloc[11]))

    def test_short_entry_fires_on_bounce_rejection(self):
        # mirror: falling series, final bar's high pushes into
        # [sretr382, sretr50] of the down leg, holds below sretr618,
        # and closes back below sretr382, close < 10-bar SMA
        h = [30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 21.5]
        n = len(h)
        l = np.array(h) - 1.0
        c = np.array(h) - 0.2
        c[-1] = 20.5  # rejection: close back below sretr382
        o = np.array(h) - 0.5
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame(
            {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
        )
        ind = indicators.add_indicators(df, swing_window=6, sma_n=10)
        # bar 11: swingH = max(h[6..11]) = 24, swingL = min(l[6..11]) = 19
        self.assertAlmostEqual(ind["swingH"].iloc[11], 24.0)
        self.assertAlmostEqual(ind["swingL"].iloc[11], 19.0)
        self.assertAlmostEqual(ind["sretr382"].iloc[11], 19 + 0.382 * 5)
        self.assertAlmostEqual(ind["sretr618"].iloc[11], 19 + 0.618 * 5)
        sig = signals.add_signals(ind)
        self.assertTrue(bool(sig["short_entry"].iloc[11]))
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertTrue(bool(ind["in_zone_short"].iloc[11]))

    def test_exit_at_swing_extreme(self):
        h = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 20]
        ind = indicators.add_indicators(_ohlc(h), swing_window=6, sma_n=10)
        sig = signals.add_signals(ind)
        # bar 11: c = 19.8 < swingH 20 -> no exit; craft an exit bar:
        h2 = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        ind2 = indicators.add_indicators(_ohlc(h2), swing_window=6, sma_n=10)
        sig2 = signals.add_signals(ind2)
        # bar 11: swingH = max(h2[6..11]) = 21, c = 20.8 < 21 -> still no exit
        self.assertFalse(bool(sig2["long_exit"].iloc[11]))
        exp = (ind2["c"] >= ind2["swingH"]).fillna(False)
        self.assertTrue(bool((sig2["long_exit"] == exp).all()))

    def test_signal_logic_exact_formulas(self):
        n = 500
        i = np.arange(n)
        c = 100.0 + 0.4 * i + 8.0 * np.sin(i / 25.0)
        ind = indicators.add_indicators(self._series(c), swing_window=60, sma_n=200)
        sig = signals.add_signals(ind)
        up = ind["c"] > ind["sma200"]
        dn = ind["c"] < ind["sma200"]
        exp_le = (up & (ind["l"] <= ind["lretr50"]) & (ind["l"] > ind["lretr786"])
                  & (ind["c"] > ind["lretr618"])).fillna(False)
        exp_se = (dn & (ind["h"] >= ind["sretr382"]) & (ind["h"] < ind["sretr618"])
                  & (ind["c"] < ind["sretr382"])).fillna(False)
        exp_lx = (ind["c"] >= ind["swingH"]).fillna(False)
        exp_sx = (ind["c"] <= ind["swingL"]).fillna(False)
        self.assertTrue(bool((sig["long_entry"] == exp_le).all()))
        self.assertTrue(bool((sig["short_entry"] == exp_se).all()))
        self.assertTrue(bool((sig["long_exit"] == exp_lx).all()))
        self.assertTrue(bool((sig["short_exit"] == exp_sx).all()))

    def test_long_entry_fires_on_realistic_pullback(self):
        n = 400
        i = np.arange(n)
        c = 100.0 + 0.6 * i
        dip = np.arange(20)
        c[340:360] = c[340] - 1.2 * dip          # pull back down
        c[360:380] = c[359] + 1.5 * dip          # reclaim up
        sig = signals.add_signals(
            indicators.add_indicators(self._series(c), swing_window=60, sma_n=200)
        )
        self.assertGreater(int(sig["long_entry"].sum()), 0)

    def test_no_lookahead_truncation(self):
        n = 600
        i = np.arange(n)
        c = 100.0 + 0.4 * i + 8.0 * np.sin(i / 25.0)
        full = self._series(c)
        ind_full = indicators.add_indicators(full)
        for j in (300, 550):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("swingH", "lretr618", "sretr382", "sma200"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
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
        n = 500
        i = np.arange(n)
        c = 100.0 + 0.4 * i + 8.0 * np.sin(i / 25.0)
        sig = signals.add_signals(indicators.add_indicators(self._series(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.fibonacci_pullback as mod

        self.assertEqual(mod.SPEC.slug, "fibonacci_pullback")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 100)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 260)


if __name__ == "__main__":
    unittest.main()
