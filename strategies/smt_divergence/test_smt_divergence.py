"""SMT divergence tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.smt_divergence import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(ohlc):
    """ohlc: list of (o, h, l, c) in hourly order from a fixed base."""
    n = len(ohlc)
    arr = np.array(ohlc, dtype=float)
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": arr[:, 0], "h": arr[:, 1], "l": arr[:, 2], "c": arr[:, 3],
        "v": np.full(n, 100.0),
    })


# Traded coin (bullish SMT): swing high 110 (centre 2), swing low 90
# (centre 7), swing high 112 (centre 12), swing low 85 (centre 17,
# lower than 90), then a rally; close 114 > 112 at bar 24.
_TRADED = [
    (100, 100, 99, 100),
    (105, 105, 104, 105),
    (110, 110, 109, 110),
    (105, 105, 104, 105),
    (100, 100, 99, 100),
    (102, 103, 98, 102),
    (100, 101, 95, 100),
    (95, 96, 90, 95),
    (98, 99, 95, 98),
    (100, 101, 98, 100),
    (103, 104, 99, 103),
    (107, 108, 103, 107),
    (111, 112, 107, 111),
    (105, 106, 101, 105),
    (101, 102, 97, 101),
    (99, 100, 95, 99),
    (96, 97, 92, 96),
    (88, 90, 85, 88),
    (93, 94, 90, 93),
    (97, 98, 94, 97),
    (99, 100, 96, 99),
    (104, 105, 100, 104),
    (109, 110, 104, 109),
    (112, 113, 108, 112),
    (114, 115, 111, 114),
]

# Reference coin: same shape, but the second swing low is 95 (centre
# 17, HIGHER than the prior low 90) -> bullish SMT divergence.
_REF = [
    (100, 100, 99, 100),
    (105, 105, 104, 105),
    (110, 110, 109, 110),
    (105, 105, 104, 105),
    (100, 100, 99, 100),
    (102, 103, 98, 102),
    (100, 101, 95, 100),
    (95, 96, 90, 95),
    (98, 99, 95, 98),
    (100, 101, 98, 100),
    (103, 104, 99, 103),
    (107, 108, 103, 107),
    (111, 112, 107, 111),
    (105, 106, 104, 105),
    (101, 102, 100, 101),
    (103, 104, 102, 103),
    (100, 101, 99, 100),
    (97, 98, 95, 97),
    (99, 100, 97, 99),
    (101, 102, 99, 101),
    (103, 104, 100, 103),
    (105, 106, 102, 105),
    (107, 108, 104, 107),
    (109, 110, 106, 109),
    (111, 112, 108, 111),
]


def _bull_merged():
    return indicators.build_merged_frame(_frame(_TRADED), _frame(_REF))


def _bear_merged():
    """Mirror of _bull_merged reflected about 200: short trigger at bar 24."""
    m = _bull_merged()
    return pd.DataFrame({
        "t": m["t"],
        "o": 200.0 - m["c"], "h": 200.0 - m["l"], "l": 200.0 - m["h"],
        "c": 200.0 - m["c"], "v": m["v"],
        "o_ref": 200.0 - m["c_ref"], "h_ref": 200.0 - m["l_ref"],
        "l_ref": 200.0 - m["h_ref"], "c_ref": 200.0 - m["c_ref"],
    })


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=1500, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


def _flat_merged(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    one = pd.DataFrame({"t": t, "o": close, "h": hi, "l": lo,
                        "c": close, "v": np.full(n, vol)})
    return indicators.build_merged_frame(one, one)


class TestSmtDivergence(unittest.TestCase):
    def test_registered(self):
        self.assertIn("smt_divergence", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(indicators.build_merged_frame(
            _random_walk_frame(), _random_walk_frame(seed=8)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_merged_frame_aligns_on_t(self):
        m = _bull_merged()
        self.assertEqual(len(m), 25)
        self.assertIn("c_ref", m.columns)
        self.assertAlmostEqual(m["c_ref"].iloc[17], 97.0)

    def test_pivots_confirmed_at_centre_plus_two(self):
        df = indicators.add_indicators(_bull_merged())
        # Traded swing high 110 (centre 2) visible from bar 4.
        self.assertTrue(np.isnan(df["t_swing_high"].iloc[3]))
        self.assertAlmostEqual(df["t_swing_high"].iloc[4], 110.0)
        # Traded swing low 90 (centre 7) visible from bar 9.
        self.assertTrue(np.isnan(df["t_swing_low"].iloc[8]))
        self.assertAlmostEqual(df["t_swing_low"].iloc[9], 90.0)
        # Reference swing low 95 (centre 17) visible from bar 19.
        self.assertAlmostEqual(df["r_swing_low"].iloc[19], 95.0)

    def test_bull_armed_at_divergence(self):
        df = indicators.add_indicators(_bull_merged())
        self.assertEqual(df["smt_state"].iloc[18], 0)
        self.assertEqual(df["smt_state"].iloc[19], 1)  # armed at bar 19
        self.assertEqual(df["smt_side"].iloc[19], -1)
        self.assertAlmostEqual(df["smt_level"].iloc[19], 112.0)

    def test_bull_long_trigger_on_structure_shift(self):
        df = _run(_bull_merged())
        self.assertFalse(df["long_entry"].iloc[:24].any())
        self.assertTrue(df["long_entry"].iloc[24])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertFalse(df["short_entry"].any())
        self.assertAlmostEqual(df["last_bull_div_low"].iloc[24], 85.0)

    def test_bear_short_trigger_on_mirrored_frame(self):
        df = _run(_bear_merged())
        self.assertFalse(df["short_entry"].iloc[:24].any())
        self.assertTrue(df["short_entry"].iloc[24])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertFalse(df["long_entry"].any())
        self.assertAlmostEqual(df["last_bear_div_high"].iloc[24], 115.0)

    def test_no_entry_when_ref_also_makes_lower_low(self):
        # Reference second low is 85 too (same as traded) -> no divergence.
        df = _run(indicators.build_merged_frame(_frame(_TRADED), _frame(_TRADED)))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_structure_shift(self):
        # Same divergence, but closes never get above the trigger 112.
        traded = list(_TRADED)
        traded[23] = (111, 112, 108, 111)
        traded[24] = (111, 112, 108, 111)
        df = _run(indicators.build_merged_frame(_frame(traded), _frame(_REF)))
        self.assertFalse(df["long_entry"].any())

    def test_no_entry_after_expiry(self):
        # Divergence arms at 19; bars 20-24 stay below the trigger 112,
        # then flat bars; the shift close only comes at bar 41 (22 bars
        # later, past the 20-bar expiry), above even the updated
        # trigger 115 from the swing high at centre 24.
        traded = list(_TRADED[:20]) + [
            (99, 100, 96, 99),
            (104, 105, 100, 104),
            (109, 110, 104, 109),
            (111, 112, 108, 111),
            (111, 112, 108, 111),
        ] + [(110, 111, 109, 110)] * 16
        traded.append((116, 117, 112, 116))  # bar 41
        ref = list(_REF) + [(111, 112, 108, 111)] * 16
        ref.append((112, 113, 109, 112))  # bar 41
        df = _run(indicators.build_merged_frame(_frame(traded), _frame(ref)))
        self.assertFalse(df["long_entry"].any())

    def test_invalidation_disarms(self):
        # Bar 21 closes 82, below the divergence low 85 -> disarmed;
        # later closes stay below the trigger 112 -> no entry.
        traded = list(_TRADED)
        traded[21] = (90, 95, 80, 82)
        traded[22] = (103, 105, 98, 103)
        traded[23] = (106, 108, 100, 106)
        traded[24] = (108, 110, 104, 108)
        df = _run(indicators.build_merged_frame(_frame(traded), _frame(_REF)))
        self.assertFalse(df["long_entry"].any())
        self.assertEqual(df["smt_state"].iloc[21], 0)  # disarmed by the close

    def test_exit_long_on_div_low_invalidation(self):
        rows = pd.DataFrame([dict(
            c=84.0, long_trigger=False, short_trigger=False,
            last_bull_div_low=85.0, last_bear_div_high=115.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_long_on_opposite_signal(self):
        rows = pd.DataFrame([dict(
            c=100.0, long_trigger=False, short_trigger=True,
            last_bull_div_low=85.0, last_bear_div_high=115.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

    def test_exit_short_mirror(self):
        rows = pd.DataFrame([dict(
            c=116.0, long_trigger=False, short_trigger=False,
            last_bull_div_low=85.0, last_bear_div_high=115.0)])
        df = signals.add_signals(rows)
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.atr_window, 14)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs)
        self.assertTrue(risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_backtest_smoke(self):
        df = _run(indicators.build_merged_frame(
            _random_walk_frame(), _random_walk_frame(seed=8)))
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        for key in ("trades", "win_rate", "net_pnl_usd", "sharpe",
                    "max_dd_pct", "expectancy_usd", "profit_factor",
                    "total_fees_usd"):
            self.assertIn(key, m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_no_lookahead_flat(self):
        df = _run(_flat_merged())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        df1 = _run(indicators.build_merged_frame(
            _random_walk_frame(1300, seed=3),
            _random_walk_frame(1300, seed=4)))
        rw_t = _random_walk_frame(1300, seed=3)
        rw_r = _random_walk_frame(1300, seed=4)
        extra_t = rw_t.tail(50).copy()
        extra_r = rw_r.tail(50).copy()
        for d in (extra_t, extra_r):
            d["c"] = d["c"] + 300.0
            d["o"] = d["o"] + 300.0
            d["h"] = d["h"] + 300.0
            d["l"] = d["l"] + 300.0
            d["t"] = d["t"] + 1300 * 3_600_000
        df2 = _run(indicators.build_merged_frame(
            pd.concat([rw_t, extra_t], ignore_index=True),
            pd.concat([rw_r, extra_r], ignore_index=True)))
        for col in ("t_swing_low", "smt_state", "smt_level", "long_entry",
                    "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_merged(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
