"""BTC Breakout Trend Climber tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.btc_breakout_trend_climber import indicators, risk, signals


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=800, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _flat_then_break(direction="up", flat=100.0, n_flat=620, jump=5.0):
    """Flat closes, then a step to flat+jump (up) or flat-jump (down)."""
    c = np.concatenate([
        np.full(n_flat, flat),
        np.full(10, flat + jump if direction == "up" else flat - jump),
    ])
    return _frame_from_close(c, seed=3)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("donch_high_600", "donch_low_600", "bb_mid", "bb_upper",
                    "bb_lower", "atr5", "atr10", "atr15", "atr"):
            self.assertIn(col, ind.columns)

    def test_donchian_is_prior_600_only(self):
        # Flat 100s: after 600 bars the prior-600 high is ~100.2
        # (high = close * up to 1.002). The level at bar 620 must not
        # include bar 620's own high.
        df = _frame_from_close(np.full(650, 100.0), seed=3)
        ind = indicators.add_indicators(df)
        lvl = float(ind["donch_high_600"].iloc[620])
        self.assertAlmostEqual(
            lvl, float(df["h"].iloc[20:620].max()), places=9)
        # The level at bar 620 equals the max high over bars 20..619
        # and therefore cannot include bar 620's own high: it is
        # unchanged if bar 620's high is raised.
        df2 = df.copy()
        df2.loc[620, "h"] = 500.0
        ind2 = indicators.add_indicators(df2)
        self.assertAlmostEqual(
            float(ind2["donch_high_600"].iloc[620]), lvl, places=9)

    def test_bollinger_ema_mid(self):
        # On a flat series the EMA mid converges to the flat level
        # and the band width collapses toward zero.
        df = _frame_from_close(np.full(700, 100.0), seed=3)
        ind = indicators.add_indicators(df)
        self.assertAlmostEqual(float(ind["bb_mid"].iloc[-1]), 100.0, places=6)
        self.assertLess(float(ind["bb_upper"].iloc[-1]) - 100.0, 0.5)

    def test_warmup_nan(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(ind["donch_high_600"].iloc[:600].isna().all())
        self.assertFalse(ind["donch_high_600"].iloc[601:].isna().any())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:700]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("donch_high_600", "bb_upper", "atr10"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:700].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_up_breakout_enters_long(self):
        sig = signals.add_signals(
            indicators.add_indicators(_flat_then_break("up")))
        fires = np.where(sig["long_entry"])[0]
        self.assertEqual(len(fires), 1)
        self.assertEqual(int(fires[0]), 620)
        self.assertFalse(sig["long_entry"].iloc[:620].any())

    def test_down_breakout_enters_short(self):
        sig = signals.add_signals(
            indicators.add_indicators(_flat_then_break("down")))
        fires = np.where(sig["short_entry"])[0]
        self.assertEqual(len(fires), 1)
        self.assertEqual(int(fires[0]), 620)
        self.assertFalse(sig["short_entry"].iloc[:620].any())

    def test_no_breakout_no_entry(self):
        # Flat the whole way: no cross of either Donchian or BB level.
        sig = signals.add_signals(
            indicators.add_indicators(_frame_from_close(np.full(700, 100.0))))
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_opposite_breakout_is_exit(self):
        # Hand-built frame: long breakout at bar 1, short breakout at bar 3.
        n = 5
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({
            "t": t, "o": np.full(n, 100.0), "h": np.full(n, 101.0),
            "l": np.full(n, 99.0), "c": [100.0, 102.0, 102.0, 97.0, 97.0],
            "v": np.full(n, 100.0),
            "donch_high_600": np.full(n, 101.0),
            "donch_low_600": np.full(n, 98.0),
            "bb_upper": np.full(n, 101.0), "bb_lower": np.full(n, 99.0),
        })
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["short_entry"].iloc[3])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_exit"].iloc[1])

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:700]
        sig_full = signals.add_signals(indicators.add_indicators(df))
        sig_short = signals.add_signals(indicators.add_indicators(short))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                sig_full[col].iloc[:700].reset_index(drop=True),
                sig_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 10)
        self.assertEqual(r.stop_atr_mult, 3.5)
        self.assertEqual(r.trail_atr_mult, 11.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertIsNone(r.max_hold_bars)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 610)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
