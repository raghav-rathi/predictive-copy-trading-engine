"""TD Combo tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.td_combo import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _bullish_combo_frame():
    """Hand-built series: buy setup completes at bar 12, buy countdown
    (13 bars with close<=low[2], lower lows/closes) runs bars 13..25,
    so buy_countdown_complete fires at bar 25."""
    n = 40
    c = np.empty(n)
    # bars 0..12: decline 0.5/bar -> c[i] < c[i-4] for i>=4 -> setup at 12
    for i in range(13):
        c[i] = 100.0 - 0.5 * i
    # bars 13..25: countdown, drop 1.0/bar, tight lows (c-0.1)
    for i in range(13, 26):
        c[i] = c[12] - 1.0 * (i - 12)
    # bars 26..39: chop flat
    for i in range(26, n):
        c[i] = c[25]
    o = c.copy()
    h = c + 0.5
    l = np.where(np.arange(n) >= 13, c - 0.1, c - 0.5)
    return _ohlcv(o, h, l, c)


def _bearish_combo_frame():
    """Mirror: sell setup completes at bar 12, sell countdown bars 13..25
    with close>=high[2], rising highs/closes; fires at bar 25."""
    df = _bullish_combo_frame()
    n = len(df)
    c = 200.0 - df["c"].to_numpy()  # rising mirror
    o = c.copy()
    h = np.where(np.arange(n) >= 13, c + 0.1, c + 0.5)
    l = c - 0.5
    return _ohlcv(o, h, l, c)


class TestTdCombo(unittest.TestCase):
    def test_setup_completes_at_bar_12(self):
        ind = indicators.add_indicators(_bullish_combo_frame())
        self.assertFalse(bool(ind["buy_setup_complete"].iloc[11]))
        self.assertTrue(bool(ind["buy_setup_complete"].iloc[12]))

    def test_buy_countdown_completes_at_bar_25(self):
        ind = indicators.add_indicators(_bullish_combo_frame())
        idx = ind.index[ind["buy_countdown_complete"]]
        self.assertEqual(len(idx), 1)
        self.assertEqual(idx[0], 25)
        self.assertEqual(int(ind["buy_countdown"].iloc[24]), 12)
        self.assertEqual(int(ind["sell_countdown_complete"].sum()), 0)

    def test_long_entry_fires_on_countdown_13(self):
        sig = signals.add_signals(indicators.add_indicators(_bullish_combo_frame()))
        self.assertTrue(bool(sig["long_entry"].iloc[25]))
        self.assertEqual(int(sig["long_entry"].sum()), 1)
        self.assertEqual(int(sig["short_entry"].sum()), 0)

    def test_sell_mirror(self):
        ind = indicators.add_indicators(_bearish_combo_frame())
        idx = ind.index[ind["sell_countdown_complete"]]
        self.assertEqual(len(idx), 1)
        self.assertEqual(idx[0], 25)
        sig = signals.add_signals(ind)
        self.assertTrue(bool(sig["short_entry"].iloc[25]))
        self.assertEqual(int(sig["short_entry"].sum()), 1)
        self.assertEqual(int(sig["long_entry"].sum()), 0)

    def test_countdown_rejects_non_qualifying_bar(self):
        # break the close<=low[2] condition at bar 20: countdown must
        # not reach 13 within bars 13..25 (it skips bar 20)
        df = _bullish_combo_frame()
        c = df["c"].to_numpy().copy()
        h = df["h"].to_numpy().copy()
        l = df["l"].to_numpy().copy()
        l[18] = c[18] - 2.5  # drop the low at bar 18 so c[20] > l[18]
        df = _ohlcv(df["o"].to_numpy(), h, l, c)
        ind = indicators.add_indicators(df)
        self.assertEqual(int(ind["buy_countdown_complete"].sum()), 0)

    def test_long_exit_on_price_flip(self):
        # after entry, long_exit fires exactly where c > c.shift(4)
        ind = indicators.add_indicators(_bullish_combo_frame())
        sig = signals.add_signals(ind)
        expect = ((ind["c"] > ind["c"].shift(4)).fillna(False))
        self.assertTrue(bool((sig["long_exit"] == expect).all()))
        expect_s = ((ind["c"] < ind["c"].shift(4)).fillna(False))
        self.assertTrue(bool((sig["short_exit"] == expect_s).all()))

    def test_no_lookahead_truncation(self):
        full = _bullish_combo_frame()
        ind_full = indicators.add_indicators(full)
        sig_full = signals.add_signals(ind_full)
        for j in (20, 30):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            sig_tr = signals.add_signals(ind_tr)
            for col in ("buy_setup_complete", "sell_setup_complete",
                        "buy_countdown_complete", "sell_countdown_complete"):
                self.assertEqual(bool(ind_full[col].iloc[j]), bool(ind_tr[col].iloc[j]), (col, j))
            self.assertEqual(int(ind_full["buy_countdown"].iloc[j]), int(ind_tr["buy_countdown"].iloc[j]), ("count", j))
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_bullish_combo_frame()))
        ind = indicators.add_indicators(_bullish_combo_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "buy_setup_complete", "sell_setup_complete",
                    "buy_countdown_complete", "sell_countdown_complete"):
            self.assertFalse(sig[col].isna().any() if col in sig else ind[col].isna().any(), col)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_registration(self):
        from strategies import td_combo as mod
        from strategies.registry import REGISTRY
        self.assertIn("td_combo", REGISTRY)
        self.assertIs(REGISTRY["td_combo"], mod.SPEC)


if __name__ == "__main__":
    unittest.main()
