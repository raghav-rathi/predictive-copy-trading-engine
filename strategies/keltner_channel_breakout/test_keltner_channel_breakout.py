"""Keltner channel breakout tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.keltner_channel_breakout import indicators, risk, signals
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


def _signal_frame(rows):
    """Direct signal unit-test frame from explicit per-bar dicts."""
    return pd.DataFrame(rows)


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


class TestKeltnerChannelBreakout(unittest.TestCase):
    def test_registered(self):
        self.assertIn("keltner_channel_breakout", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_keltner_bands_hand_computed(self):
        # Manual EMA(20) (alpha=2/21, seeded at first close) and Wilder
        # ATR(10) (seeded at first TR, alpha=1/10) on random data.
        rng = np.random.default_rng(11)
        closes = 100 * np.exp(np.cumsum(rng.normal(0.0, 0.005, 200)))
        highs = closes + rng.uniform(0.1, 1.0, 200)
        lows = closes - rng.uniform(0.1, 1.0, 200)
        df = indicators.add_indicators(_frame(closes, highs=highs, lows=lows))
        alpha = 2.0 / 21.0
        ema_manual = closes[0]
        for x in closes[1:]:
            ema_manual = alpha * x + (1 - alpha) * ema_manual
        tr = np.empty(200)
        for i in range(200):
            hl = highs[i] - lows[i]
            if i == 0:
                tr[i] = hl
            else:
                tr[i] = max(hl, abs(highs[i] - closes[i - 1]),
                            abs(lows[i] - closes[i - 1]))
        atr_manual = tr[0]
        for x in tr[1:]:
            atr_manual = (x + 9.0 * atr_manual) / 10.0
        self.assertAlmostEqual(df["kc_mid"].iloc[199], ema_manual, places=8)
        self.assertAlmostEqual(df["kc_upper"].iloc[199],
                               ema_manual + 2.0 * atr_manual, places=8)
        self.assertAlmostEqual(df["kc_lower"].iloc[199],
                               ema_manual - 2.0 * atr_manual, places=8)
        # Bands are NaN before bar 19 (EMA min_periods=20).
        self.assertTrue(np.isnan(df["kc_mid"].iloc[18]))
        self.assertTrue(np.isfinite(df["kc_mid"].iloc[19]))

    def test_bands_on_flat_data(self):
        # Flat bars with h=101, l=99: TR = 2, so ATR(10) converges to
        # 2.0, EMA(20) = 100, upper = 104, lower = 96.
        df = indicators.add_indicators(_flat_frame(n=100))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["kc_mid"], 100.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["kc_upper"], 104.0, atol=1e-9))
        self.assertTrue(np.allclose(tail["kc_lower"], 96.0, atol=1e-9))

    def test_long_entry_on_breakout(self):
        # Flat at 100, then a single jump bar to 115: the close clears
        # the upper band (~106.3 after the jump bar's own 15.5 true
        # range), so a long entry fires on the jump bar.
        n = 80
        closes = np.full(n, 100.0)
        closes[60] = 115.0
        closes[61:] = 115.0
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[60])
        self.assertFalse(df["long_entry"].iloc[:60].any())
        self.assertFalse(df["short_entry"].iloc[60])
        # Mirror: a jump down to 85 fires a short entry.
        closes = np.full(n, 100.0)
        closes[60] = 85.0
        closes[61:] = 85.0
        df = _run(_frame(closes))
        self.assertTrue(df["short_entry"].iloc[60])
        self.assertFalse(df["long_entry"].iloc[60])

    def test_no_entry_inside_channel(self):
        # A +0.5 move off a flat base stays inside the ~102 upper band.
        n = 80
        closes = np.full(n, 100.0)
        closes[60] = 100.5
        closes[61:] = 100.5
        df = _run(_frame(closes))
        self.assertFalse(df["long_entry"].iloc[60])
        self.assertFalse(df["short_entry"].iloc[60])

    def test_exit_on_close_back_inside(self):
        # Jump to 115 (long entry), then close back at 102: inside the
        # channel again, so long_exit fires on the pullback bar.
        n = 80
        closes = np.full(n, 100.0)
        closes[60] = 115.0
        closes[61:] = 102.0
        df = _run(_frame(closes))
        self.assertTrue(df["long_entry"].iloc[60])
        self.assertTrue(df["long_exit"].iloc[61])
        # If the close stays above the upper band, no long exit fires.
        # (short_exit is trivially True there — price above the upper
        # band is also above the lower band — but no short is open, so
        # the harness never applies it; only long_exit is asserted.)
        closes = np.full(n, 100.0)
        closes[60] = 115.0
        closes[61:] = 115.0
        df = _run(_frame(closes))
        self.assertFalse(df["long_exit"].iloc[61])

    def test_signal_logic_crafted_rows(self):
        # Single-row frames: the band columns are already computed.
        row = dict(c=110.0, kc_upper=105.0, kc_lower=95.0)
        df = signals.add_signals(_signal_frame([row]))
        self.assertTrue(df["long_entry"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        row = dict(c=90.0, kc_upper=105.0, kc_lower=95.0)
        df = signals.add_signals(_signal_frame([row]))
        self.assertTrue(df["short_entry"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[0])
        row = dict(c=100.0, kc_upper=105.0, kc_lower=95.0)
        df = signals.add_signals(_signal_frame([row]))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertTrue(df["long_exit"].iloc[0])
        self.assertTrue(df["short_exit"].iloc[0])
        # Close exactly on the upper band is not a break (strict >).
        row = dict(c=105.0, kc_upper=105.0, kc_lower=95.0)
        df = signals.add_signals(_signal_frame([row]))
        self.assertFalse(df["long_entry"].iloc[0])
        # NaN bands (warmup): no entry, no exit.
        row = dict(c=110.0, kc_upper=np.nan, kc_lower=np.nan)
        df = signals.add_signals(_signal_frame([row]))
        self.assertFalse(df["long_entry"].iloc[0])
        self.assertFalse(df["short_entry"].iloc[0])
        self.assertFalse(df["long_exit"].iloc[0])
        self.assertFalse(df["short_exit"].iloc[0])

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
        for col in ("kc_mid", "kc_upper", "kc_lower",
                    "long_entry", "long_exit"):
            pd.testing.assert_series_equal(
                df1[col].iloc[:1300].reset_index(drop=True),
                df2[col].iloc[:1300].reset_index(drop=True),
                check_names=False)

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than any lookback: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): ATR(10) is 0, bands equal the
        # EMA, close never breaks them.
        df = _run(_frame([100.0] * 100, highs=[100.0] * 100,
                         lows=[100.0] * 100))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["kc_upper"], 100.0, atol=1e-12))
        self.assertTrue(np.allclose(tail["kc_lower"], 100.0, atol=1e-12))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
