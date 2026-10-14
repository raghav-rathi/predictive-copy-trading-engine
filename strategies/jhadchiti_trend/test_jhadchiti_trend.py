"""jhadchiti trend unit tests. Network-free (btc_c / fund_ok hand-built)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.jhadchiti_trend import indicators, risk, signals


def _ohlcv(o, h, l, c, btc_c=None, fund_ok=True, v=100.0):
    n = len(c)
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    df = pd.DataFrame(
        {"t": t, "o": np.asarray(o, float), "h": np.asarray(h, float),
         "l": np.asarray(l, float), "c": np.asarray(c, float),
         "v": np.full(n, float(v))}
    )
    df["btc_c"] = np.asarray(btc_c, float) if btc_c is not None else df["c"]
    df["fund_ok"] = bool(fund_ok)
    return df


def _breakout_long(n=300):
    """Coin rallies past its 55-bar high while BTC trends up."""
    rng = np.random.default_rng(21)
    c = 100.0 + 0.15 * np.arange(n) + rng.normal(0, 0.2, n)
    c[260:] += np.linspace(0, 8, n - 260)      # breakout leg
    btc = 50000.0 + 30.0 * np.arange(n) + rng.normal(0, 5, n)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + 0.3
    l = np.minimum(o, c) - 0.3
    return _ohlcv(o, h, l, c, btc_c=btc)


class TestJhadchitiTrend(unittest.TestCase):
    def test_requires_preattached_columns(self):
        raw = _breakout_long().drop(columns=["btc_c", "fund_ok"])
        with self.assertRaises(ValueError):
            indicators.add_indicators(raw)

    def test_long_entry_needs_all_four_filters(self):
        df = signals.add_signals(indicators.add_indicators(_breakout_long()))
        longs = df.index[df["long_entry"]]
        self.assertTrue(len(longs) > 0)
        for i in longs:
            self.assertGreater(df["c"].iloc[i], df["chan55_hi"].iloc[i])
            self.assertTrue(df["btc_regime_up"].iloc[i])
            self.assertTrue(df["fund_ok"].iloc[i])
            self.assertGreater(df["ret30"].iloc[i], df["btc_ret30"].iloc[i])

    def test_funding_filter_blocks(self):
        df = signals.add_signals(
            indicators.add_indicators(_breakout_long().assign(fund_ok=False)))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_regime_blocks_countertrend(self):
        raw = _breakout_long()
        # force BTC regime down: longs blocked, shorts need channel-low break
        raw["btc_c"] = 50000.0 - 30.0 * np.arange(len(raw))
        df = signals.add_signals(indicators.add_indicators(raw))
        self.assertFalse(df["long_entry"].any())

    def test_short_mirror(self):
        n = 300
        rng = np.random.default_rng(33)
        c = 100.0 - 0.15 * np.arange(n) + rng.normal(0, 0.2, n)
        c[260:] -= np.linspace(0, 8, n - 260)   # breakdown leg
        btc = 50000.0 - 30.0 * np.arange(n) + rng.normal(0, 5, n)
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) + 0.3
        l = np.minimum(o, c) - 0.3
        df = signals.add_signals(
            indicators.add_indicators(_ohlcv(o, h, l, c, btc_c=btc)))
        shorts = df.index[df["short_entry"]]
        self.assertTrue(len(shorts) > 0)
        for i in shorts:
            self.assertLess(df["c"].iloc[i], df["chan55_lo"].iloc[i])
            self.assertFalse(df["btc_regime_up"].iloc[i])
            self.assertLess(df["ret30"].iloc[i], df["btc_ret30"].iloc[i])

    def test_exit_on_20_channel_cross(self):
        # hand-built: position logic via columns; close crosses chan20_lo
        n = 60
        df = _ohlcv(np.ones(n) * 100, np.ones(n) * 101, np.ones(n) * 99,
                    np.ones(n) * 100)
        df = indicators.add_indicators(df)
        df["chan20_lo"] = 99.5
        df.loc[50, "c"] = 99.0  # crosses below the 20-period channel low
        df = signals.add_signals(df)
        self.assertTrue(df["long_exit"].iloc[50])

    def test_no_lookahead(self):
        raw = _breakout_long()
        df_full = signals.add_signals(indicators.add_indicators(raw))
        df_tr = signals.add_signals(indicators.add_indicators(raw.iloc[:-1]))
        for col in ("chan55_hi", "btc_regime_up", "ret30", "long_entry",
                    "short_entry", "long_exit", "short_exit"):
            a = df_full[col].iloc[:-1].fillna(-999.0).to_numpy()
            b = df_tr[col].fillna(-999.0).to_numpy()
            self.assertTrue(np.allclose(a, b, equal_nan=True),
                            f"lookahead leak in {col}")

    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.atr_window, 20)
        self.assertAlmostEqual(risk.RISK.risk_frac, 0.0075)
        self.assertEqual(risk.RISK.max_hold_bars, 2160)
        self.assertGreaterEqual(risk.WARMUP, 220)


if __name__ == "__main__":
    unittest.main()
