"""Elder Ray (Bull/Bear Power) tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.elder_ray import indicators, risk, signals
from strategies import base as B


def _frame_from_close(c, h=None, l=None, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    if h is None:
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    if l is None:
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _frame(n=500, seed=7, drift=0.001, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


def _flat(n):
    return np.full(n, 100.0)


def _expected_signals(ind):
    """Direct re-derivation of the strategy rules for wiring checks."""
    ema13 = ind["ema13"]
    bull, bear = ind["bull_power"], ind["bear_power"]
    zero_bear = pd.Series(0.0, index=bear.index)
    zero_bull = pd.Series(0.0, index=bull.index)
    ema_up = (ema13 > ema13.shift(1)).fillna(False)
    ema_down = (ema13 < ema13.shift(1)).fillna(False)
    bear_rising = (bear > bear.shift(1)).fillna(False)
    bull_falling = (bull < bull.shift(1)).fillna(False)
    return {
        "long_entry": (ema_up & (bear < 0.0) & bear_rising).astype(bool),
        "short_entry": (ema_down & (bull > 0.0) & bull_falling).astype(bool),
        "long_exit": (B.crossed_above(bear, zero_bear).fillna(False) | ema_down).astype(bool),
        "short_exit": (B.crossed_below(bull, zero_bull).fillna(False) | ema_up).astype(bool),
    }


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_frame())
        for col in ("ema13", "ema13_slope", "bull_power", "bear_power", "atr"):
            self.assertIn(col, ind.columns)

    def test_ema13_matches_base_ema(self):
        df = _frame()
        ind = indicators.add_indicators(df)
        pd.testing.assert_series_equal(
            ind["ema13"], B.ema(df["c"], 13), check_names=False)

    def test_bull_bear_formulas_hand_check(self):
        # Flat close 100: ewm(adjust=False) of a constant is the constant
        # itself, so bull_power = 101-100 = 1, bear_power = 99-100 = -1.
        df = _frame_from_close(_flat(40), h=np.full(40, 101.0), l=np.full(40, 99.0))
        ind = indicators.add_indicators(df).iloc[20:]  # past warmup
        self.assertTrue(np.allclose(ind["bull_power"], 1.0),
                        f"bull_power on flat series: {ind['bull_power'].unique()}")
        self.assertTrue(np.allclose(ind["bear_power"], -1.0),
                        f"bear_power on flat series: {ind['bear_power'].unique()}")
        self.assertTrue((ind["ema13_slope"] == 0.0).all(), "slope must be 0 on flat series")

    def test_nan_warmup_behavior(self):
        # min_periods=13 -> first 12 bars have NaN ema13, hence NaN powers.
        df = _frame(n=100)
        ind = indicators.add_indicators(df)
        self.assertTrue(ind["ema13"].iloc[:12].isna().all())
        self.assertTrue(ind["bull_power"].iloc[:12].isna().all())
        self.assertTrue(ind["bear_power"].iloc[:12].isna().all())
        self.assertFalse(ind["ema13"].iloc[13:].isna().any())
        # signals still fully defined (all False) over the NaN region
        sig = signals.add_signals(ind)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].iloc[:13].any(), col)

    def test_slope_column_values(self):
        rising = np.arange(100, dtype=float) + 100.0
        ind = indicators.add_indicators(_frame_from_close(rising)).dropna()
        self.assertTrue((ind["ema13_slope"] == 1.0).all(), "rising close -> slope +1")
        falling = 200.0 - np.arange(100, dtype=float)
        ind = indicators.add_indicators(_frame_from_close(falling)).dropna()
        self.assertTrue((ind["ema13_slope"] == -1.0).all(), "falling close -> slope -1")
        ind = indicators.add_indicators(_frame_from_close(rising))
        self.assertTrue(ind["ema13_slope"].iloc[:12].isna().all(), "slope NaN in warmup")

    def test_does_not_mutate_input(self):
        df = _frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestSignals(unittest.TestCase):
    def test_columns_boolean_no_nan(self):
        sig = signals.add_signals(indicators.add_indicators(_frame()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, sig.columns)
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_wiring_matches_rules(self):
        # Full re-derivation: signals must equal the documented rules exactly.
        for seed in (1, 2, 3):
            ind = indicators.add_indicators(_frame(seed=seed))
            sig = signals.add_signals(ind)
            expect = _expected_signals(ind)
            for col, want in expect.items():
                pd.testing.assert_series_equal(
                    sig[col], want, check_names=False,
                    obj=f"{col} seed={seed}")

    def test_flat_series_no_signals(self):
        # Flat: slope 0 everywhere -> no entries; powers never cross 0 -> no exits.
        df = _frame_from_close(_flat(60), h=np.full(60, 101.0), l=np.full(60, 99.0))
        sig = signals.add_signals(indicators.add_indicators(df))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(sig[col].sum(), 0, col)

    def _dip_series(self):
        # Steady uptrend, then two dip bars whose lows undershoot the
        # rising EMA; the second dip is shallower -> bear_power rises
        # while < 0. Levels are anchored to the EMA itself so the
        # construction is robust to ewm seeding.
        n = 45
        c = 100.0 + 0.4 * np.arange(n)
        c = c.copy()
        c[40] = 100.0 + 0.4 * 40 - 1.0
        c[41] = 100.0 + 0.4 * 41 - 0.7
        ema = B.ema(_frame_from_close(c, h=c + 0.3, l=c - 0.3)["c"], 13)
        h = c + 0.3
        l = c - 0.3
        h[40] = c[40] + 0.3
        h[41] = c[41] + 0.3
        l[40] = ema.iloc[39] - 1.5   # deep undershoot of the rising EMA
        l[41] = ema.iloc[40] - 0.6   # shallower undershoot -> bear rises
        return _frame_from_close(c, h=h, l=l)

    def test_long_entry_fires_on_dip_recovery(self):
        df = self._dip_series()
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        entries = sig["long_entry"]
        self.assertGreater(entries.sum(), 0, "expected at least one long entry on the easing dip")
        self.assertEqual(entries.iloc[:40].sum(), 0,
                         "no long entries during the clean uptrend (bear_power > 0)")
        # Every firing bar must satisfy the three rule components.
        for i in entries[entries].index:
            self.assertGreater(ind["ema13"].iloc[i], ind["ema13"].iloc[i - 1],
                               f"bar {i}: EMA13 must be rising")
            self.assertLess(ind["bear_power"].iloc[i], 0.0,
                            f"bar {i}: bear_power must be < 0")
            self.assertGreater(ind["bear_power"].iloc[i], ind["bear_power"].iloc[i - 1],
                               f"bar {i}: bear_power must be rising")

    def test_long_entry_requires_bear_rising(self):
        # Same setup but the second dip is DEEPER -> bear_power falling,
        # so the entry must NOT fire on the deepening-dip bar.
        n = 45
        c = 100.0 + 0.4 * np.arange(n)
        c = c.copy()
        c[40] = 100.0 + 0.4 * 40 - 1.0
        c[41] = 100.0 + 0.4 * 41 - 0.9
        ema = B.ema(_frame_from_close(c, h=c + 0.3, l=c - 0.3)["c"], 13)
        h = c + 0.3
        l = c - 0.3
        l[40] = ema.iloc[39] - 1.5
        l[41] = ema.iloc[40] - 2.2   # deeper undershoot -> bears strengthen
        df = _frame_from_close(c, h=h, l=l)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        bear = ind["bear_power"]
        self.assertLess(bear.iloc[41], 0.0, "sanity: bar 41 must be a real dip")
        self.assertLess(bear.iloc[41], bear.iloc[40], "sanity: bears must be strengthening")
        self.assertGreater(ind["ema13"].iloc[41], ind["ema13"].iloc[40],
                           "sanity: EMA must still be rising")
        self.assertFalse(sig["long_entry"].iloc[41],
                         "entry must be withheld while bears strengthen")

    def _rip_series(self):
        # Steady downtrend, then two rip bars whose highs overshoot the
        # falling EMA; the second rip is shallower -> bull_power falls
        # while > 0. Highs anchored to the EMA itself for robustness.
        n = 45
        c = 140.0 - 0.4 * np.arange(n)
        c = c.copy()
        c[40] = 140.0 - 0.4 * 40 + 1.0
        c[41] = 140.0 - 0.4 * 41 + 1.3
        ema = B.ema(_frame_from_close(c, h=c + 0.3, l=c - 0.3)["c"], 13)
        h = c + 0.3
        l = c - 0.3
        l[40] = c[40] - 0.3
        l[41] = c[41] - 0.3
        h[40] = ema.iloc[39] + 1.5   # strong overshoot of the falling EMA
        h[41] = ema.iloc[40] + 0.6   # shallower overshoot -> bull falls
        return _frame_from_close(c, h=h, l=l)

    def test_short_entry_mirror(self):
        df = self._rip_series()
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        entries = sig["short_entry"]
        self.assertGreater(entries.sum(), 0, "expected at least one short entry on the fading rip")
        self.assertEqual(entries.iloc[:40].sum(), 0,
                         "no short entries during the clean downtrend (bull_power < 0)")
        for i in entries[entries].index:
            self.assertLess(ind["ema13"].iloc[i], ind["ema13"].iloc[i - 1],
                            f"bar {i}: EMA13 must be falling")
            self.assertGreater(ind["bull_power"].iloc[i], 0.0,
                               f"bar {i}: bull_power must be > 0")
            self.assertLess(ind["bull_power"].iloc[i], ind["bull_power"].iloc[i - 1],
                            f"bar {i}: bull_power must be falling")

    def test_long_exit_on_bear_exhaustion(self):
        # Flat grind (bear = -1), then a jump bar whose low clears the EMA:
        # bear_power crosses above 0 -> long_exit.
        c = np.concatenate([_flat(40), [110.0] * 5])
        h = np.concatenate([np.full(40, 101.0), np.full(5, 111.0)])
        l = np.concatenate([np.full(40, 99.0), np.full(5, 109.0)])
        df = _frame_from_close(c, h=h, l=l)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        self.assertLess(ind["bear_power"].iloc[39], 0.0)
        self.assertGreater(ind["bear_power"].iloc[40], 0.0)
        self.assertTrue(sig["long_exit"].iloc[40],
                        "bear_power crossing above 0 must exit the long")

    def test_long_exit_on_slope_down(self):
        # Rise then fall: EMA slope turns down while bear_power is still <= 0
        # (proves the slope-down OR-branch, not the exhaustion branch).
        c = np.concatenate([100.0 + 0.5 * np.arange(30),
                            115.0 - 2.0 * np.arange(1, 21)])
        df = _frame_from_close(c)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        ema_down = ind["ema13"] < ind["ema13"].shift(1)
        slope_only = sig["long_exit"] & ema_down.fillna(False) & (ind["bear_power"] <= 0.0)
        self.assertTrue(slope_only.any(),
                        "long_exit must fire on slope-down even with bear_power <= 0")

    def test_short_exit_on_bull_exhaustion(self):
        # Downtrend grind (bull < 0), then a collapse bar after a rip:
        # bull_power crosses below 0 -> short_exit. Build via rip then drop.
        c = 140.0 - 0.4 * np.arange(45)
        h = c + 0.3
        l = c - 0.3
        c = c.copy(); h = h.copy(); l = l.copy()
        c[40] = 140.0 - 0.4 * 40 + 2.0
        h[40] = c[40] + 3.0          # rip overshoot -> bull_power > 0
        l[40] = c[40] - 0.3
        c[41] = 140.0 - 0.4 * 41 + 0.5
        h[41] = c[41] + 0.3          # collapse -> bull_power < 0
        l[41] = c[41] - 0.3
        df = _frame_from_close(c, h=h, l=l)
        ind = indicators.add_indicators(df)
        sig = signals.add_signals(ind)
        self.assertGreater(ind["bull_power"].iloc[40], 0.0, "sanity: rip bar bull > 0")
        self.assertLess(ind["bull_power"].iloc[41], 0.0, "sanity: collapse bar bull < 0")
        self.assertTrue(sig["short_exit"].iloc[41],
                        "bull_power crossing below 0 must exit the short")

    def test_no_lookahead(self):
        df = _frame(n=800, seed=11)
        full = signals.add_signals(indicators.add_indicators(df))
        j = 420
        trunc = signals.add_signals(indicators.add_indicators(df.iloc[: j + 1]))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(bool(full[col].iloc[j]), bool(trunc[col].iloc[j]),
                             f"{col}: signal at bar {j} changed with future data")


class TestRiskAndConfig(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 1.5)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_module_constants(self):
        self.assertEqual(indicators.EMA_N, 13, "Elder's EMA(13) is fixed a priori")


if __name__ == "__main__":
    unittest.main()
