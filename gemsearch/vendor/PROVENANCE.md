# Vendor provenance

The `vendor/` directory holds reference copies of the core detection code from
the upstream project this package ports:

- **Upstream:** https://github.com/h100envy/gem-search
- **Author:** @h100envy
- **License:** MIT (see upstream LICENSE; this is a separate public repo)
- **Cloned:** 2026-10-05 (upstream repo created 2026-10-05, same day as the
  @zostaff post that surfaced it)

Files:

- `jev.py` — verbatim copy of upstream `jev.py` (the JEV local signal
  detector). It imports `TOPICS` from upstream `automation.py`; because the
  full upstream `automation.py` pulls in launch/wallet machinery
  (`launch_provider`, subprocess calls), we vendor only the `TOPICS` taxonomy
  verbatim in `upstream_topics.py` so the reference detector stays importable
  without side effects.
- `upstream_topics.py` — the `TOPICS` dict copied verbatim from upstream
  `automation.py` (5 topics: agents, robotics, privacy, devtools, science).

What the upstream code actually does (verified by reading it, not from the
hype post):

- Groups captured X posts by matching them against a small **hardcoded keyword
  regex taxonomy** — not semantic/meaning-based clustering as the X post
  claims.
- Applies four local heuristic checks named after the Grok seats
  (lookout/maker/skeptic/runner). The real Grok API reviewers are **optional**,
  require your own xAI key, and upstream notes a real paid Grok call "has not
  been validated in this checkout".
- The pump.fun launcher is a **separate experimental opt-in module**,
  dry-run by default, capped at 0.025 SOL / 5 attempts per 24h.
- There is **no slimefamilyxyz integration** anywhere in the upstream code,
  despite the X post claiming the tool is "connected via API to slimefamilyxyz".

Our crypto adaptation lives in `crypto_jev.py` / `verify.py` and does not
depend on these vendor files; they are kept as an auditable reference.
