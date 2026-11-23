"""MACD divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.macd_rsi_divergence import indicators, risk, signals


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
    """Frame with explicit h=c+1, l=c-1 so pivot lows/highs are
    strict extremes (real candles have distinct intraday lows;
    deriving l from min(o, c) would tie adjacent bars)."""
    c = np.asarray(c, dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    return _frame(o, c + 1.0, c - 1.0, c)


def _divergence_closes():
    """Sharp dip to 80, recovery, then a slow drift to a lower
    low of 75. Golden (verified by hand against the pivot rule):
    confirmed pivot lows at bars 45 (price 79) and 84 (price 74);
    MACD hist at the pivots -2.017 then -0.828 — lower low with a
    HIGHER histogram, i.e. bullish divergence confirmed at 84."""
    c = [100.0] * 40
    c += [95, 90, 85, 80, 85, 90, 95, 100]
    c += [100.0] * 10
    c += list(np.linspace(100, 75, 25))
    c += [78, 82, 88, 95, 100]
    c += [100.0] * 10
    return c


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
        for col in ("macd", "macd_signal", "macd_hist", "rsi14",
                    "pivot_low_confirmed", "pivot_high_confirmed",
                    "pivot_low_price", "pivot_low_hist",
                    "pivot_high_price", "pivot_high_hist",
                    "bullish_divergence", "bearish_divergence"):
            self.assertIn(col, ind.columns)

    def test_flat_series_macd_hist_is_zero(self):
        # Golden value: on a constant price the 12/26 EMAs both
        # equal the price, so MACD line, signal and histogram are 0.
        ind = indicators.add_indicators(_mk([100.0] * 80))
        self.assertTrue((ind["macd_hist"].abs() < 1e-9).all())
        self.assertTrue((ind["macd"].abs() < 1e-9).all())

    def test_pivot_low_confirmed_two_bars_later(self):
        ind = indicators.add_indicators(_mk(_divergence_closes()))
        # Pivot bar is 43 (low 79); it must NOT be flagged at 43 —
        # confirmation needs bars 44 and 45 — and IS flagged at 45.
        self.assertFalse(bool(ind["pivot_low_confirmed"].iloc[43]))
        self.assertFalse(bool(ind["pivot_low_confirmed"].iloc[44]))
        self.assertTrue(bool(ind["pivot_low_confirmed"].iloc[45]))
        self.assertEqual(ind["pivot_low_price"].iloc[45], 79.0)
        self.assertAlmostEqual(ind["pivot_low_hist"].iloc[45], -2.017, places=2)

    def test_flat_equal_lows_produce_no_pivot(self):
        # Strict lowest: equal lows are not a pivot.
        ind = indicators.add_indicators(_mk([100.0] * 80))
        self.assertEqual(int(ind["pivot_low_confirmed"].sum()), 0)
        self.assertEqual(int(ind["pivot_high_confirmed"].sum()), 0)

    def test_bullish_divergence_lower_low_higher_hist(self):
        ind = indicators.add_indicators(_mk(_divergence_closes()))
        lows = ind.loc[ind["pivot_low_confirmed"], "pivot_low_price"].tolist()
        self.assertEqual(lows, [79.0, 74.0])
        hists = ind.loc[ind["pivot_low_confirmed"], "pivot_low_hist"].tolist()
        self.assertLess(hists[0], hists[1])  # histogram higher at lower low
        self.assertTrue(bool(ind["bullish_divergence"].iloc[84]))
        self.assertEqual(int(ind["bullish_divergence"].sum()), 1)

    def test_bearish_divergence_on_mirrored_series(self):
        mirrored = [200.0 - x for x in _divergence_closes()]
        ind = indicators.add_indicators(_mk(mirrored))
        highs = ind.loc[ind["pivot_high_confirmed"], "pivot_high_price"].tolist()
        self.assertEqual(highs, [121.0, 126.0])
        self.assertTrue(bool(ind["bearish_divergence"].iloc[84]))
        self.assertEqual(int(ind["bearish_divergence"].sum()), 1)

    def test_no_nan_in_signal_inputs(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("macd_hist", "bullish_divergence", "bearish_divergence"):
            self.assertFalse(ind[col].isna().any(), col)
            if col == "macd_hist":
                self.assertTrue(np.isfinite(ind[col]).all())

    def test_no_lookahead(self):
        df = _mk(_divergence_closes())
        short = df.iloc[:60]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("pivot_low_confirmed", "bullish_divergence", "macd_hist"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:60].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, bull, bear, hist):
        n = len(hist)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        c = np.full(n, 100.0)
        return pd.DataFrame({
            "t": t, "o": c, "h": c + 1, "l": c - 1, "c": c,
            "v": np.full(n, 100.0),
            "macd_hist": np.asarray(hist, dtype=float),
            "bullish_divergence": np.asarray(bull, dtype=bool),
            "bearish_divergence": np.asarray(bear, dtype=bool),
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_divergence_with_rising_hist(self):
        sig = signals.add_signals(
            indicators.add_indicators(_mk(_divergence_closes())))
        self.assertTrue(sig["long_entry"].iloc[84])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_no_long_entry_when_hist_not_rising(self):
        # Divergence at bar 2 but histogram falling there: no entry.
        sig = signals.add_signals(self._signal_frame(
            bull=np.array([False, False, True, False]),
            bear=np.zeros(4, dtype=bool),
            hist=np.array([0.0, 1.0, 0.5, 0.6]),
        ))
        self.assertFalse(sig["long_entry"].any())

    def test_exit_long_on_hist_zero_cross_below(self):
        # Long at bar 1 (div + rising hist); hist crosses below 0
        # at bar 3 -> exit.
        sig = signals.add_signals(self._signal_frame(
            bull=np.array([False, True, False, False]),
            bear=np.zeros(4, dtype=bool),
            hist=np.array([0.0, 0.5, 0.2, -0.1]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertFalse(sig["long_exit"].iloc[2])

    def test_exit_long_on_bearish_divergence(self):
        sig = signals.add_signals(self._signal_frame(
            bull=np.array([False, True, False, False]),
            bear=np.array([False, False, False, True]),
            hist=np.array([0.0, 0.5, 0.6, 0.5]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_flip_on_opposite_divergence(self):
        # Long at bar 1; bar 3 has a bearish divergence AND falling
        # hist -> exit long and enter short on the same bar.
        sig = signals.add_signals(self._signal_frame(
            bull=np.array([False, True, False, False]),
            bear=np.array([False, False, False, True]),
            hist=np.array([0.0, 0.5, 0.6, 0.4]),
        ))
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_short_entry_and_zero_cross_exit(self):
        sig = signals.add_signals(self._signal_frame(
            bull=np.zeros(4, dtype=bool),
            bear=np.array([False, True, False, False]),
            hist=np.array([0.0, -0.5, -0.2, 0.1]),
        ))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertTrue(sig["short_exit"].iloc[3])

    def test_no_reentry_while_held(self):
        # Divergence + rising hist on bars 1, 2, 3: only one entry.
        sig = signals.add_signals(self._signal_frame(
            bull=np.array([False, True, True, True]),
            bear=np.zeros(4, dtype=bool),
            hist=np.array([0.0, 0.5, 0.6, 0.7]),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 120)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 60)

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
