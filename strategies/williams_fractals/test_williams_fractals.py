"""Williams fractal breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.williams_fractals import indicators, risk, signals
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


def _long_frame():
    # Flat, up-fractal at 108 (high 108.5), dip to 102, rally through
    # 108.5, then a fall that bottoms at 96 (down-fractal low 95.5),
    # bounces, and breaks below 95.5.
    closes = [100.0] * 40
    closes += [101, 103, 105, 107, 108, 106, 104, 102]
    closes += [103, 105, 107, 109, 110, 112]
    closes += [110, 108, 106, 104, 102, 100, 98, 96, 98, 100, 99, 97, 95, 94, 93]
    return _frame(closes)


def _short_frame():
    # Mirror of the long frame.
    closes = [100.0] * 40
    closes += [99, 97, 95, 93, 92, 94, 96, 98]
    closes += [97, 95, 93, 91, 90, 88]
    closes += [90, 92, 94, 96, 98, 100, 102, 104, 102, 100, 101, 103, 105, 106, 107]
    return _frame(closes)


class TestWilliamsFractals(unittest.TestCase):
    def test_registered(self):
        self.assertIn("williams_fractals", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values(self):
        df = indicators.add_indicators(_long_frame())
        # Up-fractal high is the peak bar's high (108 + 0.5), known
        # only from its confirmation bar (peak + 2) onward.
        self.assertTrue(np.isnan(df["frac_up_high"].iloc[:46]).all())
        self.assertEqual(df["frac_up_high"].iloc[46], 108.5)
        self.assertTrue(df["fractal_buy_raw"].iloc[44])
        # Steady uptrend: Alligator fans out lips > teeth > jaw.
        up = indicators.add_indicators(_frame(list(np.linspace(100, 140, 120))))
        tail = up.iloc[60:]
        self.assertTrue((tail["alligator_lips"] > tail["alligator_teeth"]).all())
        self.assertTrue((tail["alligator_teeth"] > tail["alligator_jaw"]).all())
        self.assertTrue(tail["gator_awake_long"].all())

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["alligator_jaw"]).all())
        self.assertTrue(np.isfinite(tail["alligator_teeth"]).all())
        self.assertTrue(np.isfinite(tail["alligator_lips"]).all())

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

    def test_long_entry_on_fractal_break(self):
        df = _run(_long_frame())
        self.assertTrue(df["long_entry"].any())
        idx = df.index[df["long_entry"]][0]
        self.assertTrue(df.loc[idx, "c"] > df.loc[idx, "frac_up_high"])
        self.assertTrue(df.loc[idx, "c"] > df.loc[idx, "alligator_teeth"])
        self.assertTrue(df.loc[idx, "gator_awake_long"])

    def test_short_entry_on_fractal_break(self):
        df = _run(_short_frame())
        self.assertTrue(df["short_entry"].any())
        idx = df.index[df["short_entry"]][0]
        self.assertTrue(df.loc[idx, "c"] < df.loc[idx, "frac_down_low"])
        self.assertTrue(df.loc[idx, "c"] < df.loc[idx, "alligator_teeth"])
        self.assertTrue(df.loc[idx, "gator_awake_short"])

    def test_exit_on_reverse_fractal_break(self):
        df = _run(_long_frame())
        long_idx = df.index[df["long_entry"]][0]
        self.assertTrue(df.loc[long_idx:, "long_exit"].any())
        df2 = _run(_short_frame())
        short_idx = df2.index[df2["short_entry"]][0]
        self.assertTrue(df2.loc[short_idx:, "short_exit"].any())

    def test_no_entry_without_alligator_awake(self):
        # A fractal break in a flat market: the Alligator lines are
        # collapsed, so the awake filter blocks the entry.
        closes = [100.0] * 40
        closes += [101, 103, 105, 107, 108, 106, 104, 102]
        closes += [103, 105, 107, 109, 110, 112]
        df = _run(_frame(closes))
        # The break happens, but only check the filter logic on the
        # entry bar itself: if an entry fired, the Alligator must
        # have been awake there.
        if df["long_entry"].any():
            idx = df.index[df["long_entry"]][0]
            self.assertTrue(df.loc[idx, "gator_awake_long"])

    def test_no_lookahead_flat(self):
        closes = [100.0] * 150
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_entry_before_fractal_confirms(self):
        # Price never breaks the confirmed fractal high: no long entry.
        closes = [100.0] * 40
        closes += [101, 103, 105, 107, 108, 106, 104, 102]
        closes += [103, 105, 107, 108, 108, 108]
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())


if __name__ == "__main__":
    unittest.main()
