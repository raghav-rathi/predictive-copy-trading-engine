"""Wilder Parabolic SAR tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.wilder_parabolic_sar import indicators, risk, signals


def _frame(o, h, l, c, v=None, seed=7):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _rising_frame():
    """Hand-computed series (see test_psar_hand_computed_values):
    bars 0-4 rise, bar 5 gaps down through the SAR and flips."""
    h = [102, 103, 104, 105, 106, 106]
    l = [100, 101, 102, 103, 104, 99]
    c = [101, 102, 103, 104, 105, 100]
    return _frame(c, h, l, c)


def _random_walk_frame(n=1500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("psar", "psar_dir", "psar_ep", "psar_af", "atr"):
            self.assertIn(col, ind.columns)

    def test_seed_values_bar_zero(self):
        # Seeded LONG: SAR = low[0], EP = high[0], AF = step.
        ind = indicators.add_indicators(_rising_frame())
        self.assertEqual(ind["psar"].iloc[0], 100.0)
        self.assertEqual(ind["psar_ep"].iloc[0], 102.0)
        self.assertAlmostEqual(ind["psar_af"].iloc[0], 0.02)
        self.assertEqual(ind["psar_dir"].iloc[0], 1)

    def test_psar_hand_computed_values(self):
        # Hand-computed (clamp binds on bars 1-2: SAR cannot exceed
        # the lowest low of the prior two bars, here low[0] = 100):
        #   bar1: raw 100+0.02*(102-100)=100.04 -> clamped to 100
        #   bar2: raw 100+0.04*(103-100)=100.12 -> clamped to 100
        #   bar3: raw 100+0.06*(104-100)=100.24 -> min(100.24,102,101)
        #   bar4: raw 100.24+0.08*(105-100.24)=100.6208
        ind = indicators.add_indicators(_rising_frame())
        expect_sar = [100.0, 100.0, 100.0, 100.24, 100.6208]
        for i, e in enumerate(expect_sar):
            self.assertAlmostEqual(ind["psar"].iloc[i], e, places=4, msg=f"bar {i}")
        expect_ep = [102.0, 103.0, 104.0, 105.0, 106.0]
        for i, e in enumerate(expect_ep):
            self.assertAlmostEqual(ind["psar_ep"].iloc[i], e, msg=f"ep bar {i}")
        expect_af = [0.02, 0.04, 0.06, 0.08, 0.10]
        for i, e in enumerate(expect_af):
            self.assertAlmostEqual(ind["psar_af"].iloc[i], e, msg=f"af bar {i}")

    def test_flip_to_short_on_low_below_sar(self):
        # Bar 5 low 99 < SAR 101.16: flip; new SAR = old EP (106),
        # new EP = 99, AF resets to 0.02.
        ind = indicators.add_indicators(_rising_frame())
        self.assertEqual(ind["psar_dir"].iloc[5], -1)
        self.assertAlmostEqual(ind["psar"].iloc[5], 106.0)
        self.assertAlmostEqual(ind["psar_ep"].iloc[5], 99.0)
        self.assertAlmostEqual(ind["psar_af"].iloc[5], 0.02)

    def test_af_caps_at_max(self):
        n = 40
        hh = 100 + np.arange(n, dtype=float)
        ll = hh - 2
        cc = hh - 0.5
        ind = indicators.add_indicators(_frame(cc, hh, ll, cc))
        self.assertLessEqual(ind["psar_af"].max(), 0.20)
        self.assertAlmostEqual(ind["psar_af"].iloc[-1], 0.20)
        self.assertTrue((ind["psar_dir"] == 1).all())

    def test_short_trend_continues_after_flip(self):
        # After the bar-5 flip, keep falling: SAR stays above price
        # and AF grows as new lows print.
        h = [102, 103, 104, 105, 106, 106, 105, 104, 103]
        l = [100, 101, 102, 103, 104, 99, 98, 97, 96]
        c = [101, 102, 103, 104, 105, 100, 99, 98, 97]
        ind = indicators.add_indicators(_frame(c, h, l, c))
        self.assertTrue((ind["psar_dir"].iloc[5:] == -1).all())
        self.assertTrue((ind["psar"].iloc[5:] > ind["c"].iloc[5:]).all())
        self.assertGreater(ind["psar_af"].iloc[-1], 0.02)

    def test_no_nan_in_psar_columns(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("psar", "psar_dir", "psar_ep", "psar_af"):
            self.assertFalse(ind[col].isna().any(), col)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:500]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("psar", "psar_dir", "psar_ep", "psar_af"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:500].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )

    def test_sar_below_price_in_uptrend_above_in_downtrend(self):
        ind = indicators.add_indicators(_random_walk_frame())
        up = ind["psar_dir"] == 1
        self.assertTrue((ind.loc[up, "psar"] <= ind.loc[up, "c"]).all())
        dn = ind["psar_dir"] == -1
        self.assertTrue((ind.loc[dn, "psar"] >= ind.loc[dn, "c"]).all())


class TestSignals(unittest.TestCase):
    def _signal_frame(self, psar_dir):
        n = len(psar_dir)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": np.full(n, 100.0), "h": np.full(n, 101.0),
            "l": np.full(n, 99.0), "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
            "psar_dir": np.asarray(psar_dir, dtype=int),
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_no_entry_on_bar_zero(self):
        # Seeded long from bar 0 must NOT emit an entry.
        sig = signals.add_signals(self._signal_frame([1] * 10))
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_first_flip_to_short_enters_short(self):
        sig = signals.add_signals(
            self._signal_frame([1, 1, 1, -1, -1, -1]))
        self.assertTrue(sig["short_entry"].iloc[3])
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_flip_back_to_long_exits_short_and_enters_long(self):
        sig = signals.add_signals(
            self._signal_frame([1, 1, -1, -1, 1, 1]))
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertTrue(sig["short_exit"].iloc[4])
        self.assertTrue(sig["long_entry"].iloc[4])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_no_reentry_while_trend_persists(self):
        sig = signals.add_signals(
            self._signal_frame([1, 1, -1, -1, -1, 1, 1, 1]))
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_end_to_end_flip_enters_on_real_data(self):
        ind = indicators.add_indicators(_rising_frame())
        sig = signals.add_signals(ind)
        # Bars 0-4 long (seeded, no entry), bar 5 flips short.
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertTrue(sig["short_entry"].iloc[5])
        self.assertEqual(int(sig["short_entry"].sum()), 1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 336)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 20)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreater(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
