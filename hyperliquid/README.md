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
   (kind: wallet | vault)            │
scorer.py: userFillsByTime ──> FIFO realized PnL ──> predictive score
              0-100 (time-weighted WR/PF, consistency, min-sample guard)
                                     │  (copy >= 65, fade <= 30)
WS userFills ──> mirror.py: dedup (fill hash) + intent aggregation
              (one fragmented entry -> one intent -> one copy)
              ──> sizing.py (proportional × Kelly cap, shrinks only)
                                     │
              ┌──────────────────────┴──────────────────────┐
              │  exits.py: SL / trailing SL / TP / max-hold / │
              │  max-age / target-exit (side-aware);          │
              │  pre-close state sync before reduce-only     │
              │  reconcile.py: drift vs clearinghouseState   │
              │    + startup sync (match leader's positions) │
              │  risk.py: 4-layer breakers (trade / target / │
              │    daily / kill switch)                      │
              │  notify.py: trade/breaker/error events       │
              └──────────────────────────────────────────────┘
                                     │
                              paper.py ──> paper_trades.csv (the gate)
                                          decisions.ndjson (why each call)
                                          shadow.csv (skipped signals, priced)
```

**Signal** (`mirror.py`): subscribe `userFills` per COPY target on
`wss://api.hyperliquid.xyz/ws` — wallets *or* vault addresses, both are
just 0x addresses to the subscription. Fill events are the copy
trigger. Per-coin serial queues keep fills for one coin from racing.

**Intent aggregation** (`mirror.py`, `IntentAggregator`): a leader's
single entry routinely arrives as many small fills (Reddit builder,
Dwellir) — copying per fill misfires. Fills are grouped by
(user, coin, dir) inside `intent_window_s` into one intent (total size,
size-weighted price) and copied once. Every fill is deduped by its
fill hash / trade ID first, so replays and redeliveries never
double-copy.

**Targets** (`targets.py`, `targets.json`): entries carry a score,
classification (copy / fade / pass), and `kind` (`"wallet"` or
`"vault"`). Hyperliquid vaults are queryable by address exactly like
wallets, so a vault's equity address can be a target with no
special-casing in the mirror loop (MaxIsOntoSomething). **Single-operator
clustering** merges wallets that repeatedly co-enter the same coin
within a short window into one vote — the fleet lesson, encoded. A
cluster is sized once, never once per member.

**Scoring** (`scorer.py`): pulls a wallet's fills from the public
`POST /info` API (`userFillsByTime`, no auth), pairs closes to opens
FIFO per coin (preferring Hyperliquid's own realized `pnl` on close
fills when present), then scores 0–100 on *predictive* structure
(@slash1sol, CopyGrade) — public leaderboards reward past luck, so:
time-weighted win rate and profit factor (recent closes count more,
90d decay), consistency (win-rate distribution across time windows —
a decaying 90%-then-30% scores below a steady 60%), max drawdown,
sample size, recency. Wallets below `min_closed_trades` are marked
**unscored** (score 0.0) and can never be copied. Thresholds in config
(copy ≥ 65, fade ≤ 30).

**Sizing** (`sizing.py`): `copySize = fill.sz × multiplier`, capped by
`max_position_usd` and `max_notional_per_trade_usd`. A fractional-Kelly
stake from the target's rolling realized closes can only *shrink* the
copy — and when measured edge ≤ 0 the open is skipped entirely.

**Exits** (`exits.py` + mirror close logic): on a target close fill,
`closePercent = fill.sz / |startPosition|` closes the same % of our
position (stays in sync through partial exits). Before any reduce-only
close, the follower's size is re-read from the authoritative source
(Dwellir's CRITICAL pre-close sync) so the percentage is computed on
fresh state. Independent hard stops — stop-loss, **trailing
stop-loss** (ratchets with favorable moves, kei_4650), take-profit,
max hold, and a tighter **max position age** — fire regardless of the
target, and all are side-aware (a short's favorable move never trips
its stop). Never baghold a loser target's position.

**Reconciliation** (`reconcile.py`): every `reconcile_interval_s`,
diff our positions against each target's `clearinghouseState` and
auto-close anything the target flattened or flipped. Only ever reduces
risk; never opens. **Startup sync** (`fetch_all_target_positions`):
on startup, open matching follower positions for anything a COPY
target already holds, so follower state matches the leader from the
first minute (MaxIsOntoSomething) — paper mode replays this via
`target_positions` events. The safety net for missed WS events.

**Paper-first** (`paper.py`): the default and intended mode. Every
decision is logged with its reason; skipped signals become priced
**shadow positions** so thresholds keep improving. Live trading is
hard-gated behind `live_trading: true` **and** a positive paper track
record (default: ≥ 30 closed paper trades, aggregate PnL ≥ 0) — and
even then, live order placement raises `NotImplementedError` until the
exchange wiring is verified.

**Risk** (`risk.py`): four independent circuit-breaker layers
(Teraus's idea, made real) — per-trade max loss (halts opens through
a cooldown), per-target max loss (stops copying that target for the
day), daily portfolio loss (halts to next UTC day), global kill-switch
file. Each layer trips independently and logs its reason; trips are
emitted to the notifier. Coin whitelist and max notional per trade on
top. Runs in paper mode too, so the paper record reflects live
constraints.

**Notifier** (`notify.py`): trade opened / trade closed / breaker
tripped / error events. Backends: `log` (stderr JSON, default) and
`telegram` — the Telegram backend reads `TELEGRAM_BOT_TOKEN` and
`TELEGRAM_CHAT_ID` from the environment at runtime only (never from
code or config), degrading to logging when unset. No credentials in
this repo, ever.

## Quickstart (paper mode)

```bash
python3 hyperliquid/paper.py \
  --config hyperliquid/config.example.json \
  --fills hyperliquid/examples/sample_fills.ndjson \
  --targets hyperliquid/examples/targets.sample.json
```

This replays a synthetic fill stream end-to-end: a COPY target's
fragmented BTC long entry (3 fills + 1 replayed duplicate → copied
once as a single intent), partial close, trailing-stop exit; a startup
`target_positions` event that opens a matching ETH position; a skipped
low-score SOL signal; a skipped FADE ETH signal; and a vault-kind
example target — all priced as shadow positions where skipped. Outputs
land under `data/` (CSVs + decision log).

## Adding real targets

1. Find candidate addresses (Hyperliquid has no public leaderboard
   API): watch WS `trades` on high-volume coins and accumulate
   address→fill counts, or pull vault leaders — vault equity addresses
   work as `targets.json` entries with `"kind": "vault"` (see
   `docs/research/copy-engine-research.md`).
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

From the Twitter/X builder track
(`docs/research/twitter-copy-engine-research.md`):
fill-fragmentation handling — group a leader's many small fills into
one intent, dedup by fill hash (Reddit r/algotrading builder, Dwellir);
pre-close position sync before reduce-only closes (Dwellir); vault
addresses as first-class targets and startup position sync
(MaxIsOntoSomething); predictive wallet scoring — time-weighted
win rate / profit factor, win-rate consistency across windows,
minimum-sample guards instead of leaderboard chasing (@slash1sol,
CopyGrade); trailing stop-loss + lifetime-based exits (kei_4650);
layered circuit breakers — per-trade, per-target, daily, global kill
switch (Teraus's 4-layer idea, made real); Telegram event
notifications (MaxIsOntoSomething, Dwellir).

*Research code. Not financial advice. Perps are leveraged; liquidation
is real; paper first, always.*
