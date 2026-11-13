"""Volume Spread Analysis tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.volume_spread_analysis import indicators, risk, signals
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
        "v": rng.uniform(50, 200, n),
    })


class TestVolumeSpreadAnalysis(unittest.TestCase):
    def test_registered(self):
        self.assertIn("volume_spread_analysis", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_spread_and_vol_mean_exact(self):
        # Hand-computed: spread = h - l; vol_mean20 at bar 19 is the
        # mean of the first 20 volumes.
        n = 30
        closes = [100.0] * n
        highs = [102.0] * n
        lows = [98.0] * n
        vols = [100.0] * 19 + [200.0] + [100.0] * 10
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows, vols=vols))
        self.assertTrue(np.allclose(df["vsa_spread"], 4.0))
        self.assertAlmostEqual(df["vsa_vol_mean20"].iloc[19], 105.0)
        # Constant true range 4 -> Wilder ATR(20) converges to 4.
        self.assertAlmostEqual(df["vsa_atr20"].iloc[29], 4.0, places=9)

    def test_narrow_flag_exact(self):
        # Spread 1 < 0.5 * ATR(20)=2 -> narrow; spread 4 is not.
        n = 30
        closes = [100.0] * n
        highs = [102.0] * 20 + [100.5] * 10
        lows = [98.0] * 20 + [99.5] * 10
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        self.assertFalse(df["vsa_narrow"].iloc[19])
        self.assertTrue(df["vsa_narrow"].iloc[29])

    def test_no_supply(self):
        # Bars 0-19: flat 100, range 4, volume 100. Bars 20-22: down
        # bars, spread 1 (narrow), volume falling 90/80/70.
        n = 24
        closes = [100.0] * 20 + [99.8, 99.6, 99.4, 99.2]
        highs = [102.0] * 20 + [100.5] * 4
        lows = [98.0] * 20 + [99.5] * 4
        vols = [100.0] * 20 + [90.0, 80.0, 70.0, 200.0]
        df = _run(_frame(closes, highs=highs, lows=lows, vols=vols))
        self.assertTrue(df["vsa_no_supply"].iloc[22])
        self.assertTrue(df["long_entry"].iloc[22])
        # Bar 23: volume jumps to 200 -> not lower than each prior bar.
        self.assertFalse(df["vsa_no_supply"].iloc[23])
        # No-supply needs a down bar: an up bar with the same volume
        # profile is no-demand instead.
        closes2 = [100.0] * 20 + [100.2, 100.4, 100.6]
        df2 = _run(_frame(closes2, highs=[102.0] * 20 + [101.0] * 3,
                          lows=[98.0] * 20 + [100.0] * 3,
                          vols=[100.0] * 20 + [90.0, 80.0, 70.0]))
        self.assertFalse(df2["vsa_no_supply"].iloc[22])
        self.assertTrue(df2["vsa_no_demand"].iloc[22])
        self.assertTrue(df2["short_entry"].iloc[22])

    def test_stopping_volume(self):
        # 30 bars declining 115 -> 102 on volume 100, range 4.
        # Bar 30: down bar (101 < 102), close 101 in the upper half
        # of [98, 103] (mid 100.5), volume 250 > 2x mean 100.
        closes = list(np.linspace(115.0, 102.0, 30)) + [101.0]
        highs = [c + 2.0 for c in closes[:30]] + [103.0]
        lows = [c - 2.0 for c in closes[:30]] + [98.0]
        vols = [100.0] * 30 + [250.0]
        df = _run(_frame(closes, highs=highs, lows=lows, vols=vols))
        self.assertTrue(df["vsa_stopping_volume"].iloc[30])
        self.assertTrue(df["long_entry"].iloc[30])
        # Same bar with volume 150 (not > 2x mean) is not stopping volume.
        vols2 = [100.0] * 30 + [150.0]
        df2 = _run(_frame(closes, highs=highs, lows=lows, vols=vols2))
        self.assertFalse(df2["vsa_stopping_volume"].iloc[30])

    def test_upthrust(self):
        # Bars 0-19: high 101. Bar 20: high 105 (above prior 20-bar
        # high), low 99, close 100.5 in the lower third
        # (99 + 6/3 = 101), volume 200 > 1.5x mean 100.
        n = 21
        closes = [100.0] * 20 + [100.5]
        highs = [101.0] * 20 + [105.0]
        lows = [99.0] * 20 + [99.0]
        vols = [100.0] * 20 + [200.0]
        df = _run(_frame(closes, highs=highs, lows=lows, vols=vols))
        self.assertTrue(df["vsa_upthrust"].iloc[20])
        self.assertTrue(df["short_entry"].iloc[20])
        # Volume 120 (not > 1.5x mean) -> no upthrust.
        df2 = _run(_frame(closes, highs=highs, lows=lows,
                          vols=[100.0] * 20 + [120.0]))
        self.assertFalse(df2["vsa_upthrust"].iloc[20])

    def test_signal_logic_crafted_rows(self):
        rows = [dict(vsa_no_supply=False, vsa_stopping_volume=False,
                     vsa_no_demand=False, vsa_upthrust=False),
                dict(vsa_no_supply=True, vsa_stopping_volume=False,
                     vsa_no_demand=False, vsa_upthrust=False)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Short signal -> short entry + long exit.
        rows = [dict(vsa_no_supply=False, vsa_stopping_volume=False,
                     vsa_no_demand=False, vsa_upthrust=False),
                dict(vsa_no_supply=False, vsa_stopping_volume=False,
                     vsa_no_demand=False, vsa_upthrust=True)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        # Both directions on one bar (stopping volume + upthrust):
        # entries fire, exits are masked.
        rows = [dict(vsa_no_supply=False, vsa_stopping_volume=True,
                     vsa_no_demand=False, vsa_upthrust=True)]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

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
        self.assertEqual(risk.WARMUP, 60)

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

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("vsa_no_supply", "vsa_upthrust", "long_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["vsa_vol_mean20"].isna().all())


if __name__ == "__main__":
    unittest.main()
