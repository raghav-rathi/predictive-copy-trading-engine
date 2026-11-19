"""New York open momentum tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.new_york_open import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest

BASE_MS = int(pd.Timestamp("2026-01-05 13:00", tz="UTC").timestamp() * 1000)


def _bars(specs):
    """specs: list of (o, h, l, c) in hourly order from BASE_MS (13:00)."""
    n = len(specs)
    arr = np.array(specs, dtype=float)
    return pd.DataFrame({
        "t": (BASE_MS + np.arange(n) * 3_600_000).astype("int64"),
        "o": arr[:, 0], "h": arr[:, 1], "l": arr[:, 2], "c": arr[:, 3],
        "v": np.full(n, 100.0),
    })


def _bull_frame():
    """13:00 bar range 110/100; 14:00 close 111 breaks high -> long
    trigger at index 1; 15:00 close 112 must not re-fire; 21:00 bar
    (index 8) is the time exit."""
    return _bars([
        (105, 110, 100, 105),   # 13:00 first hour
        (111, 112, 108, 111),   # 14:00 break -> long trigger
        (112, 113, 110, 112),   # 15:00 no re-fire
        (112, 113, 110, 112),   # 16:00
        (112, 113, 110, 112),   # 17:00
        (112, 113, 110, 112),   # 18:00
        (112, 113, 110, 112),   # 19:00
        (112, 113, 110, 112),   # 20:00
        (112, 113, 110, 112),   # 21:00 time exit
        (112, 113, 110, 112),   # 22:00
    ])


def _bear_frame():
    """Mirror of _bull_frame reflected about 200: short trigger at 14:00."""
    df = _bull_frame()
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


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


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": close, "h": hi, "l": lo,
                         "c": close, "v": np.full(n, vol)})


class TestNewYorkOpen(unittest.TestCase):
    def test_registered(self):
        self.assertIn("new_york_open", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_first_hour_range(self):
        df = indicators.add_indicators(_bull_frame())
        self.assertAlmostEqual(df["ny_high"].iloc[0], 110.0)
        self.assertAlmostEqual(df["ny_low"].iloc[0], 100.0)
        self.assertAlmostEqual(df["ny_high"].iloc[5], 110.0)
        self.assertFalse(df["ny_time_exit"].iloc[:8].any())
        self.assertTrue(df["ny_time_exit"].iloc[8])

    def test_bull_long_trigger_first_break_only(self):
        df = _run(_bull_frame())
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].any())

    def test_bear_short_trigger_on_mirrored_frame(self):
        df = _run(_bear_frame())
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_without_break(self):
        # Closes stay inside the 100-110 range all afternoon.
        df = _run(_bars([
            (105, 110, 100, 105),
            (106, 108, 104, 106),
            (107, 109, 105, 107),
            (106, 108, 104, 106),
            (106, 108, 104, 106),
        ]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_outside_window(self):
        # The break only comes on the 17:00 bar, after the window ends.
        df = _run(_bars([
            (105, 110, 100, 105),   # 13:00
            (106, 108, 104, 106),   # 14:00 inside range
            (107, 109, 105, 107),   # 15:00 inside range
            (106, 108, 104, 106),   # 16:00 inside range
            (111, 112, 108, 111),   # 17:00 break, but window closed
            (112, 113, 110, 112),   # 18:00
        ]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_time_exit_at_2100(self):
        df = _run(_bull_frame())
        self.assertTrue(df["long_exit"].iloc[8])
        self.assertFalse(df["long_exit"].iloc[:8].any())
        self.assertTrue(df["short_exit"].iloc[8])

    def test_exit_on_opposite_break(self):
        rows = pd.DataFrame([dict(
            c=105.0, long_trigger=False, short_trigger=True,
            ny_time_exit=False)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 48)
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
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_bars([(c, c + 0.5, c - 0.5, c) for c in closes]))
        df2 = _run(_bars([(c, c + 0.5, c - 0.5, c) for c in closes]
                         + [(c + 300.0, c + 300.5, c + 299.5, c + 300.0)
                            for c in closes[-50:]]))
        for col in ("ny_high", "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
