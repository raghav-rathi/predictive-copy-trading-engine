"""Vortex + ADX tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vortex_adx import indicators, risk, signals
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


def _flat_frame(n=1400, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _rising_frame(n=300):
    # Bars rising 1/bar, range 2: h = 100+i, l = 98+i, c = 99+i.
    # VM+ = 3, VM- = 1, TR = 2 -> VI+ -> 1.5, VI- -> 0.5.
    i = np.arange(n, dtype=float)
    h = 100.0 + i
    l = 98.0 + i
    c = 99.0 + i
    return _frame(c, highs=h, lows=l)


def _falling_frame(n=300):
    # Bars falling 1/bar, range 2: VM+ = 1, VM- = 3, TR = 2.
    i = np.arange(n, dtype=float)
    h = 100.0 - i
    l = 98.0 - i
    c = 99.0 - i
    return _frame(c, highs=h, lows=l)


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


class TestVortexAdx(unittest.TestCase):
    def test_registered(self):
        self.assertIn("vortex_adx", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_vi_hand_computed_rising(self):
        # Steady rise: VM+ = 3, VM- = 1, TR = 2, so the EMA ratios
        # converge to VI+ = 1.5, VI- = 0.5.
        df = indicators.add_indicators(_rising_frame(n=300))
        tail = df.iloc[200:]
        self.assertTrue(np.allclose(tail["vi_plus"], 1.5, atol=1e-9))
        self.assertTrue(np.allclose(tail["vi_minus"], 0.5, atol=1e-9))

    def test_vi_hand_computed_falling(self):
        # Steady fall: mirror image, VI+ -> 0.5, VI- -> 1.5.
        df = indicators.add_indicators(_falling_frame(n=300))
        tail = df.iloc[200:]
        self.assertTrue(np.allclose(tail["vi_plus"], 0.5, atol=1e-9))
        self.assertTrue(np.allclose(tail["vi_minus"], 1.5, atol=1e-9))

    def test_vi_formula_on_random_walk(self):
        # VI+ = EMA(VM+, 14) / EMA(TR, 14) recomputed by hand from the
        # raw columns; VI- the mirror. Checks the wiring, not the EMA.
        from strategies import base as B
        df = indicators.add_indicators(_random_walk_frame(n=400))
        raw = _random_walk_frame(n=400)
        vm_plus = (raw["h"] - raw["l"].shift(1)).abs()
        vm_minus = (raw["l"] - raw["h"].shift(1)).abs()
        tr = B.true_range(raw["h"], raw["l"], raw["c"])
        pd.testing.assert_series_equal(
            df["vi_plus"], B.ema(vm_plus, 14) / B.ema(tr, 14),
            check_names=False)
        pd.testing.assert_series_equal(
            df["vi_minus"], B.ema(vm_minus, 14) / B.ema(tr, 14),
            check_names=False)

    def test_adx_strong_on_trend(self):
        # A steady one-directional trend is a strong ADX regime.
        df = indicators.add_indicators(_rising_frame(n=300))
        self.assertGreater(df["adx"].iloc[-1], 25.0)

    def test_adx_weak_on_flat(self):
        # No directional movement at all: ADX is 0 / NaN, never strong.
        df = indicators.add_indicators(_flat_frame(n=300))
        tail = df["adx"].iloc[risk.WARMUP:]
        self.assertTrue(((tail < 20) | tail.isna()).all())

    def test_signal_logic_crafted_rows(self):
        # Cross up + strong ADX -> long entry; cross up + weak ADX ->
        # no entry; cross down + strong ADX -> short entry; ADX < 20
        # with no cross -> exit both sides.
        rows = [
            dict(vi_plus=0.9, vi_minus=1.0, adx=30.0),
            dict(vi_plus=1.1, vi_minus=1.0, adx=30.0),
            dict(vi_plus=1.2, vi_minus=1.0, adx=30.0),
            dict(vi_plus=1.2, vi_minus=1.0, adx=10.0),
            dict(vi_plus=0.9, vi_minus=1.0, adx=30.0),
            dict(vi_plus=0.9, vi_minus=1.0, adx=10.0),
        ]
        df = signals.add_signals(pd.DataFrame(rows))
        self.assertTrue(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])
        self.assertFalse(df["long_exit"].iloc[1])
        # Row 2: no new cross, no exit (ADX strong).
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])
        # Row 3: ADX fades below 20 -> both exits fire, no entry.
        self.assertTrue(df["long_exit"].iloc[3])
        self.assertTrue(df["short_exit"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[3])
        # Row 4: cross down + strong ADX -> short entry + long exit.
        self.assertTrue(df["short_entry"].iloc[4])
        self.assertTrue(df["long_exit"].iloc[4])
        # Row 5: cross already done, ADX weak -> exits stay on.
        self.assertTrue(df["long_exit"].iloc[5])
        # NaN ADX (warmup): no entry even on a cross.
        df = signals.add_signals(pd.DataFrame([
            dict(vi_plus=0.9, vi_minus=1.0, adx=np.nan),
            dict(vi_plus=1.1, vi_minus=1.0, adx=np.nan),
        ]))
        self.assertFalse(df["long_entry"].iloc[1])
        self.assertFalse(df["short_entry"].iloc[1])

    def test_no_entry_on_flat(self):
        # Flat bars: VM+ == VM- == TR, so VI+ == VI- == 1.0; no cross
        # ever fires and ADX never gets strong.
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["vi_plus"], 1.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["vi_minus"], 1.0, atol=1e-9))

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
        self.assertEqual(risk.WARMUP, 30)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
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
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending huge future jumps must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("vi_plus", "vi_minus", "adx", "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): VM and TR are 0, VI is 0/0 ->
        # NaN, never an entry.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
