"""RSI pullback to EMA(50) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.rsi_ema_pullback import indicators, risk, signals


def _frame(o, h, l, c, v=None):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _ohlc_from_closes(c):
    """Bars whose high/low bracket open/close by 0.1% (no gaps)."""
    c = np.asarray(c, dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    return _frame(o, h, l, c)


def _dip_recovery_frame():
    """60 bars rising +1, 8 bars dipping -2 (RSI falls below 40
    while price stays above a rising EMA(50)), then +2 recovery.
    Entry fires on the RSI cross back above 40 (bar 68); exit
    fires when RSI reaches 70 (bar 75)."""
    c = list(100 + np.arange(60, dtype=float))
    p = 159.0
    for _ in range(8):
        p -= 2
        c.append(p)
    for _ in range(10):
        p += 2
        c.append(p)
    return _ohlc_from_closes(c)


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
        for col in ("ema50", "rsi", "ema_rising", "ema_falling",
                    "trend_up", "trend_down", "rsi_below_40",
                    "rsi_above_60", "rsi_cross_up_40", "rsi_cross_dn_60",
                    "atr"):
            self.assertIn(col, ind.columns)

    def test_ema50_on_flat_series(self):
        # Constant 100: EMA(50) is NaN until bar 49, then exactly 100.
        ind = indicators.add_indicators(_ohlc_from_closes(np.full(100, 100.0)))
        self.assertTrue(ind["ema50"].iloc[:49].isna().all())
        self.assertAlmostEqual(ind["ema50"].iloc[49], 100.0)
        self.assertAlmostEqual(ind["ema50"].iloc[-1], 100.0)

    def test_rsi_flat_series_is_zero(self):
        # No gains and no losses: base.rsi seeds RSI at 0.
        ind = indicators.add_indicators(_ohlc_from_closes(np.full(100, 100.0)))
        self.assertAlmostEqual(ind["rsi"].iloc[-1], 0.0)

    def test_rsi_monotonic_up_is_100(self):
        ind = indicators.add_indicators(
            _ohlc_from_closes(100 + np.arange(100, dtype=float)))
        self.assertAlmostEqual(ind["rsi"].iloc[-1], 100.0)

    def test_rsi_monotonic_down_is_zero(self):
        ind = indicators.add_indicators(
            _ohlc_from_closes(200 - np.arange(100, dtype=float)))
        self.assertAlmostEqual(ind["rsi"].iloc[-1], 0.0)

    def test_trend_up_on_rising_series(self):
        ind = indicators.add_indicators(
            _ohlc_from_closes(100 + np.arange(100, dtype=float)))
        self.assertTrue(ind["trend_up"].iloc[-1])
        self.assertFalse(ind["trend_down"].iloc[-1])

    def test_trend_down_on_falling_series(self):
        ind = indicators.add_indicators(
            _ohlc_from_closes(200 - np.arange(100, dtype=float)))
        self.assertTrue(ind["trend_down"].iloc[-1])
        self.assertFalse(ind["trend_up"].iloc[-1])

    def test_no_nan_in_signal_columns(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("ema_rising", "ema_falling", "trend_up", "trend_down",
                    "rsi_below_40", "rsi_above_60", "rsi_cross_up_40",
                    "rsi_cross_dn_60"):
            self.assertFalse(ind[col].isna().any(), col)
            self.assertTrue(ind[col].dtype == bool, col)

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:500]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("ema50", "rsi", "trend_up", "trend_down",
                    "rsi_cross_up_40", "rsi_cross_dn_60"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:500].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )

    def test_deep_dip_breaks_ema_trend(self):
        # A -8/bar dip breaks EMA(50): trend_up goes False mid-dip
        # even though RSI falls below 40. The EMA filter disarms
        # the setup — see CALIBRATION.md.
        c = list(100 + np.arange(60, dtype=float))
        p = 159.0
        for _ in range(5):
            p -= 8
            c.append(p)
        for _ in range(5):
            p += 4
            c.append(p)
        ind = indicators.add_indicators(_ohlc_from_closes(c))
        self.assertTrue((ind["rsi"].iloc[60:65] < 40).any())
        self.assertFalse(ind["trend_up"].iloc[63])
        sig = signals.add_signals(ind)
        self.assertEqual(int(sig["long_entry"].sum()), 0)


class TestSignals(unittest.TestCase):
    def _signal_frame(self, c, ema50, rsi, trend_up, trend_down,
                      cross_up_40, cross_dn_60):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c,
            "v": np.full(n, 100.0),
            "ema50": ema50, "rsi": rsi,
            "trend_up": trend_up, "trend_down": trend_down,
            "rsi_cross_up_40": cross_up_40,
            "rsi_cross_dn_60": cross_dn_60,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_armed_dip_then_cross_enters_long(self):
        # Uptrend throughout; RSI < 40 on bar 1 arms, cross above
        # 40 on bar 2 enters.
        sig = signals.add_signals(self._signal_frame(
            c=np.array([105.0, 104.0, 106.0, 108.0]),
            ema50=np.array([100.0, 100.5, 101.0, 101.5]),
            rsi=np.array([50.0, 35.0, 45.0, 55.0]),
            trend_up=np.array([True, True, True, True]),
            trend_down=np.array([False, False, False, False]),
            cross_up_40=np.array([False, False, True, False]),
            cross_dn_60=np.array([False, False, False, False]),
        ))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_dip_without_cross_no_entry(self):
        sig = signals.add_signals(self._signal_frame(
            c=np.array([105.0, 104.0, 104.5, 105.0]),
            ema50=np.array([100.0, 100.5, 101.0, 101.5]),
            rsi=np.array([50.0, 35.0, 38.0, 39.0]),
            trend_up=np.array([True, True, True, True]),
            trend_down=np.array([False, False, False, False]),
            cross_up_40=np.array([False, False, False, False]),
            cross_dn_60=np.array([False, False, False, False]),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_cross_without_uptrend_no_entry(self):
        # RSI dips and recovers, but the trend is not up: no entry.
        sig = signals.add_signals(self._signal_frame(
            c=np.array([99.0, 98.0, 100.0, 102.0]),
            ema50=np.array([100.0, 100.0, 100.0, 100.0]),
            rsi=np.array([50.0, 35.0, 45.0, 55.0]),
            trend_up=np.array([False, False, False, False]),
            trend_down=np.array([True, True, False, False]),
            cross_up_40=np.array([False, False, True, False]),
            cross_dn_60=np.array([False, False, False, False]),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_long_exit_on_rsi_70(self):
        sig = signals.add_signals(self._signal_frame(
            c=np.array([105.0, 104.0, 106.0, 108.0, 110.0]),
            ema50=np.array([100.0, 100.5, 101.0, 101.5, 102.0]),
            rsi=np.array([50.0, 35.0, 45.0, 60.0, 72.0]),
            trend_up=np.array([True, True, True, True, True]),
            trend_down=np.array([False, False, False, False, False]),
            cross_up_40=np.array([False, False, True, False, False]),
            cross_dn_60=np.array([False, False, False, False, False]),
        ))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[4])
        self.assertEqual(int(sig["long_exit"].sum()), 1)

    def test_long_exit_on_close_below_ema50(self):
        # RSI stays mid-range but price closes below EMA(50).
        sig = signals.add_signals(self._signal_frame(
            c=np.array([105.0, 104.0, 106.0, 99.0]),
            ema50=np.array([100.0, 100.5, 101.0, 101.5]),
            rsi=np.array([50.0, 35.0, 45.0, 50.0]),
            trend_up=np.array([True, True, True, False]),
            trend_down=np.array([False, False, False, True]),
            cross_up_40=np.array([False, False, True, False]),
            cross_dn_60=np.array([False, False, False, False]),
        ))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_short_mirror_entry_and_rsi_30_exit(self):
        # Downtrend; RSI > 60 on bar 1 arms, cross below 60 on
        # bar 2 enters short; RSI 30 on bar 4 exits.
        sig = signals.add_signals(self._signal_frame(
            c=np.array([95.0, 96.0, 94.0, 92.0, 90.0]),
            ema50=np.array([100.0, 99.5, 99.0, 98.5, 98.0]),
            rsi=np.array([50.0, 65.0, 55.0, 40.0, 28.0]),
            trend_up=np.array([False, False, False, False, False]),
            trend_down=np.array([True, True, True, True, True]),
            cross_up_40=np.array([False, False, False, False, False]),
            cross_dn_60=np.array([False, False, True, False, False]),
        ))
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertTrue(sig["short_exit"].iloc[4])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_no_reentry_while_holding(self):
        # Two crosses above 40 while already long: one entry only.
        sig = signals.add_signals(self._signal_frame(
            c=np.array([105.0, 104.0, 106.0, 105.0, 104.0, 106.0, 108.0]),
            ema50=np.array([100.0, 100.5, 101.0, 101.5, 102.0, 102.5, 103.0]),
            rsi=np.array([50.0, 35.0, 45.0, 38.0, 36.0, 44.0, 55.0]),
            trend_up=np.array([True, True, True, True, True, True, True]),
            trend_down=np.array([False, False, False, False, False, False, False]),
            cross_up_40=np.array([False, False, True, False, False, True, False]),
            cross_dn_60=np.array([False, False, False, False, False, False, False]),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_end_to_end_dip_recovery(self):
        ind = indicators.add_indicators(_dip_recovery_frame())
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[68])
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(sig["long_exit"].iloc[75])
        self.assertAlmostEqual(ind["rsi"].iloc[75], 70.82, places=1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 120)
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
