"""Breakout-retest (throwback) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.breakout_retest import indicators, risk, signals
from strategies import base as B


def _frame_from_arrays(o, h, l, c):
    o = np.asarray(o, dtype=float)
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    c = np.asarray(c, dtype=float)
    n = len(c)
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


BRK = 25  # breakout bar: flat range must be >= 25 bars so that
# level_high[BRK-1] and level_high[BRK-2] are both valid (rolling(20)
# with min_periods=20, plus the cross's own shift(1))


def _range_breakout_up(touch_l=99.8, touch_c=102.0, touch_bar=31, n=70):
    """Flat 90/100 range, breakout up at bar 25, controlled retest."""
    o = np.full(n, 95.0)
    h = np.full(n, 100.0)
    l = np.full(n, 90.0)
    c = np.full(n, 95.0)
    # bar 25: breakout up (level = 100, ATR = 10)
    h[BRK], l[BRK], c[BRK] = 102.0, 96.0, 101.0
    # bars after: hover above (no touch, no loss, no new breakout)
    h[BRK + 1:], l[BRK + 1:], c[BRK + 1:] = 106.0, 103.0, 105.0
    # the controlled retest bar
    h[touch_bar], l[touch_bar], c[touch_bar] = touch_l + 1.0, touch_l, touch_c
    return _frame_from_arrays(o, h, l, c)


def _range_breakout_dn(touch_h=89.5, touch_c=88.5, touch_bar=31, n=70):
    """Flat 90/100 range, breakdown at bar 25, controlled retest."""
    o = np.full(n, 95.0)
    h = np.full(n, 100.0)
    l = np.full(n, 90.0)
    c = np.full(n, 95.0)
    # bar 25: breakdown (level = 90, ATR = 10)
    h[BRK], l[BRK], c[BRK] = 94.0, 88.0, 89.0
    # bars after: hover below (no touch, no loss, no new breakdown)
    h[BRK + 1:], l[BRK + 1:], c[BRK + 1:] = 87.0, 84.0, 85.0
    h[touch_bar], l[touch_bar], c[touch_bar] = touch_h, touch_h - 1.0, touch_c
    return _frame_from_arrays(o, h, l, c)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_range_breakout_up())
        for col in ("level_high", "level_low", "breakout_up",
                    "breakout_dn", "atr"):
            self.assertIn(col, ind.columns)

    def test_level_high_is_hand_computed_rolling_max(self):
        # No lookahead: level_high[j] == max(h[j-19..j]).
        df = _range_breakout_up(n=40)
        ind = indicators.add_indicators(df)
        h = df["h"].to_numpy()
        j = 33
        self.assertAlmostEqual(ind["level_high"].iloc[j], h[j - 19:j + 1].max())
        # at bar 24 the level is exactly the flat range top
        self.assertAlmostEqual(ind["level_high"].iloc[24], 100.0)

    def test_breakout_up_at_right_bar(self):
        ind = indicators.add_indicators(_range_breakout_up())
        brk = ind["breakout_up"].to_numpy()
        self.assertTrue(brk[BRK], f"breakout_up must fire at bar {BRK}")
        self.assertFalse(brk[:BRK].any(), "no breakout inside the flat range")
        self.assertFalse(brk[BRK + 1:].any(), "no spurious breakouts after")

    def test_breakout_dn_at_right_bar(self):
        ind = indicators.add_indicators(_range_breakout_dn())
        brk = ind["breakout_dn"].to_numpy()
        self.assertTrue(brk[BRK], f"breakout_dn must fire at bar {BRK}")
        self.assertFalse(brk[:BRK].any())
        self.assertFalse(brk[BRK + 1:].any())

    def test_breakout_level_is_prior_bar_level(self):
        # The setup level is the prior-bar rolling extreme, not the
        # breakout bar's own high (which includes the breakout wick).
        ind = indicators.add_indicators(_range_breakout_up())
        self.assertAlmostEqual(ind["level_high"].iloc[BRK - 1], 100.0)
        self.assertAlmostEqual(ind["level_high"].iloc[BRK], 102.0)  # wick included
        # the cross is taken against level_high.shift(1): bar BRK's close
        # 101 > 100 (prior) but not > 102 (its own bar's level)
        self.assertTrue(ind["breakout_up"].iloc[BRK])


class TestSignals(unittest.TestCase):
    def _sig(self, df):
        return signals.add_signals(indicators.add_indicators(df))

    def test_clean_retest_triggers_long_entry(self):
        sig = self._sig(_range_breakout_up())
        le = sig["long_entry"].to_numpy()
        self.assertTrue(le[31], "clean retest at bar 31 must enter long")
        self.assertFalse(le[:31].any(), "no early entries (hover bars have no touch)")

    def test_touch_without_rejection_no_entry(self):
        # Wick touched the zone but the close stayed below the line.
        sig = self._sig(_range_breakout_up(touch_l=100.5, touch_c=99.0))
        self.assertFalse(sig["long_entry"].to_numpy().any())

    def test_no_touch_no_entry(self):
        # Close is back above the line but the low never reached the zone.
        df = _range_breakout_up(touch_l=103.0, touch_c=104.0)  # l=103 > 100+1
        sig = self._sig(df)
        self.assertFalse(sig["long_entry"].to_numpy().any())

    def test_deep_retest_cancels_setup(self):
        # Bar 27 closes below level - 0.5*ATR (100 - 5 = 95) -> setup
        # dead; the would-be clean touch at bar 31 must not fire.
        df = _range_breakout_up()
        c = df["c"].to_numpy()
        c[27] = 93.0   # level lost before the retest touch
        df["c"] = c
        sig = self._sig(df)
        self.assertFalse(sig["long_entry"].to_numpy().any(),
                         "failed retest must cancel the setup: no entry ever")

    def test_window_expiry_no_signal(self):
        # Touch at bar 46 = breakout bar + 21 -> outside the 20-bar window.
        # touch_l=99.0 is a would-be valid touch, so only expiry blocks it.
        sig = self._sig(_range_breakout_up(touch_l=99.0, touch_bar=46, n=80))
        self.assertFalse(sig["long_entry"].to_numpy().any(),
                         "touch at bar 21 after breakout must not signal")

    def test_window_edge_bar_20_still_valid(self):
        # Touch exactly at breakout+20 is still inside the window.
        sig = self._sig(_range_breakout_up(touch_l=99.0, touch_bar=45, n=70))
        self.assertTrue(sig["long_entry"].to_numpy()[45])

    def test_bearish_mirror_clean_retest(self):
        sig = self._sig(_range_breakout_dn())
        se = sig["short_entry"].to_numpy()
        self.assertTrue(se[31], "clean retest must enter short")
        self.assertFalse(se[:31].any())
        self.assertFalse(sig["long_entry"].to_numpy().any())

    def test_bearish_mirror_failed_retest_cancels(self):
        df = _range_breakout_dn()
        c = df["c"].to_numpy()
        c[27] = 96.0   # close above level + 0.5*ATR (90 + 5) -> lost
        df["c"] = c
        sig = self._sig(df)
        self.assertFalse(sig["short_entry"].to_numpy().any())

    def test_long_exit_on_level_loss(self):
        df = _range_breakout_up(n=80)
        c = df["c"].to_numpy()
        c[35] = 93.0   # close below level - 0.5*ATR after entry
        df["c"] = c
        sig = self._sig(df)
        self.assertTrue(sig["long_entry"].to_numpy()[31])
        self.assertTrue(sig["long_exit"].to_numpy()[35])
        self.assertFalse(sig["long_exit"].to_numpy()[:35].any())

    def test_short_exit_on_level_loss_mirror(self):
        df = _range_breakout_dn(n=80)
        c = df["c"].to_numpy()
        c[35] = 96.0   # close above level + 0.5*ATR after short entry
        df["c"] = c
        sig = self._sig(df)
        self.assertTrue(sig["short_entry"].to_numpy()[31])
        self.assertTrue(sig["short_exit"].to_numpy()[35])

    def test_no_lookahead_truncated_frame_matches(self):
        # Signals on bars 0..30 must not change when future bars exist.
        df_full = _range_breakout_up(n=70)
        df_trunc = _range_breakout_up(n=70).iloc[:36].copy()
        sig_full = self._sig(df_full).iloc[:36]
        sig_trunc = self._sig(df_trunc)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "breakout_up", "breakout_dn"):
            pd.testing.assert_series_equal(sig_full[col], sig_trunc[col],
                                           check_names=False)

    def test_most_recent_breakout_wins(self):
        # Breakout at 25 (level 100), second breakout at 30 (level 106).
        # A touch of the NEW level at 31 must enter; the old level's
        # zone (100 +/- band) is not even touched, so an entry at 31
        # proves the newer setup replaced the older one.
        n = 70
        o = np.full(n, 95.0); h = np.full(n, 100.0)
        l = np.full(n, 90.0); c = np.full(n, 95.0)
        h[25], l[25], c[25] = 102.0, 96.0, 101.0    # breakout 1, level 100
        h[26:30], l[26:30], c[26:30] = 106.0, 96.0, 105.0
        h[30], l[30], c[30] = 108.0, 102.0, 106.5   # breakout 2, level 106
        h[31], l[31], c[31] = 107.0, 106.2, 106.3   # touch of 106 only
        df = _frame_from_arrays(o, h, l, c)
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["breakout_up"].iloc[30], "second breakout must print")
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[31],
                        "entry on the most recent setup's level")

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(3)
        n = 500
        rets = rng.normal(0.0, 0.01, n)
        c = 100.0 * np.exp(np.cumsum(rets))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.003, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.003, n))
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                           "v": rng.uniform(50, 150, n)})
        sig = self._sig(df)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(sig[col].dtype, bool)
            self.assertEqual(sig[col].isna().sum(), 0)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertEqual(r.target_atr_mult, 2.0)
        self.assertEqual(r.max_hold_bars, 96)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertEqual(r.fee_rate, 0.00045)
        self.assertEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 80)

    def test_spec_slug(self):
        from strategies.breakout_retest import SPEC
        self.assertEqual(SPEC.slug, "breakout_retest")
        self.assertEqual(SPEC.warmup_bars, 80)


if __name__ == "__main__":
    unittest.main()
