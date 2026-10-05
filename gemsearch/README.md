# gemsearch — narrative/token discovery port

Branch: `feat/gemsearch-narrative`

## What this is

A crypto-adapted port of the **GemSearch** narrative-discovery strategy
surfaced by [@zostaff](https://x.com/zostaff/status/2107146358142402954)
(Oct 5, 2026), whose builder is [@h100envy](https://github.com/h100envy)
(upstream repo: https://github.com/h100envy/gem-search, MIT).

The upstream tool is a Chrome extension + local Python engine: a "spider"
captures visible X posts, **JEV** groups them into narratives, a crawler
reads linked project sites, and four reviewer seats (Lookout/Maker/Skeptic/
Runner — optionally backed by the Grok API) verify each narrative. A
shortlist can then feed an experimental pump.fun launcher.

This package ports the **discovery core** — the only part that is a real,
testable strategy — into the engine:

| File | Role |
|---|---|
| `vendor/jev.py` | Verbatim upstream JEV detector (reference; see `vendor/PROVENANCE.md`) |
| `vendor/upstream_topics.py` | Upstream keyword taxonomy, verbatim |
| `crypto_jev.py` | Crypto-native port: ingest posts → narrative topics → `$ticker` extraction |
| `verify.py` | Four-seat local verification (same structure as upstream's seats) |
| `scripts/run_discovery.py` | CLI: run discovery on a posts corpus, print JSON shortlist |
| `data/corpus_2026-10-05.json` | 50 real crypto social posts (Oct 4–5, 2026) used for the empirical test |
| `data/discovery_2026-10-05.json` | Discovery output on that corpus |
| `tests/test_crypto_jev.py` | 9 offline unit tests |

Deliberately **not** ported: the Chrome extension overlay, the Grok API seats
(need your own xAI key; upstream never validated a real paid call), and the
pump.fun launcher (experimental, dry-run by default upstream; launching tokens
is out of scope for this engine).

## Empirical test — does it find tokens?

Run: `python3 -m gemsearch.scripts.run_discovery`
Corpus: 50 real crypto posts from Instagram/Threads/Facebook (Oct 4–5, 2026).
Note: corpus texts are platform-provided post summaries, not raw post text,
and carry no external links — noisier than the X-DOM captures upstream uses.

Result: **5 narratives, 33 ticker mentions extracted.**

- `meme_coins` — 35 mentions / 21 authors → $AGENCY, $RETARDIO, $CLAUDIA,
  $AIDEN, $SLOPCORE, $SWORDCAT, $KNIGHTCAT, $JEANPHIL (held: no links)
- `defi_yield` — 22 mentions / 9 authors → $WORLD, $BATON, $PURRSWORD,
  $BRAIN, $AGENCY… (held: no links)
- `perps_dex` — 3 mentions / 3 authors → $ADAN, $FARTCOIN (held)
- `l1_l2` — 48 mentions / 31 authors → **rejected** (scam tripwire)
- `cex_listings` — 4 mentions / 4 authors → **rejected** (scam tripwire)

## Honest verdict

**The core mechanism holds, in a limited sense.** Given real social chatter,
the pipeline genuinely surfaces tradeable tokens ($FARTCOIN, $RETARDIO,
$AGENCY are real Solana meme coins) grouped into coherent narratives —
offline, deterministically, with 9/9 unit tests green. "It finds tokens" is
not vaporware.

**But the X post oversells it, on four specific points:**

1. **Not "grouped by meaning".** Upstream JEV matches posts against a small
   hardcoded keyword-regex taxonomy (5 topics upstream; 12 here). It is
   keyword bucketing, not semantic clustering. It will miss novel memes and
   misfile sarcasm — upstream's own README admits this.
2. **The "4 Grok agents" are optional and unvalidated.** They require your
   own xAI API key, and upstream states a real paid Grok call "has not been
   validated in this checkout". Without a key, four local heuristic checks
   do the verification — which is what this port implements.
3. **The slimefamilyxyz claim is false.** The post says the tool is
   "connected via API to slimefamilyxyz". There is zero slimefamily code,
   config, or reference anywhere in the upstream repo (verified by search).
4. **Crude scam tripwire.** The `l1_l2` narrative (48 posts, 31 authors) was
   rejected because one post's summary contained the words "seed phrase" in
   an educational context. One keyword nukes a whole narrative — inherited
   from upstream, and a real false-positive risk.

Related note: this engine already has Slime Family guardrails (`slime/`,
PR #1). If a real slimefamilyxyz API ever exists, `crypto_jev.py`'s
narrative output is shaped to feed it — but today there is nothing to
connect to.

## Status

Research port. Paper only. A shortlist is a research lead, not a signal —
same disclaimer as upstream. Not wired into the live engine.
