"""Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.supertrend_vwap import indicators, risk, signals


def _df_from_c(c, spread=0.2):
    c = np.asarray(c, float)
    n = len(c)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) + spread
    l = np.minimum(o, c) - spread
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame(
        {"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, 100.0)}
    )


def _rand_df(n=400, seed=11):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)

def _up_series():
    # flat, then a steady 1.5/bar rise, then flat. First long entry at 41.
    return np.concatenate(
        [np.full(40, 100.0), 100 + 1.5 * np.arange(40), np.full(30, 160.0)]
    )


def _down_series():
    # flat, then a steady 1.5/bar fall, then flat. First short at 41.
    return np.concatenate(
        [np.full(40, 160.0), 160 - 1.5 * np.arange(40), np.full(30, 100.0)]
    )


def _up_then_down_series():
    # uptrend (long entry 41) then a reversal; first exit after entry is 74.
    return np.concatenate(
        [np.full(40, 100.0), 100 + 1.5 * np.arange(30),
         145 - 1.5 * np.arange(30), np.full(20, 100.0)]
    )


class TestSupertrendVwap(unittest.TestCase):
    def test_supertrend_matches_base(self):
        from strategies import base as B

        df = indicators.add_indicators(_rand_df(800, seed=5))
        st = B.supertrend(df["h"], df["l"], df["c"], 10, 3.0)
        valid = st["supertrend"].notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "supertrend"], st.loc[valid, "supertrend"])))
        self.assertTrue(bool((df.loc[valid, "supertrend_dir"] == st.loc[valid, "supertrend_dir"]).all()))

    def test_vwap_matches_anchored_vwap(self):
        from strategies import base as B

        df = indicators.add_indicators(_rand_df(800, seed=5))
        expect = B.anchored_vwap(df["h"], df["l"], df["c"], df["v"], df["t"])
        valid = expect.notna()
        self.assertTrue(bool(np.allclose(df.loc[valid, "vwap"], expect[valid])))

    def test_vwap_resets_each_utc_day(self):
        # bars from 22:00 UTC day 1 through 01:00 UTC day 2: the first
        # bar of day 2 must be exactly its own typical price (fresh
        # session), and the first bar of day 1 its own typical price.
        t0 = int(pd.Timestamp("2023-11-14 22:00", tz="UTC").timestamp() * 1000)
        c = np.array([100.0, 101.0, 102.0, 103.0])
        o = np.array([100.0, 100.0, 101.0, 102.0])
        h = c + 0.2
        l = c - 0.2
        df = pd.DataFrame({
            "t": (t0 + np.arange(4) * 3_600_000).astype("int64"),
            "o": o, "h": h, "l": l, "c": c, "v": np.full(4, 100.0),
        })
        df = indicators.add_indicators(df)
        tp = (h + l + c) / 3.0
        self.assertAlmostEqual(float(df["vwap"].iloc[0]), float(tp[0]))
        self.assertAlmostEqual(float(df["vwap"].iloc[2]), float(tp[2]))
        # day 2's second bar is the volume-weighted mean of bars 2 and 3
        self.assertAlmostEqual(float(df["vwap"].iloc[3]), float((tp[2] + tp[3]) / 2.0))

    def test_long_fires_when_supertrend_up_and_close_above_vwap(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_up_series())))
        entries = sig.index[sig["long_entry"]].tolist()
        self.assertEqual(entries[0], 41)
        i = entries[0]
        self.assertEqual(float(sig["supertrend_dir"].iloc[i]), 1.0)
        self.assertGreater(float(sig["c"].iloc[i]), float(sig["vwap"].iloc[i]))

    def test_short_fires_when_supertrend_down_and_close_below_vwap(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_down_series())))
        entries = sig.index[sig["short_entry"]].tolist()
        self.assertEqual(entries[0], 41)
        i = entries[0]
        self.assertEqual(float(sig["supertrend_dir"].iloc[i]), -1.0)
        self.assertLess(float(sig["c"].iloc[i]), float(sig["vwap"].iloc[i]))

    def test_vwap_filter_blocks_long_below_vwap(self):
        ind = indicators.add_indicators(_df_from_c(_up_series()))
        ind["vwap"] = 1e9  # close never above VWAP: no long may fire
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_supertrend_filter_blocks_long_when_down(self):
        ind = indicators.add_indicators(_df_from_c(_up_series()))
        ind["supertrend_dir"] = -1.0  # Supertrend short: no long may fire
        sig = signals.add_signals(ind)
        self.assertFalse(bool(sig["long_entry"].any()))

    def test_exit_on_supertrend_flip_after_long(self):
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(_up_then_down_series())))
        entries = sig.index[sig["long_entry"]].tolist()
        exits = sig.index[sig["long_exit"]].tolist()
        self.assertTrue(len(entries) > 0)
        after = [e for e in exits if e > entries[0]]
        self.assertEqual(after[0], 74)

    def test_exit_on_close_below_vwap(self):
        ind = indicators.add_indicators(_df_from_c(_up_series()))
        ind["vwap"] = ind["c"] + 1.0  # close always below VWAP
        sig = signals.add_signals(ind)
        self.assertTrue(bool(sig["long_exit"].all()))

    def test_random_walk_fires_both_sides(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        self.assertTrue(bool(sig["long_entry"].any()))
        self.assertTrue(bool(sig["short_entry"].any()))
        self.assertFalse(bool((sig["long_entry"] & sig["short_entry"]).any()))

    def test_no_nan_after_warmup_and_boolean_signals(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df(800, seed=5)))
        for col in ("supertrend", "supertrend_dir", "vwap", "atr14"):
            self.assertFalse(sig[col].iloc[60:].isna().any(), col)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("supertrend", "supertrend_dir", "vwap", "atr14"):
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
        import strategies.supertrend_vwap as mod

        self.assertEqual(mod.SPEC.slug, "supertrend_vwap")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 120)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertEqual(risk.RISK.fee_rate, 0.00045)
        self.assertEqual(risk.RISK.slippage_rate, 0.0001)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 40)


if __name__ == "__main__":
    unittest.main()
