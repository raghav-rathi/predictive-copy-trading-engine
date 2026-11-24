"""Gap Fill Fade tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.gap_fill_fade import indicators, risk, signals


def _bars(rows):
    """Frame from a list of (o, h, l, c) tuples."""
    n = len(rows)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    arr = np.asarray(rows, dtype=float)
    return pd.DataFrame({"t": t, "o": arr[:, 0], "h": arr[:, 1],
                         "l": arr[:, 2], "c": arr[:, 3],
                         "v": np.full(n, 100.0)})


def _flat(n, px=100.0, half_range=1.0):
    """n flat bars at px with true range 2*half_range (ATR = 2)."""
    return [(px, px + half_range, px - half_range, px)] * n


def _gap_down_series():
    """30 flat bars at 100 (ATR 2.0), then a gap down to open 90 /
    close 92, drift to 95, then close 101 (fill)."""
    rows = _flat(30)
    rows += [(90, 93, 89, 92), (92, 96, 91, 95), (95, 102, 94, 101),
             (101, 103, 100, 102)]
    return rows


def _gap_up_series():
    """30 flat bars at 100, then a gap up to open 110 / close 108,
    drift to 105, then close 99 (fill)."""
    rows = _flat(30)
    rows += [(110, 111, 107, 108), (108, 109, 104, 105), (105, 106, 98, 99),
             (99, 100, 97, 98)]
    return rows


def _random_walk_frame(n=500, seed=7, drift=0.0, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.001, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.001, n))
    v = rng.uniform(50, 150, n)
    return _bars(list(zip(o, h, l, c)))


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("prev_close", "gap", "gap_atr", "gap_up", "gap_dn",
                    "fill_level", "atr14"):
            self.assertIn(col, ind.columns)

    def test_gap_down_detected(self):
        ind = indicators.add_indicators(_bars(_gap_down_series()))
        # Gap bar (index 30): open 90 vs prev close 100 -> gap -10.
        self.assertAlmostEqual(ind["gap"].iloc[30], -10.0, places=9)
        self.assertAlmostEqual(ind["fill_level"].iloc[30], 100.0, places=9)
        self.assertTrue(bool(ind["gap_dn"].iloc[30]))
        self.assertFalse(bool(ind["gap_up"].iloc[30]))
        self.assertGreater(ind["gap_atr"].iloc[30], 0.5)

    def test_gap_up_detected(self):
        ind = indicators.add_indicators(_bars(_gap_up_series()))
        self.assertAlmostEqual(ind["gap"].iloc[31 - 1], 10.0, places=9)
        self.assertAlmostEqual(ind["fill_level"].iloc[30], 100.0, places=9)
        self.assertTrue(bool(ind["gap_up"].iloc[30]))
        self.assertFalse(bool(ind["gap_dn"].iloc[30]))

    def test_exact_half_atr_boundary_is_not_a_gap(self):
        # Flat bars have TR = 2, so ATR(14) = 2.0. A gap of exactly
        # -1.0 is exactly 0.5 ATR: strict inequality means NO gap
        # signal. The gap bar is built with TR exactly 2 as well
        # (h=100, l=98, prev close 100) so ATR stays 2.0.
        rows = _flat(30)
        rows += [(99, 100, 98, 99), (99, 100, 98, 99)]
        ind = indicators.add_indicators(_bars(rows))
        self.assertAlmostEqual(ind["atr14"].iloc[30], 2.0, places=9)
        self.assertAlmostEqual(ind["gap"].iloc[30], -1.0, places=9)
        self.assertAlmostEqual(ind["gap_atr"].iloc[30], 0.5, places=9)
        self.assertFalse(bool(ind["gap_dn"].iloc[30]))
        self.assertFalse(bool(ind["gap_up"].iloc[30]))
        # Mirror: gap of exactly +1.0 is not a gap up either.
        rows2 = _flat(30)
        rows2 += [(101, 102, 100, 101)]
        ind2 = indicators.add_indicators(_bars(rows2))
        self.assertAlmostEqual(ind2["gap_atr"].iloc[30], 0.5, places=9)
        self.assertFalse(bool(ind2["gap_up"].iloc[30]))

    def test_just_beyond_half_atr_is_a_gap(self):
        # Gap of -1.1 with ATR ~2.0 -> gap_atr > 0.5 -> gap_dn.
        rows = _flat(30)
        rows += [(98.9, 99.9, 97.9, 98.9)]
        ind = indicators.add_indicators(_bars(rows))
        self.assertGreater(ind["gap_atr"].iloc[30], 0.5)
        self.assertTrue(bool(ind["gap_dn"].iloc[30]))

    def test_fill_level_is_prev_close(self):
        ind = indicators.add_indicators(_bars(_gap_down_series()))
        for i in range(1, 34):
            self.assertAlmostEqual(
                ind["fill_level"].iloc[i], ind["c"].iloc[i - 1], places=9)

    def test_first_bar_no_gap(self):
        ind = indicators.add_indicators(_bars(_gap_down_series()))
        self.assertEqual(ind["gap"].iloc[0], 0.0)
        self.assertFalse(bool(ind["gap_up"].iloc[0]))
        self.assertFalse(bool(ind["gap_dn"].iloc[0]))

    def test_no_nan_in_gap_columns(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("gap", "gap_atr", "gap_up", "gap_dn", "fill_level"):
            self.assertFalse(ind[col].isna().any(), col)
            if col in ("gap", "gap_atr", "fill_level"):
                self.assertTrue(np.isfinite(ind[col]).all(), col)

    def test_no_lookahead(self):
        df = _bars(_gap_down_series() + _flat(20, px=102.0))
        short = df.iloc[:35]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        for col in ("gap", "gap_atr", "gap_up", "gap_dn", "fill_level"):
            pd.testing.assert_series_equal(
                ind_full[col].iloc[:35].reset_index(drop=True),
                ind_short[col].reset_index(drop=True),
                check_names=False,
            )


class TestSignals(unittest.TestCase):
    def _sig(self, rows):
        return signals.add_signals(indicators.add_indicators(_bars(rows)))

    def test_signal_columns_boolean_no_nan(self):
        sig = self._sig(_gap_down_series())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def test_long_entry_on_gap_down_bar(self):
        sig = self._sig(_gap_down_series())
        self.assertTrue(sig["long_entry"].iloc[30])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_long_exit_on_fill(self):
        sig = self._sig(_gap_down_series())
        # Close 101 at bar 32 >= fill level 100 -> exit. No exit
        # at bar 31 (close 95 < 100).
        self.assertFalse(sig["long_exit"].iloc[31])
        self.assertTrue(sig["long_exit"].iloc[32])

    def test_short_entry_and_fill_exit(self):
        sig = self._sig(_gap_up_series())
        self.assertTrue(sig["short_entry"].iloc[30])
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertFalse(sig["short_exit"].iloc[31])
        self.assertTrue(sig["short_exit"].iloc[32])  # close 99 <= 100

    def test_one_fade_per_gap(self):
        # Two consecutive gap-down bars: the second gap fires while
        # the first fade is still held -> no second entry.
        rows = _flat(30)
        rows += [(90, 93, 89, 92), (82, 85, 81, 84), (84, 90, 83, 88)]
        ind = indicators.add_indicators(_bars(rows))
        self.assertTrue(bool(ind["gap_dn"].iloc[30]))
        self.assertTrue(bool(ind["gap_dn"].iloc[31]))
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[30])
        self.assertFalse(sig["long_entry"].iloc[31])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_fill_on_gap_bar_itself_does_not_exit(self):
        # Gap down to 90 but the same bar closes at 101, above the
        # fill level: the position only exists from the next bar's
        # open, so the exit cannot fire on the gap bar itself.
        rows = _flat(30)
        rows += [(90, 102, 89, 101), (101, 103, 100, 102)]
        sig = self._sig(rows)
        self.assertTrue(sig["long_entry"].iloc[30])
        self.assertFalse(sig["long_exit"].iloc[30])
        self.assertTrue(sig["long_exit"].iloc[31])

    def test_flip_on_opposite_gap(self):
        # Long on the gap down at bar 30; bar 31 gaps UP ->
        # exit long and enter short on the same bar.
        rows = _flat(30)
        rows += [(90, 93, 89, 92), (102, 103, 101, 100), (100, 101, 95, 92)]
        ind = indicators.add_indicators(_bars(rows))
        self.assertTrue(bool(ind["gap_up"].iloc[31]))
        sig = signals.add_signals(ind)
        self.assertTrue(sig["long_entry"].iloc[30])
        self.assertTrue(sig["long_exit"].iloc[31])
        self.assertTrue(sig["short_entry"].iloc[31])
        # The short's fill level is bar 30's close (92); bar 32
        # closes at 92 -> short exit.
        self.assertTrue(sig["short_exit"].iloc[32])

    def test_no_entry_without_gap(self):
        # Flat series: no gaps at all, no entries.
        sig = self._sig(_flat(60))
        self.assertFalse(sig["long_entry"].any())
        self.assertFalse(sig["short_entry"].any())


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 2.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 24)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 30)

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
