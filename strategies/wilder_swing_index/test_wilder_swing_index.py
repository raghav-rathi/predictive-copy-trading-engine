"""Wilder Swing Index / ASI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wilder_swing_index import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _df_from_c(c):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    return _ohlcv(o, h, l, c)


class TestWilderSwingIndex(unittest.TestCase):
    def test_si_hand_computed(self):
        # Bar1: O=101 H=104 L=100 C=103, prev close Cy=101
        # A=H-Cy=3 > Bc=Cy-L=1 -> T=H=104
        # R = 3 - 0.5*(100-101) + 0.25*(101-101) = 3.5
        # K = 0.5*(104-100)/(104-100) = 0.5
        # SI = 50*[(103-101) + 0.5*(103-101) + 0.5*(104-101)]/3.5
        #    = 50*4.5/3.5 = 64.285714...
        df = _ohlcv(
            np.array([100.0, 101.0]),
            np.array([102.0, 104.0]),
            np.array([99.0, 100.0]),
            np.array([101.0, 103.0]),
        )
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["swing_index"].iloc[0], 0.0, places=12)
        self.assertAlmostEqual(ind["swing_index"].iloc[1], 50 * 4.5 / 3.5, places=9)
        self.assertAlmostEqual(ind["asi"].iloc[1], 50 * 4.5 / 3.5, places=9)

    def test_si_down_branch(self):
        # Bar1 gaps down: O=101 H=102 L=96 C=97, Cy=101
        # A=1 < Bc=5 -> T=L=96
        # R = 5 - 0.5*(102-101) + 0.25*(101-101) = 4.5
        # K = 0.5*(max(102,101)-min(96,101))/(102-96) = 0.5*6/6 = 0.5
        # SI = 50*[(97-101) + 0.5*(97-101) + 0.5*(96-101)]/4.5
        #    = 50*(-4 - 2 - 2.5)/4.5 = 50*(-8.5)/4.5
        df = _ohlcv(
            np.array([100.0, 101.0]),
            np.array([102.0, 102.0]),
            np.array([99.0, 96.0]),
            np.array([101.0, 97.0]),
        )
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["swing_index"].iloc[1], 50 * -8.5 / 4.5, places=9)

    def test_limit_move_scores_pm100(self):
        # limit-up day: O=Cy=100, C=H=110, L=100 -> SI = +100
        df = _ohlcv(
            np.array([100.0, 100.0]),
            np.array([100.0, 110.0]),
            np.array([100.0, 100.0]),
            np.array([100.0, 110.0]),
        )
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(ind["swing_index"].iloc[1], 100.0, places=9)
        # limit-down day mirror -> SI = -100
        df2 = _ohlcv(
            np.array([100.0, 100.0]),
            np.array([100.0, 100.0]),
            np.array([100.0, 90.0]),
            np.array([100.0, 90.0]),
        )
        ind2 = indicators.add_indicators(df2)
        self.assertAlmostEqual(ind2["swing_index"].iloc[1], -100.0, places=9)

    def test_flat_bar_no_crash_k_zero(self):
        n = 30
        c = np.full(n, 100.0)
        df = _df_from_c(c)
        # force a zero-range bar mid-series
        df.loc[15, ["o", "h", "l", "c"]] = [100.0, 100.0, 100.0, 100.0]
        ind = indicators.add_indicators(df)
        self.assertFalse(ind["swing_index"].isna().any())
        self.assertFalse(np.isinf(ind["swing_index"].to_numpy()).any())

    def test_asi_is_cumsum_of_si(self):
        n = 100
        rng = np.random.default_rng(4)
        ind = indicators.add_indicators(_df_from_c(100 + np.cumsum(rng.normal(0, 0.5, n))))
        np.testing.assert_allclose(
            ind["asi"].to_numpy(), ind["swing_index"].cumsum().to_numpy(), rtol=1e-12
        )

    def test_breakout_long_and_short(self):
        # sustained rally: ASI makes repeated new 20-bar highs -> long entries
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.4 * i
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        longs = sig.index[sig["long_entry"]]
        self.assertGreater(len(longs), 0)
        j = longs[0]
        self.assertGreater(ind["asi"].iloc[j], ind["asi_prior_high"].iloc[j])
        # sustained decline mirror -> short entries
        c2 = 100.0 - 0.4 * i
        ind2 = indicators.add_indicators(_df_from_c(c2))
        sig2 = signals.add_signals(ind2)
        shorts = sig2.index[sig2["short_entry"]]
        self.assertGreater(len(shorts), 0)
        j2 = shorts[0]
        self.assertLess(ind2["asi"].iloc[j2], ind2["asi_prior_low"].iloc[j2])

    def test_exit_wiring_is_opposite_break(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.3 * np.sin(i / 6.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        # exits are exactly the opposite break by construction
        self.assertTrue(bool(((sig["long_exit"]) == (sig["short_entry"])).all()))
        self.assertTrue(bool(((sig["short_exit"]) == (sig["long_entry"])).all()))

    def test_no_lookahead_truncation(self):
        n = 300
        rng = np.random.default_rng(8)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        full = _df_from_c(c)
        sig_full = signals.add_signals(indicators.add_indicators(full))
        ind_full = indicators.add_indicators(full)
        for j in (150, 250):
            sig_tr = signals.add_signals(indicators.add_indicators(full.iloc[: j + 1]))
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("swing_index", "asi", "asi_prior_high", "asi_prior_low"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                )
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        n = 200
        rng = np.random.default_rng(12)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        from strategies import wilder_swing_index
        from strategies.registry import REGISTRY

        self.assertIs(REGISTRY["wilder_swing_index"], wilder_swing_index.SPEC)
        self.assertEqual(wilder_swing_index.SPEC.slug, "wilder_swing_index")


if __name__ == "__main__":
    unittest.main()
