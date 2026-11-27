"""Funding-rate carry tests. Network-free, synthetic data only.

Funding is injected via add_indicators(df, funding_df=...), so no
cache file is read. THRESH = 0.0000125, exit level THRESH/2 =
0.00000625 (see signals.py).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.funding_rate_carry import indicators, risk, signals
from strategies.funding_rate_carry.run_backtest import (
    equity_with_funding,
    trade_funding_usd,
)

T0 = 1700006400000  # 2023-11-15 00:00 UTC (hour-aligned)
TH = 0.0000125
HALF = TH / 2


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _funding_df(rates):
    n = len(rates)
    return pd.DataFrame(
        {
            "t": (T0 + np.arange(n) * 3_600_000).astype("int64"),
            "funding_rate": np.asarray(rates, float),
        }
    )


def _signal_frame(avg24):
    n = len(avg24)
    return pd.DataFrame(
        {
            "t": (T0 + np.arange(n) * 3_600_000).astype("int64"),
            "o": np.full(n, 100.0),
            "h": np.full(n, 100.2),
            "l": np.full(n, 99.8),
            "c": np.full(n, 100.0),
            "v": np.full(n, 100.0),
            "fund_avg_24h": np.asarray(avg24, float),
        }
    )


class TestFundingRateCarry(unittest.TestCase):
    def test_constant_funding_avg_is_the_constant(self):
        # Flat funding 0.00002: after the 24-bar window the rolling
        # mean is exactly 0.00002.
        ind = indicators.add_indicators(
            _df_from_c(np.full(60, 100.0)),
            funding_df=_funding_df(np.full(60, 0.00002)),
        )
        self.assertTrue(ind["fund_avg_24h"].iloc[:23].isna().all())
        self.assertAlmostEqual(float(ind["fund_avg_24h"].iloc[30]), 0.00002, places=12)
        self.assertAlmostEqual(float(ind["fund_avg_24h"].iloc[59]), 0.00002, places=12)

    def test_rolling_mean_hand_computed(self):
        # 24 bars of 0, then 0.000024: at bar 30 the window (bars
        # 7..30) holds 17 zeros and 7 x 0.000024, so the mean is
        # 7 * 0.000024 / 24 = 0.000007. At bar 47 the window is
        # all 0.000024.
        rates = np.concatenate([np.zeros(24), np.full(24, 0.000024)])
        ind = indicators.add_indicators(
            _df_from_c(np.full(48, 100.0)), funding_df=_funding_df(rates)
        )
        self.assertAlmostEqual(float(ind["fund_avg_24h"].iloc[30]), 0.000007, places=12)
        self.assertAlmostEqual(float(ind["fund_avg_24h"].iloc[47]), 0.000024, places=12)

    def test_funding_column_merged_1_to_1(self):
        rates = np.linspace(-0.00002, 0.00002, 40)
        ind = indicators.add_indicators(
            _df_from_c(np.full(40, 100.0)), funding_df=_funding_df(rates)
        )
        np.testing.assert_allclose(ind["funding_rate"].to_numpy(), rates)

    def test_long_entry_on_cross_below_neg_thresh(self):
        # avg24 crosses below -THRESH at bar 2, back above
        # -THRESH/2 at bar 4.
        sig = signals.add_signals(
            _signal_frame([0, 0, -0.00002, -0.00002, 0, 0])
        )
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [2])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [4])
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_short_entry_on_cross_above_pos_thresh(self):
        sig = signals.add_signals(
            _signal_frame([0, 0, 0.00002, 0.00002, 0, 0])
        )
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [2])
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [4])
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_no_entry_inside_the_band(self):
        # avg24 wiggles between -THRESH/2 and +THRESH/2: nothing fires.
        sig = signals.add_signals(
            _signal_frame([0, 0.000005, -0.000005, 0.000006, -0.000006, 0])
        )
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertFalse(bool(sig["long_exit"].any()))
        self.assertFalse(bool(sig["short_exit"].any()))

    def test_level_condition_does_not_refire(self):
        # avg24 stays below -THRESH for 10 straight bars: a level
        # condition would fire every bar, a cross fires once.
        sig = signals.add_signals(_signal_frame([-0.00002] * 10))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [])
        # Same for the short side.
        sig = signals.add_signals(_signal_frame([0.00002] * 10))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [])

    def test_long_exit_needs_normalization_past_half_thresh(self):
        # avg24 dips below -THRESH at bar 2, recovers only to
        # -0.00001 (still below -THRESH/2 = -0.00000625): no exit.
        # It exits when it crosses -0.00000625 at bar 5.
        sig = signals.add_signals(
            _signal_frame([0, 0, -0.00002, -0.00001, -0.00001, 0, 0])
        )
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [2])
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [5])

    def test_opposite_entry_exits(self):
        # Long at bar 2; at bar 4 avg24 jumps above +THRESH, so the
        # short entry fires and exits the long (the long exit also
        # fires via the normalization cross, both on bar 4).
        sig = signals.add_signals(
            _signal_frame([0, 0, -0.00002, -0.00002, 0.00002, 0.00002])
        )
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [2])
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [4])
        self.assertIn(4, sig.index[sig["long_exit"]].tolist())

    def test_missing_funding_row_raises(self):
        f = _funding_df(np.full(40, 0.00001))
        f = f.drop(index=10).reset_index(drop=True)  # one hour missing
        with self.assertRaises(ValueError):
            indicators.add_indicators(_df_from_c(np.full(40, 100.0)), funding_df=f)

    def test_missing_coin_raises(self):
        df = _df_from_c(np.full(40, 100.0))  # no df.attrs['coin']
        with self.assertRaises(ValueError):
            indicators.add_indicators(df)

    def test_unknown_coin_cache_raises(self):
        df = _df_from_c(np.full(40, 100.0))
        df.attrs["coin"] = "DOGE"  # no data/funding/DOGE_1h.csv
        with self.assertRaises(ValueError):
            indicators.add_indicators(df)

    def test_trade_funding_usd_signs(self):
        # 10 hours at +0.00001 on $10k notional: a long PAYS $1.00,
        # a short RECEIVES $1.00.
        funding = {T0 + i * 3_600_000: 0.00001 for i in range(10)}
        trade = {"side": "long", "entry_px": 100.0, "qty": 100.0,
                 "entry_t": T0, "exit_t": T0 + 10 * 3_600_000}
        self.assertAlmostEqual(trade_funding_usd(trade, funding), -1.0, places=9)
        trade["side"] = "short"
        self.assertAlmostEqual(trade_funding_usd(trade, funding), 1.0, places=9)

    def test_trade_funding_usd_empty_range_is_zero(self):
        funding = {T0: 0.00001}
        trade = {"side": "long", "entry_px": 100.0, "qty": 100.0,
                 "entry_t": T0, "exit_t": T0}
        self.assertAlmostEqual(trade_funding_usd(trade, funding), 0.0, places=9)

    def test_equity_with_funding_adds_at_exit_bar(self):
        eq = pd.Series([10000.0, 10000.0, 10010.0, 10010.0, 10005.0])
        t_vals = np.array([T0 + i * 3_600_000 for i in range(5)])
        trades = pd.DataFrame(
            {"exit_t": [T0 + 2 * 3_600_000, T0 + 4 * 3_600_000],
             "funding_usd": [5.0, -2.0]}
        )
        out = equity_with_funding(eq, trades, t_vals)
        np.testing.assert_allclose(
            out.to_numpy(), [10000.0, 10000.0, 10015.0, 10015.0, 10008.0]
        )

    def test_no_nan_after_warmup_and_boolean_signals(self):
        rng = np.random.default_rng(3)
        rates = rng.normal(0.000008, 0.00001, 400)
        sig = signals.add_signals(
            indicators.add_indicators(_rand_df_helper(400), funding_df=_funding_df(rates))
        )
        self.assertFalse(sig["fund_avg_24h"].iloc[48:].isna().any())
        self.assertFalse(sig["atr"].iloc[48:].isna().any())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        rng = np.random.default_rng(3)
        rates = rng.normal(0.000008, 0.00001, 300)
        full = _rand_df_helper(300)
        f_full = _funding_df(rates)
        ind_full = indicators.add_indicators(full, funding_df=f_full)
        for j in (100, 250):
            ind_tr = indicators.add_indicators(
                full.iloc[: j + 1], funding_df=f_full.iloc[: j + 1]
            )
            for col in ("funding_rate", "fund_avg_24h", "atr"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(
            indicators.add_indicators(
                _df_from_c([100.0, 101.0, 100.5]),
                funding_df=_funding_df([0.00001, 0.00001, 0.00001]),
            )
        )
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_threshold_constants(self):
        self.assertEqual(signals.THRESH, 0.0000125)

    def test_registration_imports_cleanly(self):
        import strategies.funding_rate_carry as mod

        self.assertEqual(mod.SPEC.slug, "funding_rate_carry")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 168)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 48)


def _rand_df_helper(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


if __name__ == "__main__":
    unittest.main()
