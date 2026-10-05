#!/usr/bin/env python3
"""Run the crypto JEV narrative discovery on a posts JSON corpus.

Usage:
    python3 -m gemsearch.scripts.run_discovery [corpus.json] [--min-authors 3] [--min-posts 3]

Corpus format: JSON list of {id, author, text, url, created_at, links?}.
Prints the narrative shortlist as JSON to stdout.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gemsearch.crypto_jev import CryptoJev  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('corpus', nargs='?',
                    default=str(Path(__file__).resolve().parent.parent / 'data' / 'corpus_2026-10-05.json'))
    ap.add_argument('--min-authors', type=int, default=3)
    ap.add_argument('--min-posts', type=int, default=3)
    args = ap.parse_args()

    posts = json.loads(Path(args.corpus).read_text())
    jev = CryptoJev()
    stats = jev.ingest(posts)
    narratives = jev.narratives(min_authors=args.min_authors, min_posts=args.min_posts)
    token_hits = sum(len(n['tokens']) for n in narratives)
    print(json.dumps({
        'corpus_posts': len(posts),
        'ingest': stats,
        'narratives_found': len(narratives),
        'token_mentions_total': token_hits,
        'narratives': narratives,
    }, indent=2))


if __name__ == '__main__':
    main()
