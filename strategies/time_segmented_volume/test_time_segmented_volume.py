"""Time segmented volume tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies import registry
from strategies.backtest import run_backtest
from strategies.time_segmented_volume import indicators, risk, signals


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


def _signal_frame(tsv, closes=None):
    n = len(tsv)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({
        "c": c,
        "tsv": np.array(tsv, dtype=float),
    })


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


class TestTimeSegmentedVolume(unittest.TestCase):
    def test_registered(self):
        self.assertIn("time_segmented_volume", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: per-bar flow is 0, so TSV is 0 once warmed up.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[indicators.PERIOD:]
        self.assertTrue(np.allclose(tail["tsv"], 0.0))
        self.assertTrue(np.allclose(tail["tsv_flow"], 0.0))
        self.assertTrue(df.iloc[: indicators.PERIOD - 1]["tsv"].isna().all())

    def test_indicator_values_steady_rise(self):
        # Close +1 every bar, volume 100: flow = 100/bar, so TSV = 1800.
        closes = 100 + np.arange(200, dtype=float)
        df = indicators.add_indicators(_frame(closes, vols=[100.0] * 200))
        self.assertAlmostEqual(df["tsv"].iloc[30], 1800.0, places=9)
        self.assertAlmostEqual(df["tsv"].iloc[199], 1800.0, places=9)
        self.assertAlmostEqual(df["tsv_flow"].iloc[30], 100.0, places=9)

    def test_indicator_values_steady_fall(self):
        # Close -1 every bar, volume 100: TSV = -1800.
        closes = 300 - np.arange(200, dtype=float)
        df = indicators.add_indicators(_frame(closes, vols=[100.0] * 200))
        self.assertAlmostEqual(df["tsv"].iloc[30], -1800.0, places=9)

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        valid = df["tsv"].dropna()
        self.assertGreater(len(valid), 50)
        self.assertTrue(np.isfinite(valid).all())
        # TSV must equal the rolling 18-bar sum of (close - close[1]) * v.
        flow = (df["c"] - df["c"].shift(1)).fillna(0.0) * df["v"]
        expect = flow.rolling(18, min_periods=18).sum()
        for i in (100, 250, 399):
            self.assertAlmostEqual(df["tsv"].iloc[i], expect.iloc[i], places=9)

    def test_indicator_values_volume_weighting(self):
        # Same +1/bar rise, but double the volume on the last 18 bars:
        # TSV doubles to 3600. Volume magnitude matters, not just sign.
        closes = 100 + np.arange(200, dtype=float)
        vols = [100.0] * 182 + [200.0] * 18
        df = indicators.add_indicators(_frame(closes, vols=vols))
        self.assertAlmostEqual(df["tsv"].iloc[199], 3600.0, places=9)

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.WARMUP, 50)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_zero_cross_up(self):
        df = signals.add_signals(_signal_frame([-5.0, 5.0, 6.0, 6.0]))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[1])
        # A zero cross up is also the short exit.
        self.assertTrue(df["short_exit"].iloc[1])

    def test_short_entry_on_zero_cross_down(self):
        df = signals.add_signals(_signal_frame([5.0, -5.0, -6.0, -6.0]))
        self.assertTrue(df["short_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertTrue(df["long_exit"].iloc[1])

    def test_no_entry_without_cross(self):
        # TSV stays above zero: no new entry after the first bar.
        df = signals.add_signals(_signal_frame([5.0, 6.0, 7.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # TSV exactly zero is not a cross in either direction.
        df = signals.add_signals(_signal_frame([0.0, 0.0, 0.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exits_are_opposite_crosses(self):
        df = signals.add_signals(_signal_frame([5.0, 6.0, -5.0]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame([-5.0, -6.0, 5.0]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_determinism(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 100))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [500.0] * 50))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue((df1[col].iloc[:100] == df2[col].iloc[:100]).all())

    def test_edge_short_frame(self):
        # Fewer bars than the 18-bar window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["tsv"].isna().all())


if __name__ == "__main__":
    unittest.main()
