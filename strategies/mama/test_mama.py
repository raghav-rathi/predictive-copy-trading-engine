"""MAMA tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mama import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(rows):
    """Direct signal unit-test frame from explicit per-bar dicts."""
    return pd.DataFrame(rows)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestMama(unittest.TestCase):
    def test_registered(self):
        self.assertIn("mama", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_smooth_wma4_hand_computed(self):
        # price = (h + l) / 2 = close here (h = c + 0.5, l = c - 0.5).
        # Smooth = (4P + 3P[1] + 2P[2] + P[3]) / 10, lags before bar 0
        # clamped to P[0].
        closes = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
        df = indicators.add_indicators(_frame(closes))
        s = df["mama_smooth"].to_numpy()
        self.assertAlmostEqual(s[0], 10.0, places=9)   # (40+30+20+10)/10
        self.assertAlmostEqual(s[1], 14.0, places=9)   # (80+30+20+10)/10
        self.assertAlmostEqual(s[2], 21.0, places=9)   # (120+60+20+10)/10
        self.assertAlmostEqual(s[3], 30.0, places=9)   # (160+90+40+10)/10
        self.assertAlmostEqual(s[4], 40.0, places=9)   # (200+120+60+20)/10
        self.assertAlmostEqual(s[5], 50.0, places=9)

    def test_detrender_zero_on_flat(self):
        # On flat data the Hilbert taps sum to zero (0.0962 + 0.5769
        # - 0.5769 - 0.0962 = 0), so the detrender stays ~0.
        df = indicators.add_indicators(_flat_frame(n=300))
        tail = df.iloc[100:]
        self.assertTrue(np.allclose(tail["mama_detrender"], 0.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["mama_i1"], 0.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["mama_q1"], 0.0, atol=1e-9))

    def test_flat_data_mama_converges_to_price(self):
        # price constant -> MAMA/FAMA converge to the price whatever
        # alpha does; no crosses, no entries.
        df = _run(_flat_frame(n=300))
        tail = df.iloc[100:]
        self.assertTrue(np.allclose(tail["mama"], 100.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["fama"], 100.0, atol=1e-9))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_alpha_and_period_bounds(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[100:]
        self.assertTrue(np.isfinite(tail["mama"]).all())
        self.assertTrue(np.isfinite(tail["fama"]).all())
        self.assertTrue(((tail["mama_alpha"] >= 0.05)
                         & (tail["mama_alpha"] <= 0.5)).all())
        self.assertTrue(((tail["mama_period"] >= 6.0)
                         & (tail["mama_period"] <= 50.0)).all())
        # One-arg atan phase lives in [-90, 90] degrees.
        self.assertTrue(((tail["mama_phase"] >= -90.0)
                         & (tail["mama_phase"] <= 90.0)).all())

    def test_mama_leads_fama_on_uptrend(self):
        # Steady ramp: FAMA is a half-alpha smoothing of MAMA, so after
        # spin-up MAMA sits above FAMA on a sustained climb.
        n = 300
        closes = 100.0 + np.arange(n) * 0.5
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[200:]
        self.assertTrue((tail["mama"] > tail["fama"]).all())
        self.assertTrue((tail["mama"] < closes[200:]).all())

    def test_cross_detection_crafted_rows(self):
        rows = [dict(mama=104.0, fama=105.0), dict(mama=106.0, fama=105.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        rows = [dict(mama=96.0, fama=95.0), dict(mama=94.0, fama=95.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        # No cross while MAMA stays on the same side of FAMA.
        rows = [dict(mama=106.0, fama=105.0), dict(mama=107.0, fama=106.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Touching exactly is not a cross (strict >).
        rows = [dict(mama=104.0, fama=105.0), dict(mama=105.0, fama=105.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        # NaN lines (warmup): no entry, no exit.
        rows = [dict(mama=110.0, fama=np.nan)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])

    def test_long_entry_on_trend(self):
        # Flat at 100, then a steady climb: MAMA must cross above FAMA.
        n = 300
        closes = np.full(n, 100.0)
        closes[150:] = 100.0 + np.arange(n - 150) * 0.5
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[150:250].any())
        self.assertFalse(df["short_entry"].iloc[:150].any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 100)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("mama_smooth", "mama_detrender", "mama_period",
                    "mama_alpha", "mama", "fama",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): no crash, MAMA/FAMA finite.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.isfinite(tail["mama"]).all())
        self.assertTrue(np.isfinite(tail["fama"]).all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
