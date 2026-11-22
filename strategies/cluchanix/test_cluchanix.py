"""ClucHAnix tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.cluchanix import indicators, risk, signals


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


def _signal_frame(n=12, **overrides):
    """Hand-built indicator frame; defaults satisfy no condition."""
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    cols = {
        "t": t, "o": np.full(n, 100.0), "h": np.full(n, 100.1),
        "l": np.full(n, 99.9), "c": np.full(n, 100.0),
        "v": np.full(n, 100.0),
        "ha_open": np.full(n, 100.0), "ha_high": np.full(n, 100.1),
        "ha_low": np.full(n, 99.9), "ha_close": np.full(n, 100.0),
        "mid": np.full(n, 100.0), "lower": np.full(n, 99.0),
        "upper": np.full(n, 101.0), "bbdelta": np.full(n, 1.0),
        "closedelta": np.full(n, 0.1), "tail": np.full(n, 0.1),
        "tail_up": np.full(n, 0.1), "ema_fast": np.full(n, 100.0),
        "ema_slow": np.full(n, 100.0), "fisher": np.zeros(n),
        "rocr_1h": np.full(n, 1.0),
    }
    for k, v in overrides.items():
        cols[k] = np.asarray(v, dtype=float)
    return pd.DataFrame(cols)


def _set_primary_long(frame, i):
    """Make bar i satisfy the primary long entry (see signals.py)."""
    frame.loc[i, "bbdelta"] = 3.0
    frame.loc[i, "closedelta"] = 1.0
    frame.loc[i, "tail"] = 0.1
    frame.loc[i, "ha_close"] = 98.0
    frame.loc[i - 1, "ha_close"] = 100.0
    frame.loc[i - 1, "lower"] = 99.0


def _set_primary_short(frame, i):
    frame.loc[i, "bbdelta"] = 3.0
    frame.loc[i, "closedelta"] = 1.0
    frame.loc[i, "tail_up"] = 0.1
    frame.loc[i, "ha_close"] = 102.0
    frame.loc[i - 1, "ha_close"] = 100.0
    frame.loc[i - 1, "upper"] = 101.0


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("ha_open", "ha_high", "ha_low", "ha_close", "mid",
                    "lower", "upper", "bbdelta", "closedelta", "tail",
                    "tail_up", "ema_fast", "ema_slow", "rsi", "fisher",
                    "rocr", "rocr_1h", "atr"):
            self.assertIn(col, ind.columns)

    def test_heikin_ashi_flat(self):
        n = 50
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0), "h": np.full(n, 100.0),
            "l": np.full(n, 100.0), "c": np.full(n, 100.0),
            "v": np.full(n, 100.0)})
        ind = indicators.add_indicators(df)
        self.assertTrue(np.allclose(ind["ha_close"].iloc[10:], 100.0))
        self.assertTrue(np.allclose(ind["ha_open"].iloc[10:], 100.0))

    def test_heikin_ashi_close_is_ohlc_average(self):
        # ha_close[0] = (o+h+l+c)/4 on the first bar by construction.
        df = _frame_from_close([100.0, 102.0, 101.0])
        ind = indicators.add_indicators(df)
        o, h, l, c = df.iloc[0][["o", "h", "l", "c"]]
        self.assertAlmostEqual(ind["ha_close"].iloc[0],
                               (o + h + l + c) / 4.0, places=9)

    def test_fisher_is_tanh_of_rsi(self):
        ind = indicators.add_indicators(_random_walk_frame())
        expect = np.tanh(0.1 * (ind["rsi"] - 50.0))
        pd.testing.assert_series_equal(ind["fisher"], expect,
                                       check_names=False)

    def test_rocr_1h_is_168_bar_ratio(self):
        ind = indicators.add_indicators(_random_walk_frame())
        expect = ind["ha_close"] / ind["ha_close"].shift(168)
        pd.testing.assert_series_equal(ind["rocr_1h"], expect,
                                       check_names=False)

    def test_bb_lower_below_mid(self):
        ind = indicators.add_indicators(_random_walk_frame())
        valid = ind["lower"].notna() & ind["mid"].notna()
        self.assertTrue((ind.loc[valid, "lower"] < ind.loc[valid, "mid"]).all())
        self.assertTrue((ind.loc[valid, "upper"] > ind.loc[valid, "mid"]).all())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        full = indicators.add_indicators(df)
        part = indicators.add_indicators(short)
        for col in ("ha_close", "mid", "lower", "bbdelta", "fisher", "rocr_1h"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                part[col].reset_index(drop=True), check_names=False)


class TestSignals(unittest.TestCase):
    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_primary_long_entry_fires(self):
        f = _signal_frame()
        _set_primary_long(f, 5)
        sig = signals.add_signals(f)
        self.assertTrue(sig["long_entry"].iloc[5])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_primary_long_blocked_when_not_below_band(self):
        # ha_close above the prior lower band -> primary path fails.
        f = _signal_frame()
        _set_primary_long(f, 5)
        f.loc[5, "ha_close"] = 100.0  # not below lower.shift(1) = 99
        sig = signals.add_signals(f)
        self.assertFalse(sig["long_entry"].any())

    def test_primary_long_blocked_by_narrow_bbdelta(self):
        # bbdelta 1.0 < ha_close * 0.01965 = 1.93 -> fails the width gate.
        f = _signal_frame()
        _set_primary_long(f, 5)
        f.loc[5, "bbdelta"] = 1.0
        sig = signals.add_signals(f)
        self.assertFalse(sig["long_entry"].any())

    def test_alternative_long_is_dormant(self):
        # ha_close < ema_slow but ha_close < 0.00799 * lower is
        # impossible for positive prices -> no entry via alt path.
        f = _signal_frame()
        f.loc[5, "ha_close"] = 90.0
        f.loc[5, "ema_slow"] = 100.0
        sig = signals.add_signals(f)
        self.assertFalse(sig["long_entry"].any())

    def test_primary_short_entry_fires(self):
        f = _signal_frame()
        _set_primary_short(f, 5)
        sig = signals.add_signals(f)
        self.assertTrue(sig["short_entry"].iloc[5])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_long_exit_on_sell_trend(self):
        f = _signal_frame(n=12)
        _set_primary_long(f, 5)
        # Sell trend at bar 8: fisher high, two lower HA highs,
        # HA close falling, EMA fast above close, close above mid.
        f.loc[6, "ha_high"] = 102.0
        f.loc[7, "ha_high"] = 101.0
        f.loc[8, "ha_high"] = 100.0
        f.loc[7, "ha_close"] = 100.0
        f.loc[8, "ha_close"] = 99.0
        f.loc[8, "ema_fast"] = 101.0
        f.loc[8, "fisher"] = 0.5
        sig = signals.add_signals(f)
        self.assertTrue(sig["long_entry"].iloc[5])
        self.assertTrue(sig["long_exit"].iloc[8])
        self.assertEqual(int(sig["long_exit"].sum()), 1)

    def test_no_entry_while_in_position(self):
        # Primary conditions at bars 5 and 6: only the first enters.
        f = _signal_frame()
        _set_primary_long(f, 5)
        _set_primary_long(f, 6)
        sig = signals.add_signals(f)
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_no_lookahead_signals(self):
        df = _random_walk_frame()
        full = signals.add_signals(indicators.add_indicators(df))
        part = signals.add_signals(
            indicators.add_indicators(df.iloc[:200]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                full[col].iloc[:200].reset_index(drop=True),
                part[col].reset_index(drop=True), check_names=False)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 6.0)
        self.assertEqual(r.trail_atr_mult, 6.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 200)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        self.assertGreaterEqual(res.metrics()["trades"], 0)


if __name__ == "__main__":
    unittest.main()
