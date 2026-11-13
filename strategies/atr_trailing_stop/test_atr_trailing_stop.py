"""ATR trailing-stop tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.atr_trailing_stop import indicators, risk, signals
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


class TestAtrTrailingStop(unittest.TestCase):
    def test_registered(self):
        self.assertIn("atr_trailing_stop", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_stop_flat_exact_value(self):
        # Flat bars h=101, l=99, c=100: every true range is 2, so
        # Wilder ATR(14) converges to exactly 2. Highest high is 101,
        # so the long trailing stop is 101 - 3*2 = 95.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["atr"], 2.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["chand_stop"], 95.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["chand_anchor"], 101.0, atol=1e-12))
        self.assertTrue((tail["chand_dir"] == 1.0).all())

    def test_stop_ratchets_up_only(self):
        # Steady rise: the anchor (highest high) climbs and the stop
        # climbs with it, never stepping down.
        n = 200
        closes = list(np.linspace(100.0, 150.0, n))
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[risk.WARMUP:]
        stops = tail["chand_stop"].to_numpy()
        self.assertTrue(np.all(np.diff(stops) >= -1e-12))
        self.assertTrue((tail["chand_dir"] == 1.0).all())
        # Stop sits exactly 3 ATR below the running highest high.
        self.assertTrue(np.allclose(
            tail["chand_stop"],
            tail["chand_anchor"] - 3.0 * tail["atr"], atol=1e-9))

    def test_flip_short_on_close_below_stop(self):
        # 60 flat bars (stop pinned at 95), then the close drops to 90,
        # below the stop: the regime flips short on that bar.
        n = 200
        closes = [100.0] * 60 + [90.0] * 140
        df = _run(_frame(closes))
        self.assertTrue(df["chand_dir"].iloc[59] == 1.0)
        self.assertTrue(df["short_entry"].iloc[60])
        self.assertTrue(df["chand_dir"].iloc[60] == -1.0)
        self.assertTrue(df["long_exit"].iloc[60])
        # New short stop hangs 3 ATR above the flip bar's low.
        self.assertGreater(df["chand_stop"].iloc[60],
                           df["c"].iloc[60])

    def test_flip_long_on_close_above_stop(self):
        # Flat at 100 (long regime, stop 95), drop to 80 (flips short),
        # then jump to 110: the close clears the short stop and the
        # regime flips long on that bar.
        n = 300
        closes = [100.0] * 60 + [80.0] * 60 + [110.0] * 180
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].iloc[60])
        self.assertTrue(df["chand_dir"].iloc[60] == -1.0)
        self.assertTrue(df["long_entry"].iloc[120])
        self.assertTrue(df["short_exit"].iloc[120])
        self.assertTrue(df["chand_dir"].iloc[120] == 1.0)
        # New long stop hangs 3 ATR below the flip bar's high.
        self.assertLess(df["chand_stop"].iloc[120],
                        df["c"].iloc[120])

    def test_regime_flip_sequence(self):
        # Fall hard, then rise hard: at least one flip each way, and
        # every flip bar carries both the entry and the opposite exit.
        n = 300
        closes = [100.0] * 60 + [80.0] * 60 + [110.0] * 60 + [70.0] * 120
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].any())
        self.assertTrue(df["long_entry"].any())
        flips = df[df["short_entry"] | df["long_entry"]]
        for _, row in flips.iterrows():
            if row["short_entry"]:
                self.assertTrue(row["long_exit"])
            if row["long_entry"]:
                self.assertTrue(row["short_exit"])

    def test_signal_logic_crafted_rows(self):
        # chand_dir -1 -> +1: long entry + short exit.
        rows = [dict(chand_dir=-1.0), dict(chand_dir=1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertTrue(df["short_exit"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # chand_dir +1 -> -1: short entry + long exit.
        rows = [dict(chand_dir=1.0), dict(chand_dir=-1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_exit"].iloc[1])
        # No flip: no signals.
        rows = [dict(chand_dir=1.0), dict(chand_dir=1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        # NaN direction (warmup): no entry, no exit.
        rows = [dict(chand_dir=np.nan), dict(chand_dir=1.0)]
        df = signals.add_signals(_signal_frame(rows))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

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

    def test_no_lookahead_flat(self):
        # Flat close: stop pinned at 95, close 100 never crosses it.
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
        for col in ("chand_stop", "chand_dir", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
