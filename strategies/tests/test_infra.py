"""Infra tests: indicators, data cleaning, backtest harness. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.backtest import run_backtest
from strategies.data import _clean


def _frame(n=300, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[100.0], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _sig(df):
    df = df.copy()
    df["long_entry"] = False
    df["short_entry"] = False
    df["long_exit"] = False
    df["short_exit"] = False
    return df


class TestData(unittest.TestCase):
    def test_clean_sorts_and_dedups(self):
        df = _frame()
        df = pd.concat([df, df.iloc[[5]]], ignore_index=True).sample(frac=1.0, random_state=1)
        out = _clean(df)
        self.assertTrue(out["t"].is_monotonic_increasing)
        self.assertTrue(out["t"].is_unique)
        self.assertEqual(list(out.columns), ["t", "o", "h", "l", "c", "v"])


class TestIndicators(unittest.TestCase):
    def setUp(self):
        self.df = _frame()

    def test_atr_positive(self):
        self.assertTrue((B.atr(self.df.h, self.df.l, self.df.c, 14).dropna() > 0).all())

    def test_rsi_bounds(self):
        r = B.rsi(self.df.c, 14).dropna()
        self.assertTrue(((r >= 0) & (r <= 100)).all())

    def test_supertrend_direction(self):
        st = B.supertrend(self.df.h, self.df.l, self.df.c, 10, 3.0).dropna()
        self.assertTrue(set(st["supertrend_dir"].unique()) <= {1.0, -1.0})

    def test_bollinger_ordering(self):
        bb = B.bollinger(self.df.c).dropna()
        self.assertTrue(((bb["bb_upper"] >= bb["bb_mid"]) & (bb["bb_mid"] >= bb["bb_lower"])).all())

    def test_keltner_ordering(self):
        kc = B.keltner(self.df.h, self.df.l, self.df.c).dropna()
        self.assertTrue((kc["kc_upper"] > kc["kc_lower"]).all())

    def test_vwap_daily_anchor(self):
        vw = B.anchored_vwap(self.df.h, self.df.l, self.df.c, self.df.v, self.df.t)
        self.assertGreater(vw.notna().sum(), 100)

    def test_donchian_ordering(self):
        d = B.donchian(self.df.h, self.df.l, 20).dropna()
        self.assertTrue((d.iloc[:, 0] >= d.iloc[:, 1]).all())

    def test_adx_nonnegative(self):
        a = B.adx(self.df.h, self.df.l, self.df.c, 14).dropna()
        self.assertTrue((a["adx"] >= 0).all())


class TestHarness(unittest.TestCase):
    def test_long_entry_exit_fees(self):
        df = _sig(_frame(200, drift=0.002))
        df.loc[50, "long_entry"] = True
        df.loc[70, "long_exit"] = True
        risk = B.RiskConfig(stop_atr_mult=10.0, trail_atr_mult=None, target_atr_mult=None,
                            max_hold_bars=None, risk_frac=0.01, max_leverage=3.0)
        res = run_backtest(df, risk, coin="BTC", interval="1h", warmup=30, use_funding=False)
        self.assertEqual(len(res.trades), 1)
        tr = res.trades.iloc[0]
        self.assertEqual(tr["side"], "long")
        self.assertGreater(tr["fees_usd"], 0)
        self.assertEqual(tr["exit_reason"], "signal")
        m = res.metrics()
        self.assertEqual(m["trades"], 1)
        self.assertTrue(0.0 <= m["win_rate"] <= 1.0)

    def test_stop_or_max_hold_fires(self):
        df = _sig(_frame(200, drift=-0.004))
        df.loc[50, "long_entry"] = True
        risk = B.RiskConfig(stop_atr_mult=1.0, trail_atr_mult=None, target_atr_mult=None,
                            max_hold_bars=5, risk_frac=0.01)
        res = run_backtest(df, risk, coin="BTC", interval="1h", warmup=30, use_funding=False)
        self.assertEqual(len(res.trades), 1)
        self.assertIn(res.trades.iloc[0]["exit_reason"], ("stop", "max_hold"))
        self.assertLessEqual(res.metrics()["max_dd_pct"], 0.0)

    def test_short_side_wins_downtrend(self):
        df = _sig(_frame(200, drift=-0.002))
        df.loc[50, "short_entry"] = True
        df.loc[80, "short_exit"] = True
        risk = B.RiskConfig(stop_atr_mult=10.0, trail_atr_mult=None, target_atr_mult=None,
                            max_hold_bars=None, risk_frac=0.01)
        res = run_backtest(df, risk, coin="BTC", interval="1h", warmup=30, use_funding=False)
        self.assertEqual(len(res.trades), 1)
        self.assertEqual(res.trades.iloc[0]["side"], "short")
        self.assertGreater(res.trades.iloc[0]["net_pnl"], 0)

    def test_no_signals_no_trades(self):
        df = _sig(_frame(200))
        risk = B.RiskConfig()
        res = run_backtest(df, risk, coin="BTC", interval="1h", warmup=30, use_funding=False)
        self.assertEqual(len(res.trades), 0)
        self.assertEqual(res.metrics()["trades"], 0)


if __name__ == "__main__":
    unittest.main()
