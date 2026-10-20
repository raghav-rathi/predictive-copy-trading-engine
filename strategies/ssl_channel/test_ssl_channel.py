"""SSL Channel tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.ssl_channel import indicators, risk, signals


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


def _rand_df(n=400, seed=33):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


class TestSSLChannel(unittest.TestCase):
    def test_channel_formula(self):
        df = indicators.add_indicators(_rand_df())
        pd.testing.assert_series_equal(
            df["ssl_up"].dropna(),
            B.sma(df["h"], 10).dropna(),
            check_names=False,
        )
        pd.testing.assert_series_equal(
            df["ssl_dn"].dropna(),
            B.sma(df["l"], 10).dropna(),
            check_names=False,
        )

    def test_sustained_rally_goes_bullish(self):
        c = 100.0 + 2.0 * np.arange(80)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(float(sig["ssl_state"].iloc[-1]), 1.0)
        self.assertTrue(bool(sig["long_entry"].any()))

    def test_sustained_decline_goes_bearish(self):
        c = 100.0 + 2.0 * np.arange(40)
        c = np.concatenate([c, c[-1] - 3.0 * np.arange(1, 41)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(float(sig["ssl_state"].iloc[-1]), -1.0)
        self.assertTrue(bool(sig["short_entry"].any()))

    def test_state_holds_between_lines(self):
        # rally hard, then grind sideways inside the channel: state stays 1
        c = np.concatenate([100.0 + 2.0 * np.arange(40),
                            180.0 + 0.05 * np.sin(np.arange(60))])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c, spread=0.5)))
        self.assertEqual(float(sig["ssl_state"].iloc[-1]), 1.0)

    def test_exits_are_opposite_flips(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_one_entry_per_flip(self):
        c = np.concatenate([100.0 + 2.0 * np.arange(40),   # bull flip
                            180.0 - 3.0 * np.arange(40),   # bear flip
                            60.0 + 2.0 * np.arange(40)])   # bull flip again
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertEqual(int(sig["long_entry"].sum()), 2)
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_flat_no_entries(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(np.full(120, 100.0))))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_entry_on_cross_above_line(self):
        c = 100.0 + 2.0 * np.arange(80)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        i = int(sig.index[sig["long_entry"]][0])
        # on the firing bar the close broke above the upper channel line
        self.assertTrue(float(sig["c"].iloc[i]) > float(sig["ssl_up"].iloc[i]))

    def test_no_lookahead(self):
        df = _rand_df()
        full = signals.add_signals(indicators.add_indicators(df))
        prefix = signals.add_signals(indicators.add_indicators(df.iloc[:200]))
        for col in ("ssl_state", "long_entry", "short_entry"):
            self.assertEqual(float(full[col].iloc[150]), float(prefix[col].iloc[150]))

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(bool(sig[col].isna().any()))
            self.assertTrue(bool(set(sig[col].unique()) <= {True, False}))

    def test_indicators_return_copy(self):
        df = _rand_df()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 200)
        self.assertAlmostEqual(risk.RISK.fee_rate, 0.00045)
        self.assertAlmostEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertAlmostEqual(risk.RISK.risk_frac, 0.01)
        self.assertAlmostEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.WARMUP, 30)

    def test_spec_registers(self):
        from strategies.ssl_channel import SPEC
        self.assertEqual(SPEC.slug, "ssl_channel")
        self.assertEqual(SPEC.warmup_bars, risk.WARMUP)


if __name__ == "__main__":
    unittest.main()
