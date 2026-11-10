"""Chande Dynamic Momentum Index tests. Network-free, synthetic data only."""

import os
import statistics
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.chande_dmi import indicators, risk, signals
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


def _flat_frame(n=200, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


def _signal_frame(dmi, closes=None):
    n = len(dmi)
    c = np.array(closes, dtype=float) if closes is not None else np.full(n, 100.0)
    return pd.DataFrame({"c": c, "dmi": np.array(dmi, dtype=float)})


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


def _reference_dmi(closes):
    """Independent plain-Python reference for the DMI pipeline.

    Uses statistics.stdev (sample std) and explicit loops, sharing no
    code with strategies.chande_dmi.indicators.
    """
    closes = [float(x) for x in closes]
    n = len(closes)
    vol = [float("nan")] * n
    for i in range(4, n):
        vol[i] = statistics.stdev(closes[i - 4 : i + 1])
    vol_avg = [float("nan")] * n
    for i in range(13, n):
        vol_avg[i] = sum(vol[i - 9 : i + 1]) / 10.0
    out_td = [float("nan")] * n
    out_dmi = [float("nan")] * n
    for i in range(13, n):
        va = vol_avg[i]
        vi = 1.0 if va == 0.0 else vol[i] / va
        if vi <= 0.0:
            td = 30
        else:
            td = max(5, min(30, round(14 / vi)))
        out_td[i] = float(td)
        if i >= td:
            gains = sum(max(closes[j] - closes[j - 1], 0.0) for j in range(i - td + 1, i + 1))
            losses = sum(max(closes[j - 1] - closes[j], 0.0) for j in range(i - td + 1, i + 1))
            out_dmi[i] = 50.0 if gains + losses == 0.0 else 100.0 * gains / (gains + losses)
    return out_td, out_dmi


class TestChandeDmi(unittest.TestCase):
    def test_registered(self):
        self.assertIn("chande_dmi", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat price: vol = 0, vol_avg = 0 -> Vi = 1.0, TD = 14,
        # no gains/losses -> DMI = 50. Hand-computed from the spec.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["dmi_vol"], 0.0))
        self.assertTrue(np.allclose(tail["dmi_vol_avg"], 0.0))
        self.assertTrue(np.allclose(tail["dmi_vi"], 1.0))
        self.assertTrue(np.allclose(tail["dmi_td"], 14.0))
        self.assertTrue(np.allclose(tail["dmi"], 50.0))
        # First valid DMI needs i >= TD = 14.
        self.assertTrue(df["dmi"].iloc[:14].isna().all())
        self.assertEqual(df["dmi"].iloc[14], 50.0)

    def test_indicator_values_steady_uptrend(self):
        # Constant +1 per bar: every 5-bar window has sample std
        # sqrt(2.5), so Vi = 1, TD = 14; all 14 changes are gains,
        # so DMI = 100. Hand-computed from the spec.
        closes = [100.0 + i for i in range(60)]
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[30:]
        self.assertTrue(np.allclose(tail["dmi_td"], 14.0))
        self.assertTrue(np.allclose(tail["dmi"], 100.0))
        self.assertTrue(np.allclose(tail["dmi_vi"], 1.0))
        self.assertTrue(np.allclose(tail["dmi_vol"], np.sqrt(2.5)))

    def test_indicator_values_alternating(self):
        # Alternating 100/110: every 5-bar window has the same sample
        # std, so Vi = 1, TD = 14; over 14 changes there are 7 gains
        # of 10 and 7 losses of 10, so DMI = 50. Hand-computed.
        closes = [100.0 if i % 2 == 0 else 110.0 for i in range(60)]
        df = indicators.add_indicators(_frame(closes))
        tail = df.iloc[30:]
        self.assertTrue(np.allclose(tail["dmi_td"], 14.0))
        self.assertTrue(np.allclose(tail["dmi"], 50.0))

    def test_td_clamp_floor_on_volatility_spike(self):
        # 40 flat bars, then a jump 100 -> 200. At the jump bar:
        # vol = stdev([100,100,100,100,200]) = sqrt(2000) = 44.72,
        # vol_avg = 44.72/10 = 4.472, Vi = 10, round(14/10) = 1
        # -> clamped to TD = 5. Last 5 changes are 0,0,0,0,+100,
        # so DMI = 100. Hand-computed from the spec.
        closes = [100.0] * 40 + [200.0] * 20
        df = indicators.add_indicators(_frame(closes))
        self.assertEqual(df["dmi_td"].iloc[40], 5.0)
        self.assertEqual(df["dmi"].iloc[40], 100.0)

    def test_td_clamp_ceiling_when_volatility_dies(self):
        # 30 alternating bars, then flat at 110. At bar 38 the
        # 5-bar vol is 0 but vol_avg is still positive, so Vi = 0
        # and TD clamps to 30. Over the last 30 changes (indices
        # 9..38): 11 gains of 10, 10 losses of 10, 9 zeros, so
        # DMI = 100 * 110 / 210 = 52.38095. Hand-computed.
        closes = [100.0 if i % 2 == 0 else 110.0 for i in range(30)] + [110.0] * 60
        df = indicators.add_indicators(_frame(closes))
        self.assertEqual(df["dmi_td"].iloc[38], 30.0)
        self.assertAlmostEqual(df["dmi"].iloc[38], 100.0 * 110.0 / 210.0, places=5)

    def test_indicator_matches_independent_reference(self):
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(11).normal(0.0005, 0.01, 300))))
        df = indicators.add_indicators(_frame(closes))
        ref_td, ref_dmi = _reference_dmi(closes)
        np.testing.assert_allclose(
            df["dmi_td"].to_numpy(dtype=float), np.array(ref_td, dtype=float),
            rtol=1e-9, atol=1e-9, equal_nan=True)
        np.testing.assert_allclose(
            df["dmi"].to_numpy(dtype=float), np.array(ref_dmi, dtype=float),
            rtol=1e-9, atol=1e-9, equal_nan=True)

    def test_indicator_bounds_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.isfinite(tail["dmi"]).all())
        self.assertTrue(((tail["dmi"] >= 0.0) & (tail["dmi"] <= 100.0)).all())
        self.assertTrue(((tail["dmi_td"] >= 5.0) & (tail["dmi_td"] <= 30.0)).all())
        self.assertTrue(np.isfinite(tail["dmi_vi"]).all())
        self.assertTrue((tail["dmi_vi"] >= 0.0).all())

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
        self.assertEqual(risk.WARMUP, 45)

    def test_backtest_smoke(self):
        df = _run(_random_walk_frame())
        res = run_backtest(df, risk.RISK, coin="BTC", interval="1h",
                           warmup=risk.WARMUP, use_funding=False)
        m = res.metrics()
        self.assertIsInstance(m, dict)
        self.assertIn("trades", m)
        self.assertIn("net_pnl_usd", m)
        self.assertGreaterEqual(m["trades"], 0)

    def test_long_entry_on_cross_up_30(self):
        # DMI crosses up through 30 at index 2.
        df = signals.add_signals(_signal_frame([20, 25, 35, 40, 45]))
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[3])
        self.assertFalse(df["short_entry"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_short_entry_on_cross_down_70(self):
        # DMI crosses down through 70 at index 2.
        df = signals.add_signals(_signal_frame([80, 75, 65, 60, 55]))
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertFalse(df["short_entry"].iloc[3])
        self.assertFalse(df["long_entry"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])

    def test_exits(self):
        # DMI crossing above 70 exits a long.
        df = signals.add_signals(_signal_frame([60, 65, 75]))
        self.assertTrue(df["long_exit"].iloc[2])
        self.assertFalse(df["short_exit"].iloc[2])
        # DMI crossing below 30 exits a short.
        df = signals.add_signals(_signal_frame([40, 35, 25]))
        self.assertTrue(df["short_exit"].iloc[2])
        self.assertFalse(df["long_exit"].iloc[2])

    def test_no_signal_without_cross(self):
        # DMI stays above 30 the whole time: no long entry.
        df = signals.add_signals(_signal_frame([35, 40, 45, 50]))
        self.assertFalse(df["long_entry"].any())
        # DMI stays below 70: no short entry, no long exit.
        self.assertFalse(df["short_entry"].any())
        self.assertFalse(df["long_exit"].any())
        # NaN DMI produces no signals.
        df = signals.add_signals(_signal_frame([np.nan, np.nan, 35.0, 40.0]))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_no_lookahead_future_jump(self):
        # Appending a huge future jump must not change any indicator or
        # signal value on the bars before the jump.
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 200))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [200.0] * 50))
        for col in ("dmi", "dmi_td", "dmi_vi", "long_entry", "short_entry"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:200].reset_index(drop=True),
                df2[col].iloc[:200].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the DMI lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["dmi"].isna().all())
        # Zero-range bars (h == l == c): flat DMI 50, no entries.
        df = _run(_frame([100.0] * 200, highs=[100.0] * 200,
                         lows=[100.0] * 200))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["dmi"], 50.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
