"""VIX Fix tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vix_fix import indicators, risk, signals


def _df(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
                         "l": np.asarray(l, float), "c": np.asarray(c, float),
                         "v": np.full(n, float(v))})


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df(o, h, l, c)


def _rand_df(n=400, seed=7):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _crash_df():
    # 80 quiet bars, one violent down bar, then a mild recovery
    c = np.concatenate([100.0 + np.cumsum(np.zeros(80)),
                        [84.0],
                        84.0 + 0.4 * np.arange(40)])
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.3
    l = np.minimum(o, c) - 0.3
    l[80] = 82.0  # deep wick on the crash bar
    return _df(o, h, l, c)


def _spike_df():
    # 80 quiet bars, one violent up bar, then mild drift down
    c = np.concatenate([100.0 + np.zeros(80),
                        [118.0],
                        118.0 - 0.4 * np.arange(40)])
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.3
    l = np.minimum(o, c) - 0.3
    h[80] = 120.0
    return _df(o, h, l, c)


class TestVixFix(unittest.TestCase):
    def test_wvf_formula(self):
        h = np.concatenate([np.full(21, 100.0), [120.0]])
        l = np.full(22, 100.0)
        l[-1] = 90.0
        c = np.full(22, 105.0)
        o = np.full(22, 105.0)
        df = indicators.add_indicators(_df(o, h, l, c))
        # WVF = 100*(120-90)/120 = 25.0
        self.assertAlmostEqual(float(df["wvf"].iloc[-1]), 25.0, places=6)

    def test_wvf_bounded(self):
        df = indicators.add_indicators(_rand_df())
        wvf = df["wvf"].dropna()
        self.assertTrue(bool((wvf >= 0).all()))
        self.assertTrue(bool((wvf <= 100).all()))

    def test_fear_spike_fires_long(self):
        sig = signals.add_signals(indicators.add_indicators(_crash_df()))
        self.assertTrue(bool(sig["long_entry"].any()))
        idx = sig.index[sig["long_entry"]]
        # at the firing bar WVF is above its upper band
        self.assertTrue(bool((sig.loc[idx, "wvf"] > sig.loc[idx, "wvf_bb_upper"]).all()))

    def test_exit_after_entry(self):
        sig = signals.add_signals(indicators.add_indicators(_crash_df()))
        first_entry = int(sig.index[sig["long_entry"]][0])
        exits_after = sig["long_exit"].iloc[first_entry:]
        self.assertTrue(bool(exits_after.any()))

    def test_greed_spike_fires_short(self):
        sig = signals.add_signals(indicators.add_indicators(_spike_df()))
        self.assertTrue(bool(sig["short_entry"].any()))
        idx = sig.index[sig["short_entry"]]
        self.assertTrue(bool((sig.loc[idx, "iwvf"] > sig.loc[idx, "iwvf_bb_upper"]).all()))

    def test_flat_no_entries(self):
        c = np.full(120, 100.0)
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(bool(sig[col].isna().any()))
            self.assertTrue(bool(set(sig[col].unique()) <= {True, False}))

    def test_no_lookahead(self):
        # a signal at bar i must be identical when computed on a prefix
        full = signals.add_signals(indicators.add_indicators(_crash_df()))
        prefix = signals.add_signals(indicators.add_indicators(_crash_df().iloc[:90]))
        i = 85
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[i]), bool(prefix[col].iloc[i]))

    def test_indicators_return_copy(self):
        df = _rand_df()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertAlmostEqual(risk.RISK.fee_rate, 0.00045)
        self.assertAlmostEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertAlmostEqual(risk.RISK.risk_frac, 0.01)
        self.assertAlmostEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_spec_registers(self):
        from strategies.vix_fix import SPEC
        self.assertEqual(SPEC.slug, "vix_fix")
        self.assertEqual(SPEC.warmup_bars, risk.WARMUP)


if __name__ == "__main__":
    unittest.main()
