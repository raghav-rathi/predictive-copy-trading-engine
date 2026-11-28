"""Parkinson volatility-expansion tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.parkinson_volatility import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC


def _df(o, h, l, c, v=None):
    o = np.asarray(o, float)
    h = np.asarray(h, float)
    l = np.asarray(l, float)
    c = np.asarray(c, float)
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _constant_range_df(n=100, log_hl=0.2):
    """Every bar: ln(H/L) = log_hl, flat close (C == O == 100).

    Per-bar Parkinson variance is then exactly
    log_hl**2 / (4 * ln2).
    """
    h = 100.0 * math.exp(log_hl / 2)
    l = 100.0 * math.exp(-log_hl / 2)
    return _df(np.full(n, 100.0), np.full(n, h),
               np.full(n, l), np.full(n, 100.0))


def _craft_cross(n=120, cross_bar=100, side="long"):
    """Indicator frame with a forced pk_vol cross above its SMA
    at cross_bar. Close sits above EMA20 (long) or below it
    (short) at the cross bar; flat elsewhere."""
    df = _constant_range_df(n)
    ind = indicators.add_indicators(df)
    ind["pk_vol"] = 0.01
    ind.loc[cross_bar:, "pk_vol"] = 0.03
    ind["pk_vol_sma"] = 0.01
    ind["ema20"] = 100.0
    ind["c"] = 100.0
    if side == "long":
        ind.loc[cross_bar, "c"] = 101.0
    elif side == "short":
        ind.loc[cross_bar, "c"] = 99.0
    return ind


class TestParkinsonVolatility(unittest.TestCase):
    def test_pk_var_hand_computed(self):
        # ln(H/L)=0.2 -> v = 0.04 / (4 ln2) = 0.01442695...
        ind = indicators.add_indicators(_constant_range_df(30))
        expect = 0.04 / (4 * math.log(2))
        self.assertAlmostEqual(float(ind["pk_var"].iloc[0]), expect, places=9)
        self.assertAlmostEqual(float(ind["pk_var"].iloc[29]), expect, places=9)

    def test_pk_var_ignores_open_close_drift(self):
        # Same H/L range, but one frame drifts C/O by e^0.1 per
        # bar and the other is flat: Parkinson is range-only,
        # so pk_var must be identical.
        n = 10
        flat = _constant_range_df(n)
        drift = _df(np.full(n, 100.0),
                    np.full(n, 100.0 * math.exp(0.1)),
                    np.full(n, 100.0 * math.exp(-0.1)),
                    np.full(n, 100.0 * math.exp(0.1)))
        a = indicators.add_indicators(flat)["pk_var"]
        b = indicators.add_indicators(drift)["pk_var"]
        pd.testing.assert_series_equal(a, b)

    def test_pk_vol_constant_range(self):
        # Constant v = 0.04/(4 ln2) -> pk_vol = sqrt(v) from
        # bar 19 on, NaN before.
        ind = indicators.add_indicators(_constant_range_df(100))
        expect = math.sqrt(0.04 / (4 * math.log(2)))
        self.assertTrue(np.isnan(ind["pk_vol"].iloc[18]))
        self.assertAlmostEqual(float(ind["pk_vol"].iloc[19]), expect, places=9)
        self.assertAlmostEqual(float(ind["pk_vol"].iloc[99]), expect, places=9)

    def test_pk_vol_sma_warmup(self):
        # pk_vol valid from bar 19; SMA(60) needs 60 valid
        # values -> first value at bar 78, NaN at 77.
        ind = indicators.add_indicators(_constant_range_df(100))
        expect = math.sqrt(0.04 / (4 * math.log(2)))
        self.assertTrue(np.isnan(ind["pk_vol_sma"].iloc[77]))
        self.assertAlmostEqual(float(ind["pk_vol_sma"].iloc[78]), expect, places=9)

    def test_long_entry_on_vol_cross_above_sma_with_close_above_ema(self):
        sig = signals.add_signals(_craft_cross(side="long"))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [100])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_entry_on_vol_cross_above_sma_with_close_below_ema(self):
        sig = signals.add_signals(_craft_cross(side="short"))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [100])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_entry_when_close_equals_ema20(self):
        # Vol crosses up at bar 100 but close == EMA20: neither
        # side's trend filter passes, so no entry at all.
        ind = _craft_cross(side="long")
        ind.loc[100, "c"] = 100.0
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_entry_without_a_cross(self):
        # Vol sits flat ABOVE its SMA for the whole frame (a
        # level condition, never a cross): no entry fires.
        ind = indicators.add_indicators(_constant_range_df(120))
        ind["pk_vol"] = 0.03
        ind["pk_vol_sma"] = 0.01
        ind["ema20"] = 100.0
        ind["c"] = 101.0
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_long_exit_on_vol_cross_below_sma(self):
        # Vol 0.03 -> 0.005 at bar 105 crosses below SMA 0.01;
        # close stays above EMA20, so the exit is the vol cross.
        # A vol contraction ends EITHER side's trade, so the
        # short exit fires on the same bar too; the harness
        # applies only the exit matching the open side.
        ind = indicators.add_indicators(_constant_range_df(120))
        ind["pk_vol"] = 0.03
        ind.loc[105:, "pk_vol"] = 0.005
        ind["pk_vol_sma"] = 0.01
        ind["ema20"] = 100.0
        ind["c"] = 101.0
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [105])
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [105])

    def test_long_exit_on_close_cross_below_ema20(self):
        # Vol flat (no cross); close 101 -> 99 at bar 105 and
        # stays there: crosses below EMA20 100 once, long exit,
        # no short exit.
        ind = indicators.add_indicators(_constant_range_df(120))
        ind["pk_vol"] = 0.03
        ind["pk_vol_sma"] = 0.01
        ind["ema20"] = 100.0
        ind["c"] = 101.0
        ind.loc[105:, "c"] = 99.0
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [105])
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_short_exit_on_close_cross_above_ema20(self):
        # Vol flat (no cross); close 99 -> 101 at bar 105 and
        # stays there: crosses above EMA20 100 once, short exit,
        # no long exit.
        ind = indicators.add_indicators(_constant_range_df(120))
        ind["pk_vol"] = 0.03
        ind["pk_vol_sma"] = 0.01
        ind["ema20"] = 100.0
        ind["c"] = 99.0
        ind.loc[105:, "c"] = 101.0
        sig = signals.add_signals(ind)
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [105])
        self.assertFalse(bool(sig["long_exit"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("pk_var", "pk_vol", "pk_vol_sma", "ema20", "atr14"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("pk_var", "pk_vol", "pk_vol_sma", "ema20", "atr14"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.parkinson_volatility as mod

        self.assertEqual(mod.SPEC.slug, "parkinson_volatility")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 80)


if __name__ == "__main__":
    unittest.main()
