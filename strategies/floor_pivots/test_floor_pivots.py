"""Floor-trader pivots tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.floor_pivots import indicators, risk, signals
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


def _flat_frame(n=130, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


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


class TestFloorPivots(unittest.TestCase):
    def test_registered(self):
        self.assertIn("floor_pivots", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Trailing 24 bars: H=101, L=99, C=100 -> PP=100, R1=101,
        # S1=99, R2=102, S2=98, vol_avg=100.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["fp_pp"], 100.0))
        self.assertTrue(np.allclose(tail["fp_r1"], 101.0))
        self.assertTrue(np.allclose(tail["fp_s1"], 99.0))
        self.assertTrue(np.allclose(tail["fp_r2"], 102.0))
        self.assertTrue(np.allclose(tail["fp_s2"], 98.0))
        self.assertTrue(np.allclose(tail["fp_vol_avg"], 100.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            h24 = df["h"].iloc[i - 24:i].max()
            l24 = df["l"].iloc[i - 24:i].min()
            c_prev = df["c"].iloc[i - 1]
            pp = (h24 + l24 + c_prev) / 3.0
            self.assertAlmostEqual(df["fp_pp"].iloc[i], pp, places=9)
            self.assertAlmostEqual(df["fp_r1"].iloc[i], 2 * pp - l24, places=9)
            self.assertAlmostEqual(df["fp_r2"].iloc[i], pp + (h24 - l24), places=9)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_above_r1_with_volume(self):
        base = _flat_frame()
        bar = _frame([101.5], highs=[102.0], lows=[100.5],
                     vols=[200.0], opens=[100.0])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_short_entry_below_s1_with_volume(self):
        base = _flat_frame()
        bar = _frame([98.5], highs=[99.5], lows=[98.0],
                     vols=[200.0], opens=[100.0])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_without_volume(self):
        # Close above R1 but volume below its 20-bar average: no entry.
        base = _flat_frame()
        bar = _frame([101.5], highs=[102.0], lows=[100.5],
                     vols=[50.0], opens=[100.0])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_wrong_side_of_pp(self):
        # Close above R1 requires close above PP; a close between PP
        # and R1 is not an entry.
        base = _flat_frame()
        bar = _frame([100.5], highs=[101.0], lows=[100.0],
                     vols=[200.0], opens=[100.0])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_long_exit_at_r2_and_below_pp(self):
        base = _flat_frame()
        bar_r2 = _frame([102.5], highs=[103.0], lows=[102.0],
                        vols=[100.0], opens=[100.0])
        df = _run(pd.concat([base, bar_r2], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])
        bar_pp = _frame([99.5], highs=[100.0], lows=[99.0],
                        vols=[100.0], opens=[100.0])
        df = _run(pd.concat([base, bar_pp], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_short_exit_at_s2_and_above_pp(self):
        base = _flat_frame()
        bar_s2 = _frame([97.5], highs=[98.0], lows=[97.0],
                        vols=[100.0], opens=[100.0])
        df = _run(pd.concat([base, bar_s2], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])
        bar_pp = _frame([100.5], highs=[101.0], lows=[100.0],
                        vols=[100.0], opens=[100.0])
        df = _run(pd.concat([base, bar_pp], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the session window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): pivots collapse to the price.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["fp_pp"], 100.0))
        self.assertTrue(np.allclose(tail["fp_r2"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
