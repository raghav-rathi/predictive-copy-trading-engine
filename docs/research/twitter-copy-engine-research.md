# Copy-Trading Engine Research — Twitter/X Track (2026-10-02)

Method: X native search requires login, so builders were discovered via Startpage/DuckDuckGo indexing plus direct x.com post/profile URLs (render logged-out). Paid-group promoters and affiliate shillers excluded; only builders with real mechanics listed.

## 1. @kei_4650 (Kei Novak) — STRONG
- Built: open-source Rust Solana copy-trading bot mirroring wallets across DEXs.
- Links: https://x.com/kei_4650 · https://github.com/keidev-sol/Solana-Copy-Trading-Bot-Rust
- Key ideas: (a) YellowStone gRPC feed for mempool/pending txs; (b) per-DEX instruction reconstruction via Anchor PDAs — Pump.fun, LaunchLab, Raydium AMM/CPMM/CLMM, Pumpswap; (c) "0-block copy execution": same-block or next-block inclusion with pre-calculated compute-unit budgets and tip pricing; (d) resilient signature watcher with dedup + cooldowns; (e) full lifecycle pipeline: detection → validation → instruction reconstruction → simulation → send → confirmation; (f) auto-sell engine: TP 10%, SL 5%, trailing SL, lifetime-based exits (30s default), price monitoring every 5s; (g) multiple send services (Nozomi, ZeroSlot, Jito).
- Claimed: ~500ms start-to-submit; txs confirmed <2ms after slot. Evidence: strong — real Solscan example links in README + full open-source code.

## 2. Maximilian Aigner (GitHub: MaxIsOntoSomething, Discord: maskiplays) — STRONG code, no PnL
- Built: open-source Python Hyperliquid copy trader ("real-time monitoring and smart position sizing").
- Link: https://github.com/MaxIsOntoSomething/Hyperliquid_Copy_Trader (44 stars, 19 forks)
- Key ideas: (a) real-time copying via WebSocket (not polling); (b) TARGET_WALLET accepts a wallet OR a Hyperliquid vault address — copies vault-managed positions directly; (c) auto position sizing from account-balance ratio; (d) copies existing positions on startup so follower state matches leader; (e) risk controls: MAX_OPEN_TRADES cap, blocked assets, leverage scaling (0.5x/1x/2x); (f) simulated trading mode + Telegram notifications.
- Claimed: none (no backtest/PnL). Evidence: strong (code), weak (performance).

## 3. Anonymous Solana trading team (via RPC Fast vendor case study) — MEDIUM
- Built: production Rust copy-trading bot, Solana.
- Link: https://rpcfast.com/blog/copy-trading-bot-case-study
- Key ideas: (a) YellowStone gRPC account stream filtered by target wallet(s); (b) Jito shred stream for pre-vote data (fastest public Solana source); (c) co-located infra near validators (Frankfurt) for sub-50ms gRPC latency; (d) multi-path landing: race the same tx through Helius Sender, bloXroute, QuickNode Fastlane simultaneously; (e) dynamic "Smart Transaction" tip pricing; (f) monitoring + simulation + retry loops around every send.
- Claimed: best-case landing 15ms, typically 200–300ms; same-slot or +1 slot. No PnL; vendor-authored, anonymous client. Evidence: medium.

## 4. Dwellir / Elias Faltin — MEDIUM-STRONG
- Built: open-source Python Hyperliquid copy-trading bot (tutorial/reference).
- Link: https://www.dwellir.com/blog/hyperliquid-copy-trading-bot-python (code: github.com/dwellir-public/gRPC-code-examples)
- Key ideas: (a) gRPC StreamFills feed → fill processor: wallet filter → dedup via fill hash + trade ID → open-vs-close detection; (b) position sizing as % of account value with $10 minimum; (c) slippage tolerance config; (d) CRITICAL: sync positions before reduce-only closes so follower closes match leader state; (e) dry-run mode, coin filters, multiple instances per wallet.
- Claimed: none (educational). Evidence: medium.

