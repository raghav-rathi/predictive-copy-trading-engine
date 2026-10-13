"""Network-free unit tests for the Vortex strategy."""

import unittest

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.vortex import indicators, risk, signals
from strategies.vortex.indicators import VI_PERIOD


def _trend_df(n: int = 60, direction: int = 1, start: float = 100.0) -> pd.DataFrame:
    """Deterministic staircase candles; direction=1 rising, -1 falling."""
    c = start + direction * np.arange(n, dtype=float)
    o = c - 0.2 * direction
    h = np.maximum(o, c) + 0.3
    l = np.minimum(o, c) - 0.3
    return pd.DataFrame(
        {
            "t": np.arange(n, dtype=np.int64) * 3600_000,
            "o": o,
            "h": h,
            "l": l,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


class TestVortexIndicators(unittest.TestCase):
    def test_columns_and_warmup(self):
        df = indicators.add_indicators(_trend_df())
        for col in ("vi_plus", "vi_minus", "vi_plus_prev", "vi_minus_prev", "adx"):
            self.assertIn(col, df.columns)
        self.assertTrue(df["vi_plus"].iloc[: VI_PERIOD - 1].isna().all())
        self.assertFalse(df["vi_plus"].iloc[VI_PERIOD:].isna().any())

    def test_rising_market_vi_plus_dominates(self):
        df = indicators.add_indicators(_trend_df(80, direction=1))
        tail = df.iloc[VI_PERIOD + 5 :]
        self.assertTrue((tail["vi_plus"] > tail["vi_minus"]).all())

    def test_falling_market_vi_minus_dominates(self):
        df = indicators.add_indicators(_trend_df(80, direction=-1))
        tail = df.iloc[VI_PERIOD + 5 :]
        self.assertTrue((tail["vi_minus"] > tail["vi_plus"]).all())

    def test_no_lookahead(self):
        df = _trend_df(80)
        full = indicators.add_indicators(df)
        trunc = indicators.add_indicators(df.iloc[:-1])
        for col in ("vi_plus", "vi_minus", "adx"):
            pd.testing.assert_series_equal(
                full[col].iloc[:-1], trunc[col], check_names=False
            )


class TestVortexSignals(unittest.TestCase):
    def _frame(self, vi_p, vi_m, adx):
        n = len(vi_p)
        return pd.DataFrame(
            {
                "vi_plus": vi_p,
                "vi_minus": vi_m,
                "vi_plus_prev": np.r_[np.nan, vi_p[:-1]],
                "vi_minus_prev": np.r_[np.nan, vi_m[:-1]],
                "adx": adx,
            }
        )

    def test_cross_up_triggers_long(self):
        df = signals.add_signals(
            self._frame(
                [0.8, 0.9, 1.1, 1.2], [1.2, 1.1, 0.9, 0.8], [25, 26, 27, 28]
            )
        )
        self.assertTrue(df["long_entry"].iloc[2])
        self.assertFalse(df["long_entry"].iloc[:2].any())
        self.assertFalse(df["short_entry"].any())

    def test_cross_down_triggers_short_and_exits_long(self):
        df = signals.add_signals(
            self._frame(
                [1.2, 1.1, 0.9, 0.8], [0.8, 0.9, 1.1, 1.2], [25, 26, 27, 28]
            )
        )
        self.assertTrue(df["short_entry"].iloc[2])
        self.assertTrue(df["long_exit"].iloc[2])

    def test_adx_filter_blocks_weak_trend(self):
        frame = self._frame(
            [0.8, 0.9, 1.1, 1.2], [1.2, 1.1, 0.9, 0.8], [15, 16, 17, 18]
        )
        gated = signals.add_signals(frame, adx_filter=True)
        ungated = signals.add_signals(frame, adx_filter=False)
        self.assertFalse(gated["long_entry"].any())
        self.assertTrue(ungated["long_entry"].iloc[2])
        # exits still fire regardless of the filter
        self.assertTrue(gated["short_exit"].iloc[2])

    def test_no_cross_no_signal(self):
        df = signals.add_signals(
            self._frame(
                [1.1, 1.1, 1.1, 1.1], [0.9, 0.9, 0.9, 0.9], [25, 26, 27, 28]
            )
        )
        self.assertFalse(
            df[["long_entry", "short_entry", "long_exit", "short_exit"]].any().any()
        )

    def test_boolean_columns(self):
        df = signals.add_signals(_trend_df(40).pipe(indicators.add_indicators))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)


class TestVortexRisk(unittest.TestCase):
    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)

    def test_base_primitives(self):
        df = _trend_df(40)
        a = B.atr(df["h"], df["l"], df["c"], 14)
        self.assertTrue((a.dropna() > 0).all())


if __name__ == "__main__":
    unittest.main()
