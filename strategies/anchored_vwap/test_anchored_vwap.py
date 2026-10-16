"""Anchored VWAP tests. Network-free, synthetic data only."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.anchored_vwap import indicators, risk, signals


def _frame(n, c, v=None):
    c = pd.Series(np.asarray(c, float))
    o = pd.Series(np.concatenate([[c.iloc[0]], c.iloc[:-1].to_numpy()]))
    h = pd.concat([o, c], axis=1).max(axis=1) + 0.05
    l = pd.concat([o, c], axis=1).min(axis=1) - 0.05
    t = (1_700_000_000_000 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c,
                         "v": np.full(n, 100.0) if v is None else np.asarray(v, float)})


class TestAnchoredVWAP(unittest.TestCase):
    def _trendy(self, n=400, seed=7):
        rng = np.random.default_rng(seed)
        c = 100 + 0.08 * np.arange(n) + np.cumsum(rng.normal(0, 0.3, n))
        return indicators.add_indicators(_frame(n, c))

    def test_avwap_matches_manual_formula(self):
        df = self._trendy()
        sub = df.dropna(subset=["avwap"]).iloc[200:]
        i = sub.index[50]
        a = int(df.loc[i, "avwap_anchor"])
        seg = df.iloc[a:i + 1]
        tp = (seg["h"] + seg["l"] + seg["c"]) / 3.0
        expected = (tp * seg["v"]).sum() / seg["v"].sum()
        self.assertAlmostEqual(df.loc[i, "avwap"], expected, places=8)

    def test_anchor_used_only_after_confirmation_lag(self):
        # a swing low centred at bar j may not anchor anything before j+25
        df = self._trendy()
        valid = df[df["avwap"].notna()]
        lag = valid.index.to_numpy() - valid["avwap_anchor"].to_numpy()
        self.assertTrue((lag >= 25).all(),
                        f"anchor used before confirmation: min lag {lag.min()}")

    def test_swing_low_anchors_bull_line(self):
        n = 400
        c = np.full(n, 100.0)
        c[150] = 80.0  # isolated deep dip -> confirmed swing low at 150
        df = indicators.add_indicators(_frame(n, c))
        # before confirmation the anchor cannot exist
        self.assertTrue(df.loc[:174, "avwap"].isna().all())
        # after bar 175 the bull anchor (bar 150) is live
        self.assertFalse(df.loc[176:, "avwap_bull"].isna().all())
        self.assertEqual(int(df.loc[180, "avwap_anchor"]), 150)

    def test_reclaim_entry_fires_on_dip_reclaim(self):
        # rally -> 30-bar decline -> flat base -> breakout: the base
        # anchors the VWAP and the breakout is a genuine reclaim
        n = 400
        i = np.arange(n)
        c = np.where(i < 100, 100 + 0.1 * i,
             np.where(i < 130, 110 - (i - 100) * (20 / 30),
             np.where(i < 160, 90.0, 90.0 + 0.4 * (i - 160))))
        sig = signals.add_signals(indicators.add_indicators(_frame(n, c)))
        longs = sig.index[sig["long_entry"]].tolist()
        self.assertTrue(any(155 <= j <= 180 for j in longs),
                        f"no reclaim entry near the breakout; got {longs[:6]}")

    def test_graze_without_dip_does_not_fire(self):
        # price kisses the line: only 1 bar below in the window -> no entry
        df = self._trendy()
        df = df.copy()
        av = df["avwap"].ffill().bfill()
        cl = av + 0.5
        cl.iloc[200] = av.iloc[200] - 0.1  # single bar below
        df["c"] = cl
        df["avwap"] = av
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].iloc[190:215].any())

    def test_slope_filter_blocks_falling_line_cross(self):
        # a cross-up while the anchor line itself is falling must not fire
        df = self._trendy()
        df = df.copy()
        av = pd.Series(100.0 - 0.1 * np.arange(len(df)), index=df.index)
        cl = av + 0.5
        cl.iloc[250] = av.iloc[250] - 0.5  # cross happens, line falling
        df["c"], df["avwap"] = cl, av
        sig = signals.add_signals(df)
        self.assertFalse(sig["long_entry"].iloc[245:260].any())

    def test_no_lookahead_signal_uses_only_past(self):
        # duplicating the close series into the future must not change
        # any signal at or before the original end
        df = self._trendy()
        sig1 = signals.add_signals(df)
        df2 = pd.concat([df, df], ignore_index=True)
        sig2 = signals.add_signals(indicators.add_indicators(df2))
        pd.testing.assert_series_equal(
            sig1["long_entry"], sig2["long_entry"].iloc[:len(df)].reset_index(drop=True),
            check_names=False)

    def test_signal_columns_bool_no_nan(self):
        df = self._trendy()
        sig = signals.add_signals(df)
        for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
            self.assertFalse(sig[col].isna().any())
            self.assertTrue(sig[col].dtype == bool)

    def test_risk_config_sane(self):
        self.assertEqual(risk.WARMUP, 120)
        self.assertEqual(risk.RISK.stop_atr_mult, 2.0)
        self.assertEqual(risk.RISK.trail_atr_mult, 3.0)

    def test_registration(self):
        import strategies.anchored_vwap as m
        from strategies.registry import REGISTRY
        self.assertIn("anchored_vwap", REGISTRY)
        self.assertIs(REGISTRY["anchored_vwap"], m.SPEC)


if __name__ == "__main__":
    unittest.main()
