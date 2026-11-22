"""Oliver Kell 20-EMA Reclaim tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.oliver_kell_ema_reclaim import indicators, risk, signals


def _frame(c, v=None, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    if v is None:
        v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame(c, seed=seed)


def _v_path():
    """Uptrend 100->160, one-bar dip to 140 (-12.5% off the high,
    below the 20 EMA), then reclaim 155/162/165. Quiet volume
    (40 vs 100) from the dip bar on. Fires exactly once, bar 252.
    """
    c = np.concatenate([
        np.linspace(100, 160, 250),
        [140.0, 155.0, 162.0, 165.0, 168.0, 170.0],
        np.linspace(170, 180, 20),
    ])
    n = len(c)
    v = np.full(n, 100.0)
    v[250:] = 40.0
    return _frame(c, v=v)


def _inverted_v_path():
    """Mirror: downtrend 160->100, one-bar spike to 120 (+12.5%
    off the low, above the 20 EMA), then 105/98/95. Quiet volume
    from the spike bar on."""
    c = np.concatenate([
        np.linspace(160, 100, 250),
        [120.0, 105.0, 98.0, 95.0, 92.0, 90.0],
        np.linspace(90, 80, 20),
    ])
    n = len(c)
    v = np.full(n, 100.0)
    v[250:] = 40.0
    return _frame(c, v=v)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("sma200", "sma200_rising", "sma200_falling", "ema10",
                    "ema20", "ema10_rising", "ema20_rising",
                    "recent_high_20", "pullback_low_20", "pullback_depth",
                    "touched_ema20", "touched_ema20_above", "vol_avg20",
                    "quiet_vol", "atr"):
            self.assertIn(col, ind.columns)

    def test_pullback_depth_on_v_path(self):
        ind = indicators.add_indicators(_v_path())
        # At the dip bar: high 160, low ~140 -> depth ~12.6%.
        d = float(ind["pullback_depth"].iloc[250])
        self.assertGreater(d, 0.05)
        self.assertLess(d, 0.19)

    def test_touched_ema20_only_after_dip(self):
        ind = indicators.add_indicators(_v_path())
        self.assertFalse(ind["touched_ema20"].iloc[250])
        self.assertTrue(ind["touched_ema20"].iloc[251])
        self.assertTrue(ind["touched_ema20"].iloc[252])

    def test_quiet_volume(self):
        ind = indicators.add_indicators(_v_path())
        self.assertFalse(ind["quiet_vol"].iloc[100])
        self.assertTrue(ind["quiet_vol"].iloc[252])

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("sma200", "ema20", "pullback_depth", "touched_ema20"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:300].reset_index(drop=True),
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

    def test_reclaim_enters_long_once(self):
        sig = signals.add_signals(indicators.add_indicators(_v_path()))
        fires = np.where(sig["long_entry"])[0]
        self.assertEqual(len(fires), 1)
        self.assertEqual(int(fires[0]), 252)

    def test_inverted_reclaim_enters_short_once(self):
        sig = signals.add_signals(
            indicators.add_indicators(_inverted_v_path()))
        fires = np.where(sig["short_entry"])[0]
        self.assertEqual(len(fires), 1)
        self.assertEqual(int(fires[0]), 252)

    def test_no_pullback_no_entry(self):
        # Straight uptrend, no dip below the 20 EMA: never touches.
        c = np.linspace(100, 200, 300)
        sig = signals.add_signals(indicators.add_indicators(_frame(c)))
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())

    def test_too_deep_pullback_rejected(self):
        # Dip to 120 = 25% off the 160 high: outside the 5-19% band.
        c = np.concatenate([
            np.linspace(100, 160, 250),
            [120.0, 155.0, 162.0, 165.0, 168.0, 170.0],
            np.linspace(170, 180, 20),
        ])
        n = len(c)
        v = np.full(n, 100.0)
        v[250:] = 40.0
        sig = signals.add_signals(
            indicators.add_indicators(_frame(c, v=v)))
        self.assertFalse(sig["long_entry"].any())

    def test_loud_volume_rejected(self):
        # Same V-path but volume stays loud (100) through the reclaim.
        c = np.concatenate([
            np.linspace(100, 160, 250),
            [140.0, 155.0, 162.0, 165.0, 168.0, 170.0],
            np.linspace(170, 180, 20),
        ])
        sig = signals.add_signals(
            indicators.add_indicators(_frame(c)))
        self.assertFalse(sig["long_entry"].any())

    def test_exit_on_close_below_ema20(self):
        # Hand-built frame: cross below the 20 EMA at bar 2.
        n = 4
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        df = pd.DataFrame({
            "t": t, "o": np.full(n, 100.0), "h": np.full(n, 101.0),
            "l": np.full(n, 99.0), "c": [105.0, 104.0, 98.0, 97.0],
            "v": np.full(n, 100.0),
            "sma200": np.full(n, 90.0),
            "sma200_rising": np.full(n, True),
            "sma200_falling": np.full(n, False),
            "ema10_rising": np.full(n, True),
            "ema20_rising": np.full(n, True),
            "ema10_falling": np.full(n, False),
            "ema20_falling": np.full(n, False),
            "ema20": np.full(n, 100.0),
            "pullback_depth": np.full(n, 0.10),
            "touched_ema20": np.array([False, True, True, True]),
            "touched_ema20_above": np.full(n, False),
            "quiet_vol": np.full(n, True),
        })
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_exit"].iloc[2])
        self.assertFalse(sig["long_exit"].iloc[1])

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:300]
        sig_full = signals.add_signals(indicators.add_indicators(df))
        sig_short = signals.add_signals(indicators.add_indicators(short))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                sig_full[col].iloc[:300].reset_index(drop=True),
                sig_short[col].reset_index(drop=True),
                check_names=False,
            )


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
        self.assertEqual(risk.WARMUP, 210)

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
