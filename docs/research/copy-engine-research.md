# Copy-Trading Engine Research: Solana Bots, Hyperliquid Mechanics, Ideas Worth Stealing

Researched 2026-10-02 via web search + page fetches (no logins). Everything below is from public sources; unverified claims are flagged.

---

## 1. Open-source Solana copy-trading bots

### 1a. Kelows/million — memecoin intelligence deck (best architecture found)
- **Link:** https://github.com/Kelows/million — **4 stars, 308 commits, MIT, created Aug 2026**
- **What it is:** self-hosted whale tracker + copy-trading deck, operated through an AI coding agent (Claude Code etc.), Python/TS monorepo.
- **Watch how:** Helius websocket feed (no webhook needed, follows up to 25 wallets; webhook lifts the cap). Paper-trades by default — live trading requires an explicit typed consent phrase.
- **Execute how:** Jupiter swaps, 0.25% fee per live swap, keypair file on local disk.
- **Architecture highlights:**
  - Two-way discovery: wallets find tokens (every subscribed-wallet swap arrives within seconds) and tokens find wallets (crawl a token's biggest buyers, absorb trader-like ones).
  - **Wallet clustering:** wallets that keep entering the same tokens together are merged into one owner — "flags the four wallets that are really one operator." (Directly mirrors our Robinhood Chain fleet finding: one funder EOA behind 6 wallets.)
  - Token gauntlet: mint/freeze authority, liquidity, mcap, holder concentration, deployer history, **Jupiter sell simulation**, RugCheck.
  - Signal types: *copy* (single sized buy), *consensus* (several distinct owners buying in a window), *ladder* (repeated small buys).
  - Exits: trailing stop + hard stop + breakeven ratchet, re-checked every few seconds **and** the moment a followed wallet trades a token you hold.
  - **The loop back:** every completed round trip re-scores the wallet; losing styles get churned out. Skipped signals are priced as **shadow positions**; cached candle paths feed a backtester.
  - Full decision log — every trade or skip carries the reason.
- **Caveat:** authors state plainly that past returns don't predict future ones; it's a research tool.

### 1b. rezzecup/whale-wallet-mirror-copy-trader — Solana + Base mirror engine
- **Link:** https://github.com/rezzecup/whale-wallet-mirror-copy-trader/blob/HEAD/README.md — **~10 stars, Python, Mar 2026** (several forks exist; treat forks as copies)
- **Watch how:** real-time wallet surveillance on Solana and Base (Helius recommended for Solana RPC).
- **Execute how:** proportional sizing (`mirror_scale`, default 0.08 = 8% of source position), `max_position_usd` hard cap.
- **Architecture highlights:**
  - **Live wallet scoring 0–100**, rescored every 6h from on-chain history; `min_score_to_mirror: 65` — below that = monitor only.
  - **Slippage tiers per wallet rank** (tier_s 2.0% → default 0.8%) — looser slippage for top-tier wallets, execution priority where it matters.
  - Paper/live modes (`--mode paper` default; live is a deliberate flag flip).
  - Dynamic Solana priority fees; Jito bundles noted as private-build only.
  - Risk gate (fail-fast design per its commit history).

### 1c. ddewhun/copy-trading-bot-free-source — minimal Jupiter copier (reference only)
- **Link:** https://github.com/ddewhun/copy-trading-bot-free-source — 1 star, fork, single commit
- **Pattern:** WebSocket watches a target wallet's Jupiter swaps, extracts token/amount/price, re-executes via Jupiter aggregator with `MAXIMUM_BUY_AMOUNT` cap and SOL-balance checks. The simplest viable loop: subscribe → parse → Jupiter swap. Useful as a minimal template, not production code.

### 1d. rdin777/solana-copy-trade-bot-public — alert-only monitor
- **Link:** https://github.com/rdin777/solana-copy-trade-bot-public — Python, WebSocket monitoring, **Telegram alerts** for large txs above a SOL threshold. No execution — but a good pattern for the notification layer.

### 1e. The "Geyser + MEV-aware submission" template (pattern, not a trusted repo)
- Seen in near-identical form across `trade-research-labs/nexus-tracker-2596`, `market-insight-core/curve-tracker-2691`, `outcome-execution-core/ledger-tracker-2414`. These look like **auto-generated SEO-spam repos** (identical copy, odd org names) — do not trust their code sight unseen. But the **infrastructure pattern they describe is real and is the correct Solana latency stack**:
  - Observe via **Yellowstone Geyser `transactionSubscribe`** on mirrored wallets (full transaction payloads, no polling).
  - Submit via **private/MEV-aware rails** (Jito bundles / direct-to-validator tips) instead of public `sendRawTransaction`, chasing 0–1 slot inclusion after the signal.
  - This is the Solana analogue of the @outputlayer lesson: the observation feed and the submission rail are separate problems, and the rail matters as much as the signal.

---

## 2. Hyperliquid copy trading — mechanics

### 2a. How copying works mechanically
Hyperliquid exposes everything a copier needs **without auth**; only order placement needs signing.

**Info (read) API — all via `POST https://api.hyperliquid.xyz/info`:**
| Query (`type`) | Returns | Copy-trading use |
|---|---|---|
| `clearinghouseState` (+ `user`) | positions, leverage, margin, account value | live target exposure |
| `userFills` / `userFillsByTime` | fills (2000/req, 10K total history) | fill stream, frequency, hold times, PnL/trade |
| `portfolio` | account value + PnL history (day/week/month/allTime) | equity curve, drawdown, Sharpe |
| `historicalOrders` | up to 2000 orders w/ status | cancel-to-fill ratio |
| `userFees` / `userRateLimit` | fee tier, volume, request usage | volume/activity tiering |
| `userFunding` | funding payments (500/req) | funding PnL component |
| `openOrders`, `orderStatus`, `metaAndAssetCtxs`, `allMids`, `l2Book`, `candleSnapshot` | market + order state | pricing, slippage, discovery |

**WebSocket — `wss://api.hyperliquid.xyz/ws`:**
| Channel | Use |
|---|---|
| `userFills` (per address) | **the copy trigger** — fires within milliseconds of the target's fill, includes PnL |
| `userEvents` | consolidated fills + funding + liquidations |
| `orderUpdates` | order lifecycle |
| `clearinghouseState` | live position/margin pushes |
| `trades` (per coin) | every execution **with the trader's address** — the primary address-discovery method |
| `allMids`, `l2Book`, `bbo`, `candle` | pricing/feeds |

**Execution — `POST https://api.hyperliquid.xyz/exchange`:**
- Actions are **EIP-712 signed**; `nonce` = current Unix ms.
- **API wallet (`approveAgent`): trade-only sub-wallet that cannot withdraw** — the non-custodial pattern every serious bot uses.
- **Subaccounts/vaults:** query with the actual sub-account or vault address, not the master.
- **Rate limits:** ~1200 weight/min per IP; most info endpoints cost ~20 weight (≈1 req/sec sustainable). Scanning thousands of addresses needs proxy rotation.
- Fees (secondary source, MEXC comparison): ~0.015% maker / 0.045% taker on BTC perp.

**The canonical mirror loop (as implemented by jonny-traders, below):**
1. Subscribe `userFills` for the target → event gives `coin`, `dir` (Open/Close Long/Short), `sz`, `px`, `startPosition`, `side`.
2. On open: `copySize = fill.sz × SIZE_MULTIPLIER`, capped by max-notional and (optionally) Kelly stake.
3. On close: `closePercent = fill.sz / |startPosition|`; close the same % of your position — stays in sync through partial exits.
4. Sync leverage to the target's (capped), execute as **IOC limit orders with a slippage buffer** (behaves like a market order).
5. **Reconcile every N seconds:** fetch both sides' `clearinghouseState`; close anything the target flattened that you still hold; warn on size drift.

### 2b. Reference implementation: jonny-traders/hyperliquid-trading-bot-386
- **Link:** https://github.com/jonny-traders/hyperliquid-trading-bot-386 (TypeScript, `@nktkas/hyperliquid` SDK)
- Implements the full loop above plus: **Kelly sizing** (fractional-Kelly stake from a rolling window of the target's realized closes; *never sizes above the mirror; skips opens when measured edge ≤ 0*), per-position stop-loss monitor, daily-loss circuit breaker (pauses to midnight UTC), per-coin serial task queue (concurrency safety), graceful shutdown (optional close-all), structured logging, testnet-first config. This is the single best open-source template for a Hyperliquid copier.

### 2c. Reference implementation: gharrr544/hyperliquid-copy-trading-bot
- **Link:** https://github.com/gharrr544/hyperliquid-copy-trading-bot/blob/HEAD/README.md
- Adds: `mirror_delay_ms` (deliberate delay to avoid front-running-detection patterns — interesting anti-detection idea), coin whitelist, max-notional-per-trade, L2/mid/candle feeds, kill switch, performance dashboard (equity curve, PnL distribution).
- **Flag:** its README advertises specific PnL figures (+$7,890, 63.7% win rate, Sharpe 1.95) — **self-reported marketing, unverified**. Take the architecture, not the numbers.

### 2d. Native vaults (the no-code alternative)
- **HLP** (protocol vault: market-making + liquidations, ~7% of platform fees to depositors, **4-day lock**).
- **User vaults:** anyone can create one; leader gets **10% of profits**; leader must keep **≥5% ownership** (skin in the game); depositors face a **1-day lock**. Creation reportedly costs a **10,000 USDC protocol fee** (Sep 2026 review; the community wiki separately lists a 100 USDC minimum deposit to initialize — likely both: a creation fee plus a minimum deposit). Copying a vault = depositing, no bot needed, but you inherit the leader's exact entries/exits with zero latency and zero code.
- **Copy services:** HyperCopy (filters: WR>75%, scalpers/whales/holders), **Copin.io** (2M+ profiles, 26-criteria percentile scoring: PnL, ROI, win rate, volume, duration, drawdown, leverage, profit factor), HypurrScan, ASXN Hyperscreener, HyperDash, PvP Trade (Telegram), BitMEX's Hyperliquid copy product (cross-exchange replication).

### 2e. Address discovery (no public leaderboard API exists)
1. **WS `trades` monitoring** on high-volume coins → accumulate address→fill counts (recommended method).
2. Undocumented `stats-data.hyperliquid.xyz/Mainnet/vaults` → ~8000 vault leader addresses.
3. Third-party scraping (Copin, HyperCopy, HypurrScan); leaderboard UI needs browser automation.

---

## 3. Ideas worth stealing (7)

1. **Continuous wallet scoring with a mirror threshold** — *from rezzecup (0–100, rescore every 6h, mirror only ≥65) and Copin.io (26-criteria percentile scoring).* Our scorer already does FIFO realized PnL; add win rate, profit factor, max drawdown, and trade-duration percentiles, and make the COPY/FADE line a score, not a one-time verdict.
2. **Proportional close logic** — *from jonny-traders:* `closePercent = fill.sz / |startPosition|`, close the same % of your own position. This is how you stay in sync through partial exits instead of binary in/out.
3. **Reconciliation loop** — *from jonny-traders:* every N seconds, diff your positions vs the target's `clearinghouseState` (or token balances on Solana) and auto-close drift. The safety net for every missed event, dropped websocket, or reverted tx.
4. **Kelly sizing as a cap from measured edge** — *from jonny-traders:* fractional-Kelly stake computed from the target's rolling realized closes; it only ever *shrinks* a copy and skips opens when edge ≤ 0. Turns "follow the whale" into "bet proportional to proven edge."
5. **Single-operator clustering** — *from million's `/find-first-whales`:* merge wallets that enter the same tokens together into one vote. We already proved this matters (one funder EOA behind 6 "whales"); a copier that treats them as independent over-bets one signal 6×.
6. **Paper-first + shadow positions + decision logs** — *from million and rezzecup:* paper mode default; price every *skipped* signal as a shadow position; log the reason for every action. This is what makes the strategy improvable instead of a black box — and it matches the paper-trade gate in our design.
7. **MEV-aware submission rails** — *from the Solana speed-stack pattern (Geyser `transactionSubscribe` + Jito/private bundles) and the @outputlayer lesson:* split the problem into observation feed vs. submission rail. On Solana, the edge is landing 0–1 slots after the signal via private rails, not just seeing it fast. On Hyperliquid the analogue is WS `userFills` (ms) + IOC orders with slippage buffer.

**Honorable mentions:** non-custodial execution (Hyperliquid API wallet / Solana keypair on your own disk — never a hosted key); slippage tiers by wallet rank (rezzecup); consensus signals requiring multiple distinct wallets (million); token gauntlet filters incl. Jupiter sell-simulation and RugCheck (million); `mirror_delay_ms` anti-detection (gharrr544); per-coin serial queues for concurrency safety (jonny-traders).

---

## What could not be verified
- Star counts for jonny-traders, gharrr544, rdin777 (not shown in fetched pages); million = 4 stars/308 commits, rezzecup ≈ 10 stars, ddewhun = 1 star per page metadata.
- Whether the nexus-tracker/curve-tracker/ledger-tracker repos contain real code (not opened; flagged as likely auto-generated — pattern only).
- gharrr544's advertised PnL figures (self-reported, treat as marketing).
- Hyperliquid fee numbers (secondary source); vault 10,000 USDC creation fee (one Sep 2026 review; wiki says 100 USDC minimum deposit — reported both).
- Exact current Hyperliquid rate-limit weights (1200 weight/min per IP from the research doc; verify at implementation time).
