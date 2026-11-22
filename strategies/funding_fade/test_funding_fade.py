"""Negative-funding fade tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.funding_fade import indicators, risk, signals


def _frame(n=60, seed=7):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0.0002, 0.005, n)))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * 1.001
    l = np.minimum(o, c) * 0.999
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0)})


def _funding_df(df, rates):
    return pd.DataFrame({"t": df["t"].to_numpy(),
                         "funding_rate": np.asarray(rates, dtype=float)})


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        df = _frame()
        rates = np.full(len(df), 0.0001)
        ind = indicators.add_indicators(df, funding_df=_funding_df(df, rates))
        for col in ("funding_rate", "funding_neg_turn", "atr"):
            self.assertIn(col, ind.columns)

    def test_turn_detected_on_first_negative_bar_only(self):
        df = _frame()
        # Positive for 5 bars, negative for 6, positive, negative again.
        rates = [0.0001] * 5 + [-0.0002] * 6 + [0.0001] * 3 + [-0.0001] * 4
        rates = rates + [0.0001] * (len(df) - len(rates))
        ind = indicators.add_indicators(df, funding_df=_funding_df(df, rates))
        turns = np.where(ind["funding_neg_turn"])[0]
        self.assertListEqual([int(x) for x in turns], [5, 14])

    def test_no_turn_when_always_negative(self):
        # Already negative from bar 0: no "turn" (no prior >= 0 bar).
        df = _frame()
        ind = indicators.add_indicators(
            df, funding_df=_funding_df(df, np.full(len(df), -0.0001)))
        self.assertFalse(ind["funding_neg_turn"].any())

    def test_no_turn_when_always_positive(self):
        df = _frame()
        ind = indicators.add_indicators(
            df, funding_df=_funding_df(df, np.full(len(df), 0.0001)))
        self.assertFalse(ind["funding_neg_turn"].any())

    def test_missing_coin_raises(self):
        df = _frame()
        df.attrs.pop("coin", None)
        with self.assertRaises(ValueError):
            indicators.add_indicators(df)

    def test_missing_cache_file_raises(self):
        df = _frame()
        df.attrs["coin"] = "NO_SUCH_COIN"
        with self.assertRaises(ValueError):
            indicators.add_indicators(df)

    def test_missing_funding_rows_raise_not_fill(self):
        df = _frame()
        partial = _funding_df(df, np.full(len(df), 0.0001)).iloc[:30]
        with self.assertRaises(ValueError):
            indicators.add_indicators(df, funding_df=partial)

    def test_no_lookahead(self):
        df = _frame(n=200)
        rates = np.where(np.arange(200) % 17 == 0, -0.0002, 0.0001)
        fdf = _funding_df(df, rates)
        full = indicators.add_indicators(df, funding_df=fdf)
        short = indicators.add_indicators(df.iloc[:100],
                                          funding_df=fdf.iloc[:100])
        pd.testing.assert_series_equal(
            full["funding_neg_turn"].iloc[:100].reset_index(drop=True),
            short["funding_neg_turn"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _signal_frame(self, turns):
        n = len(turns)
        t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
        c = np.full(n, 100.0)
        return pd.DataFrame({
            "t": t, "o": c, "h": c, "l": c, "c": c, "v": np.full(n, 100.0),
            "funding_neg_turn": np.asarray(turns, dtype=bool),
        })

    def test_signal_columns_boolean_no_nan(self):
        df = _frame()
        rates = np.where(np.arange(len(df)) % 11 == 0, -0.0002, 0.0001)
        sig = signals.add_signals(
            indicators.add_indicators(df, funding_df=_funding_df(df, rates)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_on_turn_exit_after_8_bars(self):
        turns = [False] * 5 + [True] + [False] * 20
        sig = signals.add_signals(self._signal_frame(turns))
        self.assertTrue(sig["long_entry"].iloc[5])
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(sig["long_exit"].iloc[13])  # 5 + 8
        self.assertEqual(int(sig["long_exit"].sum()), 1)

    def test_turn_while_holding_ignored(self):
        # Turns at 5 and at 7 (mid-hold): only the first enters.
        turns = [False] * 5 + [True] + [False] + [True] + [False] * 20
        sig = signals.add_signals(self._signal_frame(turns))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertTrue(sig["long_exit"].iloc[13])

    def test_reentry_after_exit(self):
        turns = [False] * 5 + [True] + [False] * 20 + [True] + [False] * 12
        sig = signals.add_signals(self._signal_frame(turns))
        self.assertEqual(int(sig["long_entry"].sum()), 2)
        self.assertTrue(sig["long_entry"].iloc[26])
        self.assertTrue(sig["long_exit"].iloc[13])
        self.assertTrue(sig["long_exit"].iloc[34])

    def test_never_shorts(self):
        turns = [False] * 5 + [True] + [False] * 20
        sig = signals.add_signals(self._signal_frame(turns))
        self.assertFalse(sig["short_entry"].any())
        self.assertFalse(sig["short_exit"].any())


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 8)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertTrue(r.allow_longs)
        self.assertFalse(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 24)

    def test_end_to_end_pipeline_runs(self):
        df = _frame(n=500)
        rates = np.where(np.arange(500) % 13 == 0, -0.0002, 0.0001)
        sig = signals.add_signals(
            indicators.add_indicators(df, funding_df=_funding_df(df, rates)))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreater(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