## 5. @slash1sol (Spottr founder) — MEDIUM
- Built: Spottr — copy-trading infra on Polygon with direct node + direct mempool reads for sub-second latency; long X thread arguing "the entire Polymarket copy trading meta is built on a metric that doesn't [work]."
- Link: https://x.com/slash1sol
- Key ideas: (a) public win-rate/ROI leaderboards are misleading for wallet selection — need metrics that predict future edge, not past luck; (b) speed stack: direct node + mempool reads for sub-second execution; (c) copy-trading is a wallet-scoring problem, not a speed problem.
- Claimed: none. Evidence: medium (operator insight, no hard numbers).

## 6. @stacy_muur (Stacy Muur, researcher) — CONTEXT ONLY
- X thread "The Secret Sauce of Hyperliquid" (Mar 8, 2025) documenting native copy-trading via Vaults: anyone can create a vault, depositors browse by performance, 10% profit share to the manager.
- Link: https://x.com/stacy_muur/status/1898307251233780079
- Evidence: medium (accurate explainer; no build).

## 7. CopyGrade (copygrade.com) — MEDIUM
- Copy-trading due-diligence tooling; "How to vet a wallet before you copy it" + CopyGradeScore. Polygon/EVM (Polymarket-focused; methodology generalizes).
- Link: https://copygrade.com
- Key ideas: (a) vet wallets before copying — score, don't blind-copy; (b) criteria: win-rate distribution, bet counts, trade-size distribution, ROI per bet, wallet type/age; (c) portfolio view: correlated wallets = single point of failure.
- Evidence: medium (methodology, no independent audit).

## 8. Reddit r/algotrading anonymous builder — MEDIUM (not X; included for mechanics)
- Thread: "Built my own copy trading bot for hyperliquid. 10 things i learned" (Jul 24, 2026).
- Key ideas: (a) entry latency is a red herring — worse fills come from position fragmentation + size, not speed; (b) fragmentation: leaders' entries arrive as many small fills, naive copy logic misfires; (c) stop-loss discipline decides outcomes; (d) copy size relative to account; (e) fees eat edge; (f) leverage magnifies mistakes; (g) wallet selection > speed; (h) exits are where money is made; (i) Hyperliquid quirks (funding, cross margin).
- Evidence: medium-weak (claimed experience, no verifiable PnL).

## 9. Teraus (Medium @Teraus) — WEAK
- "How I Built a High-Performance Polymarket Copy Trading Bot in Rust" (Mar 3, 2026); headline mechanic: "4-layer circuit breaker". Article URL 404'd, unverifiable; no X handle found.

## Deprioritized
Affiliate/promo accounts with no technical substance: @dextrabot, @OdinBot, Apexliquid_bot, DexAiTrading, TradeWiz promos, CopyCat_Bot, dextools.io promo threads.

## Synthesis — 5 best ideas to steal
1. Detect from the mempool/shred stream, not confirmed blocks. Speed is won at ingestion: YellowStone gRPC (+ Jito shred pre-vote on Solana; StreamFills/WebSocket on Hyperliquid). Polling confirmed blocks = always last. (rpcfast, kei_4650, Dwellir)
2. Decode per-venue instructions, don't generic-parse. kei_4650's per-DEX Anchor-PDA reconstruction is what makes mirroring accurate; on Hyperliquid, distinguish opens vs closes from fills and sync follower state before reduce-only closes. (kei_4650, Dwellir)
3. Race multiple execution paths with dynamic pricing. Multi-path landing (Helius Sender + bloXroute + QuickNode), pre-calculated CU budgets, dynamic smart tips. ~500ms start-to-submit / 15–300ms landing achievable. (kei_4650, rpcfast)
4. Score wallets and guard with circuit breakers, not blind copying. Leaderboards mislead (slash1sol); vet on win-rate distribution, bet counts, size distribution, wallet age (CopyGrade); cap open trades, scale leverage down, hard-kill on drawdown. Wallet selection >> raw speed. (slash1sol, CopyGrade, Reddit builder)
5. Copy sizing math, not trade-for-trade. Size as % of account with minimum notionals, expect fragmentation (one leader entry = many small fills), dedup by fill hash/trade ID, run the exit engine separately (TP/SL/trailing/time-based). Exits are where money is made. (Dwellir, MaxIsOntoSomething, kei_4650, Reddit builder)
