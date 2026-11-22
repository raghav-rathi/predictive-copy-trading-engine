"""Minervini Trend Template tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.minervini_trend_template import indicators, risk, signals


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


def _trend_frame(n=1500, up=True, seed=7):
    """Steady exponential trend: +0.2%/bar up, -0.2%/bar down."""
    g = 1.002 if up else 0.998
    c = 100.0 * g ** np.arange(n)
    return _frame_from_close(c, seed)


def _random_walk_frame(n=1500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("sma50", "sma150", "sma200", "sma200_slope720",
                    "trail_high", "trail_low", "rsi14", "donch_high20",
                    "donch_low20", "gate_long", "gate_short", "atr"):
            self.assertIn(col, ind.columns)

    def test_gate_long_true_in_steady_uptrend(self):
        ind = indicators.add_indicators(_trend_frame(up=True))
        # Late bars: every gate condition holds in a steady +0.2%/bar
        # rise (RSI ~100, SMAs stacked, price near trailing high and
        # far above the trailing low).
        self.assertTrue(bool(ind["gate_long"].iloc[-1]))
        self.assertFalse(bool(ind["gate_short"].iloc[-1]))

    def test_gate_short_true_in_steady_downtrend(self):
        ind = indicators.add_indicators(_trend_frame(up=False))
        self.assertTrue(bool(ind["gate_short"].iloc[-1]))
        self.assertFalse(bool(ind["gate_long"].iloc[-1]))

    def test_gate_long_false_when_price_below_sma200(self):
        # Flat then a sharp drop below all SMAs: no long gate.
        c = np.concatenate([np.full(1000, 100.0), np.full(500, 50.0)])
        ind = indicators.add_indicators(_frame_from_close(c))
        self.assertFalse(bool(ind["gate_long"].iloc[-1]))

    def test_gate_needs_rsi_above_55(self):
        # Sideways drift: RSI hovers near 50, gate must stay off even
        # if the SMAs happen to stack.
        rng = np.random.default_rng(3)
        c = 100 + np.cumsum(rng.normal(0, 0.05, 1500))
        ind = indicators.add_indicators(_frame_from_close(c))
        late = ind.iloc[-100:]
        self.assertTrue(((late["rsi14"] <= 55) | (~late["gate_long"])).all())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:1000]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("gate_long", "gate_short", "sma200_slope720"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:1000].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, n, gate_long, gate_short, c, sma50, dh, dl):
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "gate_long": gate_long, "gate_short": gate_short,
            "sma50": sma50, "donch_high20": dh, "donch_low20": dl,
        })

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_uptrend_breakout_enters_long(self):
        ind = indicators.add_indicators(_trend_frame(up=True))
        sig = signals.add_signals(ind)
        self.assertGreater(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_downtrend_breakdown_enters_short(self):
        ind = indicators.add_indicators(_trend_frame(up=False))
        sig = signals.add_signals(ind)
        self.assertGreater(int(sig["short_entry"].sum()), 0)
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_exit_on_close_below_sma50(self):
        # Long at bar 1 (gate + breakout), then close under SMA50.
        n = 4
        sig = signals.add_signals(self._signal_frame(
            n,
            gate_long=np.array([False, True, True, True]),
            gate_short=np.zeros(n, dtype=bool),
            c=np.array([100.0, 110.0, 109.0, 90.0]),
            sma50=np.array([100.0, 100.0, 100.0, 100.0]),
            dh=np.array([105.0, 105.0, 105.0, 105.0]),
            dl=np.array([95.0, 95.0, 95.0, 95.0]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertFalse(sig["long_exit"].iloc[2])
        self.assertTrue(sig["long_exit"].iloc[3])

    def test_no_entry_without_gate(self):
        # Breakout levels crossed but the gate is off: no entry.
        n = 3
        sig = signals.add_signals(self._signal_frame(
            n,
            gate_long=np.zeros(n, dtype=bool),
            gate_short=np.zeros(n, dtype=bool),
            c=np.array([100.0, 110.0, 120.0]),
            sma50=np.array([100.0, 100.0, 100.0]),
            dh=np.array([105.0, 105.0, 105.0]),
            dl=np.array([95.0, 95.0, 95.0]),
        ))
        self.assertEqual(int(sig["long_entry"].sum()), 0)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_opposite_breakout_flips_position(self):
        # Long at bar 1, short-gate breakdown at bar 3 -> flip.
        n = 4
        sig = signals.add_signals(self._signal_frame(
            n,
            gate_long=np.array([False, True, False, False]),
            gate_short=np.array([False, False, False, True]),
            c=np.array([100.0, 110.0, 108.0, 90.0]),
            sma50=np.array([100.0, 100.0, 100.0, 100.0]),
            dh=np.array([105.0, 105.0, 105.0, 105.0]),
            dl=np.array([95.0, 95.0, 95.0, 95.0]),
        ))
        self.assertTrue(sig["long_entry"].iloc[1])
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertTrue(sig["short_entry"].iloc[3])


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 6.0)
        self.assertEqual(r.trail_atr_mult, 8.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 720)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 960)

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
