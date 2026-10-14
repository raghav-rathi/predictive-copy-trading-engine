"""Klinger Volume Oscillator tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.klinger_oscillator import indicators, risk, signals
from strategies import base as B

HOUR_MS = 3_600_000
T0 = 20_000 * 86_400_000


def _frame(c, v=None, spread=0.2):
    c = np.asarray(c, dtype=float)
    n = len(c)
    prev = np.concatenate([[c[0]], c[:-1]])
    if v is None:
        v = np.full(n, 100.0)
    return pd.DataFrame(
        {
            "t": np.array([T0 + i * HOUR_MS for i in range(n)], dtype="int64"),
            "o": prev,
            "h": np.maximum(c, prev) + spread,
            "l": np.minimum(c, prev) - spread,
            "c": c,
            "v": np.asarray(v, dtype=float),
        }
    )


def _run(df):
    return signals.add_signals(indicators.add_indicators(df))


class TestKlinger(unittest.TestCase):
    def test_volume_force_formula_independent(self):
        # Independent loop recomputation of VF and KVO.
        rng = np.random.default_rng(13)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        df = _frame(c)
        got = indicators.add_indicators(df)
        h = df["h"].to_numpy()
        l = df["l"].to_numpy()
        cc = df["c"].to_numpy()
        v = df["v"].to_numpy()
        hlc = h + l + cc
        dm = h - l
        n = len(df)
        vf = np.zeros(n)
        t_prev, cm = 1.0, dm[0]
        for i in range(n):
            if i == 0:
                t, cm = 1.0, dm[0]
            else:
                t = 1.0 if hlc[i] > hlc[i - 1] else (-1.0 if hlc[i] < hlc[i - 1] else t_prev)
                cm = dm[i - 1] + dm[i] if t != t_prev else cm + dm[i]
            t_prev = t
            vf[i] = v[i] * abs(2.0 * (dm[i] / cm) - 1.0) * 100.0 * t if cm != 0 else 0.0
        kvo = B.ema(pd.Series(vf), 34) - B.ema(pd.Series(vf), 55)
        np.testing.assert_allclose(
            got["kvo"].to_numpy()[60:], kvo.to_numpy()[60:], rtol=1e-9
        )

    def test_signal_line_is_ema_of_kvo(self):
        rng = np.random.default_rng(5)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        df = indicators.add_indicators(_frame(c))
        expect = B.ema(df["kvo"], 13)
        pd.testing.assert_series_equal(df["kvo_signal"], expect, check_names=False)

    def test_warmup_nans_then_valid(self):
        rng = np.random.default_rng(5)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 200)))
        df = indicators.add_indicators(_frame(c))
        self.assertTrue(df["kvo"].iloc[:54].isna().all())
        self.assertTrue(np.isfinite(df["kvo"].iloc[-1]))

    def test_rising_volume_rally_gives_long(self):
        rng = np.random.default_rng(7)
        n1, n2 = 160, 240
        c1 = 100.0 + rng.normal(0, 0.4, n1).cumsum() * 0.1
        v1 = np.full(n1, 80.0)
        c2 = c1[-1] + 0.5 * np.arange(n2) + rng.normal(0, 0.4, n2).cumsum() * 0.1
        v2 = np.full(n2, 220.0)  # rising volume on the rally
        df = _run(_frame(np.concatenate([c1, c2]), v=np.concatenate([v1, v2])))
        self.assertGreater(int(df["long_entry"].sum()), 0)

    def test_signal_columns_boolean_no_nan(self):
        rng = np.random.default_rng(2)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.015, 250)))
        df = _run(_frame(c))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertEqual(str(df[col].dtype), "bool")

    def test_no_lookahead(self):
        rng = np.random.default_rng(17)
        c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 300)))
        full = indicators.add_indicators(_frame(c))
        cut = indicators.add_indicators(_frame(c[:200]))
        pd.testing.assert_series_equal(
            full["kvo"].iloc[:200], cut["kvo"], check_names=False
        )

    def test_risk_config_sane(self):
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 100)


if __name__ == "__main__":
    unittest.main()
