"""CVD divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cvd_divergence import indicators, risk, signals


def _df_from_ohlc(o, h, l, c, v=None):
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _indicator_frame(n, piv_lows=(), piv_highs=(), c=None, cvd=None):
    """Hand-built post-indicator frame: bare t/o/h/l/c/v plus the
    indicator columns add_signals consumes."""
    cc = np.arange(n, dtype=float) if c is None else np.asarray(c, dtype=float)
    vv = np.zeros(n) if cvd is None else np.asarray(cvd, dtype=float)
    df = _df_from_ohlc(cc, cc + 1.0, cc - 1.0, cc)
    df["delta"] = 0.0
    df["cvd"] = vv
    df["pivot_low"] = False
    df["pivot_high"] = False
    df.loc[list(piv_lows), "pivot_low"] = True
    df.loc[list(piv_highs), "pivot_high"] = True
    df["atr"] = 1.0
    return df


class TestCvdDivergence(unittest.TestCase):
    def test_delta_formula_hand_computed(self):
        # close at high -> loc = +1 -> delta = +v
        c = np.array([10.0, 11.0, 10.5])
        o = np.array([10.0, 10.0, 11.0])
        h = np.array([10.5, 11.0, 11.0])
        l = np.array([9.5, 10.0, 10.0])
        v = np.array([100.0, 200.0, 150.0])
        df = indicators.add_indicators(_df_from_ohlc(o, h, l, c, v))
        # bar1: (2*11 - 11 - 10)/(11 - 10) = 1 -> +200
        self.assertAlmostEqual(float(df["delta"].iloc[1]), 200.0, places=9)
        # bar0: (2*10 - 10.5 - 9.5)/(10.5 - 9.5) = 0 -> 0
        self.assertAlmostEqual(float(df["delta"].iloc[0]), 0.0, places=9)
        # bar2: (2*10.5 - 11 - 10)/(11 - 10) = 0 -> 0
        self.assertAlmostEqual(float(df["delta"].iloc[2]), 0.0, places=9)

    def test_delta_zero_range_guard(self):
        # h == l (doji with no range): no divide-by-zero, delta = 0
        c = np.array([10.0, 10.0, 10.0])
        o = np.array([10.0, 10.0, 10.0])
        h = np.array([10.0, 10.0, 10.0])
        l = np.array([10.0, 10.0, 10.0])
        v = np.array([100.0, 200.0, 300.0])
        df = indicators.add_indicators(_df_from_ohlc(o, h, l, c, v))
        self.assertTrue(bool((df["delta"] == 0.0).all()))
        self.assertFalse(df["delta"].isna().any())
        self.assertFalse(df["cvd"].isna().any())

    def test_cvd_is_cumsum_of_delta(self):
        n = 60
        i = np.arange(n)
        c = 100.0 + np.sin(i / 5.0)
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(_df_from_ohlc(o, c + 0.4, c - 0.4, c))
        self.assertTrue(np.allclose(df["cvd"], df["delta"].cumsum(), rtol=1e-12))

    def test_pivot_detection(self):
        # unique V bottom at bar 15 inside a 10-bar window
        n = 40
        c = np.full(n, 100.0)
        c[15] = 90.0
        o = np.concatenate([[c[0]], c[:-1]])
        df = indicators.add_indicators(_df_from_ohlc(o, c + 0.5, c - 0.5, c))
        self.assertTrue(bool(df["pivot_low"].iloc[15]))
        # a flat plateau is not a unique min: no pivots
        self.assertFalse(bool(df["pivot_low"].iloc[5]))
        # unique top at bar 25
        c2 = np.full(n, 100.0)
        c2[25] = 110.0
        df2 = indicators.add_indicators(
            _df_from_ohlc(np.concatenate([[c2[0]], c2[:-1]]), c2 + 0.5, c2 - 0.5, c2)
        )
        self.assertTrue(bool(df2["pivot_high"].iloc[25]))

    def test_bullish_divergence_fires(self):
        # pivot lows at bars 10 and 20: price lower low, CVD higher low
        n = 30
        c = np.full(n, 100.0)
        c[10] = 95.0
        c[20] = 94.0  # lower low
        cvd = np.zeros(n)
        cvd[10] = -50.0
        cvd[20] = -40.0  # higher low
        df = _indicator_frame(n, piv_lows=(10, 20), c=c, cvd=cvd)
        sig = signals.add_signals(df, lookback=60)
        self.assertTrue(bool(sig["long_entry"].iloc[20]))
        self.assertFalse(bool(sig["short_entry"].iloc[20]))
        # exits mirror the opposite divergence: a bullish divergence
        # exits an open short, so short_exit is True on the same bar
        self.assertTrue(bool(sig["short_exit"].iloc[20]))

    def test_bearish_divergence_fires(self):
        n = 30
        c = np.full(n, 100.0)
        c[10] = 105.0
        c[20] = 106.0  # higher high
        cvd = np.zeros(n)
        cvd[10] = 50.0
        cvd[20] = 40.0  # lower high
        df = _indicator_frame(n, piv_highs=(10, 20), c=c, cvd=cvd)
        sig = signals.add_signals(df, lookback=60)
        self.assertTrue(bool(sig["short_entry"].iloc[20]))
        self.assertFalse(bool(sig["long_entry"].iloc[20]))

    def test_no_divergence_no_signal(self):
        # both make lower lows: no divergence -> no entries anywhere
        n = 30
        c = np.full(n, 100.0)
        c[10] = 95.0
        c[20] = 94.0
        cvd = np.zeros(n)
        cvd[10] = -40.0
        cvd[20] = -50.0  # lower low too: confirming, not diverging
        df = _indicator_frame(n, piv_lows=(10, 20), c=c, cvd=cvd)
        sig = signals.add_signals(df, lookback=60)
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_lookback_cutoff(self):
        # pivots 70 bars apart: outside the 60-bar window -> no signal
        n = 90
        c = np.full(n, 100.0)
        c[10] = 95.0
        c[80] = 94.0
        cvd = np.zeros(n)
        cvd[10] = -50.0
        cvd[80] = -40.0
        df = _indicator_frame(n, piv_lows=(10, 80), c=c, cvd=cvd)
        sig = signals.add_signals(df, lookback=60)
        self.assertFalse(bool(sig["long_entry"].iloc[80]))

    def test_end_to_end_synthetic(self):
        # two-leg decline: leg 1 closes near the lows (CVD dumps), leg 2
        # makes a lower low but closes near the highs (hidden buying ->
        # CVD rises). Regular bullish divergence must fire during leg 2.
        leg1 = np.linspace(110.0, 100.0, 100)   # bars 0-99
        bounce = np.linspace(100.0, 104.0, 50)  # bars 100-149
        leg2 = np.linspace(104.0, 98.0, 100)    # bars 150-249
        c = np.concatenate([leg1, bounce, leg2])
        o = c.copy()
        h = c.copy()
        l = c.copy()
        o[:100] = c[:100] + 1.0   # leg 1: closes near lows -> negative delta
        h[:100] = o[:100] + 0.5
        l[:100] = c[:100] - 0.5
        o[150:] = c[150:] - 1.0   # leg 2: closes near highs -> positive delta
        h[150:] = c[150:] + 0.5
        l[150:] = o[150:] - 0.5
        o[100:150] = c[100:150] - 0.5
        h[100:150] = c[100:150] + 0.5
        l[100:150] = c[100:150] - 0.5
        sig = signals.add_signals(
            indicators.add_indicators(_df_from_ohlc(o, h, l, c))
        )
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        # bullish divergence fires somewhere in leg 2's lower-low zone
        self.assertGreater(sig["long_entry"].iloc[150:].sum(), 0)

    def test_no_lookahead_truncation(self):
        n = 400
        i = np.arange(n)
        c = 100.0 + 12.0 * np.sin(i / 25.0) + 0.02 * i
        o = np.concatenate([[c[0]], c[:-1]])
        full = _df_from_ohlc(o, c + 1.0, c - 1.0, c)
        sig_full = signals.add_signals(indicators.add_indicators(full))
        for j in (200, 390):
            tr = full.iloc[: j + 1]
            sig_tr = signals.add_signals(indicators.add_indicators(tr))
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_registration_imports_cleanly(self):
        import strategies.cvd_divergence as mod

        self.assertEqual(mod.SPEC.slug, "cvd_divergence")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(
            set(mod.__all__), {"indicators", "signals", "risk", "SPEC"}
        )
        self.assertIn("zjvhcYEe", mod.SPEC.source_url)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 4.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertIsNone(risk.RISK.max_hold_bars)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 100)


if __name__ == "__main__":
    unittest.main()
