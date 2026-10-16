"""Tests for funding.strategy decision rules."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

from funding.config import FarmConfig
from funding.ranking import RankedCoin
from funding.strategy import Action, Position, decide, four_leg_cost_hr


def rc(coin, avg):
    return RankedCoin(coin, avg, avg * 24 * 365, 200)


class TestStrategy(unittest.TestCase):
    def setUp(self):
        self.cfg = FarmConfig()

    def test_opens_top_candidates(self):
        ranked = [rc("ETH", 0.00005), rc("SOL", 0.00003)]
        actions = decide(ranked, {}, self.cfg)
        opens = [a for a in actions if a.kind == "open"]
        self.assertEqual([a.coin for a in opens], ["ETH", "SOL"])

    def test_exit_on_regime_flip(self):
        ranked = [rc("ETH", -0.00001)]  # flipped negative
        pos = {"ETH": Position("ETH", 1000.0, 0.00005, age_hours=10)}
        actions = decide(ranked, pos, self.cfg)
        closes = [a for a in actions if a.kind == "close"]
        self.assertEqual(len(closes), 1)
        self.assertIn("regime flip", closes[0].reason)

    def test_exit_on_max_hold(self):
        ranked = [rc("ETH", 0.00005)]
        pos = {"ETH": Position("ETH", 1000.0, 0.00005,
                               age_hours=31 * 24)}  # past 30d
        actions = decide(ranked, pos, self.cfg)
        closes = [a for a in actions if a.kind == "close"]
        self.assertEqual(len(closes), 1)
        self.assertIn("max hold", closes[0].reason)

    def test_switch_only_when_gain_beats_cost(self):
        cost = four_leg_cost_hr(self.cfg)
        horizon = self.cfg.switch_horizon_hours
        held_avg = 0.00005
        # Candidate whose carry gain over the horizon exactly fails the test.
        weak_avg = held_avg + (cost * 0.5) / horizon
        ranked = [rc("NEW", weak_avg), rc("ETH", held_avg)]
        pos = {"ETH": Position("ETH", 1000.0, held_avg, age_hours=10)}
        actions = decide(ranked, pos, self.cfg)
        self.assertEqual([a for a in actions if a.kind == "switch"], [])

        # Strong candidate: gain clears the cost.
        strong_avg = held_avg + (cost * 2.0) / horizon
        ranked = [rc("NEW", strong_avg), rc("ETH", held_avg)]
        actions = decide(ranked, pos, self.cfg)
        switches = [a for a in actions if a.kind == "switch"]
        self.assertEqual(len(switches), 1)
        self.assertEqual(switches[0].from_coin, "ETH")
        self.assertEqual(switches[0].coin, "NEW")

    def test_no_double_position_same_coin(self):
        ranked = [rc("ETH", 0.00005), rc("SOL", 0.00003)]
        pos = {"ETH": Position("ETH", 1000.0, 0.00005, age_hours=10)}
        actions = decide(ranked, pos, self.cfg)
        coins_opened = [a.coin for a in actions if a.kind == "open"]
        self.assertNotIn("ETH", coins_opened)
        self.assertIn("SOL", coins_opened)

    def test_four_leg_cost_positive(self):
        self.assertGreater(four_leg_cost_hr(self.cfg), 0)


if __name__ == "__main__":
    unittest.main()
