"""Connors RSI(2) pullback tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.connors_rsi import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _ind_frame(n=12, sma=100.0, c=105.0, rsi_vals=None):
    """Hand-built indicator frame: override rsi2 / trend columns directly."""
    idx = pd.RangeIndex(n)
    rsi2 = pd.Series(rsi_vals if rsi_vals is not None else [50.0] * n, index=idx)
    df = pd.DataFrame(
        {
            "t": (1_700_000_000_000 + np.arange(n) * 3_600_000),
            "o": c, "h": c + 1, "l": c - 1, "c": c, "v": 100.0,
            "rsi2": rsi2,
            "sma200": sma, "sma50": sma, "atr": 1.0,
        }
    )
    df["decl3"] = indicators.streak_down(df["rsi2"], 3)
    df["rise3"] = indicators.streak_up(df["rsi2"], 3)
    return df


def _uptrend_then_pullback(n=400, seed=7):
    """Steady uptrend then a sharp 5-bar drop (real indicator path)."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:395] = 100 + 0.5 * np.arange(395) + rng.normal(0, 0.15, 395)
    c[395:] = c[394] - 5.0 * np.arange(1, 6) + rng.normal(0, 0.1, 5)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + np.abs(rng.normal(0, 0.1, n)) + 0.3
    l = np.minimum(o, c) - np.abs(rng.normal(0, 0.1, n)) - 0.3
    return _ohlcv(o, h, l, c)


class TestStreakDetectors(unittest.TestCase):
    def test_decline_streak_on_hand_built_series(self):
        s = pd.Series([50.0, 45.0, 40.0, 35.0, 38.0, 30.0, 25.0, 20.0, 25.0])
        got = indicators.streak_down(s, 3).tolist()
        # True only where s[i] < s[i-1] < s[i-2] < s[i-3]
        self.assertEqual(got, [False, False, False, True, False, False, False, True, False])

    def test_rise_streak_on_hand_built_series(self):
        s = pd.Series([20.0, 30.0, 40.0, 50.0, 45.0, 60.0, 70.0, 80.0, 75.0])
        got = indicators.streak_up(s, 3).tolist()
        self.assertEqual(got, [False, False, False, True, False, False, False, True, False])

    def test_streak_ignores_nan_warmup(self):
        s = pd.Series([np.nan, np.nan, 10.0, 9.0, 8.0, 7.0])
        self.assertFalse(indicators.streak_down(s, 3).iloc[2])
        self.assertTrue(indicators.streak_down(s, 3).iloc[5])


