"""Mitigation block tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.mitigation_block import indicators, risk, signals
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


def _bear_mb_frame():
    """Bearish mitigation block: H1=110 (centre 2, confirmed bar 4),
    L1=90 (centre 7, bar 9), H2=105 failure swing (centre 12, bar 14,
    105 < 110, never through 110), break close 88.5 < 90 at bar 16.
    Block = candle at the L1 centre (bar 7): [90, 96]. Return into
    the block: close 92.5 at bar 18 -> short."""
    highs = [100, 105, 110, 105, 100, 102, 98, 96, 95, 97,
             100, 103, 105, 102, 100, 98, 92, 90, 93]
    lows = [99, 104, 109, 104, 99, 100, 94, 90, 93, 94,
            98, 101, 103, 100, 98, 95, 88, 87, 91]
    closes = [99.5, 104.5, 109.5, 104.5, 99.5, 101, 95, 92, 94, 96,
              99, 102, 104, 101, 99, 96, 88.5, 89, 92.5]
    opens = [99, 99.5, 104.5, 109.5, 104.5, 99.5, 101, 91, 92, 94,
             96, 99, 102, 104, 101, 99, 96, 88.5, 89]
    return _frame(closes, highs=highs, lows=lows, opens=opens)


def _bull_mb_frame():
    """Mirror of _bear_mb_frame (prices reflected about 100):
    bullish mitigation block, long trigger on the final bar."""
    df = _bear_mb_frame()
    return pd.DataFrame({
        "t": df["t"],
        "o": 200.0 - df["c"],
        "h": 200.0 - df["l"],
        "l": 200.0 - df["h"],
        "c": 200.0 - df["c"],
        "v": df["v"],
    })


class TestMitigationBlock(unittest.TestCase):
    def test_registered(self):
        self.assertIn("mitigation_block", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_pivots_confirmed_at_centre_plus_two(self):
        df = indicators.add_indicators(_bear_mb_frame())
        self.assertTrue(np.isnan(df["swing_high"].iloc[3]))
        self.assertAlmostEqual(df["swing_high"].iloc[4], 110.0)
        self.assertTrue(np.isnan(df["swing_low"].iloc[8]))
        self.assertAlmostEqual(df["swing_low"].iloc[9], 90.0)
        self.assertAlmostEqual(df["swing_high"].iloc[14], 105.0)

    def test_bear_block_is_l1_centre_candle(self):
        df = indicators.add_indicators(_bear_mb_frame())
        self.assertTrue(np.isnan(df["bear_block_bottom"].iloc[15]))
        self.assertAlmostEqual(df["bear_block_bottom"].iloc[16], 90.0)
        self.assertAlmostEqual(df["bear_block_top"].iloc[16], 96.0)
        self.assertEqual(int(df["mb_state"].iloc[16]), 2)
        self.assertEqual(int(df["mb_side"].iloc[16]), 1)

    def test_bear_short_trigger_on_return_into_block(self):
        df = _run(_bear_mb_frame())
        self.assertFalse(df["short_entry"].iloc[:18].any())
        self.assertTrue(df["short_entry"].iloc[18])
        self.assertFalse(df["long_entry"].iloc[18])
        self.assertEqual(int(df["short_entry"].sum()), 1)

    def test_bull_long_trigger_on_mirrored_frame(self):
        df = _run(_bull_mb_frame())
        self.assertFalse(df["long_entry"].iloc[:18].any())
        self.assertTrue(df["long_entry"].iloc[18])
        self.assertFalse(df["short_entry"].iloc[18])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertAlmostEqual(df["bull_block_bottom"].iloc[16], 104.0)
        self.assertAlmostEqual(df["bull_block_top"].iloc[16], 110.0)

    def test_no_entry_without_break(self):
        # Same H1/L1/H2, but price never closes below L1=90.
        df0 = _bear_mb_frame()
        closes = list(df0["c"])
        closes[16] = 95.0
        closes[17] = 96.0
        closes[18] = 97.0
        df = _run(_frame(closes, highs=list(df0["h"]), lows=list(df0["l"]),
                         opens=list(df0["o"])))
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(np.isnan(df["bear_block_bottom"]).all())

    def test_no_entry_when_rally_trades_through_h1(self):
        # H2 prints at 112, above H1=110: not a failure swing, the
        # setup is invalidated and no block ever arms.
        df0 = _bear_mb_frame()
        highs = list(df0["h"])
        highs[12] = 112.0
        closes = list(df0["c"])
        closes[12] = 111.0
        df = _run(_frame(closes, highs=highs, lows=list(df0["l"]),
                         opens=list(df0["o"])))
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(np.isnan(df["bear_block_bottom"]).all())

    def test_no_entry_without_return_into_block(self):
        # Break happens, but closes stay below the block [90,96].
        df0 = _bear_mb_frame()
        closes = list(df0["c"])
        closes[17] = 89.0
        closes[18] = 88.5
        df = _run(_frame(closes, highs=list(df0["h"]), lows=list(df0["l"]),
                         opens=list(df0["o"])))
        self.assertFalse(df["short_entry"].any())
        self.assertAlmostEqual(df["bear_block_bottom"].iloc[18], 90.0)

    def test_block_invalidated_by_close_above_block_high(self):
        # After the break, a close above the block high (97 > 96)
        # clears the block before any return into it.
        df0 = _bear_mb_frame()
        highs = list(df0["h"])
        lows = list(df0["l"])
        closes = list(df0["c"])
        closes[17] = 97.0
        highs[17] = 98.0
        df = _run(_frame(closes, highs=highs, lows=lows,
                         opens=list(df0["o"])))
        self.assertTrue(np.isnan(df["bear_block_top"].iloc[18]))
        self.assertFalse(df["short_entry"].any())

    def test_block_expires_after_150_bars(self):
        # Break at bar 16; price then sits below the block (close 85)
        # with no return: block alive at bar 166 (150 bars after the
        # break) and gone at bar 167.
        df0 = _bear_mb_frame()
        n_extra = 160
        highs = list(df0["h"]) + [86.0] * n_extra
        lows = list(df0["l"]) + [84.0] * n_extra
        closes = list(df0["c"]) + [85.0] * n_extra
        opens = list(df0["o"]) + [85.0] * n_extra
        df = indicators.add_indicators(
            _frame(closes, highs=highs, lows=lows, opens=opens))
        self.assertAlmostEqual(df["bear_block_bottom"].iloc[166], 90.0)
        self.assertTrue(np.isnan(df["bear_block_bottom"].iloc[167]))
        # The base frame's own return into the block fires at bar 18;
        # the flat tail must not fire again.
        self.assertEqual(int(df["short_trigger"].sum()), 1)
        self.assertFalse(df["short_trigger"].iloc[19:].any())

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=95.0, long_trigger=False, short_trigger=True,
            bull_block_bottom=104.0, bear_block_top=96.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_on_close_above_block_high(self):
        rows = pd.DataFrame([dict(
            c=97.0, long_trigger=False, short_trigger=False,
            bull_block_bottom=90.0, bear_block_top=96.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_exit_long_on_close_below_block_low(self):
        rows = pd.DataFrame([dict(
            c=103.0, long_trigger=False, short_trigger=False,
            bull_block_bottom=104.0, bear_block_top=110.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

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
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("swing_high", "bear_block_bottom", "bear_block_top",
                    "mb_state", "long_entry", "short_entry", "long_exit"):
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
