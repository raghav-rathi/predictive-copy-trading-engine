"""Four-seat local verification, mirroring the upstream Grok-seat structure.

Upstream gem-search defines four reviewer seats (Lookout, Maker, Skeptic,
Runner) that normally call the xAI API. When no key is configured, the same
seats resolve to local heuristic checks — that is what this module
implements, so the pipeline is fully offline and deterministic.
"""

import re

# Same scam tripwires as upstream jev.py.
SCAM_RE = r'seed phrase|private key|guaranteed profit|connect wallet to claim'


def four_seats(n_posts, n_authors, has_links, duplicate, scam,
               min_authors=3, min_posts=3):
    """Return four seat votes: lookout / maker / skeptic / runner."""
    checks = [
        ('lookout', n_authors >= min_authors,
         f'{n_authors} distinct authors in sample. Sample only, not the whole feed.'),
        ('maker', has_links,
         'External project links observed; product claims need independent checks.'
         if has_links else 'No external links captured; nothing to verify the product against.'),
        ('skeptic', duplicate <= 0.5 and not scam,
         f'{duplicate:.0%} repeated text. Authenticity unverified.'
         + (' SCAM PHRASES DETECTED.' if scam else '')),
        ('runner', n_posts >= min_posts,
         f'{n_posts} captured posts; enough for a research lead, not an investment decision.'),
    ]
    votes = []
    for seat, ok, reason in checks:
        vote = 'reject' if seat == 'skeptic' and scam else 'pass' if ok else 'hold'
        votes.append({'seat': seat, 'vote': vote, 'reason': reason})
    return votes
