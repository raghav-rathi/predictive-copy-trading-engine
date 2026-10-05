"""Offline unit tests for the crypto JEV narrative detector. No network."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gemsearch.crypto_jev import CryptoJev, extract_tickers
from gemsearch.verify import four_seats


def post(pid, author, text, links=None):
    return {'id': pid, 'author': author, 'text': text,
            'url': f'https://x.com/{author}/status/{pid}',
            'created_at': '2026-10-05T12:00:00+00:00',
            'links': links or []}


class TestTickers(unittest.TestCase):
    def test_cashtags_extracted(self):
        self.assertEqual(extract_tickers('apeing $FARTCOIN and $retardio hard'),
                         ['FARTCOIN', 'RETARDIO'])

    def test_stopwords_filtered(self):
        self.assertEqual(extract_tickers('send $THE money'), [])


class TestIngest(unittest.TestCase):
    def test_dedupe(self):
        j = CryptoJev()
        p = post('1', 'a', 'meme coin $XYZ mooning')
        r = j.ingest([p, p])
        self.assertEqual(r, {'accepted': 1, 'duplicates': 1})
        self.assertEqual(j.post_count, 1)

    def test_invalid_skipped(self):
        j = CryptoJev()
        r = j.ingest([{'id': '', 'text': ''}, None, 'nope'])
        self.assertEqual(r['accepted'], 0)


class TestNarratives(unittest.TestCase):
    def _corpus(self):
        return [
            post('1', 'alice', 'meme coin season $FARTCOIN pumping on pump.fun',
                 ['https://pump.fun/coin/x']),
            post('2', 'bob', 'just aped $FARTCOIN memecoin, degen play'),
            post('3', 'carol', '$FARTCOIN meme coin 100x incoming'),
            post('4', 'dave', 'meme coins ripping, $RETARDIO too'),
            post('5', 'erin', 'unrelated post about the weather today'),
        ]

    def test_finds_meme_narrative_with_tokens(self):
        j = CryptoJev()
        j.ingest(self._corpus())
        nar = j.narratives(min_authors=3, min_posts=3)
        meme = [n for n in nar if n['topic'] == 'meme_coins']
        self.assertEqual(len(meme), 1)
        tickers = {t['ticker'] for t in meme[0]['tokens']}
        self.assertIn('FARTCOIN', tickers)
        self.assertIn('RETARDIO', tickers)
        self.assertEqual(meme[0]['status'], 'shortlisted')

    def test_scam_rejected(self):
        j = CryptoJev()
        j.ingest([post(str(i), f'u{i}',
                       'meme coin $SCAM guaranteed profit connect wallet to claim')
                  for i in range(4)])
        nar = j.narratives(min_authors=2, min_posts=3)
        meme = [n for n in nar if n['topic'] == 'meme_coins'][0]
        self.assertEqual(meme['status'], 'rejected')
        skeptic = [v for v in meme['votes'] if v['seat'] == 'skeptic'][0]
        self.assertEqual(skeptic['vote'], 'reject')

    def test_quiet_topic_held(self):
        j = CryptoJev()
        j.ingest([post('1', 'a', 'solana mainnet upgrade soon'),
                  post('2', 'b', 'solana network fees discussion'),
                  post('3', 'c', 'solana validator talk')])
        nar = j.narratives(min_authors=5, min_posts=3)
        l1 = [n for n in nar if n['topic'] == 'l1_l2']
        self.assertTrue(l1)
        self.assertEqual(l1[0]['status'], 'held')  # only 3 authors < 5


class TestSeats(unittest.TestCase):
    def test_all_pass(self):
        votes = four_seats(5, 4, True, 0.1, False)
        self.assertTrue(all(v['vote'] == 'pass' for v in votes))

    def test_structure(self):
        votes = four_seats(1, 1, False, 0.9, False)
        self.assertEqual([v['seat'] for v in votes],
                         ['lookout', 'maker', 'skeptic', 'runner'])


if __name__ == '__main__':
    unittest.main()
