"""TD Sequential tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.td_sequential import indicators, risk, signals


def _decline(n=40, start=100.0, step=1.0, seed=7):
    """Linear decline: every bar satisfies c[j] < c[j-4] for j >= 4."""
    c = start - np.arange(n) * step
    o = np.concatenate([[start], c[:-1]])
    h = np.maximum(o, c) + 0.4
    l = np.minimum(o, c) - 0.4
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 10.0)})


def _rise(n=44, start=60.0, step=1.0):
    """Rise for 13 bars (sell setup completes at 12), then a slow decline with
    wide upper wicks so sell-countdown bars (c[j] <= l[j-2]) register, with two
    flat bars (19, 24) that break the c[j] < c[j-4] chain so no buy setup
    cancels the sell countdown before it completes at bar 29."""
    c = np.zeros(n)
    c[:13] = start + np.arange(13) * step
    for j in range(13, n):
        c[j] = c[j - 1] - 0.5
    c[13] = c[12] - 1.0
    c[19] = c[15]
    c[24] = c[20]
    o = np.empty(n)
    o[0] = start
    o[1:] = c[:-1]
    h = np.maximum(o, c) + 3.0
    l = np.minimum(o, c) - 0.3
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 10.0)})


class TestTdSequential(unittest.TestCase):
    def test_buy_setup_completes_at_bar_12(self):
        df = indicators.add_indicators(_decline(40))
        # bars 4..12 satisfy c[j] < c[j-4] -> 9-bar run completes at bar 12
        self.assertTrue(df["buy_setup_done"].iloc[12])
        self.assertFalse(df["buy_setup_done"].iloc[11])
        self.assertFalse(df["sell_setup_done"].any())

    def test_setup_breaks_on_chain_violation(self):
        df = _decline(40)
        df.loc[8, "c"] = df.loc[4, "c"]  # c[8] == c[4] breaks c[j] < c[j-4]
        out = indicators.add_indicators(df)
        self.assertFalse(out["buy_setup_done"].iloc[12])
        self.assertTrue(out["buy_setup_done"].iloc[17])  # run restarts at 9, completes at 17

    def test_perfection_detected(self):
        df = _decline(40)
        out = indicators.add_indicators(df)
        # declining lows: bar 8/9 lows below bars 6/7 lows -> perfect
        self.assertTrue(out["buy_perfect"].iloc[12])

    def test_perfection_rejected(self):
        df = _decline(40)
        # make setup bars 6 and 7 (indices 9,10) the lowest lows -> not perfect
        df.loc[9, "l"] = df["l"].min() - 5.0
        df.loc[10, "l"] = df["l"].min() - 4.0
        out = indicators.add_indicators(df)
        self.assertTrue(out["buy_setup_done"].iloc[12])
        self.assertFalse(out["buy_perfect"].iloc[12])

    def test_buy_countdown_completes(self):
        df = _decline(40)
        out = indicators.add_indicators(df)
        # countdown starts at 13; every bar counts (c[j] <= l[j-2] holds);
        # 13th counted bar is bar 25
        self.assertTrue(out["buy_cd_done"].iloc[25])
        self.assertFalse(out["buy_cd_done"].iloc[24])

    def test_countdown_canceled_by_opposite_setup(self):
        dn = _decline(14)  # buy setup completes at 12
        n2 = 14
        start = dn["c"].iloc[-1]
        c2 = start + 2.0 + np.arange(n2) * 1.0
        o2 = np.empty(n2)
        o2[0] = start
        o2[1:] = c2[:-1]
        h2 = np.maximum(o2, c2) + 0.4
        l2 = np.minimum(o2, c2) - 0.4
        t2 = dn["t"].iloc[-1] + (np.arange(n2) + 1) * 3_600_000
        up = pd.DataFrame({"t": t2, "o": o2, "h": h2, "l": l2, "c": c2,
                           "v": np.full(n2, 10.0)})
        both = pd.concat([dn, up], ignore_index=True)
        out = indicators.add_indicators(both)
        self.assertTrue(out["sell_setup_done"].iloc[23])
        self.assertFalse(out["buy_cd_done"].any())  # buy countdown canceled

    def test_tdst_support_is_min_true_low_of_setup(self):
        df = _decline(40)
        out = indicators.add_indicators(df)
        tl = np.minimum(df["l"].to_numpy()[4:13], df["c"].to_numpy()[3:12])
        # setup bars are 4..12; true low of bar 4 uses c[3]
        self.assertAlmostEqual(out["tdst_s"].iloc[12], tl.min(), places=8)

    def test_sell_mirror(self):
        df = _rise()
        out = indicators.add_indicators(df)
        self.assertTrue(out["sell_setup_done"].iloc[12])
        self.assertTrue(out["sell_cd_done"].iloc[29])
        self.assertFalse(out["buy_cd_done"].any())

    def test_no_lookahead(self):
        df = _decline(40)
        full = indicators.add_indicators(df)
        cut = indicators.add_indicators(df.iloc[:30])
        for col in ("buy_cd_done", "sell_cd_done", "buy_setup_done", "sell_setup_done"):
            self.assertTrue((full[col].iloc[:30] == cut[col]).all(), col)

    def test_signals_wire_countdown_to_entries(self):
        df = signals.add_signals(indicators.add_indicators(_decline(40)))
        self.assertTrue(df["long_entry"].iloc[25])
        self.assertFalse(df["short_entry"].any())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())

    def test_tdst_break_is_exit(self):
        base = indicators.add_indicators(_decline(40))
        base.loc[30, "c"] = base["tdst_s"].iloc[30] - 1.0
        df = signals.add_signals(base)
        self.assertTrue(df["long_exit"].iloc[30])

    def test_risk_sanity(self):
        r = risk.RISK
        self.assertGreater(r.stop_atr_mult, 0)
        self.assertEqual(r.max_hold_bars, 48)
        self.assertTrue(0 < r.risk_frac < 1)
        self.assertGreaterEqual(r.max_leverage, 1.0)
        self.assertIsNone(r.trail_atr_mult)
        self.assertGreaterEqual(risk.WARMUP, 14)


if __name__ == "__main__":
    unittest.main()
