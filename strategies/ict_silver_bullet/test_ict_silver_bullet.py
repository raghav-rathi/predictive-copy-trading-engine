"""ICT Silver Bullet tests. Network-free, synthetic data only."""

import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ict_silver_bullet import indicators, risk, signals


def _ms(dt):
    return int(dt.replace(tzinfo=datetime.UTC).timestamp() * 1000)


def _setup_series(t0):
    """Full bullish Silver Bullet setup.

    t0 = first bar open (UTC). 400 1h bars: steady uptrend (4h EMA bias
    needs 200+ bars), a micro peak (278) then trough, a bullish FVG
    printed by the jump at bar 281, then bar 282 = 18:00 UTC = NY 14:00
    killzone: low dips into the gap, close recovers above the last 3-bar
    micro swing high (185.5 at bar 278) -> long_entry at 282.
    """
    n = 400
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    c = 100.0 + 0.3 * np.arange(n)
    o = np.concatenate([[c[0]], c[:-1]])
    h, l = c + 1.0, c - 1.0
    # bars 278-280: micro peak (278) then trough; no gaps (moves <= 2/2 bars)
    for i, v in {278: 184.5, 279: 183.8, 280: 184.2}.items():
        c[i] = v
        o[i] = c[i - 1]
        h[i], l[i] = v + 1.0, v - 1.0
    # bar 281: jump prints the bullish FVG (l[281] > h[279])
    c[281] = 186.5
    o[281] = c[280]
    h[281], l[281] = 187.5, 185.5
    # bar 282: killzone dip into the gap + recovery (MSS)
    o[282], h[282], l[282], c[282] = 186.5, 187.5, 184.5, 187.0
    for i in range(283, n):
        c[i] = 187.0 + 0.1 * (i - 282)
        o[i] = c[i - 1]
        h[i], l[i] = c[i] + 1.0, c[i] - 1.0
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


T0 = _ms(datetime.datetime(2026, 6, 1, 0, 0))  # bar 282 = 18:00 UTC
KZ_BAR = 282


class TestICTSilverBullet(unittest.TestCase):
    def test_ny_hour_conversion(self):
        df = _setup_series(T0)
        ind = indicators.add_indicators(df)
        # 2026-06-01 14:00 UTC = NY 10:00 (EDT) -> killzone
        self.assertEqual(int(ind["ny_hour"].iloc[14]), 10)
        self.assertTrue(bool(ind["in_killzone"].iloc[14]))
        # 07:00 UTC = NY 03:00 -> killzone; 15:00 UTC = NY 11:00 -> not
        self.assertEqual(int(ind["ny_hour"].iloc[7]), 3)
        self.assertTrue(bool(ind["in_killzone"].iloc[7]))
        self.assertEqual(int(ind["ny_hour"].iloc[15]), 11)
        self.assertFalse(bool(ind["in_killzone"].iloc[15]))
        # 18:00 UTC = NY 14:00 -> killzone
        self.assertTrue(bool(ind["in_killzone"].iloc[18]))

    def test_ny_day_boundary(self):
        df = _setup_series(T0)
        ind = indicators.add_indicators(df)
        # NY day flips at 04:00 UTC (00:00 NY)
        self.assertEqual(
            int(ind["ny_day"].iloc[4]), int(ind["ny_day"].iloc[3]) + 1
        )

    def test_fvg_touch_then_mitigated(self):
        ind = indicators.add_indicators(_setup_series(T0))
        # gap printed at 281, untouched before 282, touched at 282, dead after
        self.assertFalse(bool(ind["bull_fvg_touch"].iloc[:282].any()))
        self.assertTrue(bool(ind["bull_fvg_touch"].iloc[KZ_BAR]))
        self.assertFalse(bool(ind["bull_fvg_touch"].iloc[283:].any()))

    def test_fvg_does_not_carry_across_ny_days(self):
        # shift so bar 281 prints the gap at NY 23:00 and bar 282 lands on
        # the next NY day: the gap must not be touchable there
        df = _setup_series(T0 + 10 * 3_600_000)
        ind = indicators.add_indicators(df)
        self.assertNotEqual(
            int(ind["ny_day"].iloc[281]), int(ind["ny_day"].iloc[KZ_BAR])
        )
        self.assertFalse(bool(ind["bull_fvg_touch"].iloc[KZ_BAR]))

    def test_full_long_setup_fires(self):
        sig = signals.add_signals(indicators.add_indicators(_setup_series(T0)))
        le = np.flatnonzero(sig["long_entry"].values)
        self.assertIn(KZ_BAR, le)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_no_entry_outside_killzone(self):
        # identical price action, bar 282 shifted to NY 16:00 -> no entry
        df = _setup_series(T0 + 2 * 3_600_000)
        ind = indicators.add_indicators(df)
        self.assertFalse(bool(ind["in_killzone"].iloc[KZ_BAR]))
        self.assertTrue(bool(ind["bull_fvg_touch"].iloc[KZ_BAR]))  # setup intact
        sig = signals.add_signals(ind)
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_bias_follows_htf_ema(self):
        n = 300
        t = (T0 + np.arange(n) * 3_600_000).astype("int64")

        def _trend(slope, start):
            c = start + slope * np.arange(n)
            o = np.concatenate([[c[0]], c[:-1]])
            return pd.DataFrame(
                {"t": t, "o": o, "h": c + 1.0, "l": c - 1.0, "c": c,
                 "v": np.full(n, 100.0)}
            )

        up = indicators.add_indicators(_trend(0.3, 100.0))
        self.assertTrue(bool(up["bias_bull"].iloc[-1]))
        self.assertFalse(bool(up["bias_bear"].iloc[-1]))
        dn = indicators.add_indicators(_trend(-0.3, 400.0))
        self.assertTrue(bool(dn["bias_bear"].iloc[-1]))
        self.assertFalse(bool(dn["bias_bull"].iloc[-1]))
        # no bias before the 4h EMA(50) warms up
        self.assertFalse(bool(up["bias_bull"].iloc[100]))

    def test_mss_close_above_last_swing_high(self):
        ind = indicators.add_indicators(_setup_series(T0))
        # micro swing high at bar 278 = 185.5; killzone close 187.0
        self.assertTrue(bool(ind["mss_bull"].iloc[KZ_BAR]))
        self.assertFalse(bool(ind["mss_bear"].iloc[KZ_BAR]))

    def test_no_lookahead_truncation(self):
        df = _setup_series(T0)
        ind_full = indicators.add_indicators(df)
        sig_full = signals.add_signals(ind_full)
        for j in (KZ_BAR, 350):
            ind_tr = indicators.add_indicators(df.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            for col in ("in_killzone", "bias_bull", "bias_bear",
                        "bull_fvg_touch", "bear_fvg_touch",
                        "mss_bull", "mss_bear"):
                self.assertEqual(
                    bool(ind_full[col].iloc[j]), bool(ind_tr[col].iloc[j]),
                    (col, j),
                )
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]),
                    (col, j),
                )

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_setup_series(T0)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.ict_silver_bullet as mod

        self.assertEqual(mod.SPEC.slug, "ict_silver_bullet")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 0.75)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.target_atr_mult, 1.5)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 220)


if __name__ == "__main__":
    unittest.main()
