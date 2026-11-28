"""Follow-Through Day tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.follow_through_day import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC (Wednesday midnight)


def _daily_df(days):
    """Hourly bars from a list of (close, low, vol) per UTC day.

    Every bar of a day closes at the day's close, lows at the
    day's low, volume spread evenly (vol/24 per bar).
    """
    rows = []
    prev_c = days[0][0]
    for j, (c_, low, vol) in enumerate(days):
        for h in range(24):
            t = T0 + ((j * 24 + h) * 3_600_000)
            o = prev_c if h == 0 else c_
            rows.append((t, o, max(o, c_) + 0.5, low, c_, vol / 24.0))
        prev_c = c_
    return pd.DataFrame(rows, columns=["t", "o", "h", "l", "c", "v"])


def _ftd_scenario(day24_close=94.0, day24_vol=200.0, day22_low=91.0):
    """20 flat days at 100, a correction low day, then an attempt
    that FTDs on day 24 (bar 599) unless a knob is moved."""
    days = [(100.0, 99.0, 100.0)] * 20
    days += [
        (90.0, 89.0, 100.0),   # day 20: new 20d low, 10% correction
        (91.0, 90.5, 100.0),   # day 21: day 1 (first up close)
        (91.5, day22_low, 100.0),  # day 22: attempt-day 2
        (92.0, 91.5, 100.0),   # day 23: attempt-day 3
        (day24_close, 93.0, day24_vol),  # day 24: attempt-day 4
    ]
    return _daily_df(days)


def _rand_df(n=800, seed=7):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.5
    l = np.minimum(o, c) - 0.5
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


class TestFollowThroughDay(unittest.TestCase):
    def test_ftd_fires_on_attempt_day_4(self):
        sig = signals.add_signals(indicators.add_indicators(_ftd_scenario()))
        # Day 24's 23:00 bar is index 24*24+23 = 599.
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [599])
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_ftd_flag_and_attempt_day_columns(self):
        ind = indicators.add_indicators(_ftd_scenario())
        self.assertEqual(ind.index[ind["ftd_day"]].tolist(), [599])
        self.assertAlmostEqual(float(ind["ftd_attempt_low"].iloc[599]), 89.0, places=6)
        # Day 21/22/23/24 23:00 bars: attempt-days 1/2/3/4.
        for bar, day_no in ((527, 1), (551, 2), (575, 3), (599, 4)):
            self.assertEqual(int(ind["attempt_day"].iloc[bar]), day_no, bar)
        # Daily aggregates on the FTD bar.
        self.assertAlmostEqual(float(ind["d_close"].iloc[599]), 94.0, places=6)
        self.assertAlmostEqual(float(ind["d_low"].iloc[599]), 93.0, places=6)
        self.assertAlmostEqual(float(ind["d_vol"].iloc[599]), 200.0, places=6)

    def test_no_ftd_when_gain_below_threshold(self):
        # Day-24 return 93/92 - 1 = 1.09% < 1.5%: no FTD.
        sig = signals.add_signals(
            indicators.add_indicators(_ftd_scenario(day24_close=93.0))
        )
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_ftd_when_volume_not_up(self):
        # Day-24 volume flat at 100 (not > prior day): no FTD.
        sig = signals.add_signals(
            indicators.add_indicators(_ftd_scenario(day24_vol=100.0))
        )
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_ftd_when_gain_threshold_lowered_it_fires(self):
        # Same 1.09% day fires under a 1.0% threshold: the
        # gain parameter actually drives the signal.
        sig = signals.add_signals(
            indicators.add_indicators(_ftd_scenario(day24_close=93.0), gain_pct=0.01)
        )
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [599])

    def test_attempt_fails_on_undercut(self):
        # Day 22 low 88 undercuts attempt_low 89: attempt dies,
        # no FTD even though day 24 is a big up day on volume.
        sig = signals.add_signals(
            indicators.add_indicators(_ftd_scenario(day22_low=88.0))
        )
        self.assertFalse(bool(sig["long_entry"].any()))
        ind = indicators.add_indicators(_ftd_scenario(day22_low=88.0))
        self.assertFalse(bool(ind["ftd_day"].any()))

    def test_no_attempt_without_correction(self):
        # Only a 5% dip (95 vs 100): corr gate never true, so
        # the new low + up day start no attempt.
        days = [(100.0, 99.0, 100.0)] * 20
        days += [
            (95.0, 94.0, 100.0),
            (96.0, 95.0, 100.0),
            (97.0, 96.0, 100.0),
            (98.0, 97.0, 100.0),
            (99.5, 98.0, 200.0),
        ]
        sig = signals.add_signals(indicators.add_indicators(_daily_df(days)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_ftd_window_expires_after_day_7(self):
        # Big up day on rising volume lands on attempt-day 8:
        # too late, no FTD.
        days = [(100.0, 99.0, 100.0)] * 20
        days += [
            (90.0, 89.0, 100.0),
            (91.0, 90.5, 100.0),
            (91.2, 91.0, 100.0),
            (91.4, 91.1, 100.0),
            (91.6, 91.2, 100.0),
            (91.8, 91.3, 100.0),
            (92.0, 91.4, 100.0),
            (92.2, 91.5, 100.0),
            (94.5, 92.5, 200.0),  # attempt-day 8
        ]
        sig = signals.add_signals(indicators.add_indicators(_daily_df(days)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exit_when_close_undercuts_attempt_low(self):
        # After the FTD, a day closing at 88 (< attempt_low 89)
        # exits the long on its 23:00 bar (index 623).
        days = [(100.0, 99.0, 100.0)] * 20
        days += [
            (90.0, 89.0, 100.0),
            (91.0, 90.5, 100.0),
            (91.5, 91.0, 100.0),
            (92.0, 91.5, 100.0),
            (94.0, 93.0, 200.0),
            (88.0, 87.0, 100.0),
        ]
        sig = signals.add_signals(indicators.add_indicators(_daily_df(days)))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [599])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [623])

    def test_no_exit_while_close_holds_above_attempt_low(self):
        # Post-FTD days close above 89: no exit.
        days = [(100.0, 99.0, 100.0)] * 20
        days += [
            (90.0, 89.0, 100.0),
            (91.0, 90.5, 100.0),
            (91.5, 91.0, 100.0),
            (92.0, 91.5, 100.0),
            (94.0, 93.0, 200.0),
            (93.0, 90.0, 100.0),
            (92.0, 91.0, 100.0),
        ]
        sig = signals.add_signals(indicators.add_indicators(_daily_df(days)))
        self.assertFalse(bool(sig["long_exit"].any()))

    def test_long_only_never_shorts(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(1200, seed=3)))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(1200, seed=5)))
        for col in ("d_close", "d_low", "d_vol", "atr14"):
            self.assertFalse(sig[col].iloc[528:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "ftd_day", "corr_gate", "new_low_day"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(600)
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (150, 300, 599):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("d_close", "d_low", "d_vol", "corr_gate",
                        "new_low_day", "attempt_day", "ftd_day",
                        "ftd_attempt_low", "atr14"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_daily_df(
            [(100.0, 99.0, 100.0), (101.0, 100.0, 100.0)]).iloc[:3]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.follow_through_day as mod

        self.assertEqual(mod.SPEC.slug, "follow_through_day")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 240)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 528)


if __name__ == "__main__":
    unittest.main()
