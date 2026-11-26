"""ICT killzone tests. Network-free, synthetic data only.

All series are UTC-hour aligned: bar 0 is 2023-11-15 00:00 UTC
(t0 = 1700006400000), so bar 48 + h is day 2 at hour h.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ict_killzone import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _london_long_series():
    # Day 2, London: sweep the Asian low at 07:00 (98), back
    # inside at 08:00 (100), displacement to 104 at 09:00, then
    # retracement crossing the 50% level (101.0) at 11:00.
    # Long fires at bar 59.
    base = np.full(48, 100.0)
    day2 = np.concatenate(
        [[100] * 7, [98, 100, 104, 102, 100.5, 100], [100] * 11]
    )
    return np.concatenate([base, day2, np.full(24, 100.0)])


def _ny_short_series():
    # Day 3, NY: sweep the Asian high at 12:00 (102), back
    # inside at 13:00 (100), displacement to 96 at 14:00, then
    # retracement crossing the 50% level (99.0) at 16:00.
    # Short fires at bar 88.
    base = np.full(48, 100.0)
    day2 = np.full(24, 100.0)
    day3 = np.concatenate(
        [[100] * 12, [102, 100, 96, 98, 99.5, 100], [100] * 6]
    )
    return np.concatenate([base, day2, day3, np.full(24, 100.0)])


def _combined_series():
    base = np.full(48, 100.0)
    day2 = np.concatenate(
        [[100] * 7, [98, 100, 104, 102, 100.5, 100], [100] * 11]
    )
    day3 = np.concatenate(
        [[100] * 12, [102, 100, 96, 98, 99.5, 100], [100] * 6]
    )
    return np.concatenate([base, day2, day3, np.full(24, 100.0)])


class TestIctKillzone(unittest.TestCase):
    def test_asian_range_is_00_03_utc(self):
        # Asian bars 100 / 102 / 99 -> high 102.2, low 98.8
        # (spread 0.2); range is NaN before 03:00.
        c = np.concatenate(
            [np.full(48, 100.0), [100, 102, 99], np.full(24, 100.0)]
        )
        ind = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(np.isnan(ind["asian_high"].iloc[50]))
        self.assertAlmostEqual(float(ind["asian_high"].iloc[60]), 102.2, places=6)
        self.assertAlmostEqual(float(ind["asian_low"].iloc[60]), 98.8, places=6)

    def test_killzone_window_ids(self):
        ind = indicators.add_indicators(_df_from_c(_combined_series()))
        self.assertEqual(int(ind["kz_window"].iloc[55]), 1)   # 07:00 London
        self.assertEqual(int(ind["kz_window"].iloc[58]), 1)   # 10:00 London (end hour)
        self.assertEqual(int(ind["kz_window"].iloc[59]), 0)   # 11:00 none
        self.assertEqual(int(ind["kz_window"].iloc[60]), 2)   # 12:00 NY
        self.assertEqual(int(ind["kz_window"].iloc[62]), 2)   # 14:00 NY (end hour)
        self.assertEqual(int(ind["kz_window"].iloc[63]), 0)   # 15:00 none

    def test_long_fires_on_london_retracement(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_london_long_series())))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [59])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_fires_on_ny_retracement(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_ny_short_series())))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [88])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_both_windows_fire_in_combined_series(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_combined_series())))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [59])
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [88])

    def test_fifty_pct_level_and_leg(self):
        # Long leg 97.8 -> 104.2, mid = 101.0; short leg
        # 102.2 -> 95.8, mid = 99.0.
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_combined_series())))
        row = sig.iloc[59]
        self.assertAlmostEqual(float(row["kz_long_mid"]), 101.0, places=6)
        self.assertAlmostEqual(float(row["kz_long_leg_start"]), 97.8, places=6)
        self.assertAlmostEqual(float(row["kz_long_disp_extreme"]), 104.2, places=6)
        row = sig.iloc[88]
        self.assertAlmostEqual(float(row["kz_short_mid"]), 99.0, places=6)
        self.assertAlmostEqual(float(row["kz_short_leg_start"]), 102.2, places=6)
        self.assertAlmostEqual(float(row["kz_short_disp_extreme"]), 95.8, places=6)

    def test_no_setup_outside_killzone(self):
        # Same shape as the NY short, but the sweep lands at
        # 15:00 (outside any window): nothing arms, nothing fires.
        base = np.full(48, 100.0)
        day2 = np.full(24, 100.0)
        day3 = np.concatenate(
            [[100] * 15, [102, 100, 96, 98, 99.5], [100] * 4]
        )
        c = np.concatenate([base, day2, day3, np.full(24, 100.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["kz_short_armed"].any()))

    def test_no_entry_without_displacement(self):
        # Sweep + back inside, then flat: displacement never
        # reaches 1.0x ATR, so no setup arms.
        base = np.full(48, 100.0)
        day2 = np.concatenate(
            [[100] * 7, [98, 100, 100.5, 100.5, 100.5, 100.5], [100] * 11]
        )
        c = np.concatenate([base, day2, np.full(24, 100.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["kz_long_armed"].any()))

    def test_invalidation_beyond_leg_start_cancels_setup(self):
        # Displacement, then one close (96) blows through both
        # the 50% level and the leg start (97.8): the setup is
        # invalidated, no entry -- the close-based reading does
        # not fire an entry on a bar that also breaks the leg.
        base = np.full(48, 100.0)
        day2 = np.concatenate(
            [[100] * 7, [98, 100, 104, 96], [100] * 13]
        )
        c = np.concatenate([base, day2, np.full(24, 100.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["kz_long_armed"].any()))

    def test_setup_expires_at_day_end(self):
        # Displacement, then price hovers above the 50% level
        # for the rest of the day: armed until the day boundary,
        # then expires with no entry.
        base = np.full(48, 100.0)
        day2 = np.concatenate([[100] * 7, [98, 100, 104], [102] * 14])
        c = np.concatenate([base, day2, np.full(24, 100.0)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertEqual(sig.index[sig["kz_long_armed"]].tolist(),
                         list(range(58, 72)))

    def test_entry_consumes_setup(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_london_long_series())))
        self.assertFalse(bool(sig["kz_long_armed"].iloc[60:].any()))

    def test_exit_on_close_beyond_leg_start(self):
        # Long fires at 59, then a close below the leg start
        # (97.8) at bar 61 exits.
        c = _london_long_series().copy()
        c[60] = 99.0
        c[61] = 97.0
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [59])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [61])

    def test_disp_mult_param_changes_sensitivity(self):
        base = np.full(48, 100.0)
        day2 = np.concatenate(
            [[100] * 7, [98, 100, 100.5, 100.5, 100.5, 100.5], [100] * 11]
        )
        c = np.concatenate([base, day2, np.full(24, 100.0)])
        sig_shipped = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        sig_weak = signals.add_signals(
            indicators.add_indicators(_df_from_c(c), disp_mult=0.3))
        self.assertFalse(bool(sig_shipped["kz_long_armed"].any()))
        self.assertTrue(bool(sig_weak["kz_long_armed"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        # Asian range is legitimately NaN during 00:00-03:00 UTC
        # each day (the range is not complete yet); check it only
        # on bars at/after 03:00.
        hours = (sig["t"].to_numpy() // 3_600_000) % 24
        post_asian = sig.iloc[100:][hours[100:] >= 3]
        for col in ("asian_high", "asian_low"):
            self.assertFalse(post_asian[col].isna().any(), col)
        for col in ("swing_high_20", "swing_low_20", "atr14"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "kz_long_armed", "kz_short_armed", "killzone"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("asian_high", "asian_low", "swing_high_20",
                        "swing_low_20", "atr14", "kz_long_armed",
                        "kz_short_armed", "kz_long_mid", "kz_short_mid"):
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
        import strategies.ict_killzone as mod

        self.assertEqual(mod.SPEC.slug, "ict_killzone")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 50)


if __name__ == "__main__":
    unittest.main()
