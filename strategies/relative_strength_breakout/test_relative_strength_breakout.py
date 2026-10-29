"""Relative-strength breakout tests. Network-free, synthetic data only.

The benchmark path is tested explicitly: a synthetic BTC frame
is passed to add_indicators, and the ratio column is checked
against the hand-computed coin/BTC quotient. A second test
monkeypatches the cache path to a temp BTC CSV to cover the
default (no-benchmark-arg) load. No test substitutes a
coin-vs-own-SMA proxy.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.relative_strength_breakout import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, vols=None):
    c = np.asarray(closes, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.05
    l = np.minimum(o, c) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    v = np.full(n, 100.0) if vols is None else np.asarray(vols, dtype=float)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _run(coin, btc):
    ind = indicators.add_indicators(coin, benchmark_df=btc)
    return signals.add_signals(ind)


def _random_pair(n=300, seed=7):
    rng = np.random.default_rng(seed)
    btc = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.008, n)))
    coin = 10 * np.exp(np.cumsum(rng.normal(0.0005, 0.012, n)))
    return _frame(coin), _frame(btc)


class TestRelativeStrengthBreakout(unittest.TestCase):
    def test_ratio_math_with_explicit_benchmark(self):
        coin = _frame([10.0, 11.0, 12.0] + [12.0] * 30)
        btc = _frame([100.0, 100.0, 100.0] + [100.0] * 30)
        ind = indicators.add_indicators(coin, benchmark_df=btc)
        self.assertAlmostEqual(ind["ratio"].iloc[0], 0.10)
        self.assertAlmostEqual(ind["ratio"].iloc[1], 0.11)
        self.assertAlmostEqual(ind["ratio"].iloc[2], 0.12)
        self.assertTrue((ind["btc_close"] == 100.0).all())

    def test_default_path_loads_btc_cache_file(self):
        # monkeypatch the module-level cache path to a temp BTC CSV
        coin = _frame([10.0] * 40)
        btc = pd.DataFrame({
            "t": coin["t"].to_numpy(),
            "c": np.full(len(coin), 100.0),
        })
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "BTC_1h.csv")
            btc.to_csv(path, index=False)
            old = indicators.BTC_CACHE
            indicators.BTC_CACHE = path
            try:
                ind = indicators.add_indicators(coin)
            finally:
                indicators.BTC_CACHE = old
        self.assertTrue((ind["btc_close"] == 100.0).all())
        self.assertTrue((ind["ratio"] == 0.10).all())

    def test_missing_benchmark_raises_not_proxy(self):
        coin = _frame([10.0] * 40)
        old = indicators.BTC_CACHE
        indicators.BTC_CACHE = "/nonexistent-dir/BTC_1h.csv"
        try:
            with self.assertRaises(ValueError):
                indicators.add_indicators(coin)
        finally:
            indicators.BTC_CACHE = old

    def test_btc_vs_itself_never_trades(self):
        coin, _ = _random_pair()
        df = signals.add_signals_with_benchmark(coin, coin)
        self.assertTrue((df["ratio"] == 1.0).all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_both_directions_fire(self):
        # coin flat vs BTC, then a sharp relative rise (long
        # breakout), then a sharp relative fall (short breakout)
        n_flat = 30
        coin_c = [10.0] * n_flat + list(np.linspace(10, 16, 20)) + list(np.linspace(16, 8, 30))
        btc_c = [100.0] * (n_flat + 20 + 30)
        df = _run(_frame(coin_c), _frame(btc_c))
        self.assertTrue(df["long_entry"].any(), "relative rise must break out long")
        self.assertTrue(df["short_entry"].any(), "relative fall must break out short")

    def test_signal_columns_boolean_no_nan(self):
        coin, btc = _random_pair()
        df = _run(coin, btc)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_indicator_columns_no_nan_beyond_warmup(self):
        coin, btc = _random_pair()
        ind = indicators.add_indicators(coin, benchmark_df=btc)
        tail = ind.iloc[risk.WARMUP:]
        for col in ("ratio", "ratio_high20", "ratio_low20", "ratio_sma20", "atr"):
            self.assertFalse(tail[col].isna().any(), col)

    def test_no_lookahead_truncation(self):
        coin, btc = _random_pair()
        full = _run(coin, btc)
        trunc = _run(coin[:100], btc[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        self.assertIn("relative_strength_breakout", registry.REGISTRY)
        self.assertEqual(risk.WARMUP, 30)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.risk_frac, 0)
        self.assertLessEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)

    def test_backtest_smoke(self):
        coin, btc = _random_pair()
        df = _run(coin, btc)
        res = run_backtest(df, risk.RISK, "ETH", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
