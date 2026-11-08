"""Rolling volume-profile POC tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.volume_profile_poc import indicators, risk, signals
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


def _flat_frame(n=300, close=100.0, hi=101.0, lo=99.0, vol=100.0):
    return _frame([close] * n, highs=[hi] * n, lows=[lo] * n,
                  vols=[vol] * n)


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


def _manual_profile(df, i, window=168, n_bins=24):
    """Independent reimplementation of the window profile at bar i."""
    sl = slice(i - window + 1, i + 1)
    lo = df["l"].iloc[sl].min()
    hi = df["h"].iloc[sl].max()
    edges = np.linspace(lo, hi, n_bins + 1)
    idx = np.clip(np.digitize(df["c"].iloc[sl].to_numpy(), edges[1:-1]),
                  0, n_bins - 1)
    vb = np.bincount(idx, weights=df["v"].iloc[sl].to_numpy(),
                     minlength=n_bins)
    pb = int(np.argmax(vb))
    in_bin = idx == pb
    w = df["v"].iloc[sl].to_numpy()[in_bin]
    if len(w) and float(np.sum(w)) > 0:
        return float(np.average(df["c"].iloc[sl].to_numpy()[in_bin],
                                weights=w))
    return float((edges[pb] + edges[pb + 1]) / 2.0)


class TestVolumeProfilePoc(unittest.TestCase):
    def test_registered(self):
        self.assertIn("volume_profile_poc", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes at 100 in a 99-101 window: all volume lands in
        # one bin, so POC is the volume-weighted mean close of that
        # bin (exactly 100) and VAH/VAL are its bounds.
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["vp_poc"], 100.0))
        self.assertTrue((tail["vp_val"] <= tail["vp_poc"]).all())
        self.assertTrue((tail["vp_poc"] <= tail["vp_vah"]).all())
        self.assertTrue(np.allclose(tail["atr14"], 2.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (200, 250, 399):
            self.assertAlmostEqual(df["vp_poc"].iloc[i],
                                   _manual_profile(df, i), places=9)
            self.assertLessEqual(df["vp_val"].iloc[i], df["vp_poc"].iloc[i])
            self.assertGreaterEqual(df["vp_vah"].iloc[i], df["vp_poc"].iloc[i])
            # Value area holds >= 70% of window volume by construction.
            sl = slice(i - 167, i + 1)
            edges = np.linspace(df["l"].iloc[sl].min(),
                                df["h"].iloc[sl].max(), 25)
            idx = np.clip(np.digitize(df["c"].iloc[sl].to_numpy(),
                                      edges[1:-1]), 0, 23)
            vb = np.bincount(idx, weights=df["v"].iloc[sl].to_numpy(),
                             minlength=24)
            lo_b = int(np.searchsorted(edges, df["vp_val"].iloc[i]))
            hi_b = int(np.searchsorted(edges, df["vp_vah"].iloc[i])) - 1
            in_area = np.zeros(24, dtype=bool)
            in_area[lo_b:hi_b + 1] = True
            self.assertGreaterEqual(vb[in_area].sum() / vb.sum(), 0.70 - 1e-9)

    def test_value_area_single_bin_when_concentrated(self):
        # All closes identical: one bin holds 100% of volume, so
        # VAH/VAL are that single bin's bounds.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["vp_vah"] - tail["vp_val"],
                                    2.0 / 24, atol=1e-9))

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

    def _trend_base(self, n=300, start=100.0, step=0.05, sign=1):
        c = start + sign * step * np.arange(n)
        return _frame(c)

    def test_long_entry_pullback_to_poc(self):
        base = self._trend_base(sign=1)
        ind = indicators.add_indicators(base)
        poc = ind["vp_poc"].iloc[-1]
        a = ind["atr14"].iloc[-1]
        # Prior close is above its POC in a steady uptrend.
        self.assertGreater(base["c"].iloc[-1], ind["vp_poc"].iloc[-1])
        # Dip bar: low near POC, close back above POC. High/low stay
        # inside the window's existing range so the profile edges
        # do not shift.
        dip_close = poc + 0.5
        dip = _frame([dip_close], highs=[dip_close + 0.5],
                     lows=[poc - 0.1 * a])
        df = _run(pd.concat([base, dip], ignore_index=True))
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_short_entry_pullback_to_poc(self):
        base = self._trend_base(sign=-1)
        ind = indicators.add_indicators(base)
        poc = ind["vp_poc"].iloc[-1]
        a = ind["atr14"].iloc[-1]
        self.assertLess(base["c"].iloc[-1], ind["vp_poc"].iloc[-1])
        dip_close = poc - 0.5
        dip = _frame([dip_close], highs=[poc + 0.1 * a],
                     lows=[dip_close - 0.5])
        df = _run(pd.concat([base, dip], ignore_index=True))
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_cross_from_below(self):
        # Close back above POC, but the prior bar's close was below
        # its POC: a cross from below, not a pullback from above.
        base = self._trend_base(sign=-1)
        ind = indicators.add_indicators(base)
        poc = ind["vp_poc"].iloc[-1]
        a = ind["atr14"].iloc[-1]
        bar = _frame([poc + 0.2], highs=[poc + 0.5],
                     lows=[poc - 0.1 * a])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_low_never_near_poc(self):
        # Bar closes above POC but its low stays well above POC +
        # 0.5*ATR: no dip to POC, no entry.
        base = self._trend_base(sign=1)
        ind = indicators.add_indicators(base)
        poc = ind["vp_poc"].iloc[-1]
        a = ind["atr14"].iloc[-1]
        bar = _frame([poc + 2.0 * a], highs=[poc + 2.0 * a + 0.5],
                     lows=[poc + 1.5 * a])
        df = _run(pd.concat([base, bar], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_long_exit_at_vah_and_below_poc(self):
        base = self._trend_base(sign=1)
        ind = indicators.add_indicators(base)
        poc = ind["vp_poc"].iloc[-1]
        vah = ind["vp_vah"].iloc[-1]
        bar_vah = _frame([vah + 0.5], highs=[vah + 0.5], lows=[vah])
        df = _run(pd.concat([base, bar_vah], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])
        bar_poc = _frame([poc - 0.5], highs=[poc], lows=[poc - 0.5])
        df = _run(pd.concat([base, bar_poc], ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_short_exit_at_val_and_above_poc(self):
        base = self._trend_base(sign=-1)
        ind = indicators.add_indicators(base)
        poc = ind["vp_poc"].iloc[-1]
        val = ind["vp_val"].iloc[-1]
        bar_val = _frame([val - 0.5], highs=[val], lows=[val - 0.5])
        df = _run(pd.concat([base, bar_val], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])
        bar_poc = _frame([poc + 0.5], highs=[poc + 0.5], lows=[poc])
        df = _run(pd.concat([base, bar_poc], ignore_index=True))
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the 168-bar window: no crash, no entries.
        df = _run(_flat_frame(n=100))
        self.assertTrue(df["vp_poc"].isna().all())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): POC/VAH/VAL collapse to the
        # price, no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["vp_poc"], 100.0))
        self.assertTrue(np.allclose(tail["vp_vah"], 100.0))
        self.assertTrue(np.allclose(tail["vp_val"], 100.0))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
