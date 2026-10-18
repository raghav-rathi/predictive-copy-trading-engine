"""Elder Impulse System tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elder_impulse import indicators, risk, signals


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


def _ema_loop(x, n):
    """Independent Wilder/EMA loop: y[0]=x[0], alpha=2/(n+1), NaN for first n-1."""
    alpha = 2.0 / (n + 1)
    y = np.full(len(x), np.nan)
    acc = x[0]
    for i in range(len(x)):
        acc = x[i] if i == 0 else alpha * x[i] + (1 - alpha) * acc
        if i >= n - 1:
            y[i] = acc
    return y


class TestElderImpulse(unittest.TestCase):
    def test_ema13_hand_computed(self):
        n = 60
        rng = np.random.default_rng(7)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        ind = indicators.add_indicators(_df_from_c(c))
        exp = _ema_loop(c, 13)
        got = ind["impulse_ema"].to_numpy()
        mask = ~np.isnan(exp)
        np.testing.assert_allclose(got[mask], exp[mask], rtol=1e-12)

    def test_macd_hist_hand_computed(self):
        n = 80
        rng = np.random.default_rng(11)
        c = 100 + np.cumsum(rng.normal(0, 0.5, n))
        ind = indicators.add_indicators(_df_from_c(c))
        line = _ema_loop(c, 12) - _ema_loop(c, 26)
        # signal = EMA(9) of the line, seeded from first non-NaN line value
        sig_in = line[~np.isnan(line)]
        sig_full = np.full(n, np.nan)
        sig_full[~np.isnan(line)] = _ema_loop(sig_in, 9)
        exp = line - sig_full
        got = ind["impulse_hist"].to_numpy()
        mask = ~np.isnan(exp)
        np.testing.assert_allclose(got[mask], exp[mask], rtol=1e-9)

    def test_green_bar_long_red_bar_short(self):
        # steady uptrend -> both EMA13 and hist rising -> green -> long only
        n = 200
        i = np.arange(n)
        c = 100.0 + 0.3 * i + 0.05 * np.sin(i / 3.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        post = sig.iloc[120:]
        self.assertGreater(int(post["long_entry"].sum()), 0)
        self.assertEqual(int(post["short_entry"].sum()), 0)
        # every long_entry bar is green, every short_entry bar is red
        self.assertTrue(bool((sig.loc[sig["long_entry"], "impulse_color"] == "green").all()))
        # steady downtrend mirror
        c2 = 100.0 - 0.3 * i + 0.05 * np.sin(i / 3.0)
        sig2 = signals.add_signals(indicators.add_indicators(_df_from_c(c2)))
        post2 = sig2.iloc[120:]
        self.assertGreater(int(post2["short_entry"].sum()), 0)
        self.assertEqual(int(post2["long_entry"].sum()), 0)
        self.assertTrue(bool((sig2.loc[sig2["short_entry"], "impulse_color"] == "red").all()))

    def test_blue_bar_blocks_entries_but_exits(self):
        n = 60
        c = np.full(n, 100.0)  # flat: nothing rises or falls -> all blue
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool((sig["impulse_color"] == "blue").all()))
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)
        # exit on non-green / non-red fires on blue bars
        self.assertTrue(bool(sig["long_exit"].all()))
        self.assertTrue(bool(sig["short_exit"].all()))

    def test_exit_columns_match_color_rule(self):
        n = 200
        rng = np.random.default_rng(5)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        self.assertTrue(bool(((sig["long_exit"]) == (ind["impulse_color"] != "green")).all()))
        self.assertTrue(bool(((sig["short_exit"]) == (ind["impulse_color"] != "red")).all()))

    def test_no_lookahead_truncation(self):
        n = 300
        rng = np.random.default_rng(9)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        full = _df_from_c(c)
        sig_full = signals.add_signals(indicators.add_indicators(full))
        for j in (150, 250):
            sig_tr = signals.add_signals(indicators.add_indicators(full.iloc[: j + 1]))
            ind_full = indicators.add_indicators(full)
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            self.assertEqual(ind_full["impulse_color"].iloc[j], ind_tr["impulse_color"].iloc[j])
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        n = 200
        rng = np.random.default_rng(13)
        c = 100 + np.cumsum(rng.normal(0, 0.4, n))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(sig["impulse_color"].isna().any())
        self.assertTrue(set(sig["impulse_color"].unique()) <= {"green", "red", "blue"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        from strategies import elder_impulse
        from strategies.registry import REGISTRY

        self.assertIs(REGISTRY["elder_impulse"], elder_impulse.SPEC)
        self.assertEqual(elder_impulse.SPEC.slug, "elder_impulse")


if __name__ == "__main__":
    unittest.main()
