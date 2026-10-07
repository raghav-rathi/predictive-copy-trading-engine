"""Tests for hyperliquid.flow_filter and the scorer flow gate."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

from flow_filter import detect_uncopyable, flow_metrics, is_uncopyable
from scorer import classify


def fill(coin, dir, ts_s, sz=1.0, px=100.0):
    return {"coin": coin, "dir": dir, "time": ts_s, "sz": sz, "px": px}


def roundtrip(coin, side, t0, hold_s, n, gap_s=3600.0):
    """n open->close round trips, `side` = 'Long'|'Short'."""
    out = []
    for i in range(n):
        t = t0 + i * gap_s
        out.append(fill(coin, f"Open {side}", t))
        out.append(fill(coin, f"Close {side}", t + hold_s))
    return out


class TestFlowMetrics(unittest.TestCase):
    def test_hft_flagged(self):
        # 60 fills in 2 hours = 30/hr sustained
        fills = [fill("BTC", "Open Long", 1_700_000_000 + i * 120)
                 for i in range(60)]
        flags, m = is_uncopyable(fills, 0)
        self.assertIn("hft", flags)
        self.assertGreaterEqual(m["trades_per_hour"], 10)

    def test_hft_burst_flagged(self):
        # 45 parent orders inside each of 3 separate hours, days apart:
        # recurring machine flow, not a one-off rebalance.
        fills = []
        base = 1_700_000_000
        for day in range(3):
            t0 = base + day * 86400
            fills += [fill("ETH", "Open Long", t0 + i * 30)
                      for i in range(110)]
        flags, m = is_uncopyable(fills, 0)
        self.assertIn("hft", flags)
        self.assertGreaterEqual(m["burst_hours_100ph"], 3)

    def test_single_burst_hour_not_flagged(self):
        # one busy hour amid a month of quiet flow = rebalance, not HFT
        fills = [fill("ETH", "Open Long", 1_700_000_000 + i * 30)
                 for i in range(120)]
        fills += [fill("ETH", "Open Long", 1_700_000_000 + 86400 * d)
                  for d in range(1, 11)]
        flags, m = is_uncopyable(fills, 0)
        self.assertEqual(m["burst_hours_100ph"], 1)
        self.assertNotIn("hft", flags)

    def test_fragment_dedup(self):
        # 200 fills but only 10 distinct timestamps -> 10 parent orders
        fills = []
        for i in range(10):
            t = 1_700_000_000 + i * 3600
            fills += [fill("BTC", "Open Long", t) for _ in range(20)]
        flags, m = is_uncopyable(fills, 0)
        self.assertEqual(m["n_fills"], 10)
        self.assertNotIn("hft", flags)

    def test_scalper_flagged(self):
        fills = roundtrip("SOL", "Long", 1_700_000_000, hold_s=120, n=60,
                          gap_s=3600.0)
        flags, m = is_uncopyable(fills, 60)
        self.assertIn("scalper", flags)
        self.assertLessEqual(m["avg_hold_s"], 300)

    def test_market_maker_flagged(self):
        fills = [fill("BTC", "Open Long", 1_700_000_000),
                 fill("BTC", "Open Short", 1_700_000_100)]
        flags, m = is_uncopyable(fills, 0)
        self.assertIn("market_maker", flags)
        self.assertIn("BTC", m["both_sides_coins"])

    def test_flipper_flagged(self):
        fills = []
        t = 1_700_000_000
        for i in range(40):
            side = "Long" if i % 2 == 0 else "Short"
            fills.append(fill("DOGE", f"Open {side}", t + i * 3600))
            fills.append(fill("DOGE", f"Close {side}", t + i * 3600 + 1800))
        flags, _ = is_uncopyable(fills, 40)
        self.assertIn("flipper", flags)

    def test_swing_trader_clean(self):
        # 20 round trips, 4h holds, spread over 10 days
        fills = roundtrip("BTC", "Long", 1_700_000_000, hold_s=4 * 3600,
                          n=20, gap_s=12 * 3600)
        flags, m = is_uncopyable(fills, 20)
        self.assertEqual(flags, [])
        self.assertLess(m["trades_per_hour"], 10)

    def test_empty_fills_clean(self):
        flags, _ = is_uncopyable([], 0)
        self.assertEqual(flags, [])

    def test_small_sample_not_flagged(self):
        # 20 fills in 30 minutes looks fast but n < hft_min_fills
        fills = [fill("BTC", "Open Long", 1_700_000_000 + i * 90)
                 for i in range(20)]
        flags, _ = is_uncopyable(fills, 0)
        self.assertNotIn("hft", flags)


class TestFlowGate(unittest.TestCase):
    def test_flags_force_pass_despite_high_score(self):
        cls, watch = classify(95.0, 200, 10, 65, 30,
                              flow_flags=["hft"])
        self.assertEqual(cls, "pass")
        self.assertFalse(watch)

    def test_flags_never_fade(self):
        # a terrible score + hft flag -> pass, NOT fade
        cls, _ = classify(5.0, 200, 10, 65, 30,
                          flow_flags=["scalper"])
        self.assertEqual(cls, "pass")

    def test_no_flags_normal_classification(self):
        self.assertEqual(classify(80.0, 200, 10, 65, 30)[0], "copy")
        self.assertEqual(classify(20.0, 200, 10, 65, 30)[0], "fade")
        self.assertEqual(classify(50.0, 200, 10, 65, 30)[0], "pass")


if __name__ == "__main__":
    unittest.main()
