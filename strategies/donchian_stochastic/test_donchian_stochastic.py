"""Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.donchian_stochastic import indicators, risk, signals


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

def _df_custom(rows):
    # rows: explicit (o, h, l, c) tuples, hourly bars.
    a = np.array(rows, float)
    n = len(a)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": a[:, 0], "h": a[:, 1], "l": a[:, 2], "c": a[:, 3],
         "v": np.full(n, 100.0)}
    )


def _wick_long_df():
    # Flat 100 (bars 0-39), dip to 96 (40-42), then a breakout bar
    # with a tall upper wick: close 120 crosses the prior 20-bar
    # high (114) while %K stays at 61.7 (below 80) and above %D
    # (28.0). Long fires at bar 44. Flat 120 follows, then a drop
    # to 110 at bar 55 (Turtle exit).
    rows = [(100, 100.2, 99.8, 100)] * 40
    for cv in (98, 97, 96):
        rows.append((cv, cv + 0.2, cv - 0.2, cv))
    rows.append((99, 114, 98.8, 99))
    rows.append((120, 135, 119.8, 120))
    rows += [(120, 120.2, 119.8, 120)] * 10
    rows.append((110, 110.2, 109.8, 110))
    rows += [(110, 110.2, 109.8, 110)] * 10
    return _df_custom(rows)


def _wick_short_df():
    # Steady 1/bar rise 100..139 (bars 0-39), then a breakdown bar
    # with a tall lower wick: close 115 crosses below the prior
    # 20-bar low (119.8) while %K is 38.3 (above 20) and below %D
    # (78.4). Short fires at bar 40.
    rows = []
    for i in range(40):
        cv = 100 + i
        rows.append((cv, cv + 0.2, cv - 0.2, cv))
    rows.append((139, 139.2, 100, 115))
    rows += [(115, 115.2, 114.8, 115)] * 10
    return _df_custom(rows)


def _manual_ds(n=30, cval=100.0, k=60.0, d=50.0,
               high20=100.0, low20=100.0, high10=100.0, low10=100.0):
    # Minimal frame with the indicator columns set directly, so the
    # signal logic can be tested in isolation from the indicators.
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": np.full(n, cval), "h": np.full(n, cval),
        "l": np.full(n, cval), "c": np.full(n, cval),
        "v": np.full(n, 100.0),
        "donchian_high_20": np.full(n, high20),
        "donchian_low_20": np.full(n, low20),
        "donchian_high_10": np.full(n, high10),
        "donchian_low_10": np.full(n, low10),
        "stoch_k": np.full(n, k), "stoch_d": np.full(n, d),
    })


class TestDonchianStochastic(unittest.TestCase):
    def test_donchian_channels_are_rolling_extremes(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect_high = df["h"].rolling(20, min_periods=20).max()
        expect_low = df["l"].rolling(20, min_periods=20).min()
        valid = expect_high.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "donchian_high_20"], expect_high[valid])))
        self.assertTrue(bool(np.allclose(df.loc[valid, "donchian_low_20"], expect_low[valid])))
        expect_low10 = df["l"].rolling(10, min_periods=10).min()
        self.assertTrue(bool(np.allclose(df.loc[valid, "donchian_low_10"], expect_low10[valid])))

    def test_stochastic_matches_direct_computation(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        low_n = df["l"].rolling(14, min_periods=14).min()
        high_n = df["h"].rolling(14, min_periods=14).max()
        rng = high_n - low_n
        expect_k = (100.0 * (df["c"] - low_n) / rng).where(rng > 0, 50.0)
        valid = expect_k.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "stoch_k"], expect_k[valid])))
        expect_d = df["stoch_k"].rolling(3, min_periods=3).mean()
        valid_d = expect_d.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid_d, "stoch_d"], expect_d[valid_d])))

    def test_stochastic_bounded_and_flat_is_neutral(self):
        df = indicators.add_indicators(_rand_df(800, seed=5))
        self.assertTrue(bool(((df["stoch_k"].iloc[30:] >= 0) & (df["stoch_k"].iloc[30:] <= 100)).all()))
        self.assertFalse(df["stoch_k"].iloc[30:].isna().any())
        # a perfectly flat stretch has a zero 14-bar range: %K is 50.0
        flat = indicators.add_indicators(_df_from_c(np.full(60, 100.0)))
        self.assertTrue(bool((flat["stoch_k"].iloc[20:] == 50.0).all()))

    def test_long_fires_on_breakout_with_k_above_d_below_80(self):
        sig = signals.add_signals(indicators.add_indicators(_wick_long_df()))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertEqual(entries, [44])
        self.assertGreater(float(sig["stoch_k"].iloc[44]), float(sig["stoch_d"].iloc[44]))
        self.assertLess(float(sig["stoch_k"].iloc[44]), 80.0)

    def test_short_fires_on_breakdown_with_k_below_d_above_20(self):
        sig = signals.add_signals(indicators.add_indicators(_wick_short_df()))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertEqual(entries, [40])
        self.assertLess(float(sig["stoch_k"].iloc[40]), float(sig["stoch_d"].iloc[40]))
        self.assertGreater(float(sig["stoch_k"].iloc[40]), 20.0)

    def test_k_filter_blocks_overbought_long(self):
        ind = indicators.add_indicators(_wick_long_df())
        ind["stoch_k"] = 90.0  # overbought: the same breakout must not fire
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_k_filter_blocks_oversold_short(self):
        ind = indicators.add_indicators(_wick_short_df())
        ind["stoch_k"] = 10.0  # oversold: the same breakdown must not fire
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_kd_cross_blocks_long(self):
        # %K below %D at the breakout bar: momentum is falling, no long.
        ind = indicators.add_indicators(_wick_long_df())
        ind["stoch_k"] = 40.0
        ind["stoch_d"] = 50.0
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_manual_entry_fires_on_cross_with_k_above_d(self):
        df = _manual_ds()
        df.loc[20, "c"] = 101.0  # crosses above the prior 20-bar high (100)
        sig = signals.add_signals(df)
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [20])
        df2 = _manual_ds()
        df2.loc[20, "c"] = 99.0  # crosses below the prior 20-bar low (100)
        sig2 = signals.add_signals(df2)
        # %K 60 > %D 50 blocks the short (needs %K < %D): no entry
        self.assertEqual(sig2.index[sig2["short_entry"]].tolist(), [])
        df3 = _manual_ds(k=40.0, d=50.0)
        df3.loc[20, "c"] = 99.0
        sig3 = signals.add_signals(df3)
        self.assertEqual(sig3.index[sig3["short_entry"]].tolist(), [20])

    def test_turtle_exit_fires_after_long(self):
        sig = signals.add_signals(indicators.add_indicators(_wick_long_df()))
        entries = sig.index[sig["long_entry"]].tolist()
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertEqual(entries, [44])
        self.assertIn(55, exits)
        self.assertTrue(any(e > entries[0] for e in exits))

    def test_exit_uses_prior_channel(self):
        # %K held above %D (no momentum exit), close 90 below the
        # prior 10-bar low (95) at bar 20: the channel exit must
        # fire — the unshifted 10-bar low would include the current
        # bar's own low and could never be broken by the close.
        df = _manual_ds(high10=110.0, low10=95.0)
        df.loc[20, "c"] = 90.0
        df.loc[20, "l"] = 90.0
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_exit"].iloc[20]))
        self.assertFalse(bool(sig["long_exit"].iloc[19]))

    def test_kd_cross_exit_fires(self):
        # Close holds above the 10-bar low, but %K crosses below %D
        # at bar 20: the momentum exit must fire on its own.
        df = _manual_ds(k=60.0, d=50.0, low10=90.0)
        k = np.full(30, 60.0)
        d = np.full(30, 50.0)
        k[20] = 40.0  # %K drops below %D at bar 20
        df["stoch_k"] = k
        df["stoch_d"] = d
        sig = signals.add_signals(df)
        self.assertTrue(bool(sig["long_exit"].iloc[20]))

    def test_random_walk_no_crash_no_overlap(self):
        # Note: on tight-spread synthetic data the Stochastic filter
        # blocks nearly every Donchian breakout — a breakout close
        # sits at the range extreme, so %K is ~100 (long) or ~0
        # (short) and the <80 / >20 gates fail. Real 1h bars have
        # wicks, so the filter passes there (see _wick_long_df).
        # The random-walk test therefore only asserts hygiene.
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_entry_window_param_changes_channel(self):
        df1 = indicators.add_indicators(_rand_df(), entry_n=10)
        df2 = indicators.add_indicators(_rand_df(), entry_n=20)
        self.assertFalse(bool(np.allclose(
            df1["donchian_high_10"].iloc[30:], df2["donchian_high_20"].iloc[30:])))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("donchian_high_20", "donchian_low_20", "donchian_high_10",
                    "donchian_low_10", "stoch_k", "stoch_d", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("donchian_high_20", "donchian_low_20", "donchian_high_10",
                        "donchian_low_10", "stoch_k", "stoch_d", "atr14"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.donchian_stochastic as mod

        self.assertEqual(mod.SPEC.slug, "donchian_stochastic")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
