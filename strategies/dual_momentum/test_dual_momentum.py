"""Dual Momentum tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.dual_momentum import indicators, risk, signals
from strategies.dual_momentum.run_backtest import build_basket
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


def _signal_frame(rows):
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


class TestDualMomentum(unittest.TestCase):
    def test_registered(self):
        self.assertIn("dual_momentum", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_abs_mom_exact_value(self):
        # Close doubles exactly over the 240-bar window:
        # abs_mom = log(2) on the bar 240 after the jump.
        n = 300
        closes = [100.0] * 240 + [200.0] * 60
        df = indicators.add_indicators(_frame(closes))
        self.assertTrue(np.isnan(df["abs_mom"].iloc[239]))
        self.assertAlmostEqual(df["abs_mom"].iloc[240], np.log(2.0), places=12)
        # The jump is still inside the 240-bar window at bar 299.
        self.assertAlmostEqual(df["abs_mom"].iloc[299], np.log(2.0), places=12)
        # 480 bars after the jump the window no longer spans it.
        closes2 = [100.0] * 240 + [200.0] * 300
        df2 = indicators.add_indicators(_frame(closes2))
        self.assertAlmostEqual(df2["abs_mom"].iloc[480], 0.0, places=12)

    def test_abs_mom_hand_computed(self):
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 500)))
        df = indicators.add_indicators(_frame(closes))
        manual = np.log(pd.Series(closes) / pd.Series(closes).shift(240))
        pd.testing.assert_series_equal(
            df["abs_mom"].reset_index(drop=True),
            manual.reset_index(drop=True), check_names=False, atol=1e-12)

    def test_basket_rel_mom_and_rank(self):
        # Three coins, same timestamps: BTC doubles over 240 bars,
        # ETH flat, HYPE halves. Basket return = (log2 + 0 - log2)/3 = 0.
        n = 300
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        frames = {
            "BTC": _frame([100.0] * 240 + [200.0] * 60),
            "ETH": _frame([100.0] * n),
            "HYPE": _frame([100.0] * 240 + [50.0] * 60),
        }
        out = build_basket(frames)
        btc = out["BTC"]
        self.assertAlmostEqual(btc["basket_ret"].iloc[240], 0.0, places=12)
        self.assertAlmostEqual(btc["rel_mom"].iloc[240], np.log(2.0), places=12)
        self.assertEqual(btc["mom_rank"].iloc[240], 1.0)
        self.assertEqual(out["ETH"]["mom_rank"].iloc[240], 2.0)
        self.assertEqual(out["HYPE"]["mom_rank"].iloc[240], 3.0)
        # Geometric-mean basket close at bar 240: (200*100*50)^(1/3) = 100.
        self.assertAlmostEqual(btc["basket_close"].iloc[240], 100.0, places=9)

    def test_long_entry_top_rank_positive_mom(self):
        rows = [
            dict(abs_mom=0.10, mom_rank=2, n_coins=3),
            dict(abs_mom=0.10, mom_rank=1, n_coins=3),
            dict(abs_mom=0.10, mom_rank=1, n_coins=3),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertTrue(df["long_entry"].iloc[1])   # newly top-ranked
        self.assertFalse(df["long_entry"].iloc[2])  # still qualifies, no re-entry
        self.assertFalse(df["short_entry"].any())

    def test_no_long_when_top_but_negative_mom(self):
        rows = [
            dict(abs_mom=-0.10, mom_rank=1, n_coins=3),
            dict(abs_mom=-0.10, mom_rank=1, n_coins=3),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())  # top rank is not bottom

    def test_short_entry_bottom_rank_negative_mom(self):
        rows = [
            dict(abs_mom=-0.10, mom_rank=2, n_coins=3),
            dict(abs_mom=-0.10, mom_rank=3, n_coins=3),
            dict(abs_mom=-0.10, mom_rank=3, n_coins=3),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].any())

    def test_exit_on_rank_flip_and_mom_flip(self):
        # Long while top + positive; rank flip to 2 exits the long.
        rows = [
            dict(abs_mom=0.10, mom_rank=1, n_coins=3),
            dict(abs_mom=0.10, mom_rank=2, n_coins=3),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[1])
        # Absolute momentum turning negative also exits the long.
        rows = [
            dict(abs_mom=0.10, mom_rank=1, n_coins=3),
            dict(abs_mom=-0.05, mom_rank=1, n_coins=3),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_exit"].iloc[1])
        # Short exits when absolute momentum turns positive.
        rows = [
            dict(abs_mom=-0.10, mom_rank=3, n_coins=3),
            dict(abs_mom=0.05, mom_rank=3, n_coins=3),
        ]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_exit"].iloc[1])

    def test_flat_no_entries(self):
        # abs_mom = 0 throughout: neither positive nor negative.
        rows = [dict(abs_mom=0.0, mom_rank=1, n_coins=3)] * 10
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

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
        self.assertEqual(risk.WARMUP, 300)

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
        for col in ("abs_mom", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_frame([100.0] * 10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
