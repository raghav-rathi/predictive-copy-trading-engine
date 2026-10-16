"""Tests for funding.ranking."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

from funding.api import FundingBar
from funding.config import FarmConfig
from funding.ranking import rank_coins, top_candidates


def bars(coin, rate, n):
    return [FundingBar(coin, rate, i * 3600_000) for i in range(n)]


class TestRanking(unittest.TestCase):
    def setUp(self):
        self.cfg = FarmConfig()

    def test_ranks_by_trailing_avg_descending(self):
        h = {
            "BTC": bars("BTC", 0.00001, 200),
            "ETH": bars("ETH", 0.00005, 200),
            "SOL": bars("SOL", 0.00003, 200),
        }
        ranked = rank_coins(h, self.cfg)
        self.assertEqual([r.coin for r in ranked], ["ETH", "SOL", "BTC"])
        self.assertAlmostEqual(ranked[0].apr, 0.00005 * 24 * 365)

    def test_thin_history_excluded(self):
        h = {
            "NEW": bars("NEW", 0.001, 10),   # huge funding, not enough history
            "BTC": bars("BTC", 0.00001, 200),
        }
        ranked = rank_coins(h, self.cfg)
        self.assertEqual([r.coin for r in ranked], ["BTC"])

    def test_top_candidates_respects_threshold_and_cap(self):
        h = {
            "A": bars("A", 0.00005, 200),   # clears
            "B": bars("B", 0.00004, 200),   # clears
            "C": bars("C", 0.00003, 200),   # clears
            "D": bars("D", 0.000001, 200),   # below entry threshold
        }
        ranked = rank_coins(h, self.cfg)
        top = top_candidates(ranked, self.cfg)
        self.assertEqual([r.coin for r in top], ["A", "B"])  # max_positions=2
        self.assertNotIn("D", [r.coin for r in top])

    def test_negative_funding_never_candidate(self):
        h = {"X": bars("X", -0.00005, 200)}
        ranked = rank_coins(h, self.cfg)
        self.assertEqual(top_candidates(ranked, self.cfg), [])


if __name__ == "__main__":
    unittest.main()