class TestEntries(unittest.TestCase):
    def test_long_entry_requires_all_three_filters(self):
        rsi_vals = [50.0, 40.0, 30.0, 20.0, 15.0, 12.0, 9.0, 5.0, 30.0, 50.0, 50.0, 50.0]
        df = signals.add_signals(_ind_frame(c=105.0, sma=100.0, rsi_vals=rsi_vals))
        # rows 6 and 7: above trend, rsi2<10, 3-bar decline -> entry
        self.assertTrue(df["long_entry"].iloc[6])
        self.assertTrue(df["long_entry"].iloc[7])

        # filter 1 removed: below the 200MA -> no entry
        df2 = signals.add_signals(_ind_frame(c=95.0, sma=100.0, rsi_vals=rsi_vals))
        self.assertFalse(df2["long_entry"].any())

        # filter 2 removed: rsi2 >= 10 -> no entry
        df3 = signals.add_signals(
            _ind_frame(c=105.0, sma=100.0, rsi_vals=[v + 6.0 for v in rsi_vals])
        )
        self.assertFalse(df3["long_entry"].any())

        # filter 3 removed: streak broken (flat bar inside the window) -> no entry
        broken = [50.0, 40.0, 30.0, 20.0, 15.0, 15.0, 9.0, 5.0, 30.0, 50.0, 50.0, 50.0]
        df4 = signals.add_signals(_ind_frame(c=105.0, sma=100.0, rsi_vals=broken))
        self.assertFalse(df4["long_entry"].iloc[7])
        self.assertFalse(df4["long_entry"].iloc[6])

    def test_short_entry_mirror_requires_all_three_filters(self):
        rsi_vals = [50.0, 60.0, 70.0, 80.0, 85.0, 88.0, 91.0, 95.0, 70.0, 50.0, 50.0, 50.0]
        df = signals.add_signals(_ind_frame(c=95.0, sma=100.0, rsi_vals=rsi_vals))
        self.assertTrue(df["short_entry"].iloc[6])
        self.assertTrue(df["short_entry"].iloc[7])
        self.assertFalse(df["long_entry"].any())
        # above the 200MA -> no short entry
        df2 = signals.add_signals(_ind_frame(c=105.0, sma=100.0, rsi_vals=rsi_vals))
        self.assertFalse(df2["short_entry"].any())
        # rsi2 <= 90 -> no short entry
        df3 = signals.add_signals(
            _ind_frame(c=95.0, sma=100.0, rsi_vals=[v - 6.0 for v in rsi_vals])
        )
        self.assertFalse(df3["short_entry"].any())

    def test_entry_fires_on_real_price_path(self):
        df = signals.add_signals(indicators.add_indicators(_uptrend_then_pullback()))
        # drop bars are indices 395..399; at least one long_entry must fire
        self.assertGreater(int(df.loc[395:399, "long_entry"].sum()), 0)
        # every long entry sits above the 200MA with rsi2 < 10
        for i in df.index[df["long_entry"]]:
            self.assertGreater(df["c"].iloc[i], df["sma200"].iloc[i])
            self.assertLess(df["rsi2"].iloc[i], 10.0)


class TestExits(unittest.TestCase):
    def test_long_exit_fires_when_rsi2_over_70(self):
        rsi_vals = [50.0, 60.0, 65.0, 72.0, 80.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
        df = signals.add_signals(_ind_frame(c=105.0, sma=100.0, rsi_vals=rsi_vals))
        self.assertTrue(df["long_exit"].iloc[3])
        self.assertTrue(df["long_exit"].iloc[4])
        self.assertFalse(df["long_exit"].iloc[5])

    def test_long_exit_fires_when_close_below_sma50(self):
        rsi_vals = [50.0] * 12
        df = signals.add_signals(_ind_frame(c=105.0, sma=100.0, rsi_vals=rsi_vals))
        # sma200 == sma50 == 100; c=105 is above both -> no exit
        self.assertFalse(df["long_exit"].any())
        # force c below sma50 only: keep c > sma200, sma50 higher
        df2 = _ind_frame(c=105.0, sma=100.0, rsi_vals=rsi_vals)
        df2["sma50"] = 110.0
        df2 = signals.add_signals(df2)
        self.assertTrue(df2["long_exit"].all())

    def test_short_exit_fires_when_rsi2_under_30(self):
        rsi_vals = [50.0, 40.0, 35.0, 28.0, 20.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
        df = signals.add_signals(_ind_frame(c=95.0, sma=100.0, rsi_vals=rsi_vals))
        self.assertTrue(df["short_exit"].iloc[3])
        self.assertTrue(df["short_exit"].iloc[4])
        self.assertFalse(df["short_exit"].iloc[5])


class TestConventions(unittest.TestCase):
    def test_no_lookahead_truncation(self):
        full = _uptrend_then_pullback()
        ind_full = indicators.add_indicators(full)
        for i in (300, 390):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("rsi2", "sma200", "sma50", "atr"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9, (col, i)
                )
            for col in ("decl3", "rise3"):
                self.assertEqual(
                    ind_full[col].iloc[i], ind_tr[col].iloc[i], (col, i)
                )

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_uptrend_then_pullback()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})
            self.assertEqual(str(df[col].dtype), "bool")

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 30)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertGreaterEqual(risk.WARMUP, 220)


if __name__ == "__main__":
    unittest.main()
