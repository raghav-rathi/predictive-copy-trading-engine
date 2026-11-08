"""RSI pullback in trend tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.sma_rsi_pullback import indicators, risk, signals
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


def _override_trend(df, sma50=100.0, sma200=90.0, rsi=50.0):
    """Pin the indicator columns (signals-level control of SMA/RSI)."""
    df = df.copy()
    df["sma50"] = sma50
    df["sma200"] = sma200
    df["rsi14"] = rsi
    return df


class TestSmaRsiPullback(unittest.TestCase):
    def test_registered(self):
        self.assertIn("sma_rsi_pullback", registry.REGISTRY)

    def test_signal_columns_bool(self):
        df = _run(_random_walk_frame())
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertIn(col, df.columns)
            self.assertTrue(df[col].dtype == bool)

    def test_indicator_values_flat(self):
        # Flat closes: SMA50 == SMA200 == 100, RSI(14) == 0 (no
        # gains, no losses).
        df = indicators.add_indicators(_flat_frame())
        for col in indicators.INDICATOR_COLS:
            self.assertIn(col, df.columns)
        tail = df.iloc[risk.WARMUP:]
        self.assertTrue(np.allclose(tail["sma50"], 100.0))
        self.assertTrue(np.allclose(tail["sma200"], 100.0))
        self.assertTrue(np.allclose(tail["rsi14"], 0.0))

    def test_indicator_values_random_walk(self):
        df = indicators.add_indicators(_random_walk_frame())
        for i in (250, 300, 399):
            self.assertAlmostEqual(df["sma50"].iloc[i],
                                   df["c"].iloc[i - 49:i + 1].mean(), places=9)
            self.assertAlmostEqual(df["sma200"].iloc[i],
                                   df["c"].iloc[i - 199:i + 1].mean(), places=9)
            self.assertTrue(0.0 <= df["rsi14"].iloc[i] <= 100.0)

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

    def _pullback_scenario(self, direction="long"):
        """Six-bar tail with pinned SMA/RSI: a pullback bar 3 bars
        back, closes below SMA50 since, and a cross back on the
        last bar. Returns the signals frame."""
        n = 300
        if direction == "long":
            closes = [100.0] * (n - 6) + [99.5, 99.6, 99.7, 99.8, 99.9, 100.5]
            lows = [99.5] * (n - 6) + [99.0, 99.1, 99.2, 99.3, 99.4, 100.0]
            highs = [100.5] * n
            sma50, sma200, rsi = 100.0, 90.0, 50.0
        else:
            closes = [100.0] * (n - 6) + [100.5, 100.4, 100.3, 100.2, 100.1, 99.5]
            highs = [100.5] * (n - 6) + [101.0, 100.9, 100.8, 100.7, 100.6, 100.0]
            lows = [99.5] * n
            sma50, sma200, rsi = 100.0, 110.0, 50.0
        df = _frame(closes, highs=highs, lows=lows)
        df = indicators.add_indicators(df)
        df = _override_trend(df, sma50=sma50, sma200=sma200, rsi=rsi)
        return signals.add_signals(df)

    def test_long_entry_after_pullback(self):
        df = self._pullback_scenario("long")
        # Bar -6 (index -6) is the pullback bar: low 99.0 <= SMA50
        # 100 with RSI 50 in 40-55; the last bar crosses back above.
        self.assertTrue(df["long_entry"].iloc[-1])
        self.assertFalse(df["short_entry"].iloc[-1])

    def test_short_entry_after_pullback(self):
        df = self._pullback_scenario("short")
        self.assertTrue(df["short_entry"].iloc[-1])
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_without_cross_back(self):
        # Pullback armed, but the last bar's close is still below
        # SMA50: no cross back, no entry.
        df = self._pullback_scenario("long")
        df = df.copy()
        df.loc[df.index[-1], "c"] = 99.9
        df = signals.add_signals(df)
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_pullback_too_old(self):
        # Pullback bar 6 bars back: outside the 5-bar window. RSI is
        # pinned out of the pullback band on every other bar so only
        # that one bar counts as a pullback.
        n = 300
        closes = [100.0] * (n - 7) + [99.5, 99.6, 99.7, 99.8, 99.9, 99.9, 100.5]
        lows = [99.5] * (n - 7) + [99.0, 99.1, 99.2, 99.3, 99.4, 99.4, 100.0]
        df = _frame(closes, highs=[100.5] * n, lows=lows)
        df = indicators.add_indicators(df)
        df = _override_trend(df, sma50=100.0, sma200=90.0, rsi=65.0)
        df.loc[df.index[-7], "rsi14"] = 50.0
        df = signals.add_signals(df)
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_rsi_out_of_pullback_band(self):
        # Same shape, but RSI 65: not a pullback bar (needs 40-55).
        df = self._pullback_scenario("long")
        df = _override_trend(df, sma50=100.0, sma200=90.0, rsi=65.0)
        df = signals.add_signals(df)
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_wrong_trend(self):
        # Pullback shape in a downtrend (SMA50 < SMA200): no long.
        df = self._pullback_scenario("long")
        df = _override_trend(df, sma50=90.0, sma200=100.0, rsi=50.0)
        df = signals.add_signals(df)
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_no_entry_low_never_touches_sma50(self):
        # Closes dip below SMA50 but no bar's low ever touches it.
        n = 300
        closes = [100.0] * (n - 6) + [99.5, 99.6, 99.7, 99.8, 99.9, 100.5]
        lows = [100.5] * n  # lows pinned above SMA50 100
        df = _frame(closes, highs=[101.0] * n, lows=lows)
        df = indicators.add_indicators(df)
        df = _override_trend(df, sma50=100.0, sma200=90.0, rsi=50.0)
        df = signals.add_signals(df)
        self.assertFalse(df["long_entry"].iloc[-1])

    def test_long_exit_rsi_overbought_and_below_sma200(self):
        df = _run(_random_walk_frame())
        df = _override_trend(df, sma50=100.0, sma200=90.0, rsi=75.0)
        df = signals.add_signals(df)
        self.assertTrue(df["long_exit"].iloc[-1])
        df = _override_trend(df, sma50=100.0, sma200=110.0, rsi=50.0)
        df.loc[df.index[-1], "c"] = 105.0  # close below SMA200 110
        df = signals.add_signals(df)
        self.assertTrue(df["long_exit"].iloc[-1])

    def test_short_exit_rsi_oversold_and_above_sma200(self):
        df = _run(_random_walk_frame())
        df = _override_trend(df, sma50=100.0, sma200=110.0, rsi=25.0)
        df = signals.add_signals(df)
        self.assertTrue(df["short_exit"].iloc[-1])
        df = _override_trend(df, sma50=100.0, sma200=90.0, rsi=50.0)
        df.loc[df.index[-1], "c"] = 95.0  # close above SMA200 90
        df = signals.add_signals(df)
        self.assertTrue(df["short_exit"].iloc[-1])

    def test_entries_match_manual_recomputation(self):
        # Full pipeline on a random walk: every flagged entry must
        # satisfy the armed-window + cross-back definition.
        df = _run(_random_walk_frame(n=600, seed=11))
        c, l, sma50, sma200, rsi14 = (df["c"], df["l"], df["sma50"],
                                      df["sma200"], df["rsi14"])
        pull_long = ((l <= sma50) & (rsi14 >= 40) & (rsi14 <= 55)
                     & (sma50 > sma200)).fillna(False)
        for i in df.index[df["long_entry"]]:
            self.assertTrue(pull_long.iloc[max(0, i - 5):i].any())
            self.assertGreater(c.iloc[i], sma50.iloc[i])
            self.assertLessEqual(c.iloc[i - 1], sma50.iloc[i - 1])

    def test_no_lookahead_flat(self):
        df = _run(_flat_frame())
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())

    def test_edge_short_frame_and_zero_range(self):
        # Fewer bars than the SMA200 window: no crash, no entries.
        df = _run(_flat_frame(n=10))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())
        # Zero-range bars (h == l == c): no pullback, no entries.
        df = _run(_frame([100.0] * 300, highs=[100.0] * 300,
                         lows=[100.0] * 300))
        self.assertFalse(df["long_entry"].any())
        self.assertFalse(df["short_entry"].any())


if __name__ == "__main__":
    unittest.main()
