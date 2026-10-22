"""Original Turtle Rules tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.turtle_classic import indicators, risk, signals
from strategies import base as B


def _ohlc(o, h, l, c):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({
        "t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
        "l": np.asarray(l, float), "c": np.asarray(c, float),
        "v": np.full(n, 100.0),
    })


def _flat(n, px=100.0):
    o = np.full(n, px); h = np.full(n, px + 1.0)
    l = np.full(n, px - 1.0); c = np.full(n, px)
    return o, h, l, c


def _winner_skip_frame():
    """First S1 long is a winner; the next S1 long breakout is skipped,
    and it is NOT a 55-bar breakout (pure skip, no failsafe)."""
    n = 130
    o, h, l, c = _flat(n)
    o[60] = 100; h[60] = 109; l[60] = 100; c[60] = 108      # breakout
    for i in range(61, 71):                                  # rally 109..118
        c[i] = 108 + (i - 60)
        o[i] = c[i - 1]; h[i] = c[i] + 0.5; l[i] = c[i] - 0.5
    for i in range(71, 81):                                  # fade 117..108
        c[i] = 118 - (i - 70)
        o[i] = c[i - 1]; h[i] = c[i] + 0.5; l[i] = c[i] - 0.5
    o[81:101] = 112; h[81:101] = 112.5                      # base at 112
    l[81:101] = 111.5; c[81:101] = 112
    o[50] = 100; h[50] = 105; l[50] = 99; c[50] = 100       # high pokes, close doesn't
    o[101] = 112; h[101] = 116; l[101] = 112; c[101] = 115  # 2nd breakout (< 55-bar high)
    o[102:] = 115; h[102:] = 115.5; l[102:] = 114.5; c[102:] = 115
    return _ohlc(o, h, l, c)


def _failsafe_frame():
    """Same as the winner frame, but the second breakout also clears the
    55-bar high -> the S2 failsafe must be taken."""
    df = _winner_skip_frame()
    o = df["o"].to_numpy().copy(); h = df["h"].to_numpy().copy()
    l = df["l"].to_numpy().copy(); c = df["c"].to_numpy().copy()
    o[101] = 112; h[101] = 141; l[101] = 112; c[101] = 140
    o[102:] = 140; h[102:] = 140.5; l[102:] = 139.5; c[102:] = 140
    return _ohlc(o, h, l, c)


def _loser_allow_frame():
    """First S1 long stops out for a loss; the next S1 long is taken."""
    n = 120
    o, h, l, c = _flat(n)
    o[60] = 100; h[60] = 109; l[60] = 100; c[60] = 108      # breakout
    o[61:66] = 108; h[61:66] = 108.5; l[61:66] = 107.5; c[61:66] = 108
    o[66] = 108; h[66] = 108; l[66] = 95; c[66] = 96        # crash -> 2N stop
    o[67:91] = 100; h[67:91] = 100.5; l[67:91] = 99.5; c[67:91] = 100
    o[91] = 100; h[91] = 109; l[91] = 100; c[91] = 108      # 2nd breakout
    o[92:] = 108; h[92:] = 108.5; l[92:] = 107.5; c[92:] = 108
    return _ohlc(o, h, l, c)


def _s2_exit_frame():
    """S2 long, then a dip that crosses the 10-bar low but not the
    20-bar low (must NOT exit), then a deeper slide that crosses the
    20-bar low (must exit)."""
    n = 160
    o, h, l, c = _flat(n)
    o[60] = 100; h[60] = 109; l[60] = 100; c[60] = 108      # breakout
    for i in range(61, 71):                                  # rally 109..118
        c[i] = 108 + (i - 60)
        o[i] = c[i - 1]; h[i] = c[i] + 0.5; l[i] = c[i] - 0.5
    for i in range(71, 81):                                  # fade 117..108
        c[i] = 118 - (i - 70)
        o[i] = c[i - 1]; h[i] = c[i] + 0.5; l[i] = c[i] - 0.5
    o[81:101] = 112; h[81:101] = 112.5                      # base at 112
    l[81:101] = 111.5; c[81:101] = 112
    o[101] = 112; h[101] = 141; l[101] = 112; c[101] = 140  # monster -> S2
    for i in range(102, 112):                                # rally 142..160
        c[i] = 140 + 2 * (i - 101)
        o[i] = c[i - 1]; h[i] = c[i] + 0.5; l[i] = c[i] - 0.5
    o[112:126] = 160; h[112:126] = 160.5                    # base at 160
    l[112:126] = 159.5; c[112:126] = 160
    o[126] = 160; h[126] = 160; l[126] = 150; c[126] = 151  # dip: 10-bar cross only
    for i in range(127, n):                                  # slide 150..118
        c[i] = 151 - (i - 126)
        o[i] = c[i - 1]; h[i] = c[i] + 0.3; l[i] = c[i] - 0.3
    return _ohlc(o, h, l, c)


def _short_frame():
    """S1 short breakdown, stopped out on the bounce."""
    n = 110
    o, h, l, c = _flat(n)
    o[60] = 100; h[60] = 100; l[60] = 91; c[60] = 92        # breakdown
    for i in range(61, 71):                                  # slide 91..82
        c[i] = 92 - (i - 60)
        o[i] = c[i - 1]; h[i] = c[i] + 0.5; l[i] = c[i] - 0.5
    o[71] = 82; h[71] = 98; l[71] = 82; c[71] = 97          # sharp bounce -> stop
    o[72:] = 97; h[72:] = 97.5; l[72:] = 96.5; c[72:] = 97
    return _ohlc(o, h, l, c)


def _sig(df, **kw):
    kw.setdefault("warmup", 30)
    return signals.generate(indicators.add_indicators(df), **kw)


class TestIndicators(unittest.TestCase):
    def test_columns_and_values(self):
        df = _winner_skip_frame()
        ind = indicators.add_indicators(df)
        for col in ("dc20_high", "dc20_low", "dc55_high", "dc55_low",
                    "exit10_high", "exit10_low", "exit20_high", "exit20_low",
                    "atr"):
            self.assertIn(col, ind.columns)
        pd.testing.assert_series_equal(
            ind["dc20_high"], df["h"].rolling(20, min_periods=20).max(),
            check_names=False)
        pd.testing.assert_series_equal(
            ind["exit10_low"], df["l"].rolling(10, min_periods=10).min(),
            check_names=False)
        pd.testing.assert_series_equal(
            ind["atr"], B.atr(df["h"], df["l"], df["c"], 20), check_names=False)

    def test_does_not_mutate_input(self):
        df = _winner_skip_frame()
        before = df.copy()
        indicators.add_indicators(df)
        pd.testing.assert_frame_equal(df, before)


class TestEntries(unittest.TestCase):
    def test_breakout_triggers_on_breakout_bar_close(self):
        # Entry channels are shifted by 1: the breakout bar's close fires.
        sig, _ = _sig(_winner_skip_frame())
        self.assertFalse(bool(sig["long_entry"].iloc[59]))
        self.assertTrue(bool(sig["long_entry_s1"].iloc[60]))
        self.assertTrue(bool(sig["long_entry"].iloc[60]))
        self.assertEqual(sig["system"].iloc[60], "S1")

    def test_entry_needs_close_not_high(self):
        # Bar 50: high pokes above the 20-bar high, close does not.
        sig, _ = _sig(_winner_skip_frame())
        self.assertFalse(bool(sig["long_entry_s1"].iloc[50]))
        self.assertFalse(bool(sig["long_entry"].iloc[50]))

    def test_breakdown_short_entry(self):
        sig, trades = _sig(_short_frame())
        self.assertTrue(bool(sig["short_entry_s1"].iloc[60]))
        self.assertTrue(bool(sig["short_entry"].iloc[60]))
        self.assertEqual(sig["system"].iloc[60], "S1")
        self.assertEqual(trades[0]["system"], "S1")
        self.assertEqual(trades[0]["side"], "short")

    def test_warmup_gates_early_entries(self):
        # Default WARMUP=120 suppresses the bar-60 breakout entry.
        sig = signals.add_signals(indicators.add_indicators(_winner_skip_frame()))
        self.assertFalse(bool(sig["long_entry"].iloc[60]))
        self.assertEqual(sig["long_entry"].sum(), 0)


class TestSkipRule(unittest.TestCase):
    def test_skip_suppresses_after_winner(self):
        sig, trades = _sig(_winner_skip_frame())
        self.assertEqual(trades[0]["system"], "S1")
        self.assertEqual(trades[0]["outcome"], "win")
        self.assertEqual(trades[0]["reason"], "channel")
        # Raw 20-bar breakout condition is true at bar 101...
        ind = indicators.add_indicators(_winner_skip_frame())
        self.assertTrue(ind["c"].iloc[101] > ind["dc20_high"].shift(1).iloc[101])
        # ...but the entry is skipped, and it is not a 55-bar breakout.
        self.assertFalse(bool(sig["long_entry"].iloc[101]))
        self.assertFalse(bool(sig["long_entry_s1"].iloc[101]))
        self.assertFalse(ind["c"].iloc[101] > ind["dc55_high"].shift(1).iloc[101])
        self.assertEqual(sig["long_entry_s2"].sum(), 0)

    def test_skip_allows_after_loser(self):
        sig, trades = _sig(_loser_allow_frame())
        self.assertEqual(trades[0]["outcome"], "loss")
        self.assertEqual(trades[0]["reason"], "stop")
        self.assertTrue(bool(sig["long_entry"].iloc[91]))
        self.assertTrue(bool(sig["long_entry_s1"].iloc[91]))
        self.assertEqual(sig["system"].iloc[91], "S1")

    def test_skip_disabled_takes_everything(self):
        sig, _ = _sig(_winner_skip_frame(), use_skip=False)
        self.assertTrue(bool(sig["long_entry_s1"].iloc[101]))
        self.assertTrue(bool(sig["long_entry"].iloc[101]))

    def test_s2_failsafe_fires_after_skip(self):
        sig, trades = _sig(_failsafe_frame())
        s2 = [t for t in trades if t["system"] == "S2"]
        self.assertEqual(len(s2), 1)
        self.assertEqual(s2[0]["side"], "long")
        self.assertEqual(s2[0]["entry_bar"], 101)
        self.assertTrue(bool(sig["long_entry_s2"].iloc[101]))
        self.assertTrue(bool(sig["long_entry"].iloc[101]))
        self.assertEqual(sig["system"].iloc[101], "S2")

    def test_s2_not_taken_without_prior_skip(self):
        # A first-bar monster breakout is a 20- and 55-bar breakout at
        # once: S1 takes precedence, no failsafe needed.
        n = 80
        o, h, l, c = _flat(n)
        o[60] = 100; h[60] = 141; l[60] = 100; c[60] = 140
        o[61:] = 140; h[61:] = 140.5; l[61:] = 139.5; c[61:] = 140
        sig, trades = _sig(_ohlc(o, h, l, c))
        self.assertTrue(bool(sig["long_entry_s1"].iloc[60]))
        self.assertFalse(bool(sig["long_entry_s2"].iloc[60]))
        self.assertEqual(sig["system"].iloc[60], "S1")


class TestExits(unittest.TestCase):
    def test_s1_exit_on_10bar_channel(self):
        sig, trades = _sig(_winner_skip_frame())
        t = trades[0]
        self.assertEqual(t["exit_signal_bar"], 76)
        self.assertTrue(bool(sig["long_exit"].iloc[76]))
        # exit executes at the next open
        self.assertAlmostEqual(t["entry_px"], 108.0)
        self.assertGreater(t["exit_bar"], t["exit_signal_bar"])

    def test_s2_ignores_10bar_cross_exits_on_20bar(self):
        sig, trades = _sig(_s2_exit_frame())
        s2 = [t for t in trades if t["system"] == "S2"]
        self.assertEqual(len(s2), 1)
        t = s2[0]
        # bar 126: 10-bar low crossed, 20-bar low not crossed -> no exit
        ind = indicators.add_indicators(_s2_exit_frame())
        c = ind["c"]
        x1 = B.crossed_below(c, ind["exit10_low"].shift(1)).fillna(False)
        x2 = B.crossed_below(c, ind["exit20_low"].shift(1)).fillna(False)
        self.assertTrue(bool(x1.iloc[126]))
        self.assertFalse(bool(x2.iloc[126]))
        self.assertFalse(bool(sig["long_exit"].iloc[126]))
        # the S2 trade exits on a 20-bar cross
        self.assertTrue(bool(x2.iloc[t["exit_signal_bar"]]))
        self.assertEqual(t["reason"], "channel")
        self.assertTrue(bool(sig["long_exit"].iloc[t["exit_signal_bar"]]))

    def test_2n_stop(self):
        _, trades = _sig(_loser_allow_frame())
        t = trades[0]
        self.assertEqual(t["reason"], "stop")
        # stop distance is 2 * ATR(20) at the signal bar
        ind = indicators.add_indicators(_loser_allow_frame())
        N = float(ind["atr"].iloc[60])
        self.assertAlmostEqual(t["entry_px"] - 2 * N, 103.3, delta=1.0)


class TestProperties(unittest.TestCase):
    def _rand_frame(self, n=400, seed=11):
        rng = np.random.default_rng(seed)
        rets = rng.normal(0.0005, 0.012, n)
        c = 100 * np.exp(np.cumsum(rets))
        o = np.concatenate([[100.0], c[:-1]])
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
        return _ohlc(o, h, l, c)

    def test_boolean_no_nan(self):
        sig, _ = _sig(self._rand_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit",
                    "long_entry_s1", "short_entry_s1",
                    "long_entry_s2", "short_entry_s2"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)
        self.assertFalse(sig["system"].isna().any())
        self.assertTrue(set(sig["system"].unique()) <= {"S1", "S2", ""})

    def test_no_lookahead(self):
        df = self._rand_frame()
        full, _ = _sig(df)
        j = 250
        trunc, _ = _sig(df.iloc[: j + 1])
        cols = ("long_entry", "short_entry", "long_exit", "short_exit",
                "long_entry_s1", "short_entry_s1",
                "long_entry_s2", "short_entry_s2")
        for col in cols:
            pd.testing.assert_series_equal(
                full[col].iloc[: j + 1].reset_index(drop=True),
                trunc[col].reset_index(drop=True), check_names=False)

    def test_deterministic(self):
        df = self._rand_frame()
        a, _ = _sig(df)
        b, _ = _sig(df)
        pd.testing.assert_frame_equal(a, b)


class TestRiskAndRegistration(unittest.TestCase):
    def test_risk_config_values(self):
        self.assertEqual(risk.RISK.atr_window, 20)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)   # the 2N stop
        self.assertIsNone(risk.RISK.trail_atr_mult)      # channel exits only
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 500)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 120)

    def test_registration(self):
        import strategies.turtle_classic as mod
        from strategies.registry import REGISTRY

        self.assertIn("turtle_classic", REGISTRY)
        self.assertIs(REGISTRY["turtle_classic"], mod.SPEC)
        self.assertEqual(mod.SPEC.slug, "turtle_classic")
        self.assertEqual(mod.SPEC.name, "Original Turtle Rules")
        self.assertEqual(mod.SPEC.source_name,
                         "Original Turtle Trading Rules (Curtis Faith, 2003)")
        self.assertEqual(mod.SPEC.source_url, "http://mql5.com/en/articles/23448")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})


if __name__ == "__main__":
    unittest.main()
