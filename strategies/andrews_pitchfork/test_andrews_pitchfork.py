"""Andrews Pitchfork tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.andrews_pitchfork import indicators, risk, signals
from strategies import registry
from strategies.backtest import run_backtest


def _frame(closes, highs=None, lows=None, vols=None, opens=None):
    closes = np.array(closes, dtype=float)
    n = len(closes)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    h = np.array(highs, dtype=float) if highs is not None else closes + 0.5
    l = np.array(lows, dtype=float) if lows is not None else closes - 0.5
    o = np.array(opens, dtype=float) if opens is not None else np.concatenate([[closes[0]], closes[:-1]])
    v = np.array(vols, dtype=float) if vols is not None else np.full(n, 100.0)
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": closes, "v": v})


def _legs_frame(legs, tail, preamble=30, step=6):
    closes = [legs[0]] * preamble
    for a, b in zip(legs, legs[1:]):
        for k in range(1, step + 1):
            closes.append(a + (b - a) * k / step)
    closes.extend(tail)
    return _frame(closes)


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


def _random_walk_frame(n=400, seed=7):
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0005, 0.01, n)
    c = 100 * np.exp(np.cumsum(rets))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({
        "t": (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64"),
        "o": o, "h": c + 0.5, "l": c - 0.5, "c": c,
        "v": np.full(n, 100.0),
    })


# Bullish fork: P0=90 (low), P1=110 (high), P2=95 (low, above P0).
# Median runs P0 -> midpoint(110, 95) = 102.5; lower parallel through P2.
BULL_LEGS = [100, 90, 110, 95]
BULL_TAIL = [96, 98, 100, 102, 104, 106, 108, 110]
# Bearish mirror: P0=110 (high), P1=90 (low), P2=105 (high, below P0).
BEAR_LEGS = [100, 110, 90, 105]
BEAR_TAIL = [104, 102, 100, 98, 96, 94, 92, 90]


def _bounce_frame(legs, tail, direction):
    """Base legs frame + a decline/rise bar + a touch bar on the fork line.

    Returns (df, touch_bar_index). The touch bar's low (long) or high
    (short) sits on the fork parallel and the close is back inside it.
    """
    base = _legs_frame(legs, tail)
    ind = indicators.add_indicators(base)
    n0 = len(base)
    closes = list(base["c"])
    highs = list(base["h"])
    lows = list(base["l"])
    if direction == 1:
        line = ind["pf_bull_lower"].to_numpy()
        slope = line[-1] - line[-2]
        closes.append(109.0); highs.append(109.5); lows.append(108.5)
        lv = line[-1] + slope * 2
        closes.append(lv + 0.3); highs.append(lv + 0.8); lows.append(lv - 0.1)
    else:
        line = ind["pf_bear_upper"].to_numpy()
        slope = line[-1] - line[-2]
        closes.append(91.0); highs.append(91.5); lows.append(90.5)
        lv = line[-1] + slope * 2
        closes.append(lv - 0.3); highs.append(lv + 0.1); lows.append(lv - 0.8)
    return _frame(closes, highs, lows), n0 + 1


class TestAndrewsPitchfork(unittest.TestCase):
    def test_registered(self):
        self.assertIn("andrews_pitchfork", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicators_finite_after_warmup(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.isfinite(tail["atr14"]).all())

    def test_risk_config_sane(self):
        self.assertGreater(risk.RISK.stop_atr_mult, 0)
        self.assertGreater(risk.RISK.max_leverage, 0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIn("trades", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_fork_geometry_bullish(self):
        df = indicators.add_indicators(_legs_frame(BULL_LEGS, BULL_TAIL))
        self.assertTrue(df["pf_bullish"].any())
        # Lower < median < upper on every active bar.
        act = df[df["pf_bullish"] == 1.0]
        self.assertTrue((act["pf_bull_lower"] < act["pf_bull_median"]).all())
        self.assertTrue((act["pf_bull_median"] < act["pf_bull_upper"]).all())
        # Median passes through the midpoint of P1-P2: pivots are
        # h/l-based (P0=89.5, P1=110.5, P2=94.5), midpoint 102.5 at bar 44,
        # slope 13/9; the fork is only known from the P2-confirm bar (49).
        self.assertAlmostEqual(df.loc[49, "pf_bull_median"],
                               89.5 + (13.0 / 9.0) * 14, places=4)

    def test_fork_geometry_bearish(self):
        df = indicators.add_indicators(_legs_frame(BEAR_LEGS, BEAR_TAIL))
        self.assertTrue(df["pf_bearish"].any())
        act = df[df["pf_bearish"] == 1.0]
        self.assertTrue((act["pf_bear_lower"] < act["pf_bear_median"]).all())
        self.assertTrue((act["pf_bear_median"] < act["pf_bear_upper"]).all())
        # Pivots h/l-based (P0=110.5, P1=89.5, P2=105.5), midpoint 97.5 at
        # bar 44, slope -13/9; fork known from the P2-confirm bar (49).
        self.assertAlmostEqual(df.loc[49, "pf_bear_median"],
                               110.5 - (13.0 / 9.0) * 14, places=4)

    def test_long_entry_on_lower_parallel_bounce(self):
        df, touch = _bounce_frame(BULL_LEGS, BULL_TAIL, 1)
        out = _run(df)
        self.assertTrue(out.loc[touch, "long_entry"])

    def test_short_entry_on_upper_parallel_bounce(self):
        df, touch = _bounce_frame(BEAR_LEGS, BEAR_TAIL, -1)
        out = _run(df)
        self.assertTrue(out.loc[touch, "short_entry"])

    def test_long_exit_at_median_line(self):
        df, touch = _bounce_frame(BULL_LEGS, BULL_TAIL, 1)
        closes = list(df["c"]); highs = list(df["h"]); lows = list(df["l"])
        # Climb faster than the rising median line until the close reaches it.
        for _ in range(12):
            closes.append(closes[-1] + 3.5)
            highs.append(closes[-1] + 0.5)
            lows.append(closes[-1] - 0.5)
        out = _run(_frame(closes, highs, lows))
        self.assertTrue(out.loc[touch, "long_entry"])
        self.assertTrue(out["long_exit"].any())
        first_exit = out.index[out["long_exit"]][0]
        self.assertGreater(first_exit, touch)

    def test_no_lookahead_flat(self):
        closes = [100.0] * 120
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_entry_without_touch(self):
        # Price stays well above the lower parallel: no bounce, no entry
        # after the P2-confirm bar (index 49 may fire on the pullback
        # itself, so check only bars after the rising tail).
        df = _run(_legs_frame(BULL_LEGS, [120, 122, 124, 126, 128, 130]))
        self.assertFalse(df["long_entry"].iloc[56:].any())

    def test_no_fork_when_p2_below_p0(self):
        # L,H,L triple with P2 (88) below P0 (90): no bullish fork.
        df = indicators.add_indicators(
            _legs_frame([100, 90, 110, 88], [89, 90, 91, 92]))
        self.assertFalse(df["pf_bullish"].any())


if __name__ == "__main__":
    unittest.main()
