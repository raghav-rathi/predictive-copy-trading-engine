"""Order-block retest tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.order_block_retest import indicators, risk, signals


def _frame_from_parts(o, h, l, c, v=None):
    n = len(c)
    if v is None:
        v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _bullish_displacement_frame(n=120):
    """30 bearish base bars, a 3-bar +4 displacement leg, then flat."""
    o = np.full(n, 100.2)
    c = np.full(n, 100.0)
    h = np.full(n, 100.3)
    l = np.full(n, 99.9)
    # leg bars 30..32: closes 101 / 102.5 / 104 (move +4 over 3 bars)
    o[30], c[30], h[30], l[30] = 100.0, 101.0, 101.2, 99.9
    o[31], c[31], h[31], l[31] = 101.0, 102.5, 102.7, 100.9
    o[32], c[32], h[32], l[32] = 102.5, 104.0, 104.2, 102.4
    # flat tail (doji bars: c == o, no displacement, no new block)
    o[33:], c[33:], h[33:], l[33:] = 104.0, 104.0, 104.1, 103.9
    return _frame_from_parts(o, h, l, c)


def _bearish_displacement_frame(n=120):
    """30 bullish base bars, a 3-bar -4 displacement leg, then flat."""
    o = np.full(n, 99.8)
    c = np.full(n, 100.0)
    h = np.full(n, 100.1)
    l = np.full(n, 99.7)
    o[30], c[30], h[30], l[30] = 100.0, 99.0, 100.1, 98.8
    o[31], c[31], h[31], l[31] = 99.0, 97.5, 99.1, 97.3
    o[32], c[32], h[32], l[32] = 97.5, 96.0, 97.6, 95.8
    o[33:], c[33:], h[33:], l[33:] = 96.0, 96.0, 96.1, 95.9
    return _frame_from_parts(o, h, l, c)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("disp_dir", "ob_dir", "ob_low", "ob_high",
                    "ob_age", "ob_id", "atr"):
            self.assertIn(col, ind.columns)

    def test_bullish_displacement_and_block(self):
        ind = indicators.add_indicators(_bullish_displacement_frame())
        self.assertEqual(int(ind["disp_dir"].iloc[32]), 1)
        # Block = last bearish candle before the leg = bar 29 range.
        self.assertEqual(int(ind["ob_dir"].iloc[32]), 1)
        self.assertAlmostEqual(float(ind["ob_low"].iloc[32]), 99.9, places=9)
        self.assertAlmostEqual(float(ind["ob_high"].iloc[32]), 100.3, places=9)
        self.assertEqual(int(ind["ob_age"].iloc[32]), 0)

    def test_bearish_displacement_and_block(self):
        ind = indicators.add_indicators(_bearish_displacement_frame())
        self.assertEqual(int(ind["disp_dir"].iloc[32]), -1)
        self.assertEqual(int(ind["ob_dir"].iloc[32]), -1)
        self.assertAlmostEqual(float(ind["ob_low"].iloc[32]), 99.7, places=9)
        self.assertAlmostEqual(float(ind["ob_high"].iloc[32]), 100.1, places=9)

    def test_no_block_without_opposite_color_candle(self):
        # All-bullish base bars, then a bullish leg: displacement fires
        # but there is no bearish candle to form a block from.
        o = np.full(120, 99.8)
        c = np.full(120, 100.0)
        h = np.full(120, 100.1)
        l = np.full(120, 99.7)
        o[30], c[30], h[30], l[30] = 100.0, 101.0, 101.2, 99.9
        o[31], c[31], h[31], l[31] = 101.0, 102.5, 102.7, 100.9
        o[32], c[32], h[32], l[32] = 102.5, 104.0, 104.2, 102.4
        o[33:], c[33:], h[33:], l[33:] = 104.0, 104.0, 104.1, 103.9
        ind = indicators.add_indicators(_frame_from_parts(o, h, l, c))
        self.assertEqual(int(ind["disp_dir"].iloc[32]), 1)
        self.assertEqual(int(ind["ob_dir"].iloc[32]), 0)

    def test_block_expires_after_48_bars(self):
        # The 3-bar displacement window keeps firing through bar 34
        # (c[33]-c[30] and c[34]-c[31] still clear the threshold), so
        # the last displacement bar — not bar 32 — anchors expiry.
        ind = indicators.add_indicators(_bullish_displacement_frame())
        last_disp = int(np.where(ind["disp_dir"] != 0)[0].max())
        self.assertEqual(int(ind["ob_dir"].iloc[last_disp + 48]), 1)
        self.assertEqual(int(ind["ob_dir"].iloc[last_disp + 49]), 0)

    def test_flat_data_no_displacement(self):
        ind = indicators.add_indicators(_frame_from_parts(
            np.full(200, 100.0), np.full(200, 100.1),
            np.full(200, 99.9), np.full(200, 100.0)))
        self.assertFalse((ind["disp_dir"] != 0).any())
        self.assertFalse((ind["ob_dir"] != 0).any())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["ob_dir"].iloc[:200].reset_index(drop=True),
            ind_short["ob_dir"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, c, disp, ob_dir, low, high, age, bid):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "disp_dir": disp, "ob_dir": ob_dir, "ob_low": low,
            "ob_high": high, "ob_age": age, "ob_id": bid,
        })

    def _bull_block(self, closes, disp_extra=None):
        n = len(closes)
        disp = np.zeros(n, dtype=int)
        if disp_extra:
            for i, d in disp_extra.items():
                disp[i] = d
        return self._signal_frame(
            np.asarray(closes, dtype=float), disp,
            np.ones(n, dtype=int),
            np.full(n, 99.9), np.full(n, 100.3),
            np.arange(n), np.zeros(n, dtype=int))

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_retest_and_only_once(self):
        # Bar 0: close above block (left it). Bar 1: close inside ->
        # long entry. Bar 2: inside again -> no second entry.
        sig = signals.add_signals(self._bull_block([101.0, 100.1, 100.2]))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_no_entry_if_block_never_left(self):
        # Closes start inside the block: no displacement-away first,
        # so this is not a retest.
        sig = signals.add_signals(self._bull_block([100.1, 100.2, 100.1]))
        self.assertFalse(sig["long_entry"].any())

    def test_no_entry_after_block_age_48(self):
        # Block left at age 0, but the inside close arrives at age 49.
        df = self._bull_block([101.0, 100.1])
        df["ob_age"] = [0, 49]
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())

    def test_short_entry_mirror(self):
        n = 3
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        c = np.array([99.0, 99.9, 99.8])
        df = pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "disp_dir": np.zeros(n, dtype=int),
            "ob_dir": -np.ones(n, dtype=int),
            "ob_low": np.full(n, 99.7), "ob_high": np.full(n, 100.1),
            "ob_age": np.arange(n), "ob_id": np.zeros(n, dtype=int),
        })
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_exit_on_block_violation(self):
        # Entry at bar 1, close below block low at bar 3 -> long exit.
        sig = signals.add_signals(
            self._bull_block([101.0, 100.1, 100.2, 99.0]))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertFalse(sig["long_exit"].iloc[1])

    def test_exit_on_opposite_displacement(self):
        # Entry at bar 1, bearish displacement at bar 3 -> long exit
        # even though price is still inside the block.
        sig = signals.add_signals(
            self._bull_block([101.0, 100.1, 100.2, 100.2],
                             disp_extra={3: -1}))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_end_to_end_pipeline_fires(self):
        # Full pipeline on the crafted displacement frame: price never
        # re-enters the block in the flat tail, so entries stay 0 —
        # but the pipeline must run and produce boolean columns.
        # A pullback variant: append a drift back into the block.
        df = _bullish_displacement_frame()
        df = df.copy()
        tail = np.linspace(104.0, 100.1, 40)
        df.loc[33:72, "c"] = tail
        df.loc[33:72, "o"] = np.concatenate([[104.0], tail[:-1]])
        df.loc[33:72, "h"] = df.loc[33:72, ["o", "c"]].max(axis=1) + 0.1
        df.loc[33:72, "l"] = df.loc[33:72, ["o", "c"]].min(axis=1) - 0.1
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertGreaterEqual(int(sig["long_entry"].sum()), 1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 96)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 60)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
