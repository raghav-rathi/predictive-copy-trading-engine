"""Williams A/D tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.williams_ad import indicators, risk, signals
from strategies import base as B


def _df_from_ohlc(o, h, l, c, v=None):
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _df_from_c(c):
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    return _df_from_ohlc(o, h, l, c)


def _hand_wad(o, h, l, c):
    """Reference WAD computed bar by bar."""
    wad = np.zeros(len(c))
    acc = 0.0
    for i in range(1, len(c)):
        pc = c[i - 1]
        if c[i] > pc:
            acc += c[i] - min(pc, l[i])
        elif c[i] < pc:
            acc += c[i] - max(pc, h[i])
        wad[i] = acc
    return wad


class TestWilliamsAd(unittest.TestCase):
    def test_wad_hand_computed(self):
        # hand-checkable 6-bar tape
        c = np.array([100.0, 101.0, 100.5, 102.0, 102.0, 99.0])
        o = np.array([100.0, 100.0, 101.0, 100.5, 102.0, 102.0])
        h = np.array([100.5, 101.5, 101.0, 102.5, 102.5, 102.0])
        l = np.array([99.5, 99.8, 100.0, 100.2, 101.8, 98.5])
        df = indicators.add_indicators(_df_from_ohlc(o, h, l, c))
        exp = _hand_wad(o, h, l, c)
        self.assertTrue(np.allclose(df["wad"].to_numpy(), exp, rtol=1e-12))
        # bar-by-bar spot checks: bar1 up (101 > 100): += 101 - min(100, 99.8) = +1.2
        self.assertAlmostEqual(float(df["wad"].iloc[1]), 1.2, places=12)
        # bar2 down (100.5 < 101): += 100.5 - max(101, 101.0) = -0.5 -> 0.7
        self.assertAlmostEqual(float(df["wad"].iloc[2]), 0.7, places=12)
        # bar4 flat (102 == 102): unchanged
        self.assertAlmostEqual(float(df["wad"].iloc[4]), float(df["wad"].iloc[3]), places=12)
        # bar5 down (99 < 102): += 99 - max(102, 102) = -3
        self.assertAlmostEqual(float(df["wad"].iloc[5]), float(df["wad"].iloc[3]) - 3.0, places=12)

    def test_wad_bar0_is_zero(self):
        n = 30
        c = 100.0 + np.arange(n)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertEqual(float(df["wad"].iloc[0]), 0.0)

    def test_sma_windows_hand_computed(self):
        n = 100
        c = 100.0 + 0.2 * np.arange(n)
        df = indicators.add_indicators(_df_from_c(c))
        wad = df["wad"]
        exp_w = wad.rolling(20, min_periods=20).mean()
        exp_p = pd.Series(c).rolling(50, min_periods=50).mean()
        mask = exp_w.notna()
        self.assertTrue(np.allclose(df["wad_sma20"][mask], exp_w[mask], rtol=1e-12))
        mask = exp_p.notna()
        self.assertTrue(np.allclose(df["price_sma50"][mask], exp_p[mask], rtol=1e-12))
        self.assertTrue(bool(df["wad_sma20"].iloc[:19].isna().all()))
        self.assertTrue(bool(df["price_sma50"].iloc[:49].isna().all()))
        self.assertTrue(bool(df["wad_sma20"].iloc[19:].notna().all()))

    def test_signal_logic_exact_formulas(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.25 * i + 4.0 * np.sin(i / 12.0)
        ind = indicators.add_indicators(_df_from_c(c))
        sig = signals.add_signals(ind)
        x_up = B.crossed_above(ind["wad"], ind["wad_sma20"]).fillna(False)
        x_dn = B.crossed_below(ind["wad"], ind["wad_sma20"]).fillna(False)
        up = (ind["c"] > ind["price_sma50"]).fillna(False)
        dn = (ind["c"] < ind["price_sma50"]).fillna(False)
        self.assertTrue(bool(((sig["long_entry"] == (x_up & up)).fillna(False).all())))
        self.assertTrue(bool(((sig["short_entry"] == (x_dn & dn)).fillna(False).all())))
        self.assertTrue(bool((sig["long_exit"] == x_dn.astype(bool)).all()))
        self.assertTrue(bool((sig["short_exit"] == x_up.astype(bool)).all()))

    def _gated_frame(self, n, above_trend: bool):
        """Deterministic indicator frame: WAD oscillates across a flat
        SMA while price sits entirely above (or below) its SMA50."""
        i = np.arange(n, dtype=float)
        df = indicators.add_indicators(_df_from_c(100.0 + i))
        df["wad"] = 2.0 * np.sin(i / 5.0)      # crosses 0 repeatedly
        df["wad_sma20"] = 0.0
        df["price_sma50"] = 100.0
        df["c"] = 101.0 if above_trend else 99.0
        return df

    def test_long_requires_uptrend(self):
        n = 200
        sig = signals.add_signals(self._gated_frame(n, above_trend=True))
        self.assertGreater(sig["long_entry"].sum(), 0)
        # each long fires exactly on a WAD cross above its SMA
        ind = self._gated_frame(n, above_trend=True)
        x_up = B.crossed_above(ind["wad"], ind["wad_sma20"]).fillna(False)
        self.assertTrue(bool(((sig["long_entry"] == x_up).fillna(False)).all()))
        # same WAD crosses but price below its SMA50: no longs at all
        sig_dn = signals.add_signals(self._gated_frame(n, above_trend=False))
        self.assertEqual(sig_dn["long_entry"].sum(), 0)
        self.assertGreater(sig_dn["short_entry"].sum(), 0)

    def test_accumulation_cross_fires(self):
        # WAD crossing above its SMA in an uptrend fires long entries
        n = 200
        sig = signals.add_signals(self._gated_frame(n, above_trend=True))
        idx = sig.index[sig["long_entry"]]
        self.assertGreater(len(idx), 0)
        ind = self._gated_frame(n, above_trend=True)
        for j in idx:
            self.assertLessEqual(float(ind["wad"].iloc[j - 1]), 0.0)
            self.assertGreater(float(ind["wad"].iloc[j]), 0.0)

    def test_no_lookahead_truncation(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.25 * i + 4.0 * np.sin(i / 12.0)
        full = _df_from_c(c)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (150, 290):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("wad", "wad_sma20", "price_sma50"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9, (col, j)
                )
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_signals_boolean_clean(self):
        n = 300
        i = np.arange(n)
        c = 100.0 + 0.25 * i + 4.0 * np.sin(i / 12.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.williams_ad as mod

        self.assertEqual(mod.SPEC.slug, "williams_ad")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )
        self.assertIn(
            "ctrader.com", mod.SPEC.source_url
        )

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
