"""Twiggs Money Flow tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.twiggs_money_flow import indicators, risk, signals
from strategies import base as B


def _df(o, h, l, c, v=None):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _trend_df(n=400, slope=0.3):
    i = np.arange(n)
    c = 100.0 + slope * i + np.sin(i / 9.0)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    return _df(o, h, l, c)


class TestTwiggsMoneyFlow(unittest.TestCase):
    def test_mf_hand_computed(self):
        df = _trend_df(300)
        ind = indicators.add_indicators(df)
        h, l, c, v = df["h"], df["l"], df["c"], df["v"]
        prev_c = c.shift(1)
        tr = pd.concat([h - l, (h - prev_c).abs(), (l - prev_c).abs()], axis=1).max(axis=1)
        exp_mf = np.where(tr.to_numpy() > 0,
                          v.to_numpy() * (2 * c - h - l).to_numpy() / tr.to_numpy(), 0.0)
        got = ind["tmf_mf"].to_numpy()
        self.assertTrue(np.allclose(got, exp_mf, rtol=1e-9, atol=1e-12))

    def test_true_range_uses_gap(self):
        # a gap-up bar: true range must be the gap, not h-l
        n = 60
        c = np.full(n, 100.0)
        o, h, l = c.copy(), np.full(n, 100.5), np.full(n, 99.5)
        # bar 30 closes at 100; bar 31 gaps up to 115 with a 1.0-wide range
        o[31], h[31], l[31], c[31] = 115.0, 115.5, 114.5, 115.0
        ind = indicators.add_indicators(_df(o, h, l, c))
        tr = ind["tmf_trange"]
        # bar 31 trange = max(1.0, |115.5-100|, |114.5-100|) = 15.5 (the gap)
        self.assertAlmostEqual(float(tr.iloc[31]), 15.5)
        # no-gap bar: trange = h - l
        self.assertAlmostEqual(float(tr.iloc[10]), 1.0)

    def test_divide_by_zero_guard(self):
        # perfectly flat market: trange = 0 -> mf = 0, no NaN/inf
        n = 100
        c = np.full(n, 100.0)
        df = _df(c, c, c, c, v=np.full(n, 50.0))
        ind = indicators.add_indicators(df)
        self.assertTrue((ind["tmf_trange"] == 0).all())
        self.assertTrue((ind["tmf_mf"] == 0).all())
        self.assertFalse(np.isinf(ind["tmf_mf"]).any())

    def test_tmf_is_wilder_ratio_hand_computed(self):
        df = _trend_df(300)
        ind = indicators.add_indicators(df)
        mf_w = ind["tmf_mf"].ewm(alpha=1.0 / 21, adjust=False, min_periods=21).mean()
        v_w = df["v"].ewm(alpha=1.0 / 21, adjust=False, min_periods=21).mean()
        exp = mf_w / v_w.replace(0, np.nan)
        got = ind["tmf"]
        mask = exp.notna()
        self.assertTrue(np.allclose(got[mask], exp[mask], rtol=1e-9))

    def test_period_parameter(self):
        df = _trend_df(200)
        ind10 = indicators.add_indicators(df, period=10)
        ind21 = indicators.add_indicators(df)
        self.assertFalse(ind10["tmf"].dropna().equals(ind21["tmf"].dropna()))

    def _two_phase_df(self, n=400, first_up=False):
        # first half: close pinned to one extreme (outflow), second half to the
        # other (inflow) -> TMF must cross zero exactly once
        i = np.arange(n)
        half = n // 2
        if first_up:
            c = np.where(i < half, 100.0 + 0.6 * i, 220.0 - 0.9 * (i - half))
        else:
            c = np.where(i < half, 100.0 - 0.6 * i, -20.0 + 0.9 * (i - half))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.empty(n)
        l = np.empty(n)
        for j in range(n):
            if (j < half) != first_up:
                # distribution: close pinned at the low -> negative money flow
                l[j] = c[j] - 1.0
                h[j] = max(o[j], c[j]) + 2.0
            else:
                # accumulation: close pinned at the high -> positive money flow
                h[j] = c[j] + 1.0
                l[j] = min(o[j], c[j]) - 2.0
        return _df(o, h, l, c)

    def test_cross_above_zero_fires_long(self):
        df = self._two_phase_df(first_up=False)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        tmf = ind["tmf"]
        for j in idx:
            self.assertLessEqual(tmf.iloc[j - 1], 0.0)
            self.assertGreater(tmf.iloc[j], 0.0)

    def test_cross_below_zero_fires_short(self):
        df = self._two_phase_df(first_up=True)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        idx = sig.index[sig["short_entry"]]
        self.assertGreater(len(idx), 0)
        tmf = ind["tmf"]
        for j in idx:
            self.assertGreaterEqual(tmf.iloc[j - 1], 0.0)
            self.assertLess(tmf.iloc[j], 0.0)

    def test_signal_logic_exact_formulas(self):
        df = _trend_df(400)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        tmf, prev = ind["tmf"], ind["tmf"].shift(1)
        self.assertTrue(bool(
            (sig["long_entry"] == ((prev <= 0) & (tmf > 0)).fillna(False)).all()))
        self.assertTrue(bool(
            (sig["short_entry"] == ((prev >= 0) & (tmf < 0)).fillna(False)).all()))
        self.assertTrue(bool(
            (sig["long_exit"] == ((prev >= 0) & (tmf < 0)).fillna(False)).all()))
        self.assertTrue(bool(
            (sig["short_exit"] == ((prev <= 0) & (tmf > 0)).fillna(False)).all()))

    def test_no_lookahead_truncation(self):
        df = _trend_df(600)
        ind_full = indicators.add_indicators(df)
        for j in (300, 550):
            ind_tr = indicators.add_indicators(df.iloc[: j + 1])
            for col in ("tmf_trange", "tmf_mf", "tmf"):
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
        sig = signals.add_signals(indicators.add_indicators(_trend_df(500)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.twiggs_money_flow as mod

        self.assertEqual(mod.SPEC.slug, "twiggs_money_flow")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertIn("mql5.com/en/market/product/451", mod.SPEC.source_url)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
