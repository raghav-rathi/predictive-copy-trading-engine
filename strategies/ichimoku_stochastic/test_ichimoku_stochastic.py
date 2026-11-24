"""Ichimoku + Stochastic tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.ichimoku_stochastic import indicators, risk, signals


def _frame(o, h, l, c, v=None):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _mk(c):
    """Frame with h/l straddling o/c so Ichimoku midpoints are
    well-defined on every bar."""
    c = np.asarray(c, dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    return _frame(o, np.maximum(o, c) + 0.5, np.minimum(o, c) - 0.5, c)


def _golden_closes():
    """Deterministic regime series (seed 0 noise): flat 100, grind
    down to 55, flat 55, grind up to 75, flat 75. Verified against
    the shipped implementation: SHORT entries at bars 217 and 253
    (decline leg), LONG entries at bars 341 and 369 (recovery leg,
    %K crossing up from single digits while price sits above the
    low cloud)."""
    rng = np.random.default_rng(0)
    c = np.concatenate([
        np.full(120, 100.0),
        np.linspace(100, 55, 60),
        np.full(80, 55.0),
        np.linspace(55, 75, 60),
        np.full(80, 75.0),
    ])
    return c * (1 + rng.normal(0, 0.002, len(c))).cumprod() / 1.0


def _random_walk_frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    return _frame(o, h, l, c, v)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("tenkan", "kijun", "senkou_a", "senkou_b",
                    "cloud_top", "cloud_bottom", "stoch_k", "stoch_d",
                    "atr14"):
            self.assertIn(col, ind.columns)
        # Chikou Span is deliberately NOT exposed (lookahead).
        self.assertNotIn("chikou", ind.columns)

    def test_flat_series_cloud_equals_price(self):
        # Golden value: on a constant 100 series the 9/26/52
        # midpoints are all 100, so the cloud is flat at 100
        # (h/l straddle by +-0.5 in _mk, so midpoints are 100).
        ind = indicators.add_indicators(_mk([100.0] * 120))
        self.assertAlmostEqual(ind["tenkan"].iloc[-1], 100.0, places=9)
        self.assertAlmostEqual(ind["kijun"].iloc[-1], 100.0, places=9)
        self.assertAlmostEqual(ind["cloud_top"].iloc[-1], 100.0, places=9)
        self.assertAlmostEqual(ind["cloud_bottom"].iloc[-1], 100.0, places=9)

    def test_cloud_formed_only_after_78_bars(self):
        ind = indicators.add_indicators(_random_walk_frame(n=120))
        # Senkou B needs 52 bars + 26-bar shift: NaN before bar 77.
        self.assertTrue(ind["senkou_b"].iloc[:77].isna().all())
        self.assertTrue(np.isfinite(ind["senkou_b"].iloc[77]))
        self.assertTrue(np.isfinite(ind["cloud_top"].iloc[77]))

    def test_cloud_top_ge_cloud_bottom(self):
        ind = indicators.add_indicators(_random_walk_frame())
        formed = ind.dropna(subset=["cloud_top", "cloud_bottom"])
        self.assertTrue((formed["cloud_top"] >= formed["cloud_bottom"]).all())

    def test_stoch_bounds_zero_to_100(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(((ind["stoch_k"] >= 0) & (ind["stoch_k"] <= 100)).all())
        self.assertTrue(((ind["stoch_d"] >= 0) & (ind["stoch_d"] <= 100)).all())

    def test_stoch_flat_series_is_50(self):
        # Flat 14-bar range -> HH == LL -> %K defined as 50.0.
        ind = indicators.add_indicators(_mk([100.0] * 80))
        self.assertTrue((ind["stoch_k"] == 50.0).all())
        self.assertTrue((ind["stoch_d"] == 50.0).all())

    def test_stoch_k_formula_on_known_series(self):
        # Rising closes 100..113: on the last bar LL14 = 100,
        # HH14 = 113, c = 113 -> %K = 100.
        c = list(range(100, 114))
        ind = indicators.add_indicators(_mk(c))
        self.assertAlmostEqual(ind["stoch_k"].iloc[-1], 100.0, places=9)
        # Falling closes 113..100: last bar %K = 0.
        ind2 = indicators.add_indicators(_mk(list(range(113, 99, -1))))
        self.assertAlmostEqual(ind2["stoch_k"].iloc[-1], 0.0, places=9)

    def test_no_nan_in_stoch_columns(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("stoch_k", "stoch_d"):
            self.assertFalse(ind[col].isna().any(), col)
            self.assertTrue(np.isfinite(ind[col]).all(), col)

    def test_no_lookahead(self):
        df = _mk(_golden_closes())
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("tenkan", "kijun", "senkou_a", "senkou_b",
                    "stoch_k", "stoch_d"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:200].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, c, tenkan, kijun, top, bottom, k, d):
        n = len(k)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": np.asarray(c, dtype=float),
            "h": np.asarray(c, dtype=float) + 1,
            "l": np.asarray(c, dtype=float) - 1,
            "c": np.asarray(c, dtype=float),
            "v": np.full(n, 100.0),
            "tenkan": np.asarray(tenkan, dtype=float),
            "kijun": np.asarray(kijun, dtype=float),
            "cloud_top": np.asarray(top, dtype=float),
            "cloud_bottom": np.asarray(bottom, dtype=float),
            "stoch_k": np.asarray(k, dtype=float),
            "stoch_d": np.asarray(d, dtype=float),
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_golden_series(self):
        sig = signals.add_signals(indicators.add_indicators(_mk(_golden_closes())))
        self.assertTrue(sig["long_entry"].iloc[341])
        self.assertTrue(sig["long_entry"].iloc[369])
        self.assertEqual(int(sig["long_entry"].sum()), 2)
        # Bar 341: price above cloud, Tenkan > Kijun, %K crosses
        # up from 0.0 while %K = 6.92 < 30.
        self.assertGreater(sig["c"].iloc[341], sig["cloud_top"].iloc[341])
        self.assertGreater(sig["tenkan"].iloc[341], sig["kijun"].iloc[341])
        self.assertLess(sig["stoch_k"].iloc[341], 30)

    def test_short_entry_on_golden_series(self):
        sig = signals.add_signals(indicators.add_indicators(_mk(_golden_closes())))
        self.assertTrue(sig["short_entry"].iloc[217])
        self.assertTrue(sig["short_entry"].iloc[253])
        self.assertEqual(int(sig["short_entry"].sum()), 2)
        self.assertLess(sig["c"].iloc[217], sig["cloud_bottom"].iloc[217])
        self.assertGreater(sig["stoch_k"].iloc[217], 70)

    def test_long_entry_requires_all_three_conditions(self):
        # %K crosses up below 30, Tenkan > Kijun, but close is
        # INSIDE the cloud (below cloud top): no entry.
        sig = signals.add_signals(self._signal_frame(
            c=[100, 100, 100, 100], tenkan=[10, 11, 12, 13],
            kijun=[9, 9, 9, 9], top=[105, 105, 105, 105],
            bottom=[95, 95, 95, 95], k=[20, 15, 10, 25], d=[20, 18, 14, 20]))
        self.assertFalse(sig["long_entry"].any())

    def test_no_long_entry_when_k_not_oversold(self):
        # Cross up but %K = 50 on the cross bar: gate fails.
        sig = signals.add_signals(self._signal_frame(
            c=[100, 100, 100, 100], tenkan=[10, 11, 12, 13],
            kijun=[9, 9, 9, 9], top=[90, 90, 90, 90],
            bottom=[80, 80, 80, 80], k=[40, 45, 48, 50], d=[40, 44, 49, 49]))
        self.assertFalse(sig["long_entry"].any())

    def test_exit_long_on_opposite_cross(self):
        # Long at bar 1 (cross up, %K 25 < 30, above cloud); %K
        # crosses below %D at bar 3 while still above the cloud.
        sig = signals.add_signals(self._signal_frame(
            c=[100, 100, 100, 100], tenkan=[10, 11, 12, 13],
            kijun=[9, 9, 9, 9], top=[90, 90, 90, 90],
            bottom=[80, 80, 80, 80], k=[20, 25, 28, 20], d=[22, 24, 24, 26]))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertFalse(sig["long_exit"].iloc[2])

    def test_exit_long_on_close_back_into_cloud(self):
        # Long at bar 1; bar 2 closes at the cloud top (inside
        # the cloud) with no Stochastic cross: exit fires.
        sig = signals.add_signals(self._signal_frame(
            c=[100, 100, 90, 100], tenkan=[10, 11, 12, 13],
            kijun=[9, 9, 9, 9], top=[90, 90, 90, 90],
            bottom=[80, 80, 80, 80], k=[20, 25, 26, 27], d=[22, 24, 25, 26]))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[2])

    def test_no_short_entry_when_close_above_cloud_bottom(self):
        # Same setup as a short entry, except close 100 sits above
        # the cloud bottom (90): the cloud filter blocks it.
        sig = signals.add_signals(self._signal_frame(
            c=[100, 100, 90, 100], tenkan=[13, 12, 11, 10],
            kijun=[14, 14, 14, 14], top=[110, 110, 110, 110],
            bottom=[90, 90, 90, 90], k=[80, 75, 74, 73], d=[78, 76, 75, 74]))
        # Bar 1: %K 75 crosses below %D 76 while %K > 70, close
        # 100 < cloud bottom 90? No — 100 > 90, so no short.
        self.assertFalse(sig["short_entry"].any())

    def test_short_entry_and_cloud_exit(self):
        # Short at bar 1 (close 80 < cloud bottom 90, Tenkan <
        # Kijun, %K crosses below %D at 75 > 70); bar 3 closes
        # back at the cloud bottom -> exit.
        sig = signals.add_signals(self._signal_frame(
            c=[80, 80, 80, 90], tenkan=[13, 12, 11, 10],
            kijun=[14, 14, 14, 14], top=[110, 110, 110, 110],
            bottom=[90, 90, 90, 90], k=[80, 75, 74, 73], d=[78, 76, 75, 74]))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertTrue(sig["short_exit"].iloc[3])

    def test_flip_on_opposite_entry(self):
        # Long at bar 1; bar 3 carries a full short setup
        # (close below cloud bottom, Tenkan < Kijun, %K crosses
        # below %D at 75 > 70) -> exit long + enter short.
        sig = signals.add_signals(self._signal_frame(
            c=[100, 100, 100, 80], tenkan=[10, 11, 12, 8],
            kijun=[9, 9, 9, 14], top=[90, 90, 90, 90],
            bottom=[80, 80, 80, 85], k=[20, 25, 80, 75], d=[22, 24, 79, 76]))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_no_reentry_while_held(self):
        sig = signals.add_signals(self._signal_frame(
            c=[100, 100, 100, 100, 100], tenkan=[10, 11, 12, 13, 14],
            kijun=[9, 9, 9, 9, 9], top=[90, 90, 90, 90, 90],
            bottom=[80, 80, 80, 80, 80],
            k=[20, 25, 26, 27, 28], d=[22, 24, 25, 26, 27]))
        # %K stays above %D after the bar-1 cross, so no second
        # cross — but even the bar-2/3 bars satisfy the level
        # conditions; only one entry must fire.
        self.assertEqual(int(sig["long_entry"].sum()), 1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 3.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 120)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 80)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
