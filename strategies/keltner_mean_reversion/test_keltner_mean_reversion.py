"""Keltner mean-reversion tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.keltner_mean_reversion import indicators, risk, signals

T0 = 1700006400000  # 2023-11-15 00:00 UTC


def _df_from_ohlc(o, h, l, c):
    n = len(c)
    t = (T0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {
            "t": t,
            "o": np.asarray(o, float),
            "h": np.asarray(h, float),
            "l": np.asarray(l, float),
            "c": np.asarray(c, float),
            "v": np.full(n, 100.0),
        }
    )


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    return _df_from_ohlc(o, h, l, c)


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


def _flat_then_bars(extra):
    # 60 flat bars at 100 (h=101, l=99, spread 1.0), then the
    # caller-supplied (o, h, l, c) bars, then flat at the last
    # supplied close.
    base_c = np.full(60, 100.0)
    base = _df_from_c(base_c, spread=1.0)
    rows = [base]
    last_c = 100.0
    for (o, h, l, c) in extra:
        last_c = c
        rows.append(
            _df_from_ohlc(
                [o], [h], [l], [c],
            )
        )
    tail = _df_from_c(np.full(10, last_c), spread=1.0)
    df = pd.concat(rows + [tail], ignore_index=True)
    df["t"] = (T0 + np.arange(len(df)) * 3_600_000).astype("int64")
    return df


class TestKeltnerMeanReversion(unittest.TestCase):
    def test_keltner_hand_computed(self):
        # Flat 100 (h=101, l=99): EMA(20)=100, ATR(10)=2, so
        # kc_mid=100, kc_upper=104, kc_lower=96 once warmed up.
        ind = indicators.add_indicators(_df_from_c(np.full(60, 100.0), spread=1.0))
        row = ind.iloc[59]
        self.assertAlmostEqual(float(row["kc_mid"]), 100.0, places=6)
        self.assertAlmostEqual(float(row["kc_upper"]), 104.0, places=6)
        self.assertAlmostEqual(float(row["kc_lower"]), 96.0, places=6)
        self.assertAlmostEqual(float(row["atr14"]), 2.0, places=6)

    def test_k_param_widens_bands(self):
        df = _df_from_c(np.full(60, 100.0), spread=1.0)
        ind1 = indicators.add_indicators(df, k=1.0)
        ind2 = indicators.add_indicators(df, k=2.0)
        self.assertAlmostEqual(float(ind1["kc_upper"].iloc[59]), 102.0, places=6)
        self.assertAlmostEqual(float(ind2["kc_upper"].iloc[59]), 104.0, places=6)
        self.assertAlmostEqual(float(ind1["kc_lower"].iloc[59]), 98.0, places=6)
        self.assertAlmostEqual(float(ind2["kc_lower"].iloc[59]), 96.0, places=6)

    def test_long_fires_on_bullish_band_tag(self):
        # Bar 60: o=92, c=93, h=93.5, l=91.5. EMA(20) -> 99.33,
        # ATR(10) -> 2.65 (TR=8.5), kc_lower -> 94.03: the close
        # crosses below it on a bullish candle. Bar 61 jumps
        # back above the midline -> long_exit at 61.
        df = _flat_then_bars(
            [(92.0, 93.5, 91.5, 93.0), (93.0, 101.5, 92.5, 101.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [60])
        self.assertFalse(bool(sig["short_entry"].any()))
        self.assertEqual(sig.index[sig["long_exit"]].tolist(), [61])

    def test_short_fires_on_bearish_band_tag(self):
        # Bar 60: o=108, c=107, h=108.5, l=106.5. EMA(20) ->
        # 100.67, ATR(10) -> 2.65, kc_upper -> 105.97: the
        # close crosses above it on a bearish candle. Bar 61
        # falls back below the midline -> short_exit at 61.
        df = _flat_then_bars(
            [(108.0, 108.5, 106.5, 107.0), (107.0, 107.5, 98.5, 99.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["short_entry"]].tolist(), [60])
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertEqual(sig.index[sig["short_exit"]].tolist(), [61])

    def test_no_long_entry_on_bearish_candle(self):
        # Same band tag as the long test, but the tag bar is a
        # bearish candle (o=94, c=93): no entry.
        df = _flat_then_bars([(94.0, 94.5, 92.5, 93.0)])
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertFalse(bool(sig["long_entry"].any()))
        self.assertFalse(bool(sig["short_entry"].any()))

    def test_no_refire_while_below_band(self):
        # Close stays below the lower band for bars 60-62: the
        # cross fires once (bar 60), not on every bar below it.
        df = _flat_then_bars(
            [
                (92.0, 93.5, 91.5, 93.0),
                (92.5, 92.5, 91.5, 92.0),
                (90.0, 92.0, 90.5, 91.0),
            ]
        )
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [60])

    def test_no_exit_without_midline_cross(self):
        # Tag at bar 60, then price hovers below the midline:
        # no long_exit (the midline cross is the exit).
        df = _flat_then_bars(
            [(92.0, 93.5, 91.5, 93.0), (93.0, 95.5, 92.5, 94.0)]
        )
        sig = signals.add_signals(indicators.add_indicators(df))
        self.assertEqual(sig.index[sig["long_entry"]].tolist(), [60])
        self.assertFalse(bool(sig["long_exit"].any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("kc_mid", "kc_upper", "kc_lower", "atr14"):
            self.assertFalse(sig[col].iloc[100:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("kc_mid", "kc_upper", "kc_lower", "atr14"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue(
                    (pd.isna(av) and pd.isna(bv)) or av == bv, (col, j)
                )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_short_series_no_crash(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5])))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)

    def test_registration_imports_cleanly(self):
        import strategies.keltner_mean_reversion as mod

        self.assertEqual(mod.SPEC.slug, "keltner_mean_reversion")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 72)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
