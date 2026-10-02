# Hyperliquid copy-trading module

A near-real-time perps copy engine for Hyperliquid, built on the same
philosophy as the rest of this repo: **score the wallets, don't
blind-copy.** The Robinhood Chain research proved why — the most-copied
"whale" there was one bot in a losing fleet.

## Why Hyperliquid

On Robinhood Chain the edge was landing in the *same block* as a fill,
which takes MEV-grade plumbing. On Hyperliquid the observation problem
is nearly free: the public websocket fires `userFills` within
milliseconds of a target's fill, with coin, direction, size, price and
starting position attached. Latency is solved by the venue itself — so
the entire game moves to **target selection**, which is exactly what
this repo's scorer already does. This module is the execution half of
the same strategy on a venue where copying is a data problem, not a
latency problem.

## How it works

```
targets.json ──> targets.py ──> cluster merge (one operator, one vote)
                                     │
scorer.py: userFillsByTime ──> FIFO realized PnL ──> score 0-100
                                     │  (copy >= 65, fade <= 30)
WS userFills ──> mirror.py ──> sizing.py (proportional × Kelly cap, shrinks only)
                                     │
              ┌──────────────────────┴──────────────────────┐
              │  exits.py: stop / TP / max-hold / target-exit │
              │  reconcile.py: drift vs clearinghouseState   │
              │  risk.py: daily-loss breaker, kill switch     │
              └──────────────────────────────────────────────┘
                                     │
                              paper.py ──> paper_trades.csv (the gate)
                                          decisions.ndjson (why each call)
                                          shadow.csv (skipped signals, priced)
```

**Signal** (`mirror.py`): subscribe `userFills` per COPY target on
`wss://api.hyperliquid.xyz/ws`. Fill events are the copy trigger.
Per-coin serial queues keep fills for one coin from racing.

**Targets** (`targets.py`, `targets.json`): wallets carry a score and
classification (copy / fade / pass). **Single-operator clustering**
merges wallets that repeatedly co-enter the same coin within a short
window into one vote — the fleet lesson, encoded. A cluster is sized
once, never once per member.

**Scoring** (`scorer.py`): pulls a wallet's fills from the public
`POST /info` API (`userFillsByTime`, no auth), pairs closes to opens
FIFO per coin (preferring Hyperliquid's own realized `pnl` on close
fills when present), and computes win rate, profit factor, max
drawdown, sample size and recency → score 0–100. Thresholds in config.

**Sizing** (`sizing.py`): `copySize = fill.sz × multiplier`, capped by
`max_position_usd` and `max_notional_per_trade_usd`. A fractional-Kelly
stake from the target's rolling realized closes can only *shrink* the
copy — and when measured edge ≤ 0 the open is skipped entirely.

**Exits** (`exits.py` + mirror close logic): on a target close fill,
`closePercent = fill.sz / |startPosition|` closes the same % of our
position (stays in sync through partial exits). Independent hard stops
— stop-loss, take-profit, max hold — fire regardless of the target.
Never baghold a loser target's position.

**Reconciliation** (`reconcile.py`): every `reconcile_interval_s`,
diff our positions against each target's `clearinghouseState` and
auto-close anything the target flattened or flipped. Only ever reduces
risk; never opens. The safety net for missed WS events.

**Paper-first** (`paper.py`): the default and intended mode. Every
decision is logged with its reason; skipped signals become priced
**shadow positions** so thresholds keep improving. Live trading is
hard-gated behind `live_trading: true` **and** a positive paper track
record (default: ≥ 30 closed paper trades, aggregate PnL ≥ 0) — and
even then, live order placement raises `NotImplementedError` until the
exchange wiring is verified.

**Risk** (`risk.py`): daily-loss circuit breaker (halts to next UTC
day), kill-switch file, coin whitelist, max notional per trade. Runs in
paper mode too, so the paper record reflects live constraints.

## Quickstart (paper mode)

```bash
python3 hyperliquid/paper.py \
  --config hyperliquid/config.example.json \
  --fills hyperliquid/examples/sample_fills.ndjson \
  --targets hyperliquid/examples/targets.sample.json
```

This replays a synthetic fill stream end-to-end: a COPY target's
BTC long (opened, partial-closed, closed), a skipped low-score SOL
signal, and a skipped FADE ETH signal — all priced as shadow
positions. Outputs land under `data/` (CSVs + decision log).

## Adding real targets

1. Find candidate addresses (Hyperliquid has no public leaderboard
   API): watch WS `trades` on high-volume coins and accumulate
   address→fill counts, or pull vault leaders from the undocumented
   vaults endpoint (see `docs/research/copy-engine-research.md`).
2. Score them: `python3 hyperliquid/scorer.py --config
   hyperliquid/config.example.json --out hyperliquid/targets.json
   0xabc... 0xdef...`
3. Review the scores by hand before anything copies — the file is the
   allow-list. `targets.json` in this repo ships with EXAMPLE
   placeholders only; never invent real trader addresses.

## Deployment

The non-custodial pattern is a Hyperliquid **API wallet**
(`approveAgent`): a trade-only sub-wallet that **cannot withdraw**.
Create it from your main wallet, fund it, and point the engine at it.
Private-key handling for the API wallet is **TODO-operator** — keys
never live in this repo, in config files, or in logs; load them from
your deployment host's secret manager at runtime.

Rate limits (~1200 weight/min per IP; most info endpoints ~20 weight)
mean address discovery needs pacing; the scorer backs off on 429s.

## Ideas stolen (with credit)

From the open-source research in `docs/research/copy-engine-research.md`:
continuous 0–100 scoring with a mirror threshold (rezzecup, Copin.io);
proportional close logic (jonny-traders); the reconcile loop
(jonny-traders); Kelly-as-a-cap from measured edge (jonny-traders);
single-operator clustering (Kelows/million); paper-first + shadow
positions + decision logs (million, rezzecup); MEV-aware submission
thinking — here expressed as WS `userFills` + IOC-with-slippage
(million, @outputlayer). Native vaults remain the no-code alternative
if you don't want to run a bot at all.

*Research code. Not financial advice. Perps are leveraged; liquidation
is real; paper first, always.*
