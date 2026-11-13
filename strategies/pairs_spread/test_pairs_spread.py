"""Pairs Spread (BTC-ETH) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pairs_spread import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None, t0=1_700_000_000_000):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _signal_frame(rows):
    return pd.DataFrame(rows)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _spread_frame(n=1500, seed=7):
    """Synthetic spread instrument: random-walk log-spread, USD price
    spread built around it so the harness can run."""
    rng = np.random.default_rng(seed)
    spread = np.cumsum(rng.normal(0.0, 0.01, n))
    price = 60000.0 + 1000.0 * spread
    o = np.concatenate([[price[0]], price[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": price + 5.0, "l": price - 5.0, "c": price,
        "v": np.full(n, 100.0),
        "beta": np.full(n, 1.5),
        "spread": spread,
    })


class TestPairsSpread(unittest.TestCase):
    def test_registered(self):
        self.assertIn("pairs_spread", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_spread_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_beta_exact_value(self):
        # log_btc = 2 * log_eth + 1 exactly -> OLS slope is 2.
        x = np.linspace(1.0, 5.0, 20)
        log_eth = pd.Series(x)
        log_btc = pd.Series(2.0 * x + 1.0)
        beta = indicators.compute_beta(log_btc, log_eth, n=5)
        self.assertTrue(np.isnan(beta.iloc[3]))
        self.assertTrue(np.allclose(beta.iloc[4:], 2.0, atol=1e-12))

    def test_beta_flat_eth_undefined(self):
        # Zero variance in log_eth -> beta NaN, not inf/crash.
        log_eth = pd.Series([1.0] * 10)
        log_btc = pd.Series(np.linspace(1.0, 2.0, 10))
        beta = indicators.compute_beta(log_btc, log_eth, n=5)
        self.assertTrue(beta.iloc[5:].isna().all())

    def test_build_spread_frame_exact(self):
        # ETH log-close linear in t, BTC log-close = 2x + 1: beta -> 2,
        # log-spread -> 1 exactly; USD spread close = BTC - 2*ETH.
        n = 600
        x = np.linspace(8.0, 9.0, n)
        eth_c = np.exp(x)
        btc_c = np.exp(2.0 * x + 1.0)
        btc = _frame(btc_c)
        eth = _frame(eth_c)
        sp = indicators.build_spread_frame(btc, eth)
        self.assertEqual(len(sp), n)
        self.assertTrue(np.isnan(sp["beta"].iloc[498]))
        self.assertTrue(np.allclose(sp["beta"].iloc[499:], 2.0, atol=1e-9))
        self.assertTrue(np.allclose(sp["spread"].iloc[499:], 1.0, atol=1e-9))
        expected_c = btc_c - 2.0 * eth_c
        self.assertTrue(np.allclose(sp["c"].iloc[499:], expected_c[499:], rtol=1e-9))
        # Volume comes from the BTC leg.
        self.assertTrue((sp["v"] == 100.0).all())

    def test_z_exact_value(self):
        # Spread pinned at 0 for 100 bars, then jumps to 10 and stays:
        # on the jump bar the 100-bar window is 99 zeros + one 10,
        # mean 0.1, sample std sqrt(99*0.01 + 81*0.01 ... ) -- compute
        # directly instead of hand-arithmetic.
        n = 150
        spread = np.array([0.0] * 100 + [10.0] * 50)
        price = 60000.0 + spread
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": price, "h": price + 1, "l": price - 1, "c": price,
            "v": np.full(n, 100.0), "beta": np.full(n, 1.5),
            "spread": spread,
        })
        out = indicators.add_indicators(df)
        window = spread[1:101]  # bars 1..100, the jump bar is index 100
        mean = window.mean()
        std = window.std(ddof=1)
        self.assertAlmostEqual(out["spread_mean"].iloc[100], mean, places=12)
        self.assertAlmostEqual(out["spread_std"].iloc[100], std, places=12)
        self.assertAlmostEqual(out["z"].iloc[100], (10.0 - mean) / std, places=12)
        # Flat spread before the jump: std 0 -> z defined as 0.
        self.assertTrue(np.allclose(out["z"].iloc[99:100], 0.0, atol=1e-12))

    def test_z_hand_computed(self):
        df = _spread_frame()
        out = indicators.add_indicators(df)
        s = df["spread"]
        mean = s.rolling(100, min_periods=100).mean()
        std = s.rolling(100, min_periods=100).std()
        manual = ((s - mean) / std).fillna(0.0)
        pd.testing.assert_series_equal(
            out["z"].reset_index(drop=True),
            manual.reset_index(drop=True), check_names=False, atol=1e-12)

    def test_long_entry_cross_below_minus2(self):
        rows = [dict(z=-1.0), dict(z=-2.5), dict(z=-1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].any())

    def test_short_entry_cross_above_plus2(self):
        rows = [dict(z=1.0), dict(z=2.5), dict(z=1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].any())

    def test_exit_at_zero_cross(self):
        # Long spread exits when z crosses up through 0.
        rows = [dict(z=-1.0), dict(z=0.5)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # Short spread exits when z crosses down through 0.
        rows = [dict(z=1.0), dict(z=-0.5)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Touching exactly +/-2 or 0 is not a cross (strict).
        rows = [dict(z=-1.0), dict(z=-2.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        rows = [dict(z=-1.0), dict(z=0.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_exit"].iloc[1])

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
        self.assertEqual(risk.WARMUP, 600)

    def test_backtest_smoke(self):
        df = _run(_spread_frame())
        res = run_backtest(df, risk.RISK, coin="SPREAD", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_future_jump(self):
        df1 = _run(_spread_frame(n=1300))
        df2 = _run(_spread_frame(n=1350))
        for col in ("z", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_spread_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
