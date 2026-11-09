"""DeMark Range Expansion Index tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.td_rei import indicators, risk, signals
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


def _signal_frame(rei, closes=None):
    n = len(rei)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({"c": c, "rei": np.array(rei, dtype=float)})


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


def _trend_frame(n=200, drift=0.002, start=100.0, half_range=5.0):
    # Steady drift with a wide bar range so DeMark's overlap gate passes
    # (a smooth trend with a razor-thin range fails the gate by design).
    c = start * ((1 + drift) ** np.arange(n))
    return _frame(c, highs=c + half_range, lows=c - half_range)


class TestTdRei(unittest.TestCase):
    def test_registered(self):
        self.assertIn("td_rei", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # No high/low movement at all: denominator sums are 0 -> REI NaN.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertIn("rei", df.columns)
        self.assertTrue(tail["rei"].isna().all())

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        valid = df["rei"].dropna()
        self.assertGreater(len(valid), 50)
        # REI is bounded to [-100, +100] by construction.
        self.assertTrue(((valid >= -100.0) & (valid <= 100.0)).all())

    def test_indicator_values_uptrend(self):
        # Every bar in the window moves up with the gate open: REI = +100.
        df = indicators.add_indicators(_trend_frame(drift=0.002))
        tail = df.iloc[150:]
        self.assertTrue(np.isfinite(tail["rei"]).all())
        self.assertTrue(np.allclose(tail["rei"], 100.0))

    def test_indicator_values_downtrend(self):
        # Mirror image: every bar moves down, REI = -100.
        df = indicators.add_indicators(_trend_frame(drift=-0.002))
        tail = df.iloc[150:]
        self.assertTrue(np.isfinite(tail["rei"]).all())
        self.assertTrue(np.allclose(tail["rei"], -100.0))

    def test_rei_matches_formula(self):
        # Hand-check one bar: with the gate open, REI is 100 x the ratio
        # of the 5-bar signed momentum sum to the 5-bar absolute sum.
        df = indicators.add_indicators(_random_walk_frame())
        i = 200
        h, l, c = df["h"], df["l"], df["c"]
        hm = h - h.shift(2)
        lm = l - l.shift(2)
        gate_a = (((h >= l.shift(5)) | (h >= l.shift(6)))
                  & ((l <= h.shift(5)) | (l <= h.shift(6))))
        gate_b = (((h.shift(2) >= c.shift(7)) | (h.shift(2) >= c.shift(8)))
                  & ((l.shift(2) <= c.shift(7)) | (l.shift(2) <= c.shift(8))))
        gate = (gate_a | gate_b).fillna(False)
        num = (hm + lm).where(gate, 0.0)
        den = hm.abs() + lm.abs()
        expect = 100.0 * num.iloc[i - 4:i + 1].sum() / den.iloc[i - 4:i + 1].sum()
        self.assertAlmostEqual(df["rei"].iloc[i], expect, places=9)

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

    def test_long_entry_on_cross_above_minus_60(self):
        # REI crosses above -60 at index 2.
        df = signals.add_signals(_signal_frame([-70, -65, -55, -50, -45]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])

    def test_short_entry_on_cross_below_plus_60(self):
        # REI crosses below +60 at index 2.
        df = signals.add_signals(_signal_frame([70, 65, 55, 50, 45]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])

    def test_no_entry_without_cross(self):
        # REI sits above -60 / below +60 the whole time: no cross, no entry.
        df = signals.add_signals(_signal_frame([-50, -40, -30, -20, -10]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_exits_on_opposite_extreme_cross(self):
        # REI crossing below +60 exits a long; crossing above -60 exits a short.
        df = signals.add_signals(_signal_frame([70, 65, 55]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        df = signals.add_signals(_signal_frame([-70, -65, -55]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        # REI on bar i must not change when later bars are appended.
        full = indicators.add_indicators(_random_walk_frame())
        trunc = indicators.add_indicators(_random_walk_frame().iloc[:200])
        a = full["rei"].iloc[:200].to_numpy()
        b = trunc["rei"].to_numpy()
        self.assertTrue(np.allclose(a, b, equal_nan=True))

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the REI warmup: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): REI is NaN, no entries.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        self.assertTrue(df.iloc[risk.WARMUP:]["rei"].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
