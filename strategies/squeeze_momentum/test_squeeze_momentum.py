"""LazyBear Squeeze Momentum tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.squeeze_momentum import indicators, risk, signals


def _frame_from_close(c, seed=7, hl=0.02):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + hl
    l = np.minimum(o, c) - hl
    v = np.full(n, 100.0)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _squeeze_then_expand():
    """150 bars of flat low-vol closes (squeeze ON), then a sharp
    15-bar rise. Release fires exactly once, on bar 150."""
    rng = np.random.default_rng(5)
    c1 = 100 + rng.normal(0, 0.05, 150).cumsum() * 0.1
    c1 = np.clip(c1, 99.5, 100.5)
    c2 = np.linspace(100.5, 115, 15)
    return _frame_from_close(np.concatenate([c1, c2]))


def _signal_frame(c, release, mom_rising, mom_falling, mom,
                  mom_low, mom_high, ema100):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": c, "h": c, "l": c, "c": np.asarray(c, dtype=float),
        "v": np.full(n, 100.0),
        "squeeze_release": np.asarray(release, dtype=bool),
        "mom_rising": np.asarray(mom_rising, dtype=bool),
        "mom_falling": np.asarray(mom_falling, dtype=bool),
        "mom": np.asarray(mom, dtype=float),
        "mom_100_low": np.asarray(mom_low, dtype=bool),
        "mom_100_high": np.asarray(mom_high, dtype=bool),
        "ema100": np.asarray(ema100, dtype=float),
    })


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("bb_mid", "bb_upper", "bb_lower", "kc_mid", "kc_upper",
                    "kc_lower", "squeeze", "squeeze_release", "mom",
                    "mom_rising", "mom_falling", "mom_100_low",
                    "mom_100_high", "ema100", "atr"):
            self.assertIn(col, ind.columns)

    def test_squeeze_on_during_flat(self):
        ind = indicators.add_indicators(_squeeze_then_expand())
        # Flat low-vol stretch: BB inside KC on all of bars 100-149.
        self.assertTrue(ind["squeeze"].iloc[100:150].all())

    def test_release_fires_once_on_expansion(self):
        ind = indicators.add_indicators(_squeeze_then_expand())
        fires = np.where(ind["squeeze_release"])[0]
        self.assertEqual(len(fires), 1)
        self.assertEqual(int(fires[0]), 150)

    def test_momentum_rises_on_expansion(self):
        ind = indicators.add_indicators(_squeeze_then_expand())
        self.assertGreater(float(ind["mom"].iloc[155]),
                           float(ind["mom"].iloc[150]))
        self.assertTrue(ind["mom_rising"].iloc[151:160].all())

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:300]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("squeeze", "squeeze_release", "mom", "mom_100_low"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:300].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _long_setup_frame(self):
        # Release at bar 2 with rising positive mom at its 100-bar
        # low, close above EMA100 and above the prior close.
        c = [100.0, 101.0, 102.0, 103.0, 103.0]
        return _signal_frame(
            c,
            release=[False, False, True, False, False],
            mom_rising=[False, False, True, False, False],
            mom_falling=[False, False, False, True, False],
            mom=[0.1, 0.2, 0.3, 0.2, 0.2],
            mom_low=[False, False, True, False, False],
            mom_high=[False] * 5,
            ema100=[99.0] * 5,
        )

    def test_signal_columns_boolean_no_nan(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_full_setup(self):
        sig = signals.add_signals(self._long_setup_frame())
        self.assertTrue(sig["long_entry"].iloc[2])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_short_entry_mirror(self):
        c = [100.0, 99.0, 98.0, 97.0, 97.0]
        df = _signal_frame(
            c,
            release=[False, False, True, False, False],
            mom_rising=[False, False, False, True, False],
            mom_falling=[False, False, True, False, False],
            mom=[-0.1, -0.2, -0.3, -0.2, -0.2],
            mom_low=[False] * 5,
            mom_high=[False, False, True, False, False],
            ema100=[101.0] * 5,
        )
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_entry"].iloc[2])
        self.assertEqual(int(sig["short_entry"].sum()), 1)

    def test_missing_one_condition_blocks_entry(self):
        # Same as the long setup but momentum NOT at its 100-bar low.
        df = self._long_setup_frame()
        df["mom_100_low"] = False
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())
        # And with momentum negative instead of positive.
        df = self._long_setup_frame()
        df["mom"] = [-0.1, -0.2, -0.3, -0.2, -0.2]
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())
        # And with no release.
        df = self._long_setup_frame()
        df["squeeze_release"] = False
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())

    def test_exit_on_first_momentum_downtick(self):
        sig = signals.add_signals(self._long_setup_frame())
        # Long entered at bar 2; momentum falls at bar 3 -> exit.
        self.assertTrue(sig["long_exit"].iloc[3])
        self.assertFalse(sig["long_exit"].iloc[2])

    def test_no_lookahead(self):
        df = _random_walk_frame()
        short = df.iloc[:300]
        sig_full = signals.add_signals(indicators.add_indicators(df))
        sig_short = signals.add_signals(indicators.add_indicators(short))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            pd.testing.assert_series_equal(
                sig_full[col].iloc[:300].reset_index(drop=True),
                sig_short[col].reset_index(drop=True),
                check_names=False,
            )


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
        self.assertEqual(risk.WARMUP, 110)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(
            indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
