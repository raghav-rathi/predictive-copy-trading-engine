"""Balance Line pullback tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.balance_line_pullback import indicators, risk, signals

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


def _df_from_c(c, spread=0.5):
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


def _rising_df(n=80, start=100.0, slope=0.1):
    c = start + slope * np.arange(n)
    return _df_from_c(c)


def _falling_df(n=80, start=100.0, slope=0.1):
    c = start - slope * np.arange(n)
    return _df_from_c(c)


class TestBalanceLinePullback(unittest.TestCase):
    def test_smma_seeded_by_first_n_average(self):
        # Constant median 100: jaw = 100 from bar 12, teeth from
        # bar 7, lips from bar 4 (first valid value = mean of
        # the first n prices).
        ind = indicators.add_indicators(_df_from_c([100.0] * 40))
        self.assertTrue(np.isnan(ind["jaw"].iloc[11]))
        self.assertAlmostEqual(float(ind["jaw"].iloc[12]), 100.0, places=6)
        self.assertAlmostEqual(float(ind["jaw"].iloc[39]), 100.0, places=6)
        self.assertTrue(np.isnan(ind["teeth"].iloc[6]))
        self.assertAlmostEqual(float(ind["teeth"].iloc[7]), 100.0, places=6)
        self.assertTrue(np.isnan(ind["lips"].iloc[3]))
        self.assertAlmostEqual(float(ind["lips"].iloc[4]), 100.0, places=6)

    def test_smma_recursion_hand_computed(self):
        # Closes 100, 101, ...; with spread 0.5 the median at bar
        # i is (c[i-1]+c[i])/2 (100, 100.5, 101.5, 102.5, 103.5,
        # 104.5, ...). SMMA(5) seeds at the mean of the first 5
        # medians (101.6) at bar 4, then bar 5 is
        # (101.6*4 + 104.5)/5 = 102.18.
        c = [100.0 + float(i) for i in range(20)]
        ind = indicators.add_indicators(_df_from_c(c))
        self.assertAlmostEqual(float(ind["lips"].iloc[4]), 101.6, places=6)
        self.assertAlmostEqual(float(ind["lips"].iloc[5]), 102.18, places=6)

    def test_mouth_open_up_on_rising_series(self):
        ind = indicators.add_indicators(_rising_df())
        self.assertTrue(bool(ind["mouth_up"].iloc[30]))
        self.assertFalse(bool(ind["mouth_down"].iloc[30]))

    def test_mouth_open_down_on_falling_series(self):
        ind = indicators.add_indicators(_falling_df())
        self.assertTrue(bool(ind["mouth_down"].iloc[30]))
        self.assertFalse(bool(ind["mouth_up"].iloc[30]))

    def test_mouth_closed_on_flat_series(self):
        ind = indicators.add_indicators(_df_from_c([100.0] * 40))
        self.assertFalse(bool(ind["mouth_up"].iloc[30]))
        self.assertFalse(bool(ind["mouth_down"].iloc[30]))

    def test_touch_long_when_low_near_jaw(self):
        # Flat at 100, h=101, l=99: ATR=2, jaw=100, tolerance
        # 0.5*ATR=1 -> low 99 is inside [99, 101].
        ind = indicators.add_indicators(_df_from_c([100.0] * 40))
        self.assertTrue(bool(ind["touch_long"].iloc[30]))
        self.assertTrue(bool(ind["touch_short"].iloc[30]))

    def test_long_entry_fires_once_per_pullback(self):
        # Rising series: price rides above the lagging jaw with
        # the low touching it, mouth open up. The turn condition
        # holds for many consecutive bars, but the entry must
        # fire exactly once -- on the first bar of the run --
        # and never on two consecutive bars.
        sig = signals.add_signals(indicators.add_indicators(_rising_df()))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(len(entries) >= 1)
        self.assertTrue(all(b - a > 1 for a, b in zip(entries, entries[1:])))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_entry_fires_once_per_pullback(self):
        sig = signals.add_signals(indicators.add_indicators(_falling_df()))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertTrue(len(entries) >= 1)
        self.assertTrue(all(b - a > 1 for a, b in zip(entries, entries[1:])))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_entry_without_touch_in_last_five_bars(self):
        # Flat at 100 for 35 bars, then 5 wide-range bars whose
        # lows (90) sit far below the jaw band (no touch), then
        # a jump to 110 with the low at 109.5: close > jaw and
        # rising, mouth opens up, but the low never touched the
        # jaw (~100) in the last 5 bars, so no entry.
        n = 46
        c = np.full(n, 100.0)
        h = np.full(n, 100.5)
        l = np.full(n, 99.5)
        o = np.full(n, 100.0)
        l[35:40] = 90.0
        h[35:40] = 101.0
        c[40:] = 110.0 + 0.1 * np.arange(6)
        o[40:] = c[40:]
        h[40:] = c[40:] + 0.5
        l[40:] = c[40:] - 0.5
        sig = signals.add_signals(indicators.add_indicators(_df(o, h, l, c)))
        self.assertFalse(bool(sig["long_entry"].iloc[40:].any()))

    def test_mouth_gate_blocks_entry_but_jaw_only_allows_it(self):
        # Rising series with the mouth gate manually closed:
        # require_mouth=True blocks the entry, require_mouth=False
        # (the jaw-only calibration variant) lets it through.
        ind = indicators.add_indicators(_rising_df())
        ind["mouth_up"] = False
        sig_mouth = signals.add_signals(ind, require_mouth=True)
        sig_jaw = signals.add_signals(ind, require_mouth=False)
        self.assertFalse(bool(sig_mouth["long_entry"].any()))
        self.assertTrue(bool(sig_jaw["long_entry"].any()))

    def test_long_exit_on_close_below_jaw(self):
        # Rise, then a sharp drop through the jaw: the close
        # crossing below the jaw exits the long.
        c = list(100.0 + 0.1 * np.arange(60)) + [90.0, 89.0, 88.0] + [88.0] * 10
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(any(e >= 60 for e in exits))

    def test_long_exit_on_lips_cross_below_teeth(self):
        # After a rise, a fall makes the fast lips cross below
        # the teeth (mouth closing) -- an exit even before the
        # close reaches the jaw.
        c = list(100.0 + 0.1 * np.arange(50)) + list(105.0 - 0.1 * np.arange(30))
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["long_exit"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("median", "jaw", "teeth", "lips", "atr14"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "mouth_up", "mouth_down", "touch_long", "touch_short",
                    "touch_long_recent", "touch_short_recent"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("median", "jaw", "teeth", "lips", "atr14",
                        "touch_long", "touch_long_recent"):
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
        import strategies.balance_line_pullback as mod

        self.assertEqual(mod.SPEC.slug, "balance_line_pullback")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 96)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
