"""Network-free unit tests for Camarilla pivots."""

import unittest

import numpy as np
import pandas as pd

from strategies.camarilla_pivots import indicators, risk, signals

T0 = pd.Timestamp("2026-01-01", tz="UTC").value // 10**6  # UTC midnight


def _two_days(day2):
    """day1: 24 flat bars H=110 L=100 C=105; day2: given (h,l,c) rows."""
    rows = []
    for i in range(24):
        rows.append((110.0, 100.0, 105.0))
    rows.extend(day2)
    n = len(rows)
    h = np.array([r[0] for r in rows])
    l = np.array([r[1] for r in rows])
    c = np.array([r[2] for r in rows])
    return pd.DataFrame(
        {
            "t": T0 + np.arange(n, dtype=np.int64) * 3600_000,
            "o": c,
            "h": h,
            "l": l,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


class TestCamarillaIndicators(unittest.TestCase):
    def test_levels_from_prior_session(self):
        df = indicators.add_indicators(_two_days([(106.0, 104.0, 105.0)]))
        day2 = df.iloc[24]
        self.assertAlmostEqual(day2["cam_R4"], 110.5)
        self.assertAlmostEqual(day2["cam_R3"], 107.75)
        self.assertAlmostEqual(day2["cam_S3"], 102.25)
        self.assertAlmostEqual(day2["cam_S4"], 99.5)
        self.assertAlmostEqual(day2["cam_mid"], 105.0)

    def test_first_day_has_no_levels(self):
        df = indicators.add_indicators(_two_days([(106.0, 104.0, 105.0)]))
        self.assertTrue(df["cam_R3"].iloc[:24].isna().all())

    def test_no_lookahead(self):
        df = _two_days([(106.0, 104.0, 105.0), (108.0, 105.0, 106.0)])
        full = indicators.add_indicators(df)
        trunc = indicators.add_indicators(df.iloc[:-1])
        for col in ("cam_R4", "cam_R3", "cam_S3", "cam_S4", "cam_mid"):
            pd.testing.assert_series_equal(
                full[col].iloc[:-1], trunc[col], check_names=False
            )


class TestCamarillaFade(unittest.TestCase):
    def test_fade_entries_and_one_per_level(self):
        day2 = [
            (106.0, 104.0, 105.0),  # bar 24: nothing
            (108.5, 105.0, 106.0),  # bar 25: R3 touch -> short
            (108.0, 106.0, 107.0),  # bar 26: again, no re-entry
            (109.0, 106.0, 107.0),  # bar 27: again, no re-entry
            (106.0, 104.0, 105.0),  # bar 28: nothing
            (104.0, 102.0, 103.0),  # bar 29: S3 touch -> long
            (103.0, 101.0, 102.0),  # bar 30: again, no re-entry
        ]
        df = signals.add_signals(indicators.add_indicators(_two_days(day2)), mode="fade")
        self.assertTrue(df["short_entry"].iloc[25])
        self.assertFalse(df["short_entry"].iloc[[24, 26, 27, 28, 29, 30]].any())
        self.assertTrue(df["long_entry"].iloc[29])
        self.assertFalse(df["long_entry"].iloc[[24, 25, 26, 27, 28, 30]].any())

    def test_fade_exit_at_mid(self):
        day2 = [
            (106.0, 104.0, 105.0),  # neutral: low above S3
            (104.0, 102.0, 103.0),  # S3 touch -> long
            (106.0, 103.0, 105.5),  # closes above mid -> long exit
        ]
        df = signals.add_signals(indicators.add_indicators(_two_days(day2)), mode="fade")
        self.assertTrue(df["long_entry"].iloc[25])
        self.assertTrue(df["long_exit"].iloc[26])


class TestCamarillaBreakout(unittest.TestCase):
    def test_breakout_reverse(self):
        day2 = [
            (109.0, 106.0, 107.0),  # no break
            (111.0, 108.0, 111.2),  # close > R4(110.5) -> long + reverse short exit
            (110.0, 108.0, 109.0),  # back inside -> long exit
            (111.0, 108.0, 111.3),  # second break same session -> no entry
        ]
        df = signals.add_signals(
            indicators.add_indicators(_two_days(day2)), mode="breakout"
        )
        self.assertTrue(df["long_entry"].iloc[25])
        self.assertTrue(df["short_exit"].iloc[25])  # stop-and-reverse
        self.assertTrue(df["long_exit"].iloc[26])  # back inside R4
        self.assertFalse(df["long_entry"].iloc[27])  # one reversal per session


class TestCamarillaRisk(unittest.TestCase):
    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 3.0)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 72)


if __name__ == "__main__":
    unittest.main()
