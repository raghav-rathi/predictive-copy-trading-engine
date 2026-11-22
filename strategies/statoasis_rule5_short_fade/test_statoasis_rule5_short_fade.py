"""StatOasis Rule 5 tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.statoasis_rule5_short_fade import indicators, risk, signals
from strategies.statoasis_rule5_short_fade.indicators import williams_r


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _fade_frame():
    """Long decline (SMA100 falling) then a sharp 20-bar rally.

    The rally's closes sit near the 14-bar highs (Williams %R >
    -10) with RSI(14) > 70, while SMA(100) is still falling on
    the weight of the decline — the Rule 5 short setup.
    """
    down = np.linspace(200.0, 100.0, 150)
    up = np.linspace(100.0, 145.0, 20)
    return _frame_from_close(np.concatenate([down, up]))


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("rsi14", "willr14", "sma100", "sma100_falling",
                    "sma100_rising", "short_setup", "long_setup", "atr"):
            self.assertIn(col, ind.columns)

    def test_williams_r_bounds(self):
        ind = indicators.add_indicators(_random_walk_frame())
        wr = ind["willr14"].dropna()
        self.assertTrue(((wr >= -100.0) & (wr <= 0.0)).all())

    def test_williams_r_formula(self):
        # 14 bars, high 110, low 90, close 109 -> (110-109)/20*-100 = -5.
        n = 14
        c = np.linspace(100.0, 109.0, n)
        df = pd.DataFrame({
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
            "o": c, "h": np.full(n, 110.0), "l": np.full(n, 90.0),
            "c": c, "v": np.full(n, 100.0),
        })
        wr = williams_r(df["h"], df["l"], df["c"], 14)
        self.assertAlmostEqual(float(wr.iloc[-1]), -5.0, places=6)

    def test_short_setup_fires_after_decline_then_rally(self):
        ind = indicators.add_indicators(_fade_frame())
        self.assertTrue(bool(ind["short_setup"].any()))
        # And it fires while SMA(100) is falling, by construction.
        fires = np.where(ind["short_setup"])[0]
        self.assertTrue(bool(ind["sma100_falling"].iloc[fires[0]]))

    def test_all_three_conditions_required(self):
        # RSI > 70 alone (SMA100 rising, %R middling) must not fire.
        c = 100.0 * 1.005 ** np.arange(300)
        ind = indicators.add_indicators(_frame_from_close(c))
        late = ind.iloc[-50:]
        self.assertTrue(bool((late["rsi14"] > 70).any()))
        self.assertFalse(bool(late["short_setup"].any()))

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("short_setup", "long_setup", "willr14"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:200].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, short_setup, long_setup):
        n = len(short_setup)
        c = np.full(n, 100.0)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "short_setup": short_setup, "long_setup": long_setup,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_fixed_five_bar_hold_short(self):
        # Short setup at bar 1 only; exit must land exactly 5 bars later.
        ss = np.zeros(10, dtype=bool)
        ss[1] = True
        sig = signals.add_signals(self._signal_frame(ss, np.zeros(10, dtype=bool)))
        self.assertTrue(sig["short_entry"].iloc[1])
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertTrue(sig["short_exit"].iloc[6])
        self.assertEqual(int(sig["short_exit"].sum()), 1)

    def test_fixed_five_bar_hold_long(self):
        ls = np.zeros(10, dtype=bool)
        ls[2] = True
        sig = signals.add_signals(self._signal_frame(np.zeros(10, dtype=bool), ls))
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[7])
        self.assertEqual(int(sig["long_exit"].sum()), 1)

    def test_no_new_entry_while_holding(self):
        # Setup fires on every bar: entries must still be 5 bars apart.
        ss = np.ones(12, dtype=bool)
        sig = signals.add_signals(self._signal_frame(ss, np.zeros(12, dtype=bool)))
        entries = np.where(sig["short_entry"])[0]
        self.assertTrue(len(entries) >= 2)
        self.assertTrue((np.diff(entries) >= 5).all())

    def test_end_to_end_fade_frame_trades(self):
        sig = signals.add_signals(indicators.add_indicators(_fade_frame()))
        self.assertGreater(int(sig["short_entry"].sum()), 0)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 5)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 120)

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
