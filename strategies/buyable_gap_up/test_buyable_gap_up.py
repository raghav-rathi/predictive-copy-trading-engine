"""Buyable Gap-Up tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.buyable_gap_up import indicators, risk, signals


def _frame(o, h, l, c, v, seed=7):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _flat_frame(n=1300, price=100.0, vol=100.0, seed=7):
    rng = np.random.default_rng(seed)
    c = np.full(n, price)
    o = c.copy()
    h = c * 1.001
    l = c * 0.999
    v = np.full(n, vol) * rng.uniform(0.9, 1.1, n)
    return _frame(o, h, l, c, v)


def _gap_up_frame():
    """1,300 flat bars, then a gap-up bar: open 105 (prior close
    100), close 106, high 107, low 104, volume 300 (3x average)."""
    base = _flat_frame(1300)
    gap = pd.DataFrame({
        "t": [base["t"].iloc[-1] + 3_600_000],
        "o": [105.0], "h": [107.0], "l": [104.0], "c": [106.0],
        "v": [300.0],
    })
    return pd.concat([base, gap], ignore_index=True)


def _random_walk_frame(n=1500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("atr40", "gap", "gap_up", "gap_down", "vol_avg1200",
                    "vol_ratio", "sma50", "sma200", "sma240", "trend_up",
                    "trend_down", "long_setup", "short_setup", "atr"):
            self.assertIn(col, ind.columns)

    def test_gap_up_setup_fires_on_constructed_gap(self):
        ind = indicators.add_indicators(_gap_up_frame())
        self.assertTrue(bool(ind["long_setup"].iloc[-1]))
        self.assertFalse(bool(ind["short_setup"].iloc[-1]))

    def test_gap_size_threshold(self):
        # Gap of 0.2 on flat data: ATR(40) ~ 0.2, so 0.75*ATR ~ 0.15
        # — a 0.2 gap clears it; a 0.05 gap must not.
        for gap_size, expect in ((0.2, True), (0.05, False)):
            base = _flat_frame(1300)
            gap = pd.DataFrame({
                "t": [base["t"].iloc[-1] + 3_600_000],
                "o": [100.0 + gap_size], "h": [101.0], "l": [100.0],
                "c": [100.0 + gap_size], "v": [300.0],
            })
            ind = indicators.add_indicators(
                pd.concat([base, gap], ignore_index=True))
            self.assertEqual(bool(ind["long_setup"].iloc[-1]), expect,
                             f"gap {gap_size}")

    def test_volume_gate_blocks_small_volume_gap(self):
        # Same 5-point gap but volume 100 (1x average): no setup.
        base = _flat_frame(1300)
        gap = pd.DataFrame({
            "t": [base["t"].iloc[-1] + 3_600_000],
            "o": [105.0], "h": [107.0], "l": [104.0], "c": [106.0],
            "v": [100.0],
        })
        ind = indicators.add_indicators(
            pd.concat([base, gap], ignore_index=True))
        self.assertFalse(bool(ind["long_setup"].iloc[-1]))

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:1300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("long_setup", "short_setup", "gap_up"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:1300].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, long_setup, short_setup, c, h, l, sma240):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": h, "l": l, "c": c, "v": np.full(n, 100.0),
            "long_setup": long_setup, "short_setup": short_setup,
            "sma240": sma240,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_gap_up_bar_enters_long(self):
        ind = indicators.add_indicators(_gap_up_frame())
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[-1])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_exit_on_close_below_gap_bar_low(self):
        # Long at bar 1 (gap bar low 104); close 105 holds, 103 exits.
        n = 4
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 106.0, 105.0, 103.0]),
            h=np.array([101.0, 107.0, 106.0, 104.0]),
            l=np.array([99.0, 104.0, 104.0, 102.0]),
            sma240=np.full(n, 90.0),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_exit_on_close_below_sma240(self):
        # Gap low holds (close 105 > 104) but close < SMA240 exits.
        n = 3
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False]),
            short_setup=np.zeros(n, dtype=bool),
            c=np.array([100.0, 106.0, 105.0]),
            h=np.array([101.0, 107.0, 106.0]),
            l=np.array([99.0, 104.0, 104.0]),
            sma240=np.array([90.0, 90.0, 110.0]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[2])

    def test_opposite_setup_flips_position(self):
        # Long at bar 1, gap-down at bar 3 -> flip to short.
        n = 4
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.array([False, False, False, True]),
            c=np.array([100.0, 106.0, 105.0, 104.0]),
            h=np.array([101.0, 107.0, 106.0, 106.0]),
            l=np.array([99.0, 104.0, 104.0, 100.0]),
            sma240=np.full(n, 90.0),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 240)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 1250)

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
