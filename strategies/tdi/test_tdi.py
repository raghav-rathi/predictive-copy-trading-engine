"""TDI tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.tdi import indicators, risk, signals

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, spread=0.2):
    c = np.asarray(c, dtype=float)
    n = len(c)
    prev = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": prev,
            "h": np.maximum(c, prev) + spread,
            "l": np.minimum(c, prev) - spread,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestTdi(unittest.TestCase):
    def test_lines_match_manual_sma(self):
        # independent check: red/yellow are exact SMAs of the green RSI line
        rng = np.random.default_rng(4)
        df = indicators.add_indicators(_frame(100 + np.cumsum(rng.normal(0, 0.6, 300))))
        g = df["tdi_green"].to_numpy()
        sma = lambda x, n: pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()
        np.testing.assert_allclose(df["tdi_red"].to_numpy()[35:], sma(g, 2)[35:], rtol=1e-9)
        np.testing.assert_allclose(df["tdi_yellow"].to_numpy()[40:], sma(g, 34)[40:], rtol=1e-9)

    def test_vb_width_is_golden_ratio(self):
        rng = np.random.default_rng(5)
        df = indicators.add_indicators(_frame(100 + np.cumsum(rng.normal(0, 0.6, 300))))
        g = pd.Series(df["tdi_green"].to_numpy())
        width = df["tdi_vb_up"] - df["tdi_vb_dn"]
        exp = 2 * 1.6185 * g.rolling(34, min_periods=34).std()
        np.testing.assert_allclose(width.to_numpy()[40:], exp.to_numpy()[40:], rtol=1e-9)

    def test_long_needs_yellow_above_50(self):
        # sustained rally: yellow > 50 eventually, crosses of green/red occur
        rng = np.random.default_rng(21)
        c = np.concatenate([np.full(120, 100.0), 100.0 + 0.8 * np.arange(200)]) + rng.normal(0, 0.7, 320)
        df = _run(_frame(c))
        self.assertTrue(bool(df["long_entry"].any()))
        # every long entry has yellow > 50
        self.assertTrue(bool((df.loc[df["long_entry"], "tdi_yellow"] > 50).all()))

    def test_bear_market_shorts(self):
        rng = np.random.default_rng(22)
        c = np.concatenate([np.full(120, 100.0), 100.0 - 0.8 * np.arange(200)]) + rng.normal(0, 0.7, 320)
        df = _run(_frame(c))
        self.assertTrue(bool(df["short_entry"].any()))

    def test_signal_columns_boolean_and_causal(self):
        rng = np.random.default_rng(6)
        c = 100 + np.cumsum(rng.normal(0, 0.6, 400))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(df[col].dtype, bool)
        # truncation: entry decisions at bar 199 identical with/without later data
        trunc = _run(_frame(c[:200]))
        for col in ("long_entry", "short_entry"):
            self.assertEqual(bool(df[col].iloc[199]), bool(trunc[col].iloc[199]))


if __name__ == "__main__":
    unittest.main()
