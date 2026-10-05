"""Crypto-adapted port of the GemSearch JEV narrative detector.

Mirrors the upstream pipeline (h100envy/gem-search, MIT — see vendor/):
ingest social posts -> group by narrative topic -> extract $tickers ->
four-seat local verification -> shortlist.

Differences from upstream, made explicit:
- Upstream groups posts with a 5-topic keyword taxonomy (agents, robotics,
  privacy, devtools, science). This port uses a crypto-native taxonomy and
  additionally extracts $TICKER cashtags per narrative, because the testable
  claim is "it finds tokens".
- Upstream's four Grok seats are optional and need your own xAI key. Here the
  four seats are local heuristic checks with the same structure and names,
  so the pipeline runs fully offline and deterministically.
- No token launching. Discovery only; a shortlist is a research lead.

Input post dict: {id, author, text, url, created_at (ISO), links?}
"""

import re
from collections import Counter
from datetime import datetime, timezone

from .verify import four_seats, SCAM_RE

# Crypto-native narrative taxonomy: keyword regexes, same role as upstream TOPICS.
CRYPTO_TOPICS = {
    'ai_agents': r'\b(ai agent[s]?|agentic|autonomous trad\w+|llm trad\w+|bot trad\w+|artificial intelligence)\b',
    'meme_coins': r'\b(meme ?coin[s]?|memecoin[s]?|shitcoin[s]?|pump\.?fun|pumpfun|degen|100x|moonbag[s]?)\b',
    'perps_dex': r'\b(hyperliquid|perp[s]?|leverage|funding rate|short squeeze|long squeeze|liquidat\w+|dex trad\w+|drift|jupiter)\b',
    'defi_yield': r'\b(defi|yield farm\w*|stak\w+|lending|liquidity|amm|tvl|vault[s]?|restak\w+)\b',
    'l1_l2': r'\b(solana|ethereum|eth|base|arbitrum|sol|btc|bitcoin|mainnet|testnet|layer ?2|rollup)\b',
    'airdrops': r'\b(airdrop[s]?|points farm\w*|snapshot|eligib\w+|claim\w* token|taskon|galxe)\b',
    'rwa': r'\b(rwa|tokenized|treasur\w+|real world asset|onchain stock|equit\w+ token)\b',
    'gaming_nft': r'\b(gaming|gamefi|nft[s]?|play.to.earn|p2e|metaverse)\b',
    'privacy': r'\b(privacy|zero.knowledge|\bzk\b|mixer|encryption|anonym\w+)\b',
    'stablecoins': r'\b(stablecoin[s]?|usdc|usdt|dai|depeg|yield.?bearing stable)\b',
    'cex_listings': r'\b(binance|coinbase|list\w+|kraken|bybit|okx|upbit)\b',
    'macro': r'\b(fed|cpi|rate cut|etf inflow|etf outflow|macro|powell|inflation)\b',
}

# $TICKER cashtags. 2-15 chars; filter common non-token words below.
TICKER_RE = re.compile(r'\$([A-Za-z][A-Za-z0-9]{1,14})\b')
TICKER_STOPWORDS = {
    'THE', 'AND', 'FOR', 'YOU', 'THIS', 'THAT', 'WITH', 'FROM', 'THEY',
    'WILL', 'WOULD', 'COULD', 'SHOULD', 'ABOUT', 'INTO', 'OVER', 'UNDER',
}


def extract_tickers(text):
    """Return cashtag tickers in order of appearance, stopwords removed."""
    out = []
    for m in TICKER_RE.finditer(text or ''):
        t = m.group(1).upper()
        if t not in TICKER_STOPWORDS and t not in out:
            out.append(t)
    return out


def _norm(text):
    return re.sub(r'https?://\S+|[^\w\s]', '', (text or '').lower()).strip()


class CryptoJev:
    """Narrative detector over ingested social posts."""

    def __init__(self):
        self._posts = {}
        self._order = []

    def ingest(self, posts):
        """Validate, dedupe by id, store. Returns {accepted, duplicates}."""
        accepted = duplicates = 0
        for p in posts or []:
            if not isinstance(p, dict):
                continue
            pid = str(p.get('id') or '')
            text = p.get('text') or ''
            if not pid or not isinstance(text, str) or not text.strip():
                continue
            if pid in self._posts:
                duplicates += 1
                continue
            self._posts[pid] = {
                'id': pid,
                'author': str(p.get('author') or 'unknown'),
                'text': text,
                'url': str(p.get('url') or ''),
                'created_at': str(p.get('created_at') or ''),
                'links': list(p.get('links') or []),
            }
            self._order.append(pid)
            accepted += 1
        return {'accepted': accepted, 'duplicates': duplicates}

    @property
    def post_count(self):
        return len(self._posts)

    def narratives(self, min_authors=3, min_posts=3):
        """Group posts by topic, extract tickers, run four-seat verification."""
        posts = [self._posts[pid] for pid in self._order]
        out = []
        for topic, regex in CRYPTO_TOPICS.items():
            group = [p for p in posts if re.search(regex, p['text'], re.I)]
            if len(group) < min_posts:
                continue
            authors = {p['author'].lower() for p in group}
            texts = {_norm(p['text']) for p in group}
            duplicate = 1 - len(texts) / len(group)
            tickers = Counter()
            for p in group:
                for t in extract_tickers(p['text']):
                    tickers[t] += 1
            scam = any(re.search(SCAM_RE, p['text'], re.I) for p in group)
            votes = four_seats(
                n_posts=len(group), n_authors=len(authors),
                has_links=any(p['links'] for p in group),
                duplicate=duplicate, scam=scam,
                min_authors=min_authors, min_posts=min_posts,
            )
            passed = all(v['vote'] == 'pass' for v in votes)
            status = 'rejected' if scam else 'shortlisted' if passed else 'held'
            out.append({
                'id': f'jev-{topic}',
                'topic': topic,
                'status': status,
                'score': sum(v['vote'] == 'pass' for v in votes) * 25,
                'votes': votes,
                'signals': {
                    'mentions': len(group),
                    'authors': len(authors),
                    'duplicate_ratio': round(duplicate, 3),
                    'scam_flags': scam,
                },
                'tokens': [
                    {'ticker': t, 'mentions': c}
                    for t, c in tickers.most_common(10)
                ],
                'sample_posts': [
                    {'author': p['author'], 'url': p['url'],
                     'text': p['text'][:280]}
                    for p in group[:5]
                ],
            })
        out.sort(key=lambda n: (-n['score'], -n['signals']['mentions']))
        return out
