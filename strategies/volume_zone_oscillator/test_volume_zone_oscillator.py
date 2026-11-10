"""Volume Zone Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.volume_zone_oscillator import indicators, risk, signals
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


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(vzo, closes=None, ema60=None, adx=None):
    n = len(vzo)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    e = np.array(ema60, dtype=float) if ema60 is not None else np.full(n, 90.0)
    a = np.array(adx, dtype=float) if adx is not None else np.full(n, 25.0)
    return pd.DataFrame({
        "c": c,
        "vzo": np.array(vzo, dtype=float),
        "ema60": e,
        "adx": a,
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


class TestVolumeZoneOscillator(unittest.TestCase):
    def test_registered(self):
        self.assertIn("volume_zone_oscillator", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: signed volume is 0 every bar, so VP = 0, TV = 100,
        # VZO = 0 exactly once the EMA warmup passes.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["vzo"], 0.0, atol=1e-12))
        self.assertTrue(np.allclose(tail["signed_volume"], 0.0))
        self.assertTrue(np.allclose(tail["ema60"], 100.0, atol=1e-9))
        self.assertTrue(np.isfinite(tail["vzo"]).all())

    def test_indicator_values_steady_rise(self):
        # Closes +1 every bar, volume 100: signed volume is 100 on every
        # bar after the first, so VP -> 100, TV = 100, VZO -> 100.
        # Hand-computed: EMA(14) alpha = 2/15, VP_n = 100*(1-(13/15)^n),
        # so by bar 200 VZO is 100 to within 1e-9.
        closes = 100.0 + np.arange(300)
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["vzo"].iloc[200], 100.0, places=6)
        self.assertTrue(np.allclose(df["vzo"].iloc[100:], 100.0, atol=1e-4))

    def test_indicator_values_alternating(self):
        # Closes alternate 100/101 with volume 100: signed volume
        # alternates +100/-100. Steady state of EMA(14) (alpha = 2/15):
        # VP after an up bar = 100*a/(2-a) = 100*(2/15)/(28/15) = 50/7,
        # so VZO alternates +/-50/7 = +/-7.142857...
        closes = np.where(np.arange(300) % 2 == 0, 100.0, 101.0)
        df = indicators.add_indicators(_frame(closes))
        self.assertAlmostEqual(df["vzo"].iloc[200], -50.0 / 7.0, places=5)
        self.assertAlmostEqual(df["vzo"].iloc[201], 50.0 / 7.0, places=5)

    def test_indicator_values_zero_volume(self):
        # Zero volume everywhere: TV = 0, guarded VZO = 0, no crash.
        df = indicators.add_indicators(_flat_frame(vol=0.0))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["vzo"], 0.0, atol=1e-12))
        self.assertTrue(np.isfinite(tail["vzo"]).all())
        df2 = _run(_flat_frame(vol=0.0))
        self.assertFalse(df2["long_entry"].any())
        self.assertFalse(df2["short_entry"].any())

    def test_indicator_bounded_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.isfinite(tail["vzo"]).all())
        self.assertTrue(((tail["vzo"] >= -100.0 - 1e-9)
                         & (tail["vzo"] <= 100.0 + 1e-9)).all())
        self.assertTrue(np.isfinite(tail["ema60"]).all())
        self.assertTrue(np.isfinite(tail["adx"]).all())

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
        self.assertEqual(risk.WARMUP, 80)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_cross_above_minus40(self):
        # VZO crosses above -40 at index 3, uptrend context throughout.
        df = signals.add_signals(_signal_frame([-50, -45, -41, -39, -30]))
        self.assertTrue(df["long_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[4])
        self.assertFalse(df["short_entry"].iloc[3])

    def test_long_entry_cross_above_zero_never_oversold(self):
        # VZO crosses above 0 at index 11; the trailing 10-bar minimum
        # (-10) never reached -40, so the failed-pullback rule fires.
        vzo = [-10.0] * 10 + [-5.0, 5.0, 10.0]
        df = signals.add_signals(_signal_frame(vzo))
        self.assertTrue(df["long_entry"].iloc[11])
        self.assertFalse(df["long_entry"].iloc[10])

    def test_long_entry_blocked_when_window_hit_oversold(self):
        # Same cross above 0, but VZO dipped to -50 inside the trailing
        # 10-bar window, so the failed-pullback rule must NOT fire at the
        # zero cross (index 11). (The dip's own recovery above -40 at
        # index 6 IS a valid oversold-reversal entry under the first rule.)
        vzo = [-10.0] * 5 + [-50.0] + [-10.0] * 4 + [-5.0, 5.0]
        df = signals.add_signals(_signal_frame(vzo))
        self.assertFalse(df["long_entry"].iloc[11])
        self.assertTrue(df["long_entry"].iloc[6])

    def test_short_entry_cross_below_plus40(self):
        # VZO crosses below +40 at index 3, downtrend context throughout.
        df = signals.add_signals(_signal_frame(
            [50, 45, 41, 39, 30], ema60=[110.0] * 5))
        self.assertTrue(df["short_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[4])
        self.assertFalse(df["long_entry"].iloc[3])

    def test_short_entry_cross_below_zero_never_overbought(self):
        vzo = [10.0] * 10 + [5.0, -5.0, -10.0]
        df = signals.add_signals(_signal_frame(vzo, ema60=[110.0] * 13))
        self.assertTrue(df["short_entry"].iloc[11])
        self.assertFalse(df["short_entry"].iloc[10])

    def test_no_entry_without_trend_context(self):
        # Oversold-reversal cross, but ADX too weak (10 < 18).
        df = signals.add_signals(_signal_frame(
            [-50, -45, -41, -39, -30], adx=[10.0] * 5))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Same cross, but close below EMA(60): not an uptrend.
        df = signals.add_signals(_signal_frame(
            [-50, -45, -41, -39, -30], ema60=[110.0] * 5))
        self.assertFalse(df["long_entry"].any())

    def test_exits_vzo_zero_cross(self):
        df = signals.add_signals(_signal_frame([5.0, -5.0]))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        df = signals.add_signals(_signal_frame([-5.0, 5.0]))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])

    def test_exits_close_through_ema60(self):
        # Close crosses below EMA(60) at index 1 -> long exit.
        df = signals.add_signals(_signal_frame(
            [50.0, 50.0], closes=[105.0, 95.0], ema60=[100.0, 100.0]))
        self.assertTrue(df["long_exit"].iloc[1])
        # Close crosses above EMA(60) at index 1 -> short exit.
        df = signals.add_signals(_signal_frame(
            [-50.0, -50.0], closes=[95.0, 105.0], ema60=[100.0, 100.0]))
        self.assertTrue(df["short_exit"].iloc[1])

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("vzo", "ema60", "adx", "long_entry", "short_entry",
                    "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # Fewer bars than warmup: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
