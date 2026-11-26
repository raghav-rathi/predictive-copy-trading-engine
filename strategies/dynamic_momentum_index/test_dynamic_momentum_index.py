"""Dynamic Momentum Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dynamic_momentum_index import indicators, risk, signals


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _reference_dmi(c, base_period=14):
    """Independent re-implementation: rolling stdev(5), SMA(10),
    TD = clamp(int(14/Vi), 5, 30), simple-mean RSI over TD."""
    c = pd.Series(np.asarray(c, float))
    sd5 = c.rolling(5, min_periods=5).std()
    sd_avg = sd5.rolling(10, min_periods=10).mean()
    vi = sd5 / sd_avg
    td = np.floor((base_period / vi).clip(lower=5, upper=30))
    d = c.diff().to_numpy(dtype=float)
    out = np.full(len(c), np.nan)
    for i in range(len(c)):
        if np.isnan(td.iloc[i]):
            continue
        k = int(td.iloc[i])
        if i - k + 1 < 1:
            continue
        w = d[i - k + 1:i + 1]
        ag = np.clip(w, 0, None).mean()
        al = (-np.clip(w, None, 0)).mean()
        if al == 0 and ag == 0:
            out[i] = 50.0
        elif al == 0:
            out[i] = 100.0
        elif ag == 0:
            out[i] = 0.0
        else:
            out[i] = 100 - 100 / (1 + ag / al)
    return pd.Series(out), td


def _decline_then_recovery():
    # Steady 1/bar decline (DMI pinned at 0), then a steady
    # recovery — DMI climbs back through 30.
    down = 100.0 - np.arange(40)
    up = 61.0 + np.arange(40)
    return np.concatenate([down, up, np.full(20, 100.0)])


def _rise_then_decline():
    up = 60.0 + np.arange(40)
    down = 99.0 - np.arange(40)
    return np.concatenate([up, down, np.full(20, 60.0)])


class TestDynamicMomentumIndex(unittest.TestCase):
    def test_dmi_matches_direct_computation(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        ref_dmi, ref_td = _reference_dmi(df["c"].to_numpy())
        valid = ref_dmi.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "dmi"], ref_dmi[valid])))
        self.assertTrue(bool(np.allclose(
            df.loc[valid, "td"], ref_td[valid], equal_nan=True)))

    def test_td_clamped_5_to_30(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        td = df["td"].dropna()
        self.assertTrue(bool(((td >= 5) & (td <= 30)).all()))

    def test_td_shortens_after_volatility_spike(self):
        # Long flat stretch (Vi -> 0, TD -> 30), then a jump:
        # sd5 spikes against a near-zero sd_avg, so TD -> 5.
        c = np.concatenate([np.full(60, 100.0),
                            [110, 120, 130, 140], np.full(40, 140.0)])
        df = indicators.add_indicators(_df_from_c(c))
        self.assertEqual(float(df["td"].iloc[60:70].min()), 5.0)

    def test_td_lengthens_in_calm_after_volatility(self):
        # Volatile stretch, then flat: sd5 -> 0 while sd_avg is
        # still positive, so Vi -> 0 and TD -> 30. (After 10 flat
        # bars sd_avg itself reaches 0 and Vi/TD go NaN — no
        # volatility, no momentum reading — so check bars 60-69.)
        rng = np.random.default_rng(3)
        c = np.concatenate([100.0 + np.cumsum(rng.normal(0, 3.0, 60)),
                            np.full(40, 100.0)])
        df = indicators.add_indicators(_df_from_c(c))
        self.assertEqual(float(df["td"].iloc[60:70].max()), 30.0)

    def test_dmi_bounded_0_100_after_warmup(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((df["dmi"].iloc[40:] >= 0) & (df["dmi"].iloc[40:] <= 100)).all()))
        self.assertFalse(df["dmi"].iloc[40:].isna().any())

    def test_long_fires_on_cross_up_through_30(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_decline_then_recovery())))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        i = entries[0]
        self.assertLessEqual(float(sig["dmi"].iloc[i - 1]), 30.0)
        self.assertGreater(float(sig["dmi"].iloc[i]), 30.0)

    def test_short_fires_on_cross_down_through_70(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_rise_then_decline())))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) > 0)
        i = entries[0]
        self.assertGreaterEqual(float(sig["dmi"].iloc[i - 1]), 70.0)
        self.assertLess(float(sig["dmi"].iloc[i]), 70.0)

    def test_long_exit_on_cross_below_50(self):
        # Decline, recovery (long entry), then a fresh decline:
        # DMI falls back through 50 after the entry.
        c = np.concatenate([100.0 - np.arange(40), 61.0 + np.arange(40),
                            100.0 - np.arange(40), np.full(20, 61.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        entries = sig.index[sig["long_entry"]].tolist()
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        self.assertTrue(any(e > entries[0] for e in exits))

    def test_flat_series_no_entries_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(np.full(100, 100.0))))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(bool(sig[col].any()), col)
        self.assertTrue(sig["dmi"].isna().all())

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_base_period_param_changes_td(self):
        df1 = indicators.add_indicators(_rand_df(), base_period=7)
        df2 = indicators.add_indicators(_rand_df(), base_period=28)
        self.assertFalse(bool(np.allclose(
            df1["td"].iloc[40:], df2["td"].iloc[40:], equal_nan=True)))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("sd5", "sd_avg", "volatility_index", "td", "dmi", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("sd5", "sd_avg", "volatility_index", "td", "dmi", "atr14"):
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
        import strategies.dynamic_momentum_index as mod

        self.assertEqual(mod.SPEC.slug, "dynamic_momentum_index")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
