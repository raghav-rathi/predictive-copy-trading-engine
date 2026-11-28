"""Day-of-week effect tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.day_of_week_effect import indicators, risk, signals

T0 = 1699747200000  # 2023-11-12 00:00 UTC (a Sunday)


def _flat_df(n_bars=504, seed=1):
    """Flat 100.0 closes, 3 weeks of hourly bars from a Sunday."""
    rng = np.random.default_rng(seed)
    c = np.full(n_bars, 100.0) + rng.normal(0, 0.01, n_bars).cumsum() * 0
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    t = (T0 + np.arange(n_bars) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n_bars, 100.0)}
    )


class TestDayOfWeekEffect(unittest.TestCase):
    def test_weekday_hour_columns(self):
        ind = indicators.add_indicators(_flat_df())
        # Bar 0: Sunday 00:00; bar 23: Sunday 23:00; bar 24: Monday 00:00.
        self.assertEqual(int(ind["weekday"].iloc[0]), 6)
        self.assertEqual(int(ind["hour"].iloc[0]), 0)
        self.assertEqual(int(ind["weekday"].iloc[23]), 6)
        self.assertEqual(int(ind["hour"].iloc[23]), 23)
        self.assertEqual(int(ind["weekday"].iloc[24]), 0)
        self.assertEqual(int(ind["hour"].iloc[24]), 0)
        self.assertEqual(int(ind["weekday"].iloc[95]), 2)  # Wednesday 23:00
        self.assertEqual(int(ind["hour"].iloc[95]), 23)

    def test_long_entries_sundays_2300(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df()))
        # Sundays 23:00 in 3 weeks: bars 23, 191, 359.
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [23, 191, 359])

    def test_long_exits_mondays_2300(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df()))
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [47, 215, 383])

    def test_short_entries_wednesdays_2300(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df()))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [95, 263, 431])

    def test_short_exits_thursdays_2300(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df()))
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [119, 287, 455])

    def test_exactly_one_signal_per_leg_per_week(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df(504 * 2)))
        for col in ("long_entry", "long_exit", "short_entry", "short_exit"):
            self.assertEqual(int(sig[col].sum()), 6, col)

    def test_no_signals_on_other_weekdays_or_hours(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df()))
        wd = sig["weekday"].to_numpy(int)
        hr = sig["hour"].to_numpy(int)
        # Every long entry is Sunday 23:00, every short entry Wednesday 23:00.
        self.assertTrue(((wd[sig["long_entry"]] == 6) & (hr[sig["long_entry"]] == 23)).all())
        self.assertTrue(((wd[sig["short_entry"]] == 2) & (hr[sig["short_entry"]] == 23)).all())
        # No signal fires on a Tuesday, Friday, or Saturday bar.
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(bool(sig.loc[sig[col], "weekday"].isin([1, 4, 5]).any()), col)

    def test_mon_long_only_variant_has_no_shorts(self):
        sig = signals.add_signals(
            indicators.add_indicators(_flat_df()), mon_long=True, thu_short=False
        )
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [23, 191, 359])
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_wed_long_variant_adds_tuesday_entries(self):
        sig = signals.add_signals(
            indicators.add_indicators(_flat_df()), wed_long=True
        )
        # Long entries: Sundays + Tuesdays 23:00 (71, 239, 407).
        self.assertEqual(
            sig.index[sig["long_entry"]].tolist(),
            [23, 71, 191, 239, 359, 407],
        )
        # Long exits add Wednesdays 23:00; Thursday short survives.
        self.assertEqual(
            sig.index[sig["long_exit"]].tolist(),
            [47, 95, 215, 263, 383, 431],
        )
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [95, 263, 431])

    def test_no_nan_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df(2000)))
        self.assertFalse(sig["atr14"].iloc[100:].isna().any())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _flat_df(600)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (150, 300, 599):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("weekday", "hour", "atr14"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_flat_df(5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.day_of_week_effect as mod

        self.assertEqual(mod.SPEC.slug, "day_of_week_effect")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 30)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 30)


if __name__ == "__main__":
    unittest.main()
