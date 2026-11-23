"""Keltner Channel + MACD combo tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.keltner_macd_combo import indicators, risk, signals


def _frame(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": np.asarray(o, dtype=float),
                         "h": np.asarray(h, dtype=float),
                         "l": np.asarray(l, dtype=float),
                         "c": np.asarray(c, dtype=float),
                         "v": np.asarray(v, dtype=float)})


def _flat_frame(n=100, price=100.0, vol=100.0):
    c = np.full(n, price)
    return _frame(c, c * 1.001, c * 0.999, c, np.full(n, vol))


def _ramp_frame(direction=1, n_flat=60, n_ramp=40, step=1.0, price=100.0):
    """Flat bars, then closes moving `step` per bar. h/l straddle c by 0.2."""
    c_flat = np.full(n_flat, price)
    c_ramp = price + direction * step * np.arange(1, n_ramp + 1)
    c = np.concatenate([c_flat, c_ramp])
    o = np.concatenate([[c[0]], c[:-1]])
    h = c + 0.2
    l = c - 0.2
    return _frame(o, h, l, c, np.full(len(c), 100.0))


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
        for col in ("kc_mid", "kc_upper", "kc_lower", "macd", "macd_signal",
                    "macd_hist", "atr", "long_break", "short_break",
                    "long_setup", "short_setup"):
            self.assertIn(col, ind.columns)

    def test_flat_series_golden_keltner_values(self):
        # Flat 100, h/l = +/-0.1%: TR = 0.2 constant, Wilder ATR(10)
        # of a constant is 0.2, EMA(20) of a constant is 100, so the
        # bands are 100 +/- 1.5*0.2 = 100.30 / 99.70.
        ind = indicators.add_indicators(_flat_frame(100))
        self.assertAlmostEqual(ind["kc_mid"].iloc[50], 100.0, places=6)
        self.assertAlmostEqual(ind["kc_upper"].iloc[50], 100.30, places=6)
        self.assertAlmostEqual(ind["kc_lower"].iloc[50], 99.70, places=6)
        self.assertAlmostEqual(ind["atr"].iloc[50], 0.2, places=6)

    def test_band_ordering_after_warmup(self):
        ind = indicators.add_indicators(_random_walk_frame())
        tail = ind.iloc[40:]
        self.assertTrue((tail["kc_upper"] > tail["kc_mid"]).all())
        self.assertTrue((tail["kc_mid"] > tail["kc_lower"]).all())

    def test_macd_hist_sign_follows_trend(self):
        up = indicators.add_indicators(_ramp_frame(direction=1))
        self.assertGreater(up["macd_hist"].iloc[-1], 0)
        dn = indicators.add_indicators(_ramp_frame(direction=-1))
        self.assertLess(dn["macd_hist"].iloc[-1], 0)
        flat = indicators.add_indicators(_flat_frame(100))
        self.assertAlmostEqual(flat["macd_hist"].iloc[-1], 0.0, places=9)

    def test_long_setup_fires_on_up_ramp_not_down(self):
        up = indicators.add_indicators(_ramp_frame(direction=1))
        self.assertGreater(int(up["long_setup"].sum()), 0)
        self.assertEqual(int(up["short_setup"].sum()), 0)
        dn = indicators.add_indicators(_ramp_frame(direction=-1))
        self.assertGreater(int(dn["short_setup"].sum()), 0)
        self.assertEqual(int(dn["long_setup"].sum()), 0)

    def test_breakout_is_transition_only(self):
        # After the first breakout bar, the close stays above the
        # upper band every bar, so no further long_break may fire.
        ind = indicators.add_indicators(_ramp_frame(direction=1))
        first = int(np.argmax(ind["long_break"].to_numpy()))
        self.assertTrue(ind["long_break"].iloc[first])
        self.assertEqual(int(ind["long_break"].iloc[first + 1:].sum()), 0)

    def test_no_setup_before_warmup(self):
        ind = indicators.add_indicators(_random_walk_frame())
        self.assertFalse(ind["long_setup"].iloc[:40].any())
        self.assertFalse(ind["short_setup"].iloc[:40].any())
        self.assertFalse(ind["long_break"].iloc[:40].any())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:1300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("long_setup", "short_setup", "long_break", "kc_upper", "macd_hist"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:1300].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, long_setup, short_setup, c, kc_upper, kc_lower, hist):
        n = len(c)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "kc_upper": kc_upper, "kc_lower": kc_lower, "macd_hist": hist,
            "long_setup": long_setup, "short_setup": short_setup,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_ramp_enters_long_exactly_once(self):
        sig = signals.add_signals(indicators.add_indicators(_ramp_frame(direction=1)))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_exit_long_on_close_back_inside_channel(self):
        # Long at bar 1; bar 2 closes above the band (hold), bar 3
        # closes below the upper band -> exit.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.zeros(4, dtype=bool),
            c=np.array([100.0, 106.0, 105.0, 103.0]),
            kc_upper=np.array([100.0, 100.0, 104.0, 104.0]),
            kc_lower=np.array([100.0, 100.0, 96.0, 96.0]),
            hist=np.array([0.0, 0.5, 0.5, 0.5]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_exit_long_on_hist_turning_negative(self):
        # Close stays above the upper band, but the histogram flips
        # negative -> exit anyway.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.zeros(4, dtype=bool),
            c=np.array([100.0, 106.0, 107.0, 108.0]),
            kc_upper=np.array([100.0, 100.0, 100.0, 100.0]),
            kc_lower=np.array([100.0, 100.0, 100.0, 100.0]),
            hist=np.array([0.0, 0.5, 0.5, -0.2]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_short_entry_and_exit_on_close_back_inside(self):
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.zeros(4, dtype=bool),
            short_setup=np.array([False, True, False, False]),
            c=np.array([100.0, 94.0, 95.0, 97.0]),
            kc_upper=np.array([100.0, 100.0, 104.0, 104.0]),
            kc_lower=np.array([100.0, 100.0, 96.0, 96.0]),
            hist=np.array([0.0, -0.5, -0.5, -0.5]),
        ))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertFalse(sig["short_exit"].iloc[2])
        self.assertTrue(sig["short_exit"].iloc[3])

    def test_opposite_setup_flips_position(self):
        # Long at bar 1; bar 3 is a short breakout (close below the
        # lower band, histogram negative) -> exit long + enter short.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, False, False]),
            short_setup=np.array([False, False, False, True]),
            c=np.array([100.0, 106.0, 105.0, 90.0]),
            kc_upper=np.array([100.0, 100.0, 100.0, 100.0]),
            kc_lower=np.array([100.0, 100.0, 100.0, 95.0]),
            hist=np.array([0.0, 0.5, 0.5, -0.5]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])

    def test_no_reentry_while_holding(self):
        # Setup repeats on bars 1-3 while long; only one entry.
        sig = signals.add_signals(self._signal_frame(
            long_setup=np.array([False, True, True, True]),
            short_setup=np.zeros(4, dtype=bool),
            c=np.array([100.0, 106.0, 107.0, 108.0]),
            kc_upper=np.array([100.0, 100.0, 100.0, 100.0]),
            kc_lower=np.array([100.0, 100.0, 100.0, 100.0]),
            hist=np.array([0.0, 0.5, 0.5, 0.5]),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 1)


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
        self.assertEqual(risk.WARMUP, 40)

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
