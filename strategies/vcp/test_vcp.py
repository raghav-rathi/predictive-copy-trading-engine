"""Volatility Contraction Pattern (VCP) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vcp import indicators, risk, signals
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


def _vcp_frame(leg2_vol=100.0):
    """210 flat bars at 90, then two contracting pullbacks:
    high 120 -> low 90 (depth 25%), high 118 -> low 100 (depth
    15.3%, higher trough, drying volume). Base valid from bar 226
    (when the intermediate trough 96 confirms); bar 230 breaks
    above the 118 pivot on expanding volume."""
    n_base = 210
    closes = [90.0] * n_base
    highs = [91.0] * n_base
    lows = [89.0] * n_base
    vols = [100.0] * n_base
    # bars 210-214: rise to swing high 120 (centre 212)
    closes += [95, 105, 115, 110, 105]
    highs += [100, 110, 120, 110, 100]
    lows += [94, 100, 110, 100, 95]
    vols += [100, 100, 200, 100, 100]
    # bars 215-219: fall to swing low 90 (centre 217)
    closes += [102, 98, 92, 98, 103]
    highs += [105, 100, 95, 100, 105]
    lows += [100, 95, 90, 95, 100]
    vols += [200, 200, 200, 100, 100]
    # bars 220-224: rise to swing high 118 (centre 222)
    closes += [106, 112, 116, 112, 107]
    highs += [105, 112, 118, 112, 105]
    lows += [95, 100, 108, 100, 96]
    vols += [100, 100, 100, 100, 100]
    # bars 225-229: fall to swing low 100 (centre 227)
    closes += [105, 102, 101, 104, 108]
    highs += [112, 108, 104, 108, 112]
    lows += [104, 102, 100, 102, 104]
    vols += [leg2_vol] * 5
    # bar 230: breakout above the 118 pivot on volume expansion
    closes += [120.0]
    highs += [121.0]
    lows += [115.0]
    vols += [300.0]
    return _frame(closes, highs=highs, lows=lows, vols=vols)


class TestVcp(unittest.TestCase):
    def test_registered(self):
        self.assertIn("vcp", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_base_valid_after_second_pullback(self):
        df = indicators.add_indicators(_vcp_frame())
        # Only one pullback complete before bar 226 -> not valid.
        self.assertFalse(df["vcp_valid"].iloc[219])
        self.assertFalse(df["vcp_valid"].iloc[224])
        # The intermediate trough 96 (centre 224) confirms at bar 226:
        # second pullback (118 -> 96) is already shallower, higher and
        # drier than the first, so the base validates here; the later
        # extension to trough 100 only tightens it.
        self.assertTrue(df["vcp_valid"].iloc[226])
        self.assertTrue(df["vcp_valid"].iloc[229])
        self.assertTrue(df["vcp_valid"].iloc[230])
        self.assertAlmostEqual(df["pivot_high"].iloc[229], 118.0)

    def test_pivot_high_after_first_pullback(self):
        df = indicators.add_indicators(_vcp_frame())
        self.assertAlmostEqual(df["pivot_high"].iloc[219], 120.0)

    def test_no_base_when_volume_not_drying(self):
        # Second down-leg volume (300) exceeds the first leg's mean
        # -> the contraction chain breaks, base never validates.
        df = indicators.add_indicators(_vcp_frame(leg2_vol=300.0))
        self.assertFalse(df["vcp_valid"].iloc[229])
        self.assertFalse(df["vcp_valid"].iloc[230])

    def test_long_entry_on_pivot_breakout(self):
        df = _run(_vcp_frame())
        self.assertTrue(df["long_entry"].iloc[230])
        self.assertFalse(df["short_entry"].iloc[230])
        self.assertFalse(df["long_entry"].iloc[229])

    def test_trend_filter_values(self):
        df = indicators.add_indicators(_vcp_frame())
        self.assertGreater(df["c"].iloc[230], df["sma50"].iloc[230])
        self.assertGreater(df["sma50"].iloc[230], df["sma200"].iloc[230])
        self.assertTrue(np.isnan(df["sma200"].iloc[198]))
        self.assertFalse(np.isnan(df["sma200"].iloc[199]))

    def test_no_entry_without_volume_expansion(self):
        df = _vcp_frame()
        df.loc[230, "v"] = 100.0
        out = _run(df)
        self.assertFalse(out["long_entry"].iloc[230])

    def test_no_entry_without_breakout(self):
        df = _vcp_frame()
        df.loc[230, "c"] = 115.0
        out = _run(df)
        self.assertFalse(out["long_entry"].iloc[230])

    def test_signal_logic_crafted_rows(self):
        base = dict(c=120.0, sma50=100.0, sma200=95.0, pivot_high=118.0,
                    pivot_low=90.0, vcp_valid=True, vcp_valid_short=False,
                    v=300.0, vol_ma50=100.0)
        df = signals.add_signals(pd.DataFrame([base]))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        # No trend filter -> no entry.
        row = dict(base, sma50=95.0, sma200=100.0)
        df = signals.add_signals(pd.DataFrame([row]))
        self.assertFalse(df["long_entry"].iloc[0])
        # No base -> no entry.
        row = dict(base, vcp_valid=False)
        df = signals.add_signals(pd.DataFrame([row]))
        self.assertFalse(df["long_entry"].iloc[0])
        # Short mirror.
        row = dict(c=88.0, sma50=100.0, sma200=105.0, pivot_high=118.0,
                   pivot_low=90.0, vcp_valid=False, vcp_valid_short=True,
                   v=300.0, vol_ma50=100.0)
        df = signals.add_signals(pd.DataFrame([row]))
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertFalse(df["long_entry"].iloc[0])

    def test_exit_long_on_failed_breakout(self):
        # pivot_low is set to the pivot high here so the row isolates
        # the long-exit leg (a real short-exit leg cannot fire too).
        row = dict(c=117.0, sma50=100.0, sma200=95.0, pivot_high=118.0,
                   pivot_low=118.0, vcp_valid=True, vcp_valid_short=False,
                   v=100.0, vol_ma50=100.0)
        df = signals.add_signals(pd.DataFrame([row]))
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        # pivot_high is set to the pivot low here so the row isolates
        # the short-exit leg.
        row = dict(c=91.0, sma50=100.0, sma200=105.0, pivot_high=90.0,
                   pivot_low=90.0, vcp_valid=False, vcp_valid_short=True,
                   v=100.0, vol_ma50=100.0)
        df = signals.add_signals(pd.DataFrame([row]))
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_exit_long_on_opposite_signal(self):
        # Close below the short pivot on expanding volume with a valid
        # short base -> short signal prints, so a long exits too.
        row = dict(c=89.0, sma50=100.0, sma200=105.0, pivot_high=118.0,
                   pivot_low=90.0, vcp_valid=False, vcp_valid_short=True,
                   v=300.0, vol_ma50=100.0)
        df = signals.add_signals(pd.DataFrame([row]))
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[0])

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
        self.assertEqual(risk.WARMUP, 250)

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
        self.assertFalse(df["vcp_valid"].any())

    def test_no_lookahead_future_jump(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("sma50", "sma200", "pivot_high", "pivot_low",
                    "vcp_valid", "long_entry", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["vcp_valid"].any())


if __name__ == "__main__":
    unittest.main()
