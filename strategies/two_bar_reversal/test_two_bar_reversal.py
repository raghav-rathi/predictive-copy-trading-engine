"""2-bar key reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.two_bar_reversal import indicators, risk, signals


def _bars(rows):
    """Build an OHLCV frame from explicit (o, h, l, c) tuples."""
    arr = np.asarray(rows, float)
    n = len(arr)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {
            "t": t,
            "o": arr[:, 0],
            "h": arr[:, 1],
            "l": arr[:, 2],
            "c": arr[:, 3],
            "v": np.full(n, 100.0),
        }
    )


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


def _rand_df(n=800, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


# bullish key reversal: bar1 down + lower low, bar2 closes above bar1 high
BULL = [
    (100, 101, 99, 100),
    (100, 101, 90, 95),
    (95, 103, 94, 102),
]
# bearish key reversal: bar1 up + higher high, bar2 closes below bar1 low
BEAR = [
    (100, 101, 99, 100),
    (100, 110, 99, 105),
    (105, 106, 98, 98),
]


class TestTwoBarReversal(unittest.TestCase):
    def test_indicator_columns_on_constructed_bars(self):
        df = indicators.add_indicators(_bars(BULL))
        self.assertEqual(df["down_bar"].tolist(), [False, True, False])
        self.assertEqual(df["up_bar"].tolist(), [False, False, True])
        # bar1 low 90 < bar0 low 99
        self.assertTrue(bool(df["lower_low"].iloc[1]))
        self.assertFalse(bool(df["lower_low"].iloc[2]))
        # bar2 high 103 > bar1 high 101
        self.assertTrue(bool(df["higher_high"].iloc[2]))

    def test_bullish_reversal_fires_on_confirmation_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_bars(BULL)))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(bool(sig["long_entry"].iloc[2]))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_bearish_reversal_fires_on_confirmation_bar(self):
        sig = signals.add_signals(indicators.add_indicators(_bars(BEAR)))
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertTrue(bool(sig["short_entry"].iloc[2]))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_entry_without_confirmation(self):
        # bar2 closes at 100: below bar1's high (101) but above bar1's close (95)
        rows = [
            (100, 101, 99, 100),
            (100, 101, 90, 95),
            (95, 101, 94, 100),
        ]
        sig = signals.add_signals(indicators.add_indicators(_bars(rows)))
        self.assertFalse(bool(sig["long_entry"].any()))
        # ... but the weaker "close" confirmation fires
        sig_close = signals.add_signals(
            indicators.add_indicators(_bars(rows)), confirm="close"
        )
        self.assertTrue(bool(sig_close["long_entry"].iloc[2]))

    def test_no_entry_without_lower_low(self):
        # bar1 is a down bar but does NOT make a lower low (l=100 > 99)
        rows = [
            (100, 101, 99, 100),
            (100, 101, 100, 95),
            (95, 103, 94, 102),
        ]
        sig = signals.add_signals(indicators.add_indicators(_bars(rows)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_none_mode_fires_on_pattern_bar_itself(self):
        sig = signals.add_signals(
            indicators.add_indicators(_bars(BULL)), confirm="none"
        )
        self.assertTrue(bool(sig["long_entry"].iloc[1]))
        self.assertFalse(bool(sig["long_entry"].iloc[2]))
        sig_bear = signals.add_signals(
            indicators.add_indicators(_bars(BEAR)), confirm="none"
        )
        self.assertTrue(bool(sig_bear["short_entry"].iloc[1]))

    def test_exits_are_opposite_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_signal_columns_boolean_no_nan_after_warmup(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
            self.assertTrue(sig[col].dtype == bool, col)

    def test_signals_fire_both_sides_on_random_walk(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertTrue(bool(sig["long_exit"].any()))
        self.assertTrue(bool(sig["short_exit"].any()))

    def test_unknown_confirm_mode_raises(self):
        with self.assertRaises(ValueError):
            signals.add_signals(indicators.add_indicators(_bars(BULL)), confirm="bogus")

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("down_bar", "up_bar", "lower_low", "higher_high"):
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
        import strategies.two_bar_reversal as mod

        self.assertEqual(mod.SPEC.slug, "two_bar_reversal")
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
        self.assertEqual(risk.WARMUP, 5)


if __name__ == "__main__":
    unittest.main()
