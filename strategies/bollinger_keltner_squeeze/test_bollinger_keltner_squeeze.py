"""Bollinger/Keltner Squeeze tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.bollinger_keltner_squeeze import indicators, risk, signals
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


def _squeeze_frame(direction=+1):
    """60 flat bars (squeeze ON) then a steady 24-bar trend.
    direction=+1 rises 100.5 -> 112, -1 falls 99.5 -> 88."""
    base = [100.0] * 60
    trend = list(np.linspace(100.5, 112, 24)) if direction > 0 else \
        list(np.linspace(99.5, 88, 24))
    closes = base + trend
    return _frame(closes, highs=[c + 0.1 for c in closes],
                  lows=[c - 0.1 for c in closes])


class TestBollingerKeltnerSqueeze(unittest.TestCase):
    def test_registered(self):
        self.assertIn("bollinger_keltner_squeeze", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_squeeze_on_during_flat(self):
        df = indicators.add_indicators(_flat_frame())
        # BB width is 0 on a flat series (std 0) while KC width is
        # 1.5*ATR > 0, so the squeeze is ON once bands are defined.
        self.assertTrue(df["squeeze_on"].iloc[20:200].all())

    def test_bb_math_flat(self):
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["bb_mid"].iloc[100], 100.0)
        self.assertAlmostEqual(df["bb_upper"].iloc[100], 100.0)
        self.assertAlmostEqual(df["bb_lower"].iloc[100], 100.0)
        # KC: EMA(20) of a flat 100 series is 100; ATR ~2 (h-l range).
        self.assertAlmostEqual(df["kc_mid"].iloc[100], 100.0, places=6)
        self.assertGreater(df["kc_upper"].iloc[100], 100.0)
        self.assertLess(df["kc_lower"].iloc[100], 100.0)

    def test_keltner_uses_atr14(self):
        # ATR(14) on a flat frame with h-l = 2 is 2.0; KC half-width
        # is 1.5 * 2 = 3.0.
        df = indicators.add_indicators(_flat_frame())
        self.assertAlmostEqual(df["atr"].iloc[100], 2.0, places=6)
        self.assertAlmostEqual(df["kc_upper"].iloc[100], 103.0, places=6)
        self.assertAlmostEqual(df["kc_lower"].iloc[100], 97.0, places=6)

    def test_fire_long_on_uptrend_breakout(self):
        df = _run(_squeeze_frame(+1))
        self.assertTrue(df["squeeze_on"].iloc[20:60].all())
        self.assertTrue(df["squeeze_on"].iloc[60])
        self.assertFalse(df["squeeze_on"].iloc[61])
        self.assertTrue(df["long_entry"].iloc[61])
        self.assertEqual(int(df["long_entry"].sum()), 1)
        self.assertEqual(int(df["short_entry"].sum()), 0)

    def test_fire_short_on_downtrend_breakout(self):
        df = _run(_squeeze_frame(-1))
        self.assertTrue(df["short_entry"].iloc[61])
        self.assertEqual(int(df["short_entry"].sum()), 1)
        self.assertEqual(int(df["long_entry"].sum()), 0)
        self.assertLess(df["momentum"].iloc[61], 0)

    def test_momentum_sign_matches_direction(self):
        df_up = indicators.add_indicators(_squeeze_frame(+1))
        df_dn = indicators.add_indicators(_squeeze_frame(-1))
        self.assertGreater(df_up["momentum"].iloc[61], 0)
        self.assertLess(df_dn["momentum"].iloc[61], 0)

    def test_momentum_matches_polyfit(self):
        # Independent recomputation: x from closes, then a 20-bar
        # OLS fit; the fitted value at the last bar must match.
        df0 = _squeeze_frame(+1)
        df = indicators.add_indicators(df0)
        c = df0["c"].to_numpy(float)
        h = df0["h"].to_numpy(float)
        l = df0["l"].to_numpy(float)
        hh = pd.Series(h).rolling(20, min_periods=20).max().to_numpy(float)
        ll = pd.Series(l).rolling(20, min_periods=20).min().to_numpy(float)
        sma = pd.Series(c).rolling(20, min_periods=20).mean().to_numpy(float)
        x = c - ((hh + ll) / 2 + sma) / 2
        for i in (50, 61, 70):
            coef = np.polyfit(np.arange(20), x[i - 19:i + 1], 1)
            expected = np.polyval(coef, 19)
            self.assertAlmostEqual(df["momentum"].iloc[i], expected, places=8)

    def test_no_fire_while_squeeze_stays_on(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_fire_is_single_bar(self):
        # After the fire bar the squeeze stays OFF, so no second fire.
        df = _run(_squeeze_frame(+1))
        self.assertEqual(int(df["long_entry"].sum()), 1)

    def test_exit_is_opposite_signal(self):
        # Build fire manually: squeeze was ON the prior bar.
        df = pd.DataFrame({
            "squeeze_on": [True, False, True, False],
            "momentum": [0.5, 1.0, -0.5, -1.0],
        })
        out = signals.add_signals(df)
        self.assertTrue(out["long_entry"].iloc[1])
        self.assertTrue(out["long_exit"].iloc[3])  # short fires -> long exits
        self.assertTrue(out["short_entry"].iloc[3])

    def test_warmup_nans(self):
        df = indicators.add_indicators(_random_walk_frame())
        self.assertTrue(df["bb_upper"].iloc[:19].isna().all())
        self.assertTrue(df["momentum"].iloc[:38].isna().all())
        self.assertFalse(np.isnan(df["momentum"].iloc[38]))
        self.assertFalse(df["squeeze_on"].iloc[:19].any())

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
        self.assertEqual(risk.WARMUP, 40)

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
        closes = list(100 * np.exp(np.cumsum(
            np.random.default_rng(3).normal(0.0005, 0.01, 1300))))
        df1 = _run(_frame(closes))
        df2 = _run(_frame(closes + [300.0] * 50))
        for col in ("bb_upper", "kc_upper", "squeeze_on", "momentum",
                    "long_entry", "short_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        self.assertTrue(df["momentum"].isna().all())


if __name__ == "__main__":
    unittest.main()
