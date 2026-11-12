"""SineWave tests. Network-free, synthetic data only."""

import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sinewave import indicators, risk, signals
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


def _sine_frame(n=1200, period=30.0, amp=5.0, base=100.0):
    """Pure sine-wave closes; h/l bracket the close by 0.1."""
    i = np.arange(n, dtype=float)
    c = base + amp * np.sin(2.0 * math.pi * i / period)
    return _frame(c, highs=c + 0.1, lows=c - 0.1)


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


class TestSineWave(unittest.TestCase):
    def test_registered(self):
        self.assertIn("sinewave", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_hilbert_taps_antisymmetric(self):
        # The ideal Hilbert impulse response is odd: h[k] = -h[N-1-k],
        # centre tap 0. The window preserves the antisymmetry.
        taps = indicators._hilbert_taps()
        self.assertEqual(len(taps), indicators.N_TAPS)
        self.assertEqual(taps[indicators.GROUP_DELAY], 0.0)
        np.testing.assert_allclose(taps, -taps[::-1], atol=1e-15)
        # Odd-lag taps are nonzero (2/(pi*n) * window), even-lag taps 0.
        self.assertNotEqual(taps[indicators.GROUP_DELAY + 1], 0.0)
        self.assertEqual(taps[indicators.GROUP_DELAY + 2], 0.0)

    def test_phase_advances_on_pure_sine(self):
        # On a pure 30-bar sine, the instantaneous phase advances by
        # 2*pi/30 per bar (up to a constant filter phase offset).
        df = indicators.add_indicators(_sine_frame(n=1200, period=30.0))
        phase = df["phase"].iloc[200:].to_numpy()
        self.assertTrue(np.isfinite(phase).all())
        slope = np.diff(np.unwrap(phase)).mean()
        self.assertAlmostEqual(slope, 2.0 * math.pi / 30.0, delta=0.01)

    def test_sine_lead_relation(self):
        # lead_sine is exactly sin(phase + 45 deg); sine is sin(phase).
        df = indicators.add_indicators(_sine_frame(n=600, period=30.0))
        tail = df.iloc[200:]
        np.testing.assert_allclose(tail["sine"], np.sin(tail["phase"]),
                                   atol=1e-12)
        np.testing.assert_allclose(
            tail["lead_sine"], np.sin(tail["phase"] + math.pi / 4.0),
            atol=1e-12)
        # Both lines stay inside [-1, 1].
        self.assertTrue(((tail["sine"] >= -1.0) & (tail["sine"] <= 1.0)).all())
        self.assertTrue(((tail["lead_sine"] >= -1.0)
                         & (tail["lead_sine"] <= 1.0)).all())

    def test_crosses_fire_on_sine_wave(self):
        # A sustained cycle produces both long and short crosses.
        df = _run(_sine_frame(n=1200, period=30.0))
        self.assertTrue(df["long_entry"].iloc[100:].any())
        self.assertTrue(df["short_entry"].iloc[100:].any())
        # Every long entry is a sine-above-lead cross and vice versa.
        self.assertFalse((df["long_entry"] & df["short_entry"]).any())

    def test_signal_logic_crafted_rows(self):
        rows = [
            dict(sine=0.0, lead_sine=0.5),
            dict(sine=0.6, lead_sine=0.5),
            dict(sine=0.4, lead_sine=0.5),
            dict(sine=-0.4, lead_sine=-0.5),
            dict(sine=-0.6, lead_sine=-0.5),
        ]
        df = signals.add_signals(pd.DataFrame(rows))
        # Row 1: sine crosses above lead -> long entry + short exit.
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # Row 2: sine crosses below lead -> short entry + long exit.
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[2])
        # Row 3: sine crosses above lead again -> long entry.
        self.assertTrue(df["long_entry"].iloc[3])
        # Row 4: sine crosses below lead again -> short entry.
        self.assertTrue(df["short_entry"].iloc[4])
        # NaN lines (warmup): no entry, no exit.
        df = signals.add_signals(pd.DataFrame(
            [dict(sine=np.nan, lead_sine=np.nan)]))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_no_signal_on_flat(self):
        # Flat price -> detrended series 0 -> phase 0, sine 0, lead
        # constant sin(45 deg): no crosses, no entries.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["sine"], 0.0, atol=1e-12))
        self.assertTrue(np.allclose(tail["lead_sine"], math.sin(math.pi / 4.0),
                                    atol=1e-12))

    def test_warmup_nan(self):
        # Phase is NaN until the full 51-tap Hilbert window exists.
        df = indicators.add_indicators(_sine_frame(n=600, period=30.0))
        self.assertTrue(df["phase"].iloc[: indicators.N_TAPS - 1].isna().all())
        self.assertTrue(np.isfinite(df["phase"].iloc[indicators.N_TAPS - 1]))

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
        for col in ("sine", "lead_sine", "phase", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the Hilbert window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): detrended series 0, no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
