"""ICT Optimal Trade Entry (OTE) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ict_ote_entry import indicators, risk, signals


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


def _long_setup_series():
    # flat, sweep below the prior 20-bar low (98/97/96), back
    # inside (99/100), displacement up (101..109), retracement
    # into the OTE zone (99 at bar 53). Long fires at bar 53.
    return np.concatenate(
        [np.full(40, 100.0), [98, 97, 96, 99, 100, 101, 103, 105, 107, 109],
         [104, 101, 99, 98], np.full(30, 98.0)]
    )


def _short_setup_series():
    # Mirror of the long setup: sweep above the prior 20-bar
    # high, displacement down, retracement into the zone.
    # Short fires at bar 53.
    return np.concatenate(
        [np.full(40, 100.0), [102, 103, 104, 101, 100, 99, 97, 95, 93, 91],
         [96, 99, 101, 102], np.full(30, 102.0)]
    )


class TestIctOteEntry(unittest.TestCase):
    def test_swing_extremes_are_rolling(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect_high = df["h"].rolling(20, min_periods=20).max()
        expect_low = df["l"].rolling(20, min_periods=20).min()
        valid = expect_high.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "swing_high_20"], expect_high[valid])))
        self.assertTrue(bool(np.allclose(df.loc[valid, "swing_low_20"], expect_low[valid])))

    def test_atr_defined_and_positive_after_warmup(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertFalse(df["atr14"].iloc[40:].isna().any())
        self.assertTrue(bool((df["atr14"].iloc[40:] > 0).all()))

    def test_long_fires_on_ote_retracement(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_long_setup_series())))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [53])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_fires_on_ote_retracement(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_short_setup_series())))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [53])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_ote_zone_is_62_79_pct_of_leg(self):
        # Leg 95.8 -> 103.2 (range 7.4): zone = [103.2 - .79*7.4,
        # 103.2 - .62*7.4] = [97.354, 98.612], mid 70.5% = 97.983.
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_long_setup_series())))
        row = sig.iloc[53]
        self.assertAlmostEqual(float(row["ote_long_leg_start"]), 95.8, places=6)
        self.assertAlmostEqual(float(row["ote_long_disp_extreme"]), 103.2, places=6)
        self.assertAlmostEqual(float(row["ote_long_zone_lo"]), 97.354, places=3)
        self.assertAlmostEqual(float(row["ote_long_zone_hi"]), 98.612, places=3)
        self.assertAlmostEqual(float(row["ote_long_zone_mid"]), 97.983, places=3)

    def test_no_entry_without_displacement(self):
        # Sweep + back inside, then flat: displacement never
        # reaches 1.5x ATR, so no setup arms and nothing fires.
        c = np.concatenate(
            [np.full(40, 100.0), [98, 97, 96, 99, 100, 100.5, 100.5, 100.5, 100.5, 100.5],
             np.full(30, 100.5)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["ote_long_armed"].any()))

    def test_no_entry_without_sweep(self):
        # A plain rally with no prior sweep of the 20-bar low:
        # displacement without a sweep is not an OTE setup.
        c = np.concatenate(
            [np.full(40, 100.0), [101, 103, 105, 107, 109], np.full(30, 109.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["ote_long_armed"].any()))

    def test_invalidation_beyond_100_pct_cancels_setup(self):
        # Displacement, then the close falls below the sweep
        # extreme (95.8) before ever touching the zone: the
        # setup is cancelled, no entry.
        c = np.concatenate(
            [np.full(40, 100.0), [98, 97, 96, 99, 100, 101, 103, 105, 107, 109],
             [104, 101, 99, 96, 94, 93], np.full(30, 93.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertEqual(sig.index[sig["ote_long_armed"]].tolist(),
                         list(range(47, 54)))

    def test_setup_expires_after_24_bars(self):
        # Displacement, then price hovers above the zone for 30
        # bars: armed for exactly 24 bars, then expires.
        c = np.concatenate(
            [np.full(40, 100.0), [98, 97, 96, 99, 100, 101, 103, 105, 107, 109],
             np.full(30, 105.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertEqual(int(sig["ote_long_armed"].sum()), 24)

    def test_entry_consumes_setup(self):
        # After the long fires at bar 53 the setup is consumed:
        # the armed flag goes False even though later closes sit
        # inside the old zone.
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_long_setup_series())))
        self.assertFalse(bool(sig["ote_long_armed"].iloc[54:].any()))

    def test_exit_on_close_beyond_leg_start(self):
        c = np.concatenate(
            [np.full(40, 100.0), [98, 97, 96, 99, 100, 101, 103, 105, 107, 109],
             [104, 101, 99, 98], [94, 93], np.full(20, 93.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [53])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [54])

    def test_disp_mult_param_changes_sensitivity(self):
        # A weaker displacement threshold arms the setup on a
        # series where the shipped 1.5x threshold does not.
        c = np.concatenate(
            [np.full(40, 100.0), [98, 97, 96, 99, 100, 100.3, 100.5, 100.6, 100.7, 100.8],
             np.full(30, 100.8)]
        )
        sig_shipped = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        sig_weak = signals.add_signals(
            indicators.add_indicators(_df_from_c(c), disp_mult=0.5))
        self.assertFalse(bool(sig_shipped["ote_long_armed"].any()))
        self.assertTrue(bool(sig_weak["ote_long_armed"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("swing_high_20", "swing_low_20", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "ote_long_armed", "ote_short_armed"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("swing_high_20", "swing_low_20", "atr14",
                        "ote_long_armed", "ote_short_armed",
                        "ote_long_zone_lo", "ote_short_zone_lo"):
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
        import strategies.ict_ote_entry as mod

        self.assertEqual(mod.SPEC.slug, "ict_ote_entry")
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
