"""80-20 momentum-candle fade tests. Network-free."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.eighty_twenty import indicators, risk, signals


def _ohlcv(o, h, l, c, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _up_momentum_then_fade(n=300, seed=13):
    """Quiet noise, then hand-set bars 100-103: a huge up momentum candle,
    two push-up bars (also momentum bars -- levels chain to the latest),
    then a fade bar closing back inside bar 102's range -> short on 103."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:100] = 100 + rng.normal(0, 0.1, 100).cumsum() * 0.2
    c[104:] = 107.2 - 0.05 * np.arange(n - 104) + rng.normal(0, 0.08, n - 104)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.2
    l = np.minimum(o, c) - 0.2
    o[100], c[100], h[100], l[100] = 100.0, 106.0, 106.5, 99.5
    o[101], c[101], h[101], l[101] = 106.0, 106.5, 107.5, 105.5
    o[102], c[102], h[102], l[102] = 106.5, 107.6, 107.9, 106.9
    o[103], c[103], h[103], l[103] = 107.6, 107.2, 107.25, 107.0
    return _ohlcv(o, h, l, c)


def _dn_momentum_then_fade(n=300, seed=17):
    """Mirror image: down momentum bar, two push-down bars, fade bar
    closing back inside bar 102's range -> long on 103."""
    rng = np.random.default_rng(seed)
    c = np.empty(n)
    c[:100] = 100 + rng.normal(0, 0.1, 100).cumsum() * 0.2
    c[104:] = 92.8 + 0.05 * np.arange(n - 104) + rng.normal(0, 0.08, n - 104)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.2
    l = np.minimum(o, c) - 0.2
    o[100], c[100], h[100], l[100] = 100.0, 94.0, 100.5, 93.5
    o[101], c[101], h[101], l[101] = 94.0, 93.5, 94.5, 92.5
    o[102], c[102], h[102], l[102] = 93.5, 92.4, 93.1, 92.1
    o[103], c[103], h[103], l[103] = 92.4, 92.8, 93.0, 92.75
    return _ohlcv(o, h, l, c)


class TestEightyTwenty(unittest.TestCase):
    def test_up_momentum_fade_shorts(self):
        df = signals.add_signals(indicators.add_indicators(_up_momentum_then_fade()))
        # the crafted push-then-fade setup must fire a short on bar 103
        self.assertTrue(bool(df["short_entry"].iloc[103]))
        self.assertFalse(bool(df["long_entry"].iloc[103]))
        self.assertGreater(int(df["short_entry"].sum()), 0)

    def test_dn_momentum_fade_longs(self):
        df = signals.add_signals(indicators.add_indicators(_dn_momentum_then_fade()))
        self.assertTrue(bool(df["long_entry"].iloc[103]))
        self.assertFalse(bool(df["short_entry"].iloc[103]))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_momentum_bar_detected(self):
        ind = indicators.add_indicators(_up_momentum_then_fade())
        self.assertTrue(bool(ind["mom_bar"].iloc[100]))
        self.assertEqual(ind["mom_up"].iloc[100], 1.0)

    def test_no_lookahead_truncation(self):
        full = _up_momentum_then_fade()
        ind_full = indicators.add_indicators(full)
        for i in (100, 104, 200):
            ind_tr = indicators.add_indicators(full.iloc[: i + 1])
            for col in ("mom_bar", "mom_close", "mom_high", "mom_low", "mom_up"):
                a, b = ind_full[col].iloc[i], ind_tr[col].iloc[i]
                if isinstance(a, (bool, np.bool_)):
                    self.assertEqual(bool(a), bool(b))
                else:
                    self.assertTrue((pd.isna(a) and pd.isna(b)) or abs(a - b) < 1e-9)

    def test_signals_boolean_clean(self):
        df = signals.add_signals(indicators.add_indicators(_up_momentum_then_fade()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(df[col].isna().any())
            self.assertTrue(set(df[col].unique()) <= {True, False})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.target_atr_mult, 1.5)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertGreater(risk.WARMUP, 20)


if __name__ == "__main__":
    unittest.main()
