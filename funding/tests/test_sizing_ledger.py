"""Tests for funding.sizing, funding.ledger and funding.guardrails."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

from funding.config import FarmConfig
from funding.guardrails import GuardrailConfig, apply, check
from funding.ledger import Ledger
from funding.paper import FarmState, new_farm
from funding.ranking import RankedCoin
from funding.sizing import size_positions
from funding.strategy import Position


def rc(coin, avg):
    return RankedCoin(coin, avg, avg * 24 * 365, 200)


class TestSizing(unittest.TestCase):
    def test_carry_weighted_with_cap(self):
        cfg = FarmConfig(farm_capital=10_000, max_weight_per_coin=0.25)
        cands = [rc("ETH", 0.00006), rc("SOL", 0.00002)]
        sizes = size_positions(cands, cfg)
        # weights 75/25; ETH capped at 2500
        self.assertAlmostEqual(sizes["ETH"], 2500.0)
        self.assertAlmostEqual(sizes["SOL"], 2500.0)

    def test_single_dominant_coin_still_capped(self):
        cfg = FarmConfig(farm_capital=10_000, max_weight_per_coin=0.25)
        sizes = size_positions([rc("ETH", 0.00009)], cfg)
        self.assertAlmostEqual(sizes["ETH"], 2500.0)

    def test_no_positive_carry_no_sizes(self):
        self.assertEqual(size_positions([rc("X", -0.00001)]), {})


class TestLedger(unittest.TestCase):
    def test_funding_accrual_and_close(self):
        cfg = FarmConfig()
        led = Ledger(equity=10_000)
        led.open("ETH", 2500.0, 3000.0, 0.00005,
                 cfg.perp_taker_fee, cfg.spot_fee)
        for _ in range(24):
            led.accrue_funding("ETH", 0.00005)   # 24h at 0.005%/hr
        row = led.close("ETH", 3000.0, cfg.perp_taker_fee, cfg.spot_fee)
        self.assertAlmostEqual(row["carry_pnl"], 2500 * 0.00005 * 24, places=4)
        fees = 2500 * (cfg.perp_taker_fee + cfg.spot_fee) * 2
        self.assertAlmostEqual(row["fees"], fees, places=4)
        self.assertAlmostEqual(row["net"], row["carry_pnl"] - fees, places=4)
        self.assertAlmostEqual(led.equity, 10_000 + row["net"], places=4)

    def test_negative_funding_is_a_cost(self):
        cfg = FarmConfig()
        led = Ledger(equity=10_000)
        led.open("ETH", 1000.0, 3000.0, 0.00005,
                 cfg.perp_taker_fee, cfg.spot_fee)
        led.accrue_funding("ETH", -0.0001)
        row = led.close("ETH", 3000.0, cfg.perp_taker_fee, cfg.spot_fee)
        self.assertLess(row["carry_pnl"], 0)


class TestGuardrails(unittest.TestCase):
    def test_drawdown_trip_and_pause(self):
        state = new_farm()
        state.positions["ETH"] = Position("ETH", 1000.0, 0.00005)
        state.ledger.equity = 9_400  # -6% from 10k peak
        trips = check(state, peak_equity=10_000)
        self.assertTrue(any("drawdown" in t for t in trips))
        self.assertTrue(apply(state, trips))
        self.assertTrue(state.paused)

    def test_clean_state_no_trips(self):
        state = new_farm()
        self.assertEqual(check(state, peak_equity=10_000), [])
        self.assertFalse(apply(state, []))


if __name__ == "__main__":
    unittest.main()
