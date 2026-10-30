"""Structure-break BOS tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.structure_break_bos import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None):
    n = len(closes)
    c = np.array(closes, dtype=float)
    h = np.array(highs, dtype=float) if highs is not None else c + 0.5
    l = np.array(lows, dtype=float) if lows is not None else c - 0.5
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": c, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=300, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": rng.uniform(50, 150, n)})


# Flat 100, rise to a 110 peak, pull back, break above 110 (first
# break, trend-setting only), pull back, break above the new
# swing high (BOS continuation -> long entry at bar 14).
LONG_CLOSES = [100] * 6 + [102, 104, 106, 108, 110, 108, 106, 108, 111]
SHORT_CLOSES = [200 - x for x in LONG_CLOSES]


class TestStructureBreakBos(unittest.TestCase):
    def test_indicator_columns_no_nan_beyond_warmup(self):
        df = _run(_random_walk_frame())
        for col in ("swing_high", "swing_low", "atr"):
            self.assertIn(col, df.columns)
        self.assertFalse(df["atr"].iloc[risk.WARMUP:].isna().any())
        self.assertFalse(df["bos_dir"].isna().any())
        self.assertFalse(df["break_up"].isna().any())

    def test_signal_columns_boolean_no_nan(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)
            self.assertFalse(df[col].isna().any(), col)

    def test_long_bos_continuation(self):
        df = _run(_frame(LONG_CLOSES))
        self.assertEqual(df["bos_dir"].iloc[14], 1)
        self.assertTrue(df["long_entry"].iloc[14])
        self.assertFalse(df["short_entry"].any())

    def test_first_break_alone_does_not_enter(self):
        # The first upward break (bar 6, above the flat 100.5
        # swing high) only sets the trend; no entry fires there.
        df = _run(_frame(LONG_CLOSES[:7]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_short_bos_continuation(self):
        df = _run(_frame(SHORT_CLOSES))
        self.assertEqual(df["bos_dir"].iloc[14], -1)
        self.assertTrue(df["short_entry"].iloc[14])
        self.assertFalse(df["long_entry"].any())

    def test_opposite_break_exits_long(self):
        # Long entry at bar 14, then a drop below the most
        # recent confirmed swing low (105.5) exits the long.
        df = _run(_frame(LONG_CLOSES + [108, 104, 100]))
        self.assertTrue(df["long_entry"].any())
        self.assertTrue(df["long_exit"].any())
        self.assertGreater(df["long_exit"].idxmax(), df["long_entry"].idxmax())

    def test_wick_only_is_not_a_break(self):
        # Close never exceeds the swing high even though a high
        # wick does: highs spike to 112 while closes stay <= 100
        # after a 110 peak is confirmed... simpler: flat closes
        # with one high wick above the pivot level, close inside.
        closes = [100] * 12
        highs = [100.5] * 12
        highs[5] = 115.0  # wick above, but its close is 100
        df = _run(_frame(closes, highs=highs))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_truncation(self):
        full = _run(_random_walk_frame())
        trunc = _run(_random_walk_frame()[:100])
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:100].reset_index(drop=True),
                trunc[col].reset_index(drop=True),
                check_names=False,
            )

    def test_registration(self):
        import strategies.structure_break_bos  # noqa: F401  (registers SPEC)
        self.assertIn("structure_break_bos", registry.REGISTRY)
        self.assertEqual(registry.REGISTRY["structure_break_bos"].slug,
                         "structure_break_bos")

    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 20)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, "BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertTrue(np.isfinite(m["net_pnl_usd"]))


if __name__ == "__main__":
    unittest.main()
