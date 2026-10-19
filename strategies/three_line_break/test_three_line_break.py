"""Three-line break tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.three_line_break import indicators, risk, signals


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


def _rand_df(n=400, seed=5):
    rng = np.random.default_rng(seed)
    c = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    return _df_from_c(c)


class TestThreeLineBreak(unittest.TestCase):
    def test_steady_climb_stays_white(self):
        c = 100.0 + 1.0 * np.arange(100)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((df["tlb_dir"] == 1).all()))

    def test_steady_fall_stays_black(self):
        c = 100.0 - 1.0 * np.arange(100)
        df = indicators.add_indicators(_df_from_c(c))
        self.assertTrue(bool((df["tlb_dir"] == -1).all()))

    def test_v_reversal_flips_white(self):
        # deep V: black sequence, then a close above the last-3-lines high
        c = np.concatenate([100.0 - 1.0 * np.arange(60),
                            40.0 + 3.0 * np.arange(40)])
        df = indicators.add_indicators(_df_from_c(c))
        d = df["tlb_dir"].to_numpy()
        self.assertTrue(bool((d[30:55] == -1).all()))
        self.assertEqual(d[-1], 1)
        flips = np.where((d[1:] == 1) & (d[:-1] == -1))[0]
        self.assertGreater(len(flips), 0)

    def test_turnaround_fires_entry(self):
        c = np.concatenate([100.0 - 1.0 * np.arange(60),
                            40.0 + 3.0 * np.arange(40)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        d = sig["tlb_dir"].to_numpy()
        exp_long = (d[1:] == 1) & (d[:-1] == -1)
        got = sig["long_entry"].to_numpy()[1:]
        self.assertTrue(bool((got == exp_long).all()))
        self.assertGreater(int(got.sum()), 0)

    def test_bearish_turnaround_fires_short(self):
        c = np.concatenate([40.0 + 1.0 * np.arange(60),
                            100.0 - 3.0 * np.arange(40)])
        sig = signals.add_signals(indicators.add_indicators(_df_from_c(c)))
        self.assertGreater(int(sig["short_entry"].sum()), 0)

    def test_exits_are_opposite_flips(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        self.assertTrue(bool((sig["long_exit"] == sig["short_entry"]).all()))
        self.assertTrue(bool((sig["short_exit"] == sig["long_entry"]).all()))

    def test_no_reversal_without_three_lines(self):
        # 3 bars: only 2 seeded lines exist, the reversal check needs 3
        # reference lines, so the seeded direction just carries
        df = indicators.add_indicators(_df_from_c([100.0, 101.0, 100.5]))
        self.assertEqual(list(df["tlb_dir"]), [1.0, -1.0, -1.0])

    def test_n_lines_param_changes_sensitivity(self):
        rng = np.random.default_rng(3)
        c = 100.0 + np.cumsum(rng.normal(0, 0.8, 300))
        d2 = indicators.add_indicators(_df_from_c(c), n_lines=2)["tlb_dir"]
        d4 = indicators.add_indicators(_df_from_c(c), n_lines=4)["tlb_dir"]
        # the reference-line count is a real sensitivity knob: it must
        # change the series on noisy data (direction of change is
        # path-dependent, so no monotonicity claim)
        self.assertFalse(bool((d2 == d4).all()))
        for d_ in (d2, d4):
            self.assertTrue(bool(set(d_.unique()) <= {1.0, -1.0}))

    def test_run_counter_resets_on_flip(self):
        c = np.concatenate([100.0 - 1.0 * np.arange(60),
                            40.0 + 3.0 * np.arange(40)])
        df = indicators.add_indicators(_df_from_c(c))
        d = df["tlb_dir"].to_numpy()
        run = df["tlb_run"].to_numpy()
        flips = np.where(d[1:] != d[:-1])[0] + 1
        self.assertGreater(len(flips), 0)
        self.assertEqual(run[flips[0]], 1.0)

    def test_no_lookahead_truncation(self):
        full = _rand_df(300)
        ind_full = indicators.add_indicators(full)
        for j in (150, 260):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("tlb_dir", "tlb_run"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                self.assertTrue((pd.isna(av) and pd.isna(bv)) or av == bv, (col, j))
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j))

    def test_signals_boolean_clean(self):
        sig = signals.add_signals(indicators.add_indicators(_rand_df()))
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any(), col)
            self.assertTrue(set(sig[col].unique()) <= {True, False}, col)

    def test_registration_imports_cleanly(self):
        import strategies.three_line_break as mod

        self.assertEqual(mod.SPEC.slug, "three_line_break")
        self.assertEqual(mod.SPEC.warmup_bars, risk.WARMUP)
        self.assertEqual(set(mod.__all__), {"indicators", "signals", "risk", "SPEC"})

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 60)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 60)


if __name__ == "__main__":
    unittest.main()
