"""Cup and Handle breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cup_handle import indicators, risk, signals


def _build_cup_df(seed=3, breakout=True, vol_spike=True, deep_handle=False,
                   deep_cup=False, low_rrim=False, no_uptrend=False):
    """Synthetic cup-and-handle: rally to a peak (bar 120), a 16%-deep
    bowl, recovery to a right rim within 5% of the left rim, a shallow
    handle, and a volume-backed breakout close at bar 345."""
    rng = np.random.default_rng(seed)
    n = 440
    c = np.zeros(n)
    for i in range(120):
        c[i] = 100 + 0.12 * i + rng.normal(0, 1.5)
    peak = c[119] + 10.0
    c[119] = peak - 2.0
    c[120] = peak
    depth = (0.30 if deep_cup else 0.13) * peak
    for i in range(121, 191):
        c[i] = peak - depth * (i - 120) / 70 + rng.normal(0, 1.2)
    c[190] = peak - depth
    for i in range(191, 261):
        c[i] = (peak - depth) + (0.88 * peak - (peak - depth)) * (i - 190) / 70 \
            + rng.normal(0, 1.0)
    rrim_target = 0.90 * peak if low_rrim else 0.96 * peak
    for i in range(261, 331):
        c[i] = 0.88 * peak + (rrim_target - 0.88 * peak) * (i - 260) / 70 \
            + rng.normal(0, 1.0)
    slope = 0.55 if deep_handle else 0.07
    for i in range(331, 345):
        c[i] = c[330] - slope * (i - 330) + rng.normal(0, 0.5)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 2.5
    l = np.minimum(o, c) - 2.5
    if breakout:
        c[345] = h[331:345].max() + 1.0
        h[345] = c[345] + 2.5
        l[345] = c[345] - 2.5
    else:
        c[345] = (h[331:345].max() + l[331:345].min()) / 2
        h[345] = max(h[331:345].max(), c[345])
        l[345] = min(l[331:345].min(), c[345])
    for i in range(346, n):
        c[i] = c[i - 1] + rng.normal(0.3, 1.2)
        o[i] = c[i - 1]
        h[i] = max(o[i], c[i]) + 2.5
        l[i] = min(o[i], c[i]) - 2.5
    if no_uptrend:
        c[300:346] -= 12.0
        for i in range(300, n):
            o[i] = c[i - 1]
            h[i] = max(o[i], c[i]) + 2.5
            l[i] = min(o[i], c[i]) - 2.5
        h[345] = max(h[345], c[345] + 2.5)
    v = np.abs(np.full(n, 100.0) + rng.normal(0, 8, n))
    v[345] = 280.0 if vol_spike else 90.0
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v}
    )


def _rand_df(n=600, seed=31):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 1.0
    l = np.minimum(o, c) - 1.0
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


class TestCupHandle(unittest.TestCase):
    def test_full_pattern_fires_entry(self):
        sig = signals.add_signals(indicators.add_indicators(_build_cup_df()))
        entries = sig.index[sig["long_entry"]]
        self.assertEqual(list(entries), [345])

    def test_no_breakout_no_entry(self):
        sig = signals.add_signals(
            indicators.add_indicators(_build_cup_df(breakout=False)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_low_volume_no_entry(self):
        sig = signals.add_signals(
            indicators.add_indicators(_build_cup_df(vol_spike=False)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_deep_handle_no_entry(self):
        sig = signals.add_signals(
            indicators.add_indicators(_build_cup_df(deep_handle=True)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_deep_cup_no_entry(self):
        sig = signals.add_signals(
            indicators.add_indicators(_build_cup_df(deep_cup=True)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_low_right_rim_no_entry(self):
        sig = signals.add_signals(
            indicators.add_indicators(_build_cup_df(low_rrim=True)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_uptrend_no_entry(self):
        sig = signals.add_signals(
            indicators.add_indicators(_build_cup_df(no_uptrend=True)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_uptrend_flag(self):
        ind = indicators.add_indicators(_build_cup_df())
        self.assertTrue(bool(ind["uptrend"].iloc[345]))
        # early in the series the SMA has not spun up
        self.assertFalse(bool(ind["uptrend"].iloc[40]))

    def test_long_only(self):
        sig = signals.add_signals(indicators.add_indicators(_build_cup_df()))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))
        self.assertFalse(bool(sig["long_exit"].any()))
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertTrue(risk.RISK.allow_longs)

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _build_cup_df()
        ind_full = indicators.add_indicators(full)
        j = 400
        ind_tr = indicators.add_indicators(full.iloc[: j + 1])
        for col in ("sma50", "uptrend", "vol_avg20", "atr"):
            av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
            self.assertTrue(
                (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j))
        sig_full = signals.add_signals(ind_full)
        sig_tr = signals.add_signals(ind_tr)
        self.assertEqual(bool(sig_full["long_entry"].iloc[j]),
                         bool(sig_tr["long_entry"].iloc[j]))

    def test_short_series_no_crash(self):
        df = _rand_df(50)
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertFalse(bool(sig[col].any()), col)

    def test_registration_imports_cleanly(self):
        import strategies.cup_handle as mod

        self.assertEqual(mod.SPEC.slug, "cup_handle")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.target_atr_mult, 4.0)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 320)


if __name__ == "__main__":
    unittest.main()
