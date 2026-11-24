"""Premium/discount tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.premium_discount import indicators, risk, signals
from strategies.base import crossed_above, crossed_below


def _df_ohlc(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.full(n, 100.0)}
    )


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df_ohlc(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _range_df(n=60, c=100.0, hi=110.0, lo=90.0):
    return _df_ohlc(
        np.full(n, c), np.full(n, hi), np.full(n, lo), np.full(n, c)
    )


class TestPremiumDiscount(unittest.TestCase):
    def test_equilibrium_math_exact(self):
        df = indicators.add_indicators(_range_df())
        self.assertTrue(bool((df["eq"].iloc[48:] == 100.0).all()))
        self.assertTrue(bool((df["premium"].iloc[48:] == 105.0).all()))
        self.assertTrue(bool((df["discount"].iloc[48:] == 95.0).all()))
        self.assertTrue(bool((df["range_high"].iloc[48:] == 110.0).all()))
        self.assertTrue(bool((df["range_low"].iloc[48:] == 90.0).all()))

    def test_warmup_nan_head_no_nan_after(self):
        df = indicators.add_indicators(_rand_df())
        self.assertTrue(df["eq"].iloc[:47].isna().all())
        for col in ("eq", "premium", "discount", "low_touch", "high_touch"):
            self.assertFalse(df[col].iloc[60:].isna().any(), col)

    def test_discount_touch_flag(self):
        # flat range: the low (90) sits below discount (95), so the
        # touch flag is on throughout; a dip to 93 keeps it on
        base = _range_df(60)
        dip_c = [96.0, 94.0, 94.0, 95.0, 96.0]
        dip = _df_ohlc(dip_c, [110.0] * 5, [93.0] * 5, dip_c)
        df = indicators.add_indicators(pd.concat([base, dip], ignore_index=True))
        self.assertTrue(bool(df["touched_discount"].iloc[50:60].all()))
        self.assertTrue(bool(df["touched_discount"].iloc[60:65].all()))
        # premium touch is likewise on in the flat range (high 110 >= 105)
        self.assertTrue(bool(df["touched_premium"].iloc[50:60].all()))

    def test_discount_sweep_then_reclaim_fires_long(self):
        base = _range_df(60)
        dip_c = [96.0, 94.0, 94.0, 95.0, 96.0]
        dip = _df_ohlc(dip_c, [110.0] * 5, [93.0] * 5, dip_c)
        rally_c = [98.0, 101.0, 102.0, 103.0]
        rally = _df_ohlc(rally_c, [110.0] * 4, [97.0] * 4, rally_c)
        full = pd.concat([base, dip, rally], ignore_index=True)
        sig = signals.add_signals(indicators.add_indicators(full))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 65 for b in entries))

    def test_cross_without_touch_fires_no_long(self):
        # 48 flat range bars (range 110/90, eq 100, discount 95), then
        # 12 mid-range bars (low 98, high 102: range unchanged, but no
        # bar in the 12-bar touch window reaches discount), then a
        # shallow dip to 99 (low 98.5) and a cross back above eq:
        # the cross fires with NO discount touch in the last 12 bars
        base = _range_df(48)
        mid = _df_ohlc(
            np.full(12, 100.0), np.full(12, 102.0),
            np.full(12, 98.0), np.full(12, 100.0),
        )
        dip_c = [99.0, 99.0, 99.5]
        dip = _df_ohlc(dip_c, [102.0] * 3, [98.5] * 3, dip_c)
        rally_c = [100.5, 101.0]
        rally = _df_ohlc(rally_c, [102.0] * 2, [100.0] * 2, rally_c)
        full = pd.concat([base, mid, dip, rally], ignore_index=True)
        ind = indicators.add_indicators(full)
        self.assertTrue(bool((ind["eq"].iloc[60:] == 100.0).all()))
        self.assertFalse(bool(ind["touched_discount"].iloc[60:65].any()))
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_premium_sweep_then_reclaim_fires_short(self):
        base = _range_df(60)
        spike_c = [104.0, 106.0, 106.0, 105.0, 104.0]
        spike = _df_ohlc(spike_c, [107.0] * 5, [90.0] * 5, spike_c)
        fall_c = [102.0, 99.0, 98.0, 97.0]
        fall = _df_ohlc(fall_c, [103.0] * 4, [90.0] * 4, fall_c)
        full = pd.concat([base, spike, fall], ignore_index=True)
        sig = signals.add_signals(indicators.add_indicators(full))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(all(b >= 65 for b in entries))

    def test_exits_are_opposite_equilibrium_crosses(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        expect_le = crossed_below(sig["c"], sig["eq"]).fillna(False).astype(bool)
        expect_se = crossed_above(sig["c"], sig["eq"]).fillna(False).astype(bool)
        self.assertTrue(bool((sig["long_exit"] == expect_le).all()))
        self.assertTrue(bool((sig["short_exit"] == expect_se).all()))

    def test_signals_boolean_no_nan_fire_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_lookback_param_changes_equilibrium(self):
        df = indicators.add_indicators(_rand_df(600, seed=9), lookback=24)
        df48 = indicators.add_indicators(_rand_df(600, seed=9), lookback=48)
        self.assertFalse(bool((df["eq"].iloc[100:] == df48["eq"].iloc[100:]).all()))
        # shorter lookback reacts to a narrower range: range width <= 48-bar width
        w24 = (df["range_high"] - df["range_low"]).iloc[100:]
        w48 = (df48["range_high"] - df48["range_low"]).iloc[100:]
        self.assertTrue(bool((w24 <= w48 + 1e-9).all()))

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("eq", "premium", "discount"):
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
        import strategies.premium_discount as mod

        self.assertEqual(mod.SPEC.slug, "premium_discount")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
