"""Funding Squeeze Reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.funding_squeeze_reversal import indicators, risk, signals
from strategies.funding_squeeze_reversal.indicators import (
    CONF_MIN, FUND_LONG_THR, FUND_SHORT_THR, VOL_MAX_RATIO, VOL_MIN_RATIO,
)

HOUR_MS = 3_600_000
T0 = 1_700_000_000_000


def _candles(n, funding_vals, vol_vals, px=100.0):
    """Synthetic 1h bars with a caller-supplied funding print per bar."""
    t = np.arange(n, dtype="int64") * HOUR_MS + T0
    rng = np.random.default_rng(3)
    rets = rng.normal(0, 0.002, n)
    c = px * np.exp(np.cumsum(rets))
    o = np.concatenate([[px], c[:-1]])
    h = np.maximum(o, c) * 1.002
    l = np.minimum(o, c) * 0.998
    funding = pd.Series(np.asarray(funding_vals, dtype=float),
                        index=pd.Index(t, name="t"))
    return (pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                          "v": np.asarray(vol_vals, dtype=float)}),
            funding)


def _run(n, funding_vals, vol_vals, px=100.0):
    df, funding = _candles(n, funding_vals, vol_vals, px)
    ind = indicators.add_indicators(df, funding=funding)
    return signals.add_signals(ind)


class TestFundingSqueezeReversal(unittest.TestCase):
    def test_fund8_hand_built(self):
        # constant hourly funding 0.00005 -> 8h sum = 0.00040
        n = 40
        df, funding = _candles(n, [0.00005] * n, [100.0] * n)
        ind = indicators.add_indicators(df, funding=funding)
        self.assertAlmostEqual(ind["fund8"].iloc[-1], 0.00040, places=9)
        self.assertTrue(ind["fund8"].iloc[:7].isna().all())

    def test_short_entry_fires(self):
        n = 60
        # funding spikes positive in the last 8 bars -> fund8 = 8*0.00006 = 0.00048 > thr
        fund = [0.0] * 52 + [0.00006] * 8  # fund8 = 0.00048
        vol = [100.0] * 59 + [250.0]  # ratio 2.33 in (1.5, 3.0)
        df = _run(n, fund, vol)
        self.assertTrue(bool(df["short_entry"].iloc[-1]))
        self.assertFalse(bool(df["long_entry"].iloc[-1]))

    def test_long_entry_fires(self):
        n = 60
        fund = [0.0] * 52 + [-0.00005] * 8  # fund8 = -0.00040
        vol = [100.0] * 59 + [250.0]
        df = _run(n, fund, vol)
        self.assertTrue(bool(df["long_entry"].iloc[-1]))

    def test_violent_volume_guard_blocks(self):
        n = 60
        fund = [0.0] * 52 + [0.00006] * 8
        vol = [100.0] * 59 + [500.0]  # ratio 5.0 > 3.0 -> violent, skip
        df = _run(n, fund, vol)
        self.assertFalse(bool(df["short_entry"].iloc[-1]))

    def test_low_volume_blocks(self):
        n = 60
        fund = [0.0] * 52 + [0.00006] * 8
        vol = [100.0] * n  # ratio 1.0 < 1.5
        df = _run(n, fund, vol)
        self.assertFalse(bool(df["short_entry"].iloc[-1]))

    def test_confidence_formula_hand_built(self):
        n = 60
        fund = [0.0] * 52 + [0.00006] * 8  # fund8 = 0.00048
        vol = [100.0] * 59 + [250.0]  # ratio 250/107.5 = 2.32558
        df, funding = _candles(n, fund, vol)
        ind = indicators.add_indicators(df, funding=funding)
        fund_int = min(1.0, 0.00048 / (3.0 * FUND_SHORT_THR))
        vol_int = min(1.0, ((250.0 / 107.5) - VOL_MIN_RATIO) / VOL_MIN_RATIO)
        expect = 0.6 * fund_int + 0.4 * vol_int
        self.assertAlmostEqual(ind["fsr_conf"].iloc[-1], expect, places=6)
        self.assertGreaterEqual(ind["fsr_conf"].iloc[-1], CONF_MIN)

    def test_no_lookahead_truncation(self):
        rng = np.random.default_rng(11)
        n = 120
        fund = rng.normal(0, 0.0001, n).tolist()
        vol = np.abs(rng.normal(120, 30, n)).tolist()
        df, funding = _candles(n, fund, vol)
        full = indicators.add_indicators(df, funding=funding)
        for i in (60, 100):
            tr = indicators.add_indicators(df.iloc[: i + 1],
                                           funding=funding)
            for col in ("fund8", "vol_ratio", "fsr_conf"):
                a, b = full[col].iloc[i], tr[col].iloc[i]
                self.assertTrue(
                    (pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-12, (col, i))

    def test_signals_boolean_clean_and_reversing(self):
        rng = np.random.default_rng(5)
        n = 120
        fund = rng.normal(0, 0.0002, n).tolist()
        vol = np.abs(rng.normal(120, 60, n)).tolist()
        df = _run(n, fund, vol)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any(), col)
            self.assertTrue(set(df[col].unique()) <= {True, False}, col)
        pd.testing.assert_series_equal(df["long_exit"], df["short_entry"],
                                       check_names=False)
        pd.testing.assert_series_equal(df["short_exit"], df["long_entry"],
                                       check_names=False)

    def test_requires_coin_or_funding(self):
        df, _ = _candles(30, [0.0] * 30, [100.0] * 30)
        with self.assertRaises(ValueError):
            indicators.add_indicators(df)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 12)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 96)


if __name__ == "__main__":
    unittest.main()
