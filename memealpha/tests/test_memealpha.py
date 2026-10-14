"""Unit tests for the memealpha wallet-discovery pipeline.

Network-free: every test runs on synthetic fixture data.
Run:  python3 -m unittest memealpha.tests.test_memealpha
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from memealpha.convergence import convergence_coverage, find_convergence
from memealpha.discovery import (
    PROGRAM_BLOCKLIST,
    EarlyBuyer,
    earliest_buyers_from_traders,
    earliest_buyers_from_transfers,
)
from memealpha.filters import bot_verdict, filter_active, filter_bots, trade_intervals
from memealpha.pipeline import run_pipeline
from memealpha.scoring import CRITERIA, PASS_THRESHOLD, rubric_table, score_token

NOW = 1_760_000_000.0  # fixed clock for deterministic tests
DAY = 86400.0


def _trader(addr, first_buy_time, usd=100.0):
    return {"address": addr, "first_buy_time": first_buy_time, "first_buy_usd": usd}


class TestDiscovery(unittest.TestCase):
    def test_earliest_buyers_sorted_and_capped(self):
        rows = [
            _trader("W3", NOW - 3000),
            _trader("W1", NOW - 9000),
            _trader("W2", NOW - 6000),
            _trader("W1", NOW - 9000),  # duplicate wallet -> deduped
        ]
        out = earliest_buyers_from_traders(rows, n=2, now=NOW)
        self.assertEqual([b.address for b in out], ["W1", "W2"])

    def test_earliest_buyers_skips_program_addresses(self):
        prog = next(iter(PROGRAM_BLOCKLIST))
        rows = [_trader(prog, NOW - 9000), _trader("human1", NOW - 8000)]
        out = earliest_buyers_from_traders(rows, n=20, now=NOW)
        self.assertEqual([b.address for b in out], ["human1"])

    def test_earliest_buyers_ms_timestamps_normalized(self):
        rows = [_trader("W1", int((NOW - 5000) * 1000))]
        out = earliest_buyers_from_traders(rows, n=20, now=NOW)
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0].first_buy_ts, NOW - 5000, delta=1.0)

    def test_earliest_buyers_from_etherscan_transfers(self):
        zero = "0x0000000000000000000000000000000000000000"
        txs = [
            {"to": "0xaaa", "from": zero, "timeStamp": "1700000000", "hash": "0x1"},
            {"to": "0xbbb", "from": "0xccc", "timeStamp": "1700000060", "hash": "0x2"},
            {"to": "0xddd", "from": "0xeee", "timeStamp": "1700000120", "hash": "0x3"},
        ]
        out = earliest_buyers_from_transfers(txs, n=20)
        # mint leg (to 0xaaa from the zero address) is skipped
        self.assertEqual([b.address for b in out], ["0xbbb", "0xddd"])


class TestFilters(unittest.TestCase):
    def test_filter_active_keeps_recent_only(self):
        last = {"active": NOW - 5 * DAY, "stale": NOW - 60 * DAY, "never": 0.0}
        counts = {"active": 12, "stale": 3, "never": 0}
        kept, dropped = filter_active(last, counts, days=30, now=NOW)
        self.assertEqual([v.address for v in kept], ["active"])
        self.assertEqual(sorted(v.address for v in dropped), ["never", "stale"])

    def test_trade_intervals_sorted_gaps(self):
        self.assertEqual(trade_intervals([100.0, 130.0, 115.0]), [15.0, 15.0])

    def test_bot_verdict_flags_second_spaced_trades(self):
        ts = [NOW - i * 4.0 for i in range(20)]  # a trade every ~4 seconds
        v = bot_verdict("bot1", ts)
        self.assertTrue(v.is_bot)
        self.assertLess(v.median_gap_s, 60.0)
        self.assertGreater(v.sub_10s_share, 0.5)

    def test_bot_verdict_keeps_human_pacing(self):
        ts = [NOW - i * 5 * 3600.0 for i in range(10)]  # every few hours
        v = bot_verdict("human1", ts)
        self.assertFalse(v.is_bot)

    def test_bot_verdict_thin_data_not_condemned(self):
        v = bot_verdict("newbie", [NOW - 100.0, NOW - 50.0])
        self.assertFalse(v.is_bot)
        self.assertIn("insufficient evidence", v.reason)

    def test_filter_bots_splits(self):
        bot_ts = [NOW - i * 3.0 for i in range(10)]
        human_ts = [NOW - i * 7200.0 for i in range(10)]
        humans, bots = filter_bots({"b1": bot_ts, "h1": human_ts})
        self.assertEqual([v.address for v in humans], ["h1"])
        self.assertEqual([v.address for v in bots], ["b1"])


class TestConvergence(unittest.TestCase):
    def test_three_wallet_rule(self):
        holdings = {
            "w1": {"AAA", "BBB"},
            "w2": {"AAA", "CCC"},
            "w3": {"AAA", "DDD"},
            "w4": {"EEE"},
        }
        out = find_convergence(holdings, min_wallets=3)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].token, "AAA")
        self.assertEqual(out[0].wallet_count, 3)
        self.assertEqual(out[0].wallets, ["w1", "w2", "w3"])
        self.assertAlmostEqual(convergence_coverage(out[0]), 0.75)

    def test_two_wallets_is_not_signal(self):
        holdings = {"w1": {"AAA"}, "w2": {"AAA"}}
        self.assertEqual(find_convergence(holdings, min_wallets=3), [])

    def test_sorted_by_count_desc(self):
        holdings = {
            "w1": {"AAA", "BBB"},
            "w2": {"AAA", "BBB"},
            "w3": {"AAA", "BBB"},
            "w4": {"AAA"},
        }
        out = find_convergence(holdings, min_wallets=3)
        self.assertEqual([c.token for c in out], ["AAA", "BBB"])


class TestScoring(unittest.TestCase):
    def test_rubric_has_nine_criteria(self):
        self.assertEqual(len(CRITERIA), 9)
        self.assertEqual(PASS_THRESHOLD, 9)

    def test_perfect_card_passes(self):
        feats = {key: True for key, _, _ in CRITERIA}
        s = score_token("AAA", feats)
        self.assertEqual(s.total, 9)
        self.assertTrue(s.passes)
        self.assertEqual(s.missing(), [])

    def test_eight_of_nine_rejected(self):
        feats = {key: True for key, _, _ in CRITERIA}
        feats["volume_alive"] = False
        s = score_token("AAA", feats)
        self.assertEqual(s.total, 8)
        self.assertFalse(s.passes)
        self.assertEqual(s.missing(), ["volume_alive"])

    def test_missing_keys_count_as_failures(self):
        s = score_token("AAA", {"early_buyer_hold": True})
        self.assertEqual(s.total, 1)
        self.assertFalse(s.passes)

    def test_rubric_table_documents_bar(self):
        self.assertIn("9", rubric_table())


def _fixture_pipeline(**overrides):
    wallets = ["w1", "w2", "w3", "w4"]
    buyers = [
        EarlyBuyer(address=w, first_buy_ts=NOW - 90 * DAY, first_buy_usd=500.0)
        for w in wallets
    ]
    last_trade = {w: NOW - 2 * DAY for w in wallets}
    counts = {w: 8 for w in wallets}
    human_times = {w: [NOW - i * 6 * 3600.0 for i in range(8)] for w in wallets}
    holdings = {
        "w1": {"AAA", "BBB"},
        "w2": {"AAA", "CCC"},
        "w3": {"AAA", "DDD"},
        "w4": {"EEE"},
    }
    features = {
        "AAA": {
            "liquidity_ok": True,
            "holder_distribution_ok": True,
            "contract_safe": True,
            "buy_pressure_ok": True,
            "volume_alive": True,
        }
    }
    params = dict(
        fetch_early_buyers=lambda: buyers,
        fetch_last_trade=lambda ws: {w: last_trade[w] for w in ws},
        fetch_trade_counts=lambda ws: {w: counts[w] for w in ws},
        fetch_trade_times=lambda ws: {w: human_times[w] for w in ws},
        fetch_holdings=lambda ws: {w: holdings[w] for w in ws},
        fetch_features=lambda tok: features.get(tok, {}),
        now=NOW,
    )
    params.update(overrides)
    return run_pipeline("SEED", chain="sol", **params)


class TestPipeline(unittest.TestCase):
    def test_full_pass_produces_watchlist(self):
        res = _fixture_pipeline()
        self.assertEqual(len(res.early_buyers), 4)
        self.assertEqual(sorted(res.active_wallets), ["w1", "w2", "w3", "w4"])
        self.assertEqual(res.bot_wallets, [])
        self.assertEqual(len(res.convergences), 1)
        self.assertEqual(res.convergences[0].token, "AAA")
        self.assertEqual(len(res.watchlist), 1)
        self.assertEqual(res.watchlist[0].token, "AAA")
        self.assertEqual(res.watchlist[0].total, 9)

    def test_no_convergence_no_candidates(self):
        res = _fixture_pipeline(
            fetch_holdings=lambda ws: {w: {"ONLY-%s" % w} for w in ws},
        )
        self.assertEqual(res.convergences, [])
        self.assertEqual(res.watchlist, [])
        self.assertTrue(any("no token" in n for n in res.notes))

    def test_bot_wallet_excluded_before_convergence(self):
        bot_times = [NOW - i * 3.0 for i in range(10)]

        def trade_times(ws):
            return {
                w: (
                    bot_times
                    if w == "w3"
                    else [NOW - i * 6 * 3600.0 for i in range(8)]
                )
                for w in ws
            }

        res = _fixture_pipeline(fetch_trade_times=trade_times)
        self.assertEqual(res.bot_wallets, ["w3"])
        # w3 carried the AAA convergence; without it AAA drops below 3 wallets
        self.assertFalse(
            any(c.token == "AAA" and c.wallet_count >= 3 for c in res.convergences)
        )
        self.assertEqual(res.watchlist, [])

    def test_no_buyers_short_circuits(self):
        res = run_pipeline("SEED", fetch_early_buyers=lambda: [], now=NOW)
        self.assertEqual(res.early_buyers, [])
        self.assertEqual(res.watchlist, [])


if __name__ == "__main__":
    unittest.main()
