# Meme-Alpha Wallet Discovery — research port note

Source: https://x.com/crbpite8/status/2108668827412341014 (@crbpite8, Oct 9, 2026)

This is a research implementation of the method's mechanics, written in our
own words. It is not affiliated with or endorsed by the author, and nothing
here is trading advice or a guarantee of any outcome.

## The method (paraphrased)

Rather than chasing whatever is pumping today, work backwards from traders
who were early once:

1. **Seed** on a meme coin that ran hard in a previous cycle.
2. **Discover** its earliest ~20 buyer wallets — via the token's page on
   gmgn.ai for Solana tokens (gmgn.ai directly; the original post used a
   referral link, we do not), or via the earliest contract transactions on
   Etherscan for EVM tokens.
3. **Activity filter**: keep only wallets that traded in the last 30 days.
   In practice ~3–5 of the 20 survive.
4. **Bot filter**: drop wallets whose trades land seconds apart — that is a
   bot signature, and bot flow cannot be copied by a human anyway.
5. **Holdings scan**: for each surviving wallet, list what it bought and
   still holds from the last 30 days.
6. **Convergence**: a token bought/held by 3+ tracked wallets at once is
   treated as signal. One wallet is luck; three is a pattern.
7. **Score** each candidate on a 9-point rubric; reject anything below 9.

## What we built

`memealpha/` package (branch `feat/meme-alpha-wallet-discovery`):

| Module | Implements |
|---|---|
| `discovery.py` | GMGN public-API client (Solana + other GMGN chains) and an Etherscan `tokentx` path for EVM; earliest-buyer extraction with program-address exclusion |
| `filters.py` | 30-day activity filter; bot detection via inter-trade-gap analysis (median gap < 60s or >50% of gaps < 10s) |
| `convergence.py` | Multi-wallet overlap detector (3+ wallets = signal), with coverage stats |
| `scoring.py` | 9-point rubric, all weights 1.0, pass bar 9/9 (configurable) |
| `pipeline.py` | Orchestrates all 7 steps; pure logic with injectable data providers |
| `tests/` | 22 unit tests, all green |

`scripts/check_meme_alpha.py` runs the validation pass.

## Empirical findings (honest)

**Live GMGN access is blocked from this environment** (HTTP 403 from
Cloudflare on gmgn.ai's public API, confirmed by direct probe). So the
"discover real earliest buyers" step cannot run live here — the pipeline
was validated on realistic synthetic fixture data instead, every fixture
clearly labeled.

On fixtures, the pipeline behaves exactly as the method describes:

- 20 earliest buyers in → **4 active** in the 30-day window (matches the
  post's "3–5 of 20 survive" observation),
- 1 of the 4 flagged as a bot (4-second trade spacing) and removed,
- the remaining 3 converge on one token → **9/9 PASS** → watchlist of one.

What this proves: the *mechanics* are sound and correctly implemented
(filters fire where they should, the 3-wallet rule and the 9-point bar
behave as specified). What it does **not** prove: that real early-buyer
wallets found this way pick winning tokens. That requires a live
discovery pass plus a forward track record we do not have.

## The author's own cautions (worth keeping)

- **Position sizes differ**: a tracked wallet's $200 buy and its $50k buy
  are not the same signal; size-weight the convergence, don't just count
  wallets.
- **Buys are public, sells are hidden**: you see what wallets bought and
  hold, but their sell timing is invisible. Any copy is entry-only
  information with an unknown exit.
- Survivorship is brutal: most early wallets go quiet; the 3–5 survivors
  are a selected sample, not a representative one.

## Status

Research only. Discovery and watchlists — no execution wiring, no live
trading. Paper-first, like everything else in this repo.
