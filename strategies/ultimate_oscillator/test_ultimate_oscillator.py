"""Ultimate Oscillator divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ultimate_oscillator import indicators, risk, signals


def _frame_from_ohlc(o, h, l, c, seed=7):
    n = len(c)
    rng = np.random.default_rng(seed)
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t,
        "o": np.asarray(o, dtype=float),
        "h": np.asarray(h, dtype=float),
        "l": np.asarray(l, dtype=float),
        "c": np.asarray(c, dtype=float),
        "v": v,
    })


def _frame(n=600, seed=7, drift=0.0002, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    r = np.random.default_rng(seed + 1)
    h = np.maximum(o, c) * (1 + r.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - r.uniform(0, 0.002, n))
    return _frame_from_ohlc(o, h, l, c, seed)


def _bullish_divergence_frame(n=160):
    """Price lows decline steadily; UO troughs at bar 40 (25) and bar 90 (35).

    UO dips below 30 between the troughs, peaks at 55 between them, then
    rallies through 55 and 70. Expects: pivots [40, 90], long trigger on
    the cross above 55, long exit on the cross above 70.
    """
    mid = np.linspace(100, 80, n)
    l = mid - 0.3
    h = mid + 0.3
    o = np.concatenate([[mid[0]], mid[:-1]])
    c = mid.copy()
    uo = np.empty(n)
    uo[0:41] = np.linspace(60, 25, 41)     # trough 1 at bar 40 = 25
    uo[41:66] = np.linspace(26, 55, 25)    # rise to 55 at bar 65
    uo[66:91] = np.linspace(54, 35, 25)    # trough 2 at bar 90 = 35
    uo[91:] = np.linspace(36, 75, n - 91)  # rally through 55, then 70
    df = _frame_from_ohlc(o, h, l, c)
    df["uo"] = uo
    df["atr"] = 1.0
    return df


def _bearish_divergence_frame(n=160):
    """Price highs rise steadily; UO peaks at bar 40 (75) and bar 90 (65).

    UO exceeds 70 between the peaks, bottoms at 45 between them, then
    collapses through 45 and 30. Expects: pivots [40, 90], short trigger
    on the cross below 45, short exit on the cross below 30.
    """
    mid = np.linspace(80, 100, n)
    l = mid - 0.3
    h = mid + 0.3
    o = np.concatenate([[mid[0]], mid[:-1]])
    c = mid.copy()
    uo = np.empty(n)
    uo[0:41] = np.linspace(40, 75, 41)     # peak 1 at bar 40 = 75
    uo[41:66] = np.linspace(74, 45, 25)    # fall to 45 at bar 65
    uo[66:91] = np.linspace(46, 65, 25)    # peak 2 at bar 90 = 65
    uo[91:] = np.linspace(64, 25, n - 91)  # collapse through 45, then 30
    df = _frame_from_ohlc(o, h, l, c)
    df["uo"] = uo
    df["atr"] = 1.0
    return df


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("uo", "atr"):
            self.assertIn(col, ind.columns)

    def test_uo_formula_hand_check(self):
        # Independent loop implementation of BP/TR/avg/UO on a 40-bar series.
        n = 40
        rng = np.random.default_rng(3)
        c = 100 + np.cumsum(rng.normal(0, 1, n))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + rng.uniform(0, 0.5, n)
        l = np.minimum(o, c) - rng.uniform(0, 0.5, n)
        df = _frame_from_ohlc(o, h, l, c)
        got = indicators.ultimate_oscillator(df["h"], df["l"], df["c"]).to_numpy()

        # NOTE: pd.concat([l, prev_c], axis=1).min(axis=1) SKIPS NaN, so at
        # bar 0 (no prev_c) the implementation uses bp[0] = c[0]-l[0] and
        # tr[0] = h[0]-l[0]. The loop replicates that edge convention.
        bp = np.empty(n)
        tr = np.empty(n)
        bp[0] = c[0] - l[0]
        tr[0] = h[0] - l[0]
        for j in range(1, n):
            bp[j] = c[j] - min(l[j], c[j - 1])
            tr[j] = max(h[j], c[j - 1]) - min(l[j], c[j - 1])

        def avg(j, nn):
            # mirrors rolling(nn, min_periods=nn).sum(): first valid at bar nn-1
            if j + 1 < nn:
                return np.nan
            sl = slice(j - nn + 1, j + 1)
            return bp[sl].sum() / tr[sl].sum()

        exp = np.full(n, 50.0)
        for j in range(n):
            a7, a14, a28 = avg(j, 7), avg(j, 14), avg(j, 28)
            if not (np.isnan(a7) or np.isnan(a14) or np.isnan(a28)):
                exp[j] = 100.0 * (4 * a7 + 2 * a14 + a28) / 7
        np.testing.assert_allclose(got, np.clip(exp, 0, 100), rtol=1e-9, atol=1e-9)

    def test_uo_weights_4_2_1(self):
        # Cross-check the 4:2:1 blend with an independent np.cumsum path.
        df = _frame()
        c, h, l = df["c"], df["h"], df["l"]
        prev_c = c.shift(1)
        bp = c - pd.concat([l, prev_c], axis=1).min(axis=1)
        tr = pd.concat([h, prev_c], axis=1).max(axis=1) - pd.concat([l, prev_c], axis=1).min(axis=1)
        bp_v, tr_v = bp.to_numpy(), tr.to_numpy()

        def avg_conv(v, nn):
            num = np.convolve(np.nan_to_num(v), np.ones(nn), mode="valid")
            out = np.full(len(v), np.nan)
            out[nn - 1 :] = num
            return out

        n1, n2, n3 = 7, 14, 28
        a7 = avg_conv(bp_v, n1) / avg_conv(tr_v, n1)
        a14 = avg_conv(bp_v, n2) / avg_conv(tr_v, n2)
        a28 = avg_conv(bp_v, n3) / avg_conv(tr_v, n3)
        exp = np.clip(100.0 * (4 * a7 + 2 * a14 + a28) / 7, 0, 100)
        exp[: n3 - 1] = 50.0  # spin-up bars are NaN -> neutral 50
        got = indicators.ultimate_oscillator(h, l, c).to_numpy()
        np.testing.assert_allclose(got, exp, rtol=1e-9, atol=1e-9)

    def test_uo_range_0_100(self):
        got = indicators.add_indicators(_frame())["uo"]
        self.assertTrue(((got >= 0.0) & (got <= 100.0)).all(),
                        f"UO out of [0,100]: min {got.min()}, max {got.max()}")

    def test_uo_neutral_50_on_flat_series(self):
        # TR sums are 0 -> 0/0 -> neutral 50 everywhere.
        c = np.full(200, 100.0)
        df = _frame_from_ohlc(c, c, c, c)
        got = indicators.ultimate_oscillator(df["h"], df["l"], df["c"])
        self.assertTrue((got == 50.0).all(), f"expected 50 on flat tape, got {got.unique()[:5]}")

    def test_uo_100_when_close_pinned_to_high(self):
        # c rising 3/bar, h == c, l == c-2: BP == TR every bar -> UO -> 100.
        c = 100.0 + 3.0 * np.arange(200)
        h = c.copy()
        l = c - 2.0
        df = _frame_from_ohlc(c, h, l, c)
        got = indicators.ultimate_oscillator(df["h"], df["l"], df["c"])
        self.assertAlmostEqual(got.iloc[-1], 100.0, places=9)

    def test_uo_0_when_close_pinned_to_low(self):
        # c falling 3/bar, l == c, h == c+2: BP == 0 every bar -> UO -> 0.
        c = 100.0 - 3.0 * np.arange(200)
        l = c.copy()
        h = c + 2.0
        df = _frame_from_ohlc(c, h, l, c)
        got = indicators.ultimate_oscillator(df["h"], df["l"], df["c"])
        self.assertAlmostEqual(got.iloc[-1], 0.0, places=9)

    def test_no_lookahead(self):
        # Changing the last bar must not change UO on earlier bars.
        df = _frame()
        df2 = df.copy()
        df2.loc[df2.index[-1], "c"] *= 1.05
        df2.loc[df2.index[-1], "h"] *= 1.05
        got = indicators.add_indicators(df)["uo"].to_numpy()
        got2 = indicators.add_indicators(df2)["uo"].to_numpy()
        np.testing.assert_allclose(got[:-1], got2[:-1], rtol=1e-12, atol=1e-12)

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestPivotConfirmation(unittest.TestCase):
    def test_pivot_confirmation_delay(self):
        # Troughs at bars 40 and 90 must be invisible before p+3.
        df = _bullish_divergence_frame()
        uo = df["uo"].to_numpy()
        pivots = signals._all_pivots(uo, 3, 3, "low")
        self.assertEqual(pivots, [40, 90])
        self.assertEqual(signals._confirmed(pivots, 92), [40])      # 90 not yet usable
        self.assertEqual(signals._confirmed(pivots, 93), [40, 90])  # 90 usable at 93

    def test_high_pivot_detection(self):
        df = _bearish_divergence_frame()
        uo = df["uo"].to_numpy()
        self.assertEqual(signals._all_pivots(uo, 3, 3, "high"), [40, 90])


class TestSignals(unittest.TestCase):
    def test_bullish_divergence_triggers_long(self):
        df = _bullish_divergence_frame()
        out = signals.add_signals(df)
        uo = df["uo"].to_numpy()
        span_max = float(uo[41:90].max())  # divergence high between the troughs
        self.assertAlmostEqual(span_max, 55.0, places=9)
        cross = np.where((uo[1:] > span_max) & (uo[:-1] <= span_max))[0] + 1
        expected = int(cross.min())
        self.assertGreaterEqual(expected, 93, "trigger must wait for pivot confirmation")
        le = out["long_entry"].to_numpy()
        self.assertTrue(le[expected], f"expected long_entry at bar {expected}")
        self.assertEqual(int(np.where(le)[0].min()), expected)
        self.assertFalse(le[:93].any(), "no entry before the second pivot confirms")

    def test_bearish_divergence_triggers_short(self):
        df = _bearish_divergence_frame()
        out = signals.add_signals(df)
        uo = df["uo"].to_numpy()
        span_min = float(uo[41:90].min())  # divergence low between the peaks
        self.assertAlmostEqual(span_min, 45.0, places=9)
        cross = np.where((uo[1:] < span_min) & (uo[:-1] >= span_min))[0] + 1
        expected = int(cross.min())
        self.assertGreaterEqual(expected, 93, "trigger must wait for pivot confirmation")
        se = out["short_entry"].to_numpy()
        self.assertTrue(se[expected], f"expected short_entry at bar {expected}")
        self.assertEqual(int(np.where(se)[0].min()), expected)
        self.assertFalse(se[:93].any(), "no entry before the second pivot confirms")

    def test_no_divergence_no_entries(self):
        # Monotonically falling UO and price: no pivots at all -> no entries.
        n = 200
        mid = np.linspace(100, 80, n)
        df = _frame_from_ohlc(mid, mid + 0.2, mid - 0.2, mid)
        df["uo"] = np.linspace(60, 20, n)
        df["atr"] = 1.0
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].any())
        self.assertFalse(out["short_entry"].any())

    def test_failed_pair_cancels_setup(self):
        # Two troughs, but price makes a HIGHER low -> no bullish divergence.
        df = _bullish_divergence_frame()
        df["l"] = np.linspace(80, 100, len(df)) - 0.3  # rising lows kill it
        out = signals.add_signals(df)
        self.assertFalse(out["long_entry"].any())

    def test_long_exit_on_cross_above_70(self):
        df = _bullish_divergence_frame()
        out = signals.add_signals(df)
        uo = df["uo"].to_numpy()
        cross = np.where((uo[1:] > 70.0) & (uo[:-1] <= 70.0))[0] + 1
        self.assertTrue(len(cross) > 0)
        self.assertTrue(out["long_exit"].to_numpy()[cross[0]])

    def test_short_exit_on_cross_below_30(self):
        df = _bearish_divergence_frame()
        out = signals.add_signals(df)
        uo = df["uo"].to_numpy()
        cross = np.where((uo[1:] < 30.0) & (uo[:-1] >= 30.0))[0] + 1
        self.assertTrue(len(cross) > 0)
        self.assertTrue(out["short_exit"].to_numpy()[cross[0]])

    def test_signal_columns_boolean_no_nan(self):
        out = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, out.columns)
            self.assertTrue(out[col].dtype == bool, f"{col} not bool")
            self.assertFalse(out[col].isna().any(), f"{col} has NaN")

    def test_does_not_mutate_input(self):
        df = indicators.add_indicators(_frame())
        before = df.copy()
        signals.add_signals(df)
        pd.testing.assert_frame_equal(df, before)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.5)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 96)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertEqual(r.fee_rate, 0.00045)
        self.assertEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
