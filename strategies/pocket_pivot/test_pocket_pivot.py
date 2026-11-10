"""Pocket pivot tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.pocket_pivot import indicators, risk, signals
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


def _signal_frame(rows):
    """Direct signal unit-test frame from explicit per-bar dicts."""
    return pd.DataFrame(rows)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _trend_frame(n=1300, drift=0.0005, final_jump=1.01, final_vol=5000.0):
    """Steady drift with a small dip every 10th bar (a down bar, vol 100),
    then a final up bar with a volume spike. Opens = previous close."""
    closes = 100.0 * (1.0 + drift) ** np.arange(n)
    for i in range(n):
        if i % 10 == 9:
            closes[i] *= 0.998
    closes[-1] = closes[-2] * final_jump
    vols = np.full(n, 100.0)
    vols[-1] = final_vol
    return _frame(closes, vols=vols)


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


class TestPocketPivot(unittest.TestCase):
    def test_registered(self):
        self.assertIn("pocket_pivot", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat price: both EMAs sit exactly on the price; no down bars
        # exist, so max_down_vol_240 is NaN everywhere; EMA is not rising
        # (equal, not strictly greater), so no entries.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["ema_240"], 100.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["ema_1200"], 100.0, atol=1e-9))
        self.assertTrue(df["max_down_vol_240"].isna().all())
        self.assertFalse(df["ema_240_rising"].iloc[risk.WARMUP:].any())
        self.assertTrue(np.isfinite(tail["ema_240"]).all())

    def test_indicator_ema_hand_computed(self):
        # Manual EMA(240) recursion, alpha = 2/(240+1), seeded at the
        # first close; pandas ewm(adjust=False) must match it exactly
        # once min_periods is satisfied.
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 400)))
        df = indicators.add_indicators(_frame(closes))
        alpha = 2.0 / (indicators.EMA_FAST + 1)
        ema_manual = closes[0]
        for x in closes[1:]:
            ema_manual = alpha * x + (1.0 - alpha) * ema_manual
        self.assertAlmostEqual(df["ema_240"].iloc[399], ema_manual, places=8)
        # EMA(1200) is still NaN at bar 399 (min_periods=1200).
        self.assertTrue(np.isnan(df["ema_1200"].iloc[399]))

    def test_indicator_max_down_vol_hand_computed(self):
        # Down bars at indices 0,1,2 with vols 5, 50, 30; all later bars
        # flat (c == o, neither up nor down). max_down_vol_240 at bar i
        # is the max down-bar volume over bars [0, i-1].
        n = 300
        closes = np.full(n, 100.0)
        opens = np.full(n, 100.0)
        vols = np.full(n, 100.0)
        closes[0], opens[0], vols[0] = 99.0, 100.0, 5.0
        closes[1], opens[1], vols[1] = 99.0, 100.0, 50.0
        closes[2], opens[2], vols[2] = 99.0, 100.0, 30.0
        df = indicators.add_indicators(_frame(closes, opens=opens, vols=vols))
        self.assertTrue(np.isnan(df["max_down_vol_240"].iloc[0]))
        self.assertEqual(df["max_down_vol_240"].iloc[1], 5.0)
        self.assertEqual(df["max_down_vol_240"].iloc[2], 50.0)
        self.assertEqual(df["max_down_vol_240"].iloc[3], 50.0)
        # The 240-bar window slides past the early down bars: at bar 242
        # the window [2, 241] still contains bar 2 (vol 30); at bar 243
        # the window [3, 242] contains no down bar at all.
        self.assertEqual(df["max_down_vol_240"].iloc[242], 30.0)
        self.assertTrue(np.isnan(df["max_down_vol_240"].iloc[243]))
        self.assertTrue(np.isnan(df["max_down_vol_240"].iloc[299]))

    def test_indicator_ema_rising_uptrend(self):
        df = indicators.add_indicators(_trend_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(tail["ema_240_rising"].all())
        self.assertTrue((tail["ema_240"] > tail["ema_1200"]).all())
        self.assertTrue((tail["c"] > tail["ema_240"]).all())

    def test_long_entry_on_pocket_pivot(self):
        # Full pipeline: uptrend + final up bar with volume far above
        # every prior down bar's volume -> long_entry on the last bar.
        df = _run(_trend_frame())
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["short_exit"].any())

    def test_no_entry_volume_fails(self):
        # Same uptrend, but the final bar's volume (50) does not beat
        # the prior down bars' volume (100) -> no entry.
        df = _run(_trend_frame(final_vol=50.0))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_extended(self):
        # Final bar jumps +20%: close > 1.10 * EMA(240) -> extended,
        # no entry despite the volume spike.
        df = _run(_trend_frame(final_jump=1.20))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_downtrend(self):
        # Steady downtrend: EMA(240) falling and close below it, so the
        # volume spike on the final up bar is not a pocket pivot.
        df = _run(_trend_frame(drift=-0.0005))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_signal_logic_crafted_rows(self):
        base = dict(o=100.0, c=105.0, v=500.0, ema_240=100.0,
                    ema_1200=90.0, ema_240_rising=True,
                    max_down_vol_240=100.0)
        # All conditions met -> entry.
        df = signals.add_signals(_signal_frame([dict(base)]))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        # Volume fails.
        row = dict(base, v=50.0)
        self.assertFalse(signals.add_signals(_signal_frame([row]))["long_entry"].iloc[0])
        # Extended: close 115 > 1.10 * 100.
        row = dict(base, c=115.0)
        self.assertFalse(signals.add_signals(_signal_frame([row]))["long_entry"].iloc[0])
        # Close below EMA(240): no entry, long_exit fires.
        row = dict(base, c=99.0, o=98.0)
        out = signals.add_signals(_signal_frame([row]))
        self.assertFalse(out["long_entry"].iloc[0])
        self.assertTrue(out["long_exit"].iloc[0])
        # EMA(240) below EMA(1200): no entry.
        row = dict(base, ema_1200=101.0)
        self.assertFalse(signals.add_signals(_signal_frame([row]))["long_entry"].iloc[0])
        # EMA(240) not rising: no entry.
        row = dict(base, ema_240_rising=False)
        self.assertFalse(signals.add_signals(_signal_frame([row]))["long_entry"].iloc[0])
        # Down bar (close < open): no entry.
        row = dict(base, c=99.0, o=100.0, ema_240=90.0)
        self.assertFalse(signals.add_signals(_signal_frame([row]))["long_entry"].iloc[0])
        # No down-bar volume history (NaN): volume test cannot pass.
        row = dict(base, max_down_vol_240=np.nan)
        self.assertFalse(signals.add_signals(_signal_frame([row]))["long_entry"].iloc[0])
        # Shorts are never signalled.
        df = signals.add_signals(_signal_frame([dict(base)]))
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 240)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertFalse(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 1250)

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
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("ema_240", "ema_1200", "max_down_vol_240",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): indicators converge to the price,
        # no entries.
        df = _run(_frame([100.0] * 1400, highs=[100.0] * 1400,
                         lows=[100.0] * 1400))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["ema_240"], 100.0, atol=1e-9))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
