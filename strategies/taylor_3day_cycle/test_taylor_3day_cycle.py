"""Taylor 3-day cycle tests. Network-free, synthetic data only."""

import os
import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pandas as pd

from strategies.taylor_3day_cycle import indicators, risk, signals
from strategies.taylor_3day_cycle.indicators import (
    BUY_DAY, SELL_DAY, SELL_SHORT_DAY, _ny_day, _rephased_labels,
    NY_OFFSET_MS, DAY_MS, ANCHOR_UTC_MS,
)

T0 = int(datetime(2023, 11, 14, tzinfo=timezone.utc).timestamp() * 1000)  # UTC midnight


def _ohlcv(o, h, l, c, t0=T0, v=100.0):
    n = len(c)
    t = (t0 + np.arange(n) * 3_600_000).astype("int64")
    return pd.DataFrame({"t": t, "o": o, "h": h, "l": l, "c": c, "v": np.full(n, v)})


def _flat_days(n_days, px=100.0, spread=0.05):
    n = n_days * 24
    c = np.full(n, px)
    o = c.copy()
    return _ohlcv(o, c + spread, c - spread, c)


class TestTaylorCycle(unittest.TestCase):
    def test_ny_day_boundary_at_0400_utc(self):
        # bars 00:00-03:00 UTC belong to the previous NY day
        ind = indicators.add_indicators(_flat_days(3))
        ny = ind["ny_day"].to_numpy()
        # 4 bars before the 04:00 UTC boundary share a day, next 20 a new one
        self.assertTrue((ny[:4] == ny[0]).all())
        self.assertTrue((ny[4:24] == ny[0] + 1).all())
        # NY day boundary hits at 04:00 UTC -> bar 28 starts a new NY day
        self.assertEqual(int(ny[28]), int(ny[4]) + 1)
        self.assertEqual(int(ny[24]), int(ny[4]))

    def test_anchor_day_is_monday(self):
        # the NY calendar date at the anchor must be a Monday
        ny_dt = datetime.fromtimestamp(
            (ANCHOR_UTC_MS - NY_OFFSET_MS) / 1000, tz=timezone.utc
        )
        self.assertEqual(ny_dt.date().isoformat(), "2026-01-05")
        self.assertEqual(ny_dt.weekday(), 0)  # Monday

    def test_prior_day_high_low_hand_computed(self):
        n = 48
        c = np.full(n, 100.0)
        h = c + 0.05
        l = c - 0.05
        # day 0 (first 4 bars, prev NY day): push high to 105 on bar 1
        h[1] = 105.0
        # next NY day (bars 4..23): push low to 90 on bar 10
        l[10] = 90.0
        df = _ohlcv(c, h, l, c)
        ind = indicators.add_indicators(df)
        ny = ind["ny_day"].to_numpy()
        day2 = ny[0] + 2
        m2 = ny == day2
        # prior day for day2 is the day holding bars 4..23 -> high 100.05, low 90
        self.assertTrue((ind["prior_day_high"][m2] == 100.05).all())
        self.assertTrue((ind["prior_day_low"][m2] == 90.0).all())
        # first NY day in frame has no prior day -> NaN
        m0 = ny == ny[0]
        self.assertTrue(ind["prior_day_high"][m0].isna().all())

    def test_long_candidate_dip_and_recovery(self):
        # prior day low = 99; bar dips to 99.02 (within 0.1xATR) and recovers
        n = 96
        c = np.full(n, 100.0)
        o = c.copy()
        h = c + 0.05
        l = c - 0.05
        # prior-day setup on second NY day: low 99.0
        l[30] = 99.0
        # dip bar: low 98.9 (within 0.1xATR of 99.0 once the spike decays),
        # green close
        o[60], l[60], c[60], h[60] = 100.0, 98.9, 100.2, 100.3
        ind = indicators.add_indicators(_ohlcv(o, h, l, c))
        self.assertTrue(bool(ind["long_cand"].iloc[60]))

    def test_long_candidate_requires_recovery(self):
        n = 96
        c = np.full(n, 100.0)
        o = c.copy()
        h = c + 0.05
        l = c - 0.05
        l[30] = 99.0
        # dips but closes red -> no candidate
        o[60], l[60], c[60], h[60] = 100.0, 98.9, 99.8, 100.1
        ind = indicators.add_indicators(_ohlcv(o, h, l, c))
        self.assertFalse(bool(ind["long_cand"].iloc[60]))

    def test_short_candidate_rally_and_reject(self):
        n = 96
        c = np.full(n, 100.0)
        o = c.copy()
        h = c + 0.05
        l = c - 0.05
        h[30] = 101.0
        # rallies to the 101.0 level itself and rejects (red bar)
        o[60], h[60], c[60], l[60] = 100.0, 101.0, 99.8, 99.7
        ind = indicators.add_indicators(_ohlcv(o, h, l, c))
        self.assertTrue(bool(ind["short_cand"].iloc[60]))

    def test_rephase_walk_shifts_offset_after_missed_buy_day(self):
        # day 0 = Buy Day with no long candidates -> offset -1 from day 1 on;
        # day 1 then lands on Buy again, fires, and the rest of the cycle
        # resumes shifted by exactly one day.
        anchor_day = (ANCHOR_UTC_MS - NY_OFFSET_MS) // DAY_MS
        days = anchor_day + np.arange(5)
        ny_day = np.repeat(days, 24)
        long_cand = np.zeros(len(ny_day), dtype=bool)
        long_cand[ny_day == days[1]] = True  # fires on the rephased Buy Day
        labels = _rephased_labels(ny_day, long_cand)
        self.assertTrue((labels[ny_day == days[0]] == BUY_DAY).all())
        self.assertTrue((labels[ny_day == days[1]] == BUY_DAY).all())  # (1-1)%3
        self.assertTrue((labels[ny_day == days[2]] == SELL_DAY).all())  # (2-1)%3
        self.assertTrue(
            (labels[ny_day == days[3]] == SELL_SHORT_DAY).all()
        )  # (3-1)%3
        self.assertTrue((labels[ny_day == days[4]] == BUY_DAY).all())  # (4-1)%3

    def test_rephase_does_not_shift_when_buy_day_fires(self):
        anchor_day = (ANCHOR_UTC_MS - NY_OFFSET_MS) // DAY_MS
        days = anchor_day + np.arange(4)
        ny_day = np.repeat(days, 24)
        long_cand = np.zeros(len(ny_day), dtype=bool)
        long_cand[ny_day == days[0]] = False
        long_cand[5] = True  # candidate on the Buy Day (day 0)
        labels = _rephased_labels(ny_day, long_cand)
        self.assertTrue((labels[ny_day == days[1]] == SELL_DAY).all())
        self.assertTrue((labels[ny_day == days[2]] == SELL_SHORT_DAY).all())

    def test_signal_gating_by_cycle_day(self):
        # dips built on every day: entries only fire on Buy Days
        n_days = 9
        n = n_days * 24
        c = np.full(n, 100.0)
        o = c.copy()
        h = c + 0.05
        l = c - 0.05
        for d in range(n_days):
            j = d * 24 + 12
            l[j] = 99.0  # define each day's own low so next day can dip
            k = d * 24 + 36 if (d * 24 + 36) < n else None
        # next-day dip bars: low within 0.1xATR of prior low, green close
        for d in range(1, n_days):
            j = d * 24 + 12
            o[j], l[j], c[j], h[j] = 100.0, 99.0, 100.3, 100.4
        ind = indicators.add_indicators(_ohlcv(o, h, l, c))
        sig = signals.add_signals(ind)
        le = sig.index[sig["long_entry"]]
        self.assertGreater(len(le), 0)
        for j in le:
            self.assertEqual(int(ind["cycle_label"].iloc[j]), BUY_DAY)

    def test_sell_day_has_no_new_entries(self):
        n_days = 9
        n = n_days * 24
        c = np.full(n, 100.0)
        o = c.copy()
        h = c + 0.05
        l = c - 0.05
        for d in range(1, n_days):
            j = d * 24 + 12
            o[j], l[j], c[j], h[j] = 100.0, 99.0, 100.3, 100.4
        sig = signals.add_signals(indicators.add_indicators(_ohlcv(o, h, l, c)))
        # no entry signal on a Sell Day bar, whatever the price action
        ind = indicators.add_indicators(_ohlcv(o, h, l, c))
        sig = signals.add_signals(ind)
        sell_mask = ind["cycle_label"] == SELL_DAY
        self.assertEqual(int(sig.loc[sell_mask, "long_entry"].sum()), 0)
        self.assertEqual(int(sig.loc[sell_mask, "short_entry"].sum()), 0)

    def test_exit_at_prior_day_high(self):
        # a bar whose high reaches the prior NY-day high must fire long_exit
        n = 10 * 24
        c = np.full(n, 100.0)
        o = c.copy()
        h = c + 0.05
        l = c - 0.05
        ind = indicators.add_indicators(_ohlcv(o, h, l, c))
        k = 100
        self.assertFalse(np.isnan(ind["prior_day_high"].iloc[k]))
        h2 = h.copy()
        h2[k] = ind["prior_day_high"].iloc[k] + 1.0
        sig2 = signals.add_signals(indicators.add_indicators(_ohlcv(o, h2, l, c)))
        self.assertTrue(bool(sig2["long_exit"].iloc[k]))

    def test_no_lookahead_truncation(self):
        n = 10 * 24
        rng = np.random.default_rng(7)
        rets = rng.normal(0, 0.002, n)
        c = 100.0 * np.exp(np.cumsum(rets))
        o = np.concatenate([[c[0]], c[:-1]])
        h = np.maximum(o, c) * (1 + rng.uniform(0, 0.002, n))
        l = np.minimum(o, c) * (1 - rng.uniform(0, 0.002, n))
        full = _ohlcv(o, h, l, c)
        ind_full = indicators.add_indicators(full)
        for j in (120, 200):
            ind_tr = indicators.add_indicators(full.iloc[: j + 1])
            for col in ("prior_day_high", "prior_day_low", "atr",
                        "long_cand", "short_cand", "cycle_label"):
                av, bv = ind_full[col].iloc[j], ind_tr[col].iloc[j]
                if isinstance(av, (bool, np.bool_)):
                    self.assertEqual(bool(av), bool(bv), (col, j))
                else:
                    self.assertTrue(
                        (pd.isna(av) and pd.isna(bv)) or abs(av - bv) < 1e-9,
                        (col, j),
                    )
            sig_full = signals.add_signals(ind_full)
            sig_tr = signals.add_signals(ind_tr)
            for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
                self.assertEqual(
                    bool(sig_full[col].iloc[j]), bool(sig_tr[col].iloc[j]), (col, j)
                )

    def test_registration_imports_cleanly(self):
        import strategies.taylor_3day_cycle as mod
        self.assertEqual(mod.SPEC.slug, "taylor_3day_cycle")
        self.assertEqual(mod.SPEC.warmup_bars, 72)

    def test_risk_config_sane(self):
        self.assertEqual(risk.RISK.stop_atr_mult, 1.0)
        self.assertIsNone(risk.RISK.trail_atr_mult)
        self.assertIsNone(risk.RISK.target_atr_mult)
        self.assertEqual(risk.RISK.max_hold_bars, 24)
        self.assertEqual(risk.RISK.risk_frac, 0.01)
        self.assertEqual(risk.RISK.max_leverage, 3.0)
        self.assertTrue(risk.RISK.allow_longs and risk.RISK.allow_shorts)
        self.assertEqual(risk.WARMUP, 72)


if __name__ == "__main__":
    unittest.main()
