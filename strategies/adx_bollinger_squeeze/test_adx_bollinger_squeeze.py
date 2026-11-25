"""ADX Bollinger squeeze tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.adx_bollinger_squeeze import indicators, risk, signals


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _handbuilt_frame(n=30, squeeze_at=(), breakout=None, adx=25.0):
    """Frame with the indicator columns set directly, for signal-logic
    tests. breakout: (bar, price) — the close jumps to `price` there
    (and stays) so it crosses the band on that bar."""
    c = np.full(n, 100.0)
    if breakout is not None:
        bar, price = breakout
        c[bar:] = price
    df = pd.DataFrame(
        {
            "c": c,
            "bb_upper": np.full(n, 102.0),
            "bb_lower": np.full(n, 98.0),
            "adx": np.full(n, float(adx)),
            "squeeze": np.zeros(n, dtype=bool),
        }
    )
    for b in squeeze_at:
        df.loc[b, "squeeze"] = True
    return df


class TestAdxBollingerSqueeze(unittest.TestCase):
    def test_bandwidth_formula(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        valid = df["bb_mid"].notna() & (df["bb_mid"] != 0)
        expect = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"]
        self.assertTrue(bool(np.allclose(df.loc[valid, "bandwidth"], expect[valid])))

    def test_squeeze_is_bandwidth_at_20bar_min(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        rolling_min = df["bandwidth"].rolling(20, min_periods=20).min()
        expect = (df["bandwidth"] == rolling_min).fillna(False)
        self.assertTrue(bool((df["squeeze"] == expect).all()))
        self.assertTrue(bool(df["squeeze"].iloc[40:].any()))

    def test_flat_series_squeezes_after_20_bars(self):
        # flat: sd = 0, bandwidth = 0, which is its own 20-bar minimum.
        # Bandwidth itself is only defined from bar 19 (BB needs 20
        # closes), so the rolling 20-bar minimum of bandwidth needs
        # 20 valid values and first exists at bar 38.
        df = indicators.add_indicators(_df_from_c(np.full(200, 100.0)))
        self.assertTrue(bool(df["squeeze"].iloc[38:].all()))
        self.assertFalse(bool(df["squeeze"].iloc[:38].any()))

    def test_long_entry_on_squeeze_breakout_with_adx(self):
        sig = signals.add_signals(_handbuilt_frame(squeeze_at=(10,), breakout=(11, 103.0)))
        self.assertTrue(bool(sig["long_entry"].iloc[11]))
        self.assertFalse(bool(sig["long_entry"].iloc[:11].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_entry_on_squeeze_breakdown_with_adx(self):
        sig = signals.add_signals(_handbuilt_frame(squeeze_at=(10,), breakout=(11, 97.0)))
        self.assertTrue(bool(sig["short_entry"].iloc[11]))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_entry_when_adx_too_weak(self):
        sig = signals.add_signals(
            _handbuilt_frame(squeeze_at=(10,), breakout=(11, 103.0), adx=18.0)
        )
        self.assertFalse(bool(sig["long_entry"].any()))
        sig2 = signals.add_signals(
            _handbuilt_frame(squeeze_at=(10,), breakout=(11, 97.0), adx=20.0)
        )
        self.assertFalse(bool(sig2["short_entry"].any()))

    def test_no_entry_without_recent_squeeze(self):
        # squeeze at bar 10, breakout at bar 11: inside the 3-bar window
        sig = signals.add_signals(_handbuilt_frame(squeeze_at=(10,), breakout=(11, 103.0)))
        self.assertTrue(bool(sig["long_entry"].iloc[11]))
        # squeeze at bar 10, breakout at bar 12: still inside (bars 10,11,12)
        sig = signals.add_signals(_handbuilt_frame(squeeze_at=(10,), breakout=(12, 103.0)))
        self.assertTrue(bool(sig["long_entry"].iloc[12]))
        # squeeze at bar 10, breakout at bar 13: outside (only 11,12,13 count)
        sig = signals.add_signals(_handbuilt_frame(squeeze_at=(10,), breakout=(13, 103.0)))
        self.assertFalse(bool(sig["long_entry"].any()))
        # no squeeze at all: no entry even on a band cross
        sig = signals.add_signals(_handbuilt_frame(breakout=(11, 103.0)))
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_long_exit_on_close_back_inside_band(self):
        df = _handbuilt_frame(squeeze_at=(10,), breakout=(11, 103.0))
        df.loc[13:, "c"] = 101.0  # back inside the bands
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_exit"].iloc[13]))
        self.assertFalse(bool(sig["long_exit"].iloc[:13].any()))

    def test_exit_on_adx_fading_below_15(self):
        df = _handbuilt_frame(squeeze_at=(10,), breakout=(11, 103.0))
        df.loc[15:, "adx"] = 10.0  # momentum fades while price stays out
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_exit"].iloc[15]))
        self.assertFalse(bool(sig["long_exit"].iloc[:15].any()))

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("bb_mid", "bb_upper", "bb_lower", "bandwidth", "adx"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("squeeze", "long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("bb_mid", "bb_upper", "bb_lower", "bandwidth", "adx"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            for col in ("squeeze",):
                self.assertEqual(bool(ind_full[col].iloc[j]), bool(ind_tr[col].iloc[j]), (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.adx_bollinger_squeeze as mod

        self.assertEqual(mod.SPEC.slug, "adx_bollinger_squeeze")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 50)


if __name__ == "__main__":
    unittest.main()
