"""Weis Wave tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.weis_wave import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, vols=None, highs=None, lows=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 1.0
    l = np.array(lows, dtype=float) if lows is not None else closes - 1.0
    o = np.concatenate([[closes[0]], closes[:-1]]) if n else np.zeros(0)
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _flat_frame(n=200, close=100.0, vol=10.0):
    return _frame([close] * n, vols=[vol] * n)


def _long_entry_frame():
    # Bars 0-19 flat 100 (v=100); 20-24 rally to 110 (v=100);
    # bar 25 sharp drop to 105 (v=10) ends the up-wave; bars 26-29
    # drift to 101 (v=10); bar 30 bounce to 106 ends the down-wave.
    # Completed up-wave volume = 25 bars x 100 = 2500.
    # Completed down-wave volume = 5 bars x 10 = 50 < 0.85 x 2500.
    closes = [100] * 20 + [102, 104, 106, 108, 110] + [105, 104, 103, 102, 101] + [106]
    vols = [100] * 25 + [10] * 6
    return _frame(closes, vols=vols)


def _short_entry_frame():
    # Bars 0-19 flat 100 (v=10); 20-24 rally to 110 (v=10);
    # bars 25-34 fall to 92 on heavy volume (v=100); bar 35 bounce
    # to 96 ends the down-wave (1000 not < 0.85 x 250, so NO long);
    # bars 36-39 rally to 100 (v=10); bar 40 drop to 96 ends the
    # up-wave. Completed vols: up 250, down 1000, up 50 < 0.85 x 1000.
    closes = (
        [100] * 20 + [102, 104, 106, 108, 110]
        + [105, 103, 101, 99, 97, 96, 95, 94, 93, 92]
        + [96] + [97, 98, 99, 100] + [96]
    )
    vols = [10] * 25 + [100] * 10 + [10] * 6
    return _frame(closes, vols=vols)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 1.0, "l": c - 1.0, "c": c,
        "v": np.full(n, 100.0),
    })


class TestWeisWave(unittest.TestCase):
    def test_registered(self):
        self.assertIn("weis_wave", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat price, h-l = 2 every bar: TR = 2, ATR -> 2, reversal = 3,
        # close never falls 3 below the wave high, so the wave never
        # flips: wave_dir stays +1 and wave_vol accumulates 10/bar.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue((df["wave_dir"] == 1).all())
        self.assertTrue(np.allclose(df["wave_vol"], 10.0 * (np.arange(200) + 1)))
        self.assertTrue(df["last_completed_wave_vol"].isna().all())
        self.assertTrue(df["prev_completed_wave_vol"].isna().all())
        self.assertTrue(np.allclose(df["weis_atr"].iloc[100:], 2.0, atol=1e-9))
        self.assertFalse(df["wave_vol"].isna().any())

    def test_indicator_values_long_frame(self):
        # Hand-computed wave volumes on the crafted long-entry frame.
        df = indicators.add_indicators(_long_entry_frame())
        # Up-wave runs bars 0-24: 25 bars x 100 = 2500.
        self.assertEqual(df["wave_vol"].iloc[24], 2500.0)
        self.assertEqual(df["wave_dir"].iloc[24], 1)
        # Down-wave starts bar 25 (reversal bar belongs to the new wave).
        self.assertEqual(df["wave_dir"].iloc[25], -1)
        self.assertEqual(df["wave_vol"].iloc[25], 10.0)
        self.assertEqual(df["last_completed_wave_vol"].iloc[25], 2500.0)
        self.assertTrue(np.isnan(df["prev_completed_wave_vol"].iloc[25]))
        # Down-wave runs bars 25-29: 5 bars x 10 = 50.
        self.assertEqual(df["wave_vol"].iloc[29], 50.0)
        self.assertEqual(df["wave_dir"].iloc[29], -1)
        # Up-wave starts bar 30; completed vols now 50 (last) / 2500 (prev).
        self.assertEqual(df["wave_dir"].iloc[30], 1)
        self.assertEqual(df["wave_vol"].iloc[30], 10.0)
        self.assertEqual(df["last_completed_wave_vol"].iloc[30], 50.0)
        self.assertEqual(df["prev_completed_wave_vol"].iloc[30], 2500.0)

    def test_indicator_values_short_frame(self):
        df = indicators.add_indicators(_short_entry_frame())
        self.assertEqual(df["wave_vol"].iloc[24], 250.0)
        self.assertEqual(df["wave_dir"].iloc[25], -1)
        self.assertEqual(df["last_completed_wave_vol"].iloc[25], 250.0)
        # Down-wave bars 25-34: 10 bars x 100 = 1000.
        self.assertEqual(df["wave_vol"].iloc[34], 1000.0)
        # Up-wave starts bar 35; completed vols 1000 / 250.
        self.assertEqual(df["wave_dir"].iloc[35], 1)
        self.assertEqual(df["last_completed_wave_vol"].iloc[35], 1000.0)
        self.assertEqual(df["prev_completed_wave_vol"].iloc[35], 250.0)
        # Up-wave bars 35-39: 5 bars x 10 = 50; down-wave starts bar 40.
        self.assertEqual(df["wave_vol"].iloc[39], 50.0)
        self.assertEqual(df["wave_dir"].iloc[40], -1)
        self.assertEqual(df["last_completed_wave_vol"].iloc[40], 50.0)
        self.assertEqual(df["prev_completed_wave_vol"].iloc[40], 1000.0)

    def test_long_entry_on_drying_volume(self):
        df = _run(_long_entry_frame())
        self.assertTrue(df["long_entry"].iloc[30])
        self.assertEqual(df["long_entry"].sum(), 1)
        self.assertFalse(df["short_entry"].any())
        # The flip bar also exits an open short.
        self.assertTrue(df["short_exit"].iloc[30])
        # The down-wave start exits an open long.
        self.assertTrue(df["long_exit"].iloc[25])

    def test_short_entry_on_drying_volume(self):
        df = _run(_short_entry_frame())
        # Bar 35 starts an up-wave but the completed down-wave (1000)
        # is NOT under 85% of the up-wave before it (250): no long.
        self.assertFalse(df["long_entry"].iloc[35])
        self.assertFalse(df["long_entry"].any())
        # Bar 40 starts a down-wave; completed up-wave (50) < 0.85 x 1000.
        self.assertTrue(df["short_entry"].iloc[40])
        self.assertEqual(df["short_entry"].sum(), 1)
        self.assertTrue(df["long_exit"].iloc[40])

    def test_volume_gate_blocks_entry(self):
        # Same shape as the long frame, but the down-wave carries heavy
        # volume (500/bar = 2500), which is NOT under 85% of 2500,
        # so no long entry even though the wave flips up at bar 30.
        closes = [100] * 20 + [102, 104, 106, 108, 110] + [105, 104, 103, 102, 101] + [106]
        vols = [100] * 25 + [500] * 5 + [10]
        df = _run(_frame(closes, vols=vols))
        self.assertEqual(df["wave_dir"].iloc[30], 1)
        self.assertEqual(df["last_completed_wave_vol"].iloc[30], 2500.0)
        self.assertFalse(df["long_entry"].iloc[30])
        self.assertFalse(df["long_entry"].any())

    def test_no_completed_waves_no_entry(self):
        # Only one wave ever completes: prev_completed stays NaN, so the
        # volume comparison can never pass and no entry fires.
        df = _run(_long_entry_frame().iloc[:26])
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 240)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertIn("net_pnl_usd", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("wave_dir", "wave_vol", "last_completed_wave_vol",
                    "prev_completed_wave_vol", "long_entry", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_volume(self):
        # Fewer bars than the ATR window: no crash, no entries, wave
        # stays up and volume accumulates.
        df = _run(_flat_frame(n=10))
        self.assertTrue((df["wave_dir"] == 1).all())
        self.assertEqual(df["wave_vol"].iloc[9], 100.0)
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero volume bars: waves still flip on price, volumes stay 0.
        df = _run(_frame([100.0] * 200, vols=[0.0] * 200))
        self.assertTrue((df["wave_vol"] == 0.0).all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Empty frame: no crash.
        df = indicators.add_indicators(_frame([]))
        self.assertEqual(len(df), 0)


if __name__ == "__main__":
    unittest.main()
