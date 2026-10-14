"""Network-free unit tests for TSI."""

import unittest

import numpy as np
import pandas as pd

from strategies.tsi import indicators, risk, signals


def _candles(c: np.ndarray) -> pd.DataFrame:
    n = len(c)
    return pd.DataFrame(
        {
            "t": np.arange(n, dtype=np.int64) * 3600_000,
            "o": c,
            "h": c + 0.3,
            "l": c - 0.3,
            "c": c,
            "v": np.full(n, 100.0),
        }
    )


class TestTSIIndicators(unittest.TestCase):
    def test_strong_uptrend_approaches_plus_100(self):
        c = 100.0 + np.arange(400, dtype=float)
        df = indicators.add_indicators(_candles(c))
        tail = df["tsi"].iloc[-20:]
        self.assertTrue((tail > 90).all(), tail.tail(3).tolist())

    def test_strong_downtrend_approaches_minus_100(self):
        c = 500.0 - np.arange(400, dtype=float)
        df = indicators.add_indicators(_candles(c))
        tail = df["tsi"].iloc[-20:]
        self.assertTrue((tail < -90).all())

    def test_flat_market_is_nan(self):
        df = indicators.add_indicators(_candles(np.full(120, 100.0)))
        self.assertTrue(df["tsi"].iloc[-1] != df["tsi"].iloc[-1])  # NaN, no 0/0 blowup

    def test_custom_periods_change_values(self):
        c = 100.0 + np.cumsum(np.random.RandomState(0).randn(300))
        a = indicators.add_indicators(_candles(c))
        b = indicators.add_indicators(_candles(c), r=13, s=25)
        self.assertFalse(np.allclose(a["tsi"].dropna(), b["tsi"].dropna()))

    def test_no_lookahead(self):
        c = 100.0 + np.cumsum(np.random.RandomState(1).randn(200))
        df = _candles(c)
        full = indicators.add_indicators(df)
        trunc = indicators.add_indicators(df.iloc[:-1])
        for col in ("tsi", "tsi_signal"):
            pd.testing.assert_series_equal(
                full[col].iloc[:-1], trunc[col], check_names=False
            )


class TestTSISignals(unittest.TestCase):
    def _frame(self, tsi, sig, n_extra: int = 0):
        return pd.DataFrame(
            {"tsi": np.array(tsi, dtype=float), "tsi_signal": np.array(sig, dtype=float)}
        )

    def test_cross_up_with_negative_tsi_triggers_long(self):
        df2 = signals.add_signals(
            self._frame([-8, -7, -6, -5], [-6, -6, -6.5, -6.5]), zero_gate=True
        )
        # cross up at i=2 (-6 > -6.5 after -7 <= -6), tsi negative -> allowed
        self.assertTrue(df2["long_entry"].iloc[2])
        self.assertFalse(df2["long_entry"].iloc[[0, 1, 3]].any())
        self.assertFalse(df2["short_entry"].any())

    def test_zero_gate_blocks_positive_tsi_long(self):
        df = signals.add_signals(
            self._frame([8, 9, 10, 11], [9, 9.5, 9.5, 9.6]), zero_gate=True
        )
        ungated = signals.add_signals(
            self._frame([8, 9, 10, 11], [9, 9.5, 9.5, 9.6]), zero_gate=False
        )
        # cross up at i=3: 11>9.6 and prev 10<=9.5? no... adjust: i=2: 10>9.5, prev 9<=9.5 -> cross at i=2
        self.assertFalse(df["long_entry"].any())
        self.assertTrue(ungated["long_entry"].iloc[2])

    def test_exhaustion_exit(self):
        df = signals.add_signals(
            self._frame([10, 20, 26, 27], [5, 5, 5, 5]), exhaustion=True
        )
        self.assertTrue(df["long_exit"].iloc[2])
        plain = signals.add_signals(
            self._frame([10, 20, 26, 27], [5, 5, 5, 5]), exhaustion=False
        )
        self.assertFalse(plain["long_exit"].any())

    def test_boolean_columns(self):
        c = 100.0 + np.cumsum(np.random.RandomState(2).randn(300))
        df = signals.add_signals(indicators.add_indicators(_candles(c)))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertTrue(df[col].dtype == bool, col)


class TestTSIRisk(unittest.TestCase):
    def test_risk_sanity(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.5)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 90)


if __name__ == "__main__":
    unittest.main()
