"""Bill Williams fractal breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.fractal_breakout import indicators, risk, signals
from strategies import base as B


def _df_from_ohlc(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.full(n, 100.0)}
    )


class TestFractalBreakout(unittest.TestCase):
    def test_up_fractal_detected_and_confirmed_late(self):
        # spike high at bar 3 with n=2: strictly above bars 1,2,4,5
        h = [10, 11, 12, 20, 12, 11, 10, 10, 10, 10]
        l = [x - 1 for x in h]
        c = [x - 0.2 for x in h]
        df = indicators.add_indicators(_df_from_ohlc(h, h, l, c), n=2, sma_n=5)
        self.assertTrue(bool(df["up_fractal_bar"].iloc[3]))
        self.assertFalse(bool(df["up_fractal_bar"].iloc[4]))
        # not visible before confirmation bar (3 + 2 = 5)
        self.assertTrue(pd.isna(df["up_level"].iloc[4]))
        self.assertAlmostEqual(df["up_level"].iloc[5], 20.0)
        self.assertAlmostEqual(df["up_level"].iloc[9], 20.0)  # forward-filled

    def test_dn_fractal_detected_and_confirmed_late(self):
        l = [10, 9, 8, 2, 8, 9, 10, 10, 10, 10]
        h = [x + 1 for x in l]
        c = [x + 0.2 for x in l]
        df = indicators.add_indicators(_df_from_ohlc(h, h, l, c), n=2, sma_n=5)
        self.assertTrue(bool(df["dn_fractal_bar"].iloc[3]))
        self.assertTrue(pd.isna(df["dn_level"].iloc[4]))
        self.assertAlmostEqual(df["dn_level"].iloc[5], 2.0)

    def test_tied_highs_are_not_fractals(self):
        # equal highs at bars 2,3: strictness requires a unique max
        h = [10, 11, 20, 20, 11, 10, 10, 10, 10, 10]
        l = [x - 1 for x in h]
        c = [x - 0.2 for x in h]
        df = indicators.add_indicators(_df_from_ohlc(h, h, l, c), n=2, sma_n=5)
        self.assertFalse(bool(df["up_fractal_bar"].iloc[2]))
        self.assertFalse(bool(df["up_fractal_bar"].iloc[3]))
        self.assertTrue(df["up_level"].isna().all())

    def test_long_entry_on_breakout_above_confirmed_level(self):
        n = 40
        c = np.empty(n)
        c[:20] = 100.0 + np.arange(20)          # 100 -> 119
        c[20] = 149.0                           # spike close
        c[21:25] = 125.0                        # pullback
        c[25:] = 125.0 + 2.0 * np.arange(15)    # 125 -> 153, crosses 150
        h = c + 0.5
        h[20] = 150.0                           # strict up-fractal high at bar 20
        l = c - 0.5
        df = indicators.add_indicators(_df_from_ohlc(c, h, l, c), n=2, sma_n=10)
        self.assertTrue(bool(df["up_fractal_bar"].iloc[20]))
        self.assertAlmostEqual(df["up_level"].iloc[22], 150.0)
        sig = signals.add_signals(df)
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        j = idx[0]
        prev_c = df["c"].iloc[j - 1]
        self.assertLessEqual(prev_c, 150.0)
        self.assertGreater(df["c"].iloc[j], 150.0)
        self.assertGreater(df["c"].iloc[j], df["sma200"].iloc[j])

    def test_signal_logic_exact_formulas(self):
        n = 500
        i = np.arange(n)
        c = 100.0 + 0.3 * i + 6.0 * np.sin(i / 20.0)
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.8
        l = np.minimum(o, c) - 0.8
        ind = indicators.add_indicators(_df_from_ohlc(o, h, l, c), n=2, sma_n=200)
        sig = signals.add_signals(ind)
        up = ind["c"] > ind["sma200"]
        dn = ind["c"] < ind["sma200"]
        exp_le = (B.crossed_above(ind["c"], ind["up_level"]) & up).fillna(False)
        exp_se = (B.crossed_below(ind["c"], ind["dn_level"]) & dn).fillna(False)
        exp_lx = (B.crossed_below(ind["c"], ind["up_level"])
                  | B.crossed_below(ind["c"], ind["dn_level"])).fillna(False)
        exp_sx = (B.crossed_above(ind["c"], ind["dn_level"])
                  | B.crossed_above(ind["c"], ind["up_level"])).fillna(False)
        self.assertTrue(bool((sig["long_entry"] == exp_le).all()))
        self.assertTrue(bool((sig["short_entry"] == exp_se).all()))
        self.assertTrue(bool((sig["long_exit"] == exp_lx).all()))
        self.assertTrue(bool((sig["short_exit"] == exp_sx).all()))

    def test_no_lookahead_truncation(self):
        n = 600
        i = np.arange(n)
        c = 100.0 + 0.3 * i + 6.0 * np.sin(i / 20.0)
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.8
        l = np.minimum(o, c) - 0.8
        full = _df_from_ohlc(o, h, l, c)
        ind_full = indicators.add_indicators(full, n=2, sma_n=200)
        for j in (300, 550):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1], n=2, sma_n=200)
            for col in ("up_level", "dn_level", "sma200"):
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
        c = 100.0 + 0.3 * i + 6.0 * np.sin(i / 20.0)
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.8
        l = np.minimum(o, c) - 0.8
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_ohlc(o, h, l, c), n=2, sma_n=200)
        )
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.fractal_breakout as mod

        self.assertEqual(mod.SPEC.slug, "fractal_breakout")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 80)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 260)


if __name__ == "__main__":
    unittest.main()
