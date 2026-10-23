"""Rolling VWAP cross tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.vwap_cross import indicators, risk, signals
from strategies.vwap_cross.indicators import rolling_vwap, VWAP_N
from strategies.vwap_cross.signals import VOL_RATIO_MIN


def _frame_from_parts(o, h, l, c, v):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _flat_frame(n=200, close=100.0, vol=100.0):
    c = np.full(n, close)
    h = c * 1.001
    l = c * 0.999
    return _frame_from_parts(c, h, l, c, np.full(n, vol))


def _frame_from_close(c, seed=7):
    c = np.asarray(c, dtype=float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    rng = np.random.default_rng(seed)
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
    v = rng.uniform(50, 150, n)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": v})


def _random_walk_frame(n=500, seed=7, drift=0.0005, vol=0.01):
    rng = np.random.default_rng(seed)
    rets = rng.normal(drift, vol, n)
    c = 100 * np.exp(np.cumsum(rets))
    return _frame_from_close(c, seed)


class TestIndicators(unittest.TestCase):
    def test_columns_present(self):
        ind = indicators.add_indicators(_random_walk_frame())
        for col in ("vwap", "vwap_slope", "vol_ratio", "atr"):
            self.assertIn(col, ind.columns)

    def test_vwap_hand_computation(self):
        # 24 bars: tp and v all 1 except hand-set; VWAP over the full
        # window = sum(tp*v)/sum(v). Use tp=[100..123] (h=l=c), v=[1..24].
        n = 24
        tp = np.arange(100.0, 100.0 + n)
        v = np.arange(1.0, 1.0 + n)
        tps = pd.Series(tp)
        vs = pd.Series(v)
        expected = float((tps * vs).sum() / vs.sum())
        self.assertAlmostEqual(float(rolling_vwap(tps, vs, n).iloc[-1]), expected, places=9)

    def test_vwap_known_window_value(self):
        # h=l=c=100, v=1 for all 24 bars -> VWAP exactly 100.
        n = 24
        df = _flat_frame(n, close=100.0, vol=1.0)
        tp = (df["h"] + df["l"] + df["c"]) / 3.0
        got = rolling_vwap(tp, df["v"], n).iloc[-1]
        self.assertAlmostEqual(float(got), 100.0, places=9)

    def test_vwap_weights_by_volume(self):
        # Same prices, volume skewed late -> VWAP closer to the high close.
        n = 24
        c = np.linspace(100.0, 124.0, n)
        v = np.ones(n)
        v[12:] = 10.0  # heavy flow on the higher-priced half
        df = _frame_from_parts(c, c, c, c, v)
        tp = (df["h"] + df["l"] + df["c"]) / 3.0
        got = float(rolling_vwap(tp, df["v"], n).iloc[-1])
        plain_mean = float(tp.mean())
        self.assertGreater(got, plain_mean)

    def test_zero_volume_guard_falls_back_to_typical_price(self):
        # All-zero volume -> no volume to weight by -> vwap == tp.
        n = 24
        c = np.linspace(100.0, 124.0, n)
        df = _frame_from_parts(c, c, c, c, np.zeros(n))
        tp = (df["h"] + df["l"] + df["c"]) / 3.0
        got = rolling_vwap(tp, df["v"], n).iloc[-1]
        self.assertAlmostEqual(float(got), float(tp.iloc[-1]), places=9)

    def test_slope_positive_when_vwap_rising(self):
        ind = indicators.add_indicators(_flat_frame(300, close=100.0))
        # steadily rising closes after flat start
        c = np.concatenate([np.full(100, 100.0), np.linspace(100.0, 120.0, 200)])
        df = _frame_from_close(c)
        ind = indicators.add_indicators(df)
        self.assertGreater(float(ind["vwap_slope"].iloc[-1]), 0.0)

    def test_vol_ratio_spikes_on_heavy_bar(self):
        n = 60
        df = _flat_frame(n, close=100.0, vol=100.0)
        df = df.copy()
        df.loc[df.index[-1], "v"] = 500.0  # 5x on the last bar
        ind = indicators.add_indicators(df)
        self.assertGreater(float(ind["vol_ratio"].iloc[-1]), VOL_RATIO_MIN)

    def test_no_lookahead(self):
        # vwap at bar j must not change when later bars are appended.
        df = _random_walk_frame()
        short = df.iloc[:200]
        ind_full = indicators.add_indicators(df)
        ind_short = indicators.add_indicators(short)
        pd.testing.assert_series_equal(
            ind_full["vwap"].iloc[:200].reset_index(drop=True),
            ind_short["vwap"].reset_index(drop=True),
            check_names=False,
        )


class TestSignals(unittest.TestCase):
    def _signal_frame(self):
        return signals.add_signals(indicators.add_indicators(_random_walk_frame()))

    def test_signal_columns_boolean_no_nan(self):
        sig = self._signal_frame()
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(sig[col].dtype == bool, col)
            self.assertFalse(sig[col].isna().any(), col)

    def _direct_frame(self, slope_per_bar=0.05, cross_bar=50,
                      vol_at_cross=2.0, direction=1):
        """Fully deterministic frame: VWAP is a straight ramp (no noise).

        direction=1:  close rides 1 below vwap, jumps 1 above at cross_bar
                      (a clean cross_above on bar cross_bar).
        direction=-1: close rides 1 above vwap, drops 1 below at cross_bar.
        """
        n = 100
        vwap = 100.0 + slope_per_bar * np.arange(n)
        close = np.empty(n)
        if direction == 1:
            close[:] = vwap - 1.0
            close[cross_bar:] = vwap[cross_bar:] + 1.0
        else:
            close[:] = vwap + 1.0
            close[cross_bar:] = vwap[cross_bar:] - 1.0
        vol_ratio = np.ones(n)
        vol_ratio[cross_bar] = vol_at_cross
        vwap_slope = pd.Series(vwap).diff(3).fillna(0.0).to_numpy()
        df = _frame_from_close(close, seed=9)
        df["vwap"] = vwap
        df["vwap_slope"] = vwap_slope
        df["vol_ratio"] = vol_ratio
        return df

    def test_long_entry_requires_cross_rising_slope_and_volume(self):
        # Clean cross above, rising VWAP (slope = 3*0.05 = 0.15 > 0),
        # 2.0x volume -> long_entry fires exactly at the cross bar.
        df = self._direct_frame(slope_per_bar=0.05, vol_at_cross=2.0,
                                direction=1)
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_entry"].iloc[50])
        self.assertEqual(int(sig["long_entry"].sum()), 1)

    def test_flat_vwap_blocks_cross(self):
        # Same clean cross but the VWAP is dead flat -> slope == 0
        # everywhere -> the slope filter blocks the entry.
        df = self._direct_frame(slope_per_bar=0.0, vol_at_cross=2.0,
                                direction=1)
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())

    def test_low_volume_blocks_cross(self):
        # Clean cross above a rising VWAP, but the cross prints on
        # 0.5x average volume -> the volume filter blocks the entry.
        df = self._direct_frame(slope_per_bar=0.05, vol_at_cross=0.5,
                                direction=1)
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].any())

    def test_exit_on_opposite_cross(self):
        # After the long entry at bar 50, close drops back below the
        # VWAP at bar 70 -> long_exit fires exactly there (no filters
        # on exits).
        df = self._direct_frame(slope_per_bar=0.05, vol_at_cross=2.0,
                                direction=1)
        vwap = df["vwap"].to_numpy()
        close = df["c"].to_numpy().copy()
        close[70:] = vwap[70:] - 1.0
        df["c"] = close
        sig = signals.add_signals(df)
        self.assertTrue(sig["long_exit"].iloc[70])
        self.assertFalse(sig["long_exit"].iloc[50])

    def test_short_entry_symmetry(self):
        # Mirror: falling VWAP (slope = -0.15), clean cross below on
        # 2.0x volume -> short_entry fires exactly at the cross bar.
        df = self._direct_frame(slope_per_bar=-0.05, vol_at_cross=2.0,
                                direction=-1)
        sig = signals.add_signals(df)
        self.assertTrue(sig["short_entry"].iloc[50])
        self.assertEqual(int(sig["short_entry"].sum()), 1)


class TestRisk(unittest.TestCase):
    def test_risk_config_values(self):
        r = risk.RISK
        self.assertEqual(r.atr_window, 14)
        self.assertEqual(r.stop_atr_mult, 1.5)
        self.assertEqual(r.trail_atr_mult, 2.0)
        self.assertIsNone(r.target_atr_mult)
        self.assertEqual(r.max_hold_bars, 72)
        self.assertEqual(r.risk_frac, 0.01)
        self.assertEqual(r.max_leverage, 3.0)
        self.assertAlmostEqual(r.fee_rate, 0.00045)
        self.assertAlmostEqual(r.slippage_rate, 0.0001)
        self.assertTrue(r.allow_longs)
        self.assertTrue(r.allow_shorts)

    def test_warmup(self):
        self.assertEqual(risk.WARMUP, 60)

    def test_end_to_end_pipeline_runs(self):
        sig = signals.add_signals(indicators.add_indicators(_random_walk_frame()))
        from strategies import backtest as BT
        res = BT.run_backtest(sig, risk.RISK, coin="BTC", warmup=risk.WARMUP,
                              use_funding=False)
        m = res.metrics()
        self.assertGreaterEqual(m["trades"], 0)
        self.assertIn("sharpe", m)


if __name__ == "__main__":
    unittest.main()
