"""Outside-bar reversal tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.outside_bar_reversal import indicators, risk, signals
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


def _flat_frame(n=130, close=100.0, hi=101.0, lo=99.0, vol=100.0):
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


class TestOutsideBarReversal(unittest.TestCase):
    def test_registered(self):
        self.assertIn("outside_bar_reversal", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat 100, h=101, l=99: sma20=100, vol_avg20=100, no outside
        # bars, close position (100-99)/(101-99)=0.5.
        df = indicators.add_indicators(_flat_frame())
        tail = df.iloc[risk.WARMUP:]
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        self.assertTrue(np.allclose(tail["ob_sma20"], 100.0))
        self.assertTrue(np.allclose(tail["ob_vol_avg20"], 100.0))
        self.assertFalse(tail["ob_is_outside"].any())
        self.assertTrue(np.allclose(tail["ob_close_pos"], 0.5))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (150, 250, 399):
            self.assertAlmostEqual(df["ob_sma20"].iloc[i],
                                   df["c"].iloc[i - 19:i + 1].mean(), places=9)
            self.assertAlmostEqual(df["ob_close_pos"].iloc[i],
                                   (df["c"].iloc[i] - df["l"].iloc[i]) /
                                   (df["h"].iloc[i] - df["l"].iloc[i]), places=9)
            self.assertEqual(df["ob_is_outside"].iloc[i],
                             df["h"].iloc[i] > df["h"].iloc[i - 1] and
                             df["l"].iloc[i] < df["l"].iloc[i - 1])

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

    def _bullish_setup(self, vol=200.0, close=101.0):
        # Prior bar closes below SMA20 (~99.9), then an outside bar
        # closing in its upper third with high volume.
        base = _flat_frame(n=120)
        prior = _frame([98.0], highs=[99.5], lows=[97.5],
                       vols=[100.0], opens=[99.0])
        bar = _frame([close], highs=[102.0], lows=[96.0],
                     vols=[vol], opens=[97.0])
        return pd.concat([base, prior, bar], ignore_index=True)

    def _bearish_setup(self, vol=200.0, close=100.0):
        base = _flat_frame(n=120)
        prior = _frame([102.0], highs=[102.5], lows=[100.5],
                       vols=[100.0], opens=[101.0])
        bar = _frame([close], highs=[104.0], lows=[99.0],
                     vols=[vol], opens=[103.0])
        return pd.concat([base, prior, bar], ignore_index=True)

    def test_long_entry_bullish_outside_reversal(self):
        df = _run(self._bullish_setup())
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_short_entry_bearish_outside_reversal(self):
        df = _run(self._bearish_setup())
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_without_volume(self):
        df = _run(self._bullish_setup(vol=50.0))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_close_in_middle_third(self):
        # Close at 99.0 -> position (99-96)/6 = 0.5, not upper third.
        df = _run(self._bullish_setup(close=99.0))
        self.assertFalse(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_no_entry_not_outside(self):
        # Bar fails to engulf the prior bar's low (l=98 > 97.5).
        base = _flat_frame(n=120)
        prior = _frame([98.0], highs=[99.5], lows=[97.5],
                       vols=[100.0], opens=[99.0])
        bar = _frame([101.0], highs=[102.0], lows=[98.0],
                     vols=[200.0], opens=[99.0])
        df = _run(pd.concat([base, prior, bar], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_prior_close_wrong_side_of_sma(self):
        # Prior bar closes above SMA20: no bullish reversal.
        base = _flat_frame(n=120)
        prior = _frame([101.0], highs=[101.5], lows=[100.0],
                       vols=[100.0], opens=[100.0])
        bar = _frame([102.0], highs=[103.0], lows=[99.0],
                     vols=[200.0], opens=[100.0])
        df = _run(pd.concat([base, prior, bar], ignore_index=True))
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_long_exit_on_bearish_outside_bar(self):
        df = _run(self._bullish_setup())
        # Bearish outside bar engulfing the entry bar, closing low.
        bar = _frame([96.5], highs=[103.0], lows=[95.0],
                     vols=[100.0], opens=[102.0])
        df = _run(pd.concat([_run(self._bullish_setup()).iloc[:, :6], bar],
                            ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_long_exit_below_outside_bar_low(self):
        df = _run(self._bullish_setup())
        # Close 95.5 is below the entry outside bar's low (96.0).
        bar = _frame([95.5], highs=[96.0], lows=[95.0],
                     vols=[100.0], opens=[96.0])
        df = _run(pd.concat([_run(self._bullish_setup()).iloc[:, :6], bar],
                            ignore_index=True))
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): close position defaults to 0.5.
        df = _run(_frame([100.0] * 130, highs=[100.0] * 130,
                         lows=[100.0] * 130))
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["ob_close_pos"], 0.5))
        self.assertFalse(tail["ob_is_outside"].any())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
