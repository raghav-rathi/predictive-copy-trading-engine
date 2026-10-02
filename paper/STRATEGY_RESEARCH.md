# Hyperliquid Strategy Research — Beyond "Mirror Good Vaults"

**Date:** 2026-10-02
**Question:** how do the best Hyperliquid copy-traders/systems actually make money, and what concrete, implementable edges exist beyond our current mirror engine?

**Where our engine stands (context for ranking):** mirror scored vaults (gate ≥65, ≥10 closed trades), Kelly 0.25, trailing 2% / SL 8% / TP 20% / 24h max-hold. True-PnL 30d backtest: **+$220.21 per $10k, 3,716 trades, 55.7% WR** (~$0.059 net/trade). Exit-mix analysis: **our trailing exit is the profit engine (+$214.28, 277 legs) vs the targets' own exits (−$5.73, 3,380 legs)**. Per-coin edge concentrates in alts (PONS/SUI/VVV/CASHCAT/LIT/ZEC/ENA/HYPE); majors flat-negative. Gate validated (rejected shadows lose in every run). Fade trigger (≤30) never fired in 248 vault-days — untestable as designed.

**Already in progress on parallel tracks (not duplicated here):** target expansion 4→12–15 vaults; parameter/coin grid search (trailing/TP/coin filters).

**Method:** GitHub (open-source bots, research repos), web (fee/funding mechanics, HLP economics, liquidation design), social (IG/Threads/FB sweep — found only promo content, zero quant signal; the serious material is all on GitHub/web).

---

## Ranked ideas (impact × feasibility)

### 1. Maker / post-only copy entries — [Impact: HIGH | Feasibility: MEDIUM]

**Thesis.** Our backtest assumes taker entries (0.035% fee + 0.02% slippage per side). Hyperliquid's base schedule is 0.045% taker vs 0.015% maker — a 3× gap. If copy entries used post-only limits priced at/near the target's fill price instead of IOC taker orders, entry costs fall roughly half, which against a ~$0.059/trade net edge is material on every trade that fills (exact uplift depends on average notional — the paper experiment will measure it).

**Evidence.** Fee schedule documented across sources (0.045% taker / 0.015% maker base; tiers + HYPE staking lower it further). The dropstab 2026 study (100,236 copy trades: **48.48% of followers profitable vs 97% of leaders**) shows execution is where copy strategies bleed — followers don't lose on signal, they lose on fill. Every open-source copy bot surveyed (jonny-traders, gharrr544) uses IOC-with-slippage-buffer = taker-like execution; **no public bot does post-only copy entries — the gap is open.**

**Build/change.** Add an execution mode to `mirror.py`: on signal, post a post-only limit at the target's fill price (or 1 tick favorable); if unfilled after N seconds (tune 5–30s), fall back to IOC. Paper-test both modes side by side measuring fill rate, realized price improvement vs target fill, and missed-trade regret.

**Key risk.** Adverse selection: resting limits fill when price moves against us and miss when it runs away — we could systematically miss the target's best trades while catching their worst. This MUST be validated by a fill-rate experiment before going live; if fill rate < ~70% or missed-trade regret exceeds fee savings, kill it.

### 2. Walk-forward target management — persistence defense — [Impact: MEDIUM-HIGH | Feasibility: HIGH]

**Thesis.** The strongest empirical work on copy-trading says past PnL does not predict future PnL. Our 30d backtest edge could be regime luck. The structural defense: require every target to re-clear the gate on rolling walk-forward windows and auto-pause it when its live paper PnL decays — turning target selection from a one-time screen into a continuous re-validation loop.

**Evidence.** alorse/copy-trading-intel (FINDINGS.md): out-of-sample test, n=59 traders — **win rate persists (rho +0.805) but expectancy does NOT (rho +0.136)**; win rate vs payoff corr −0.497 (a style trade-off, not skill). kelbic/crypto-copytrade-research: **0/40 top-leaderboard wallets passed** a validation pipeline (kill criteria + 3× cost scenario + permutation test) for naive copy-trading. Our own fade test: stale-leaderboard "loser" songer1993.hl made **+$25.6k at 62% WR** the next 30d — regimes flip both ways.

**Build/change.** (a) Walk-forward harness: score each target on rolling 30d windows; require gate clearance in the two most recent windows (2-window confirmation) before (re)admission. (b) Auto-pause: if a live-copied target's trailing paper PnL goes negative over X days, stop opening new copies until it re-clears. (c) Tag every ledger row with a BTC regime label (trending/ranging) so we learn which regimes the edge lives in.

**Key risk.** Over-filtering: too-strict re-validation can leave zero eligible targets (Aquila already gets skipped entirely today); regime flips cause whipsaw in/out. Start with pause-not-purge and wide windows.

### 3. Delta-neutral funding farm as a second, uncorrelated book — [Impact: MEDIUM | Feasibility: MEDIUM]

**Thesis.** Separate from the copy engine, run short-perp + long-spot on the highest 7-day-average-funding coins. Hyperliquid funding is positive ~99% of hours on majors — this harvests it market-neutrally, uncorrelated to the directional copy book.

**Evidence.** The most battle-tested Hyperliquid-native strategy in the open: djienne/delta_neutral_hyperliquid_perp_spot (2 years of funding history calibrated; switches only when expected gain beats 4-leg costs, ~12 APY-point gap); srono's fork; second-state/fintool funding_arb; **Harmonix's USDC-HYPE delta-neutral vault live at 8–15% APY**; Pendle built Boros specifically to productize cross-exchange funding arb. Funding math: BTC +0.00119%/hr ≈ 10.4% APR, ETH 10.6%, SOL 8.6% (IvPalmer/Master-Trader, 60d, n=500/asset).

**Build/change.** New module outside the copy path: hourly funding scan → rank by 7d avg → 1x short perp + long spot on top 1–2 coins → switch only when (candidate 7d avg − held 7d avg) × horizon > 4-leg costs → close if 7d avg turns negative. Paper-test 30d first. Capital-split decision vs copy book comes after paper numbers.

**Key risk.** Funding regime flips (sustained bear = negative funding = the farm bleeds); spot-perp basis risk; two-leg execution complexity; returns are yield (8–15% APY), not alpha — it diversifies, it doesn't 10x.

### 4. Funding-aware accounting + short tilt — [Impact: LOW-MEDIUM | Feasibility: HIGH]

**Thesis.** Funding is positive ~99% of hours, so every copied long pays ~10% APR and every copied short earns it. At our ~5h average hold that's ~0.006%/trade — small but systematic and currently unmodeled; on 24h max-hold positions it's ~0.03%, material against a $0.059/trade edge.

**Evidence.** Same funding measurements as above (10.4%/10.6%/8.6% APR, positive 99%/100%/92% of hours). The IvPalmer analysis: "the often-cited 'shorts get paid' advantage is real for carry strategies measured in weeks; noise for a 36-hour directional trade" — our holds sit between those poles, so model it rather than assume.

**Build/change.** (a) Add hourly funding payments (rate × notional × hold hours, signed by side) to the paper ledger and backtest — honest accounting first. (b) Add a small funding term to the scorer: reward short-heavy wallets, penalize long-heavy ones on high-funding coins. (c) Optional: skip copying longs on coins with extreme funding (>0.01%/hr).

**Key risk.** Effect size is small; alt funding is noisier than majors; adds scoring complexity for what may be ~1–2% annualized drag reduction. Do (a) regardless — it's correctness; (b)/(c) only if (a) shows it matters.

### 5. Fee-tier optimization — [Impact: LOW (but free) | Feasibility: TRIVIAL]

**Thesis.** Our backtest assumes 0.035% taker, already below the 0.045% base — but the actual account tier should be verified and every available discount captured. Fees are $36.72/30d on the current book; a 10–20% fee cut is $4–7/month of pure edge for zero strategy risk.

**Evidence.** Documented fee schedule: 14-day volume tiers + HYPE staking discounts + referral discounts (open-source bot READMEs cite ~10% referral fee reduction). `userFees` API returns the account's actual tier.

**Build/change.** Pull `userFees` for the live account; plug the REAL tiered rate into the backtest instead of the assumed 0.035%; ensure the account is registered under a referral code; evaluate HYPE staking for tier discounts once volume qualifies.

**Key risk.** None, it's free money. Just small.

### 6. Fade redesign — downgraded on evidence — [Impact: LOW-MEDIUM | Feasibility: MEDIUM]

**Thesis (weakened).** Fading persistent losers is the mirror image of our validated gate. But two findings cut against it: (a) our fade trigger never fired in 248 vault-days and ~25/100 score points are free to any active wallet — the ≤30 gate is unreachable as designed; (b) the alorse persistence result is symmetric — if winners' expectancy doesn't persist, losers' expectancy likely doesn't either, and we watched a "loser" (songer1993.hl) print +$25.6k the next month.

**Evidence.** For: HyperAlpha markets a "Reverse Mode" fade product (marketing claim, **zero verifiable numbers** — treat as existence proof of the idea, not of edge). Against: alorse symmetry argument; our own recovery observation; kelbic's 0/40 (naive strategies fail both directions).

**Build/change (only if pursued).** Redesign the fade gate from scratch: score on unrealized-PnL-aware metrics (losers who never take profit), lower the bar to ≤45 with a leverage filter (degenerate leverage is the documented loser trait — "win small many times, one liquidation wipes it"), and require the fade book to paper-trade 30d before any capital.

**Key risk.** Fading has all of mirroring's costs plus short-squeeze tail risk on the fade shorts; the evidence base is the thinnest of any idea here. This is a research project, not a near-term edge.

### 7. Cross-venue funding arb (HL vs Pacifica/Binance) — [Impact: MEDIUM | Feasibility: LOW-MEDIUM]

**Thesis.** Same-coin funding differs across venues (documented example: HL 10% vs Pacifica 50% APR). Long the low-funding venue + short the high-funding venue captures the spread delta-neutrally, with more spread than single-venue farming.

**Evidence.** djienne/cross_exchange_delta_neutral_hyperliquid_pacifica is live open-source; Pendle's Boros + CrossEx product exists specifically for 4-leg fixed-rate arb (short HL funding / long Binance funding on Boros + offsetting perps = locked spread to maturity).

**Build/change.** Accounts + collateral on two venues, hourly spread scan, basis monitoring, coordinated execution. Strictly after the single-venue farm (idea 3) is proven — it's the same trade with more moving parts.

**Key risk.** Cross-exchange margin/counterparty complexity; spreads compress as arbers arrive; needs meaningfully more capital to matter. Complexity risk dominates.

---

## Rejected ideas (evaluated, cut)

| Idea | Why cut |
|---|---|
| **Liquidation-flow participation ("be the house")** | HLP's edge (41% of lifetime profit from 2 events; +$15M on the 1011-whale liquidation) is structural — it's the designated backstop with a dedicated liquidator vault (0x2e3d…94d). "Anyone can compete for liquidation flow," but we'd be competing against HLP/HFT on latency with a 30-min cadence. We'd be the flow being harvested, not the harvester. |
| **Whale stop-hunting** | Real phenomenon (10x Research: "democratized" stop-hunting via HL transparency), but it's coordinated/predatory, needs real-time whale monitoring + size to move markets, legally gray. Not a bot we build. |
| **Copying HLP's MM flow** | HLP runs market-making + liquidation strategies, not directional trades — there's nothing to "copy" that isn't just paying spread. Depositing into HLP (7% trailing APR, 15–35% historical) is a yield decision, not an edge. |
| **Latency arb on Hyperliquid** | No public mempool (HyperBFT sequencer) — the Robinhood-chain 0.5–1.6s heads-up mechanism doesn't transfer. Our WS `userFills` path is already near-instant; no further latency edge exists to buy. |
| **Naive leaderboard copying** | kelbic: 0/40 wallets passed validation after realistic costs. This is exactly what our scored gate + own exits improve on — the naive version is empirically dead. |
| **Multi-target direction consensus** | No external evidence; our single-operator clustering already handles the correlated-wallet case. Untested idea, park it. |
| **HIP-3/HIP-4 outcome-market MM** | Real (webclinic017's Rust Avellaneda-Stoikov bot), but it's a latency HFT game on prediction markets — different skill set, different infrastructure, no synergy with our engine. |

## Strategic risks the research surfaced (defensive reading)

1. **Non-persistence is the #1 threat to the 2%/mo.** alorse (expectancy rho +0.136 out-of-sample) + kelbic (0/40) both say: past PnL doesn't predict future PnL. Our edge could be a 30d regime artifact. Idea 2 is the direct defense; additionally, every future backtest should be walk-forward, not single-window.
2. **The follower execution gap is structural.** dropstab: 48.48% of followers profitable vs 97% of leaders across 100k copy trades. Our engine closes this gap with scoring + own exits (the trailing exit IS the alpha, per exit-mix), but it means any slippage in our own execution re-opens it — hence idea 1's priority.
3. **Retail's loss asymmetry bounds the fade dream.** iriton's DEX study: win rate ≈50% but avg loss > avg gain; "users cut winners early, let losers run until liquidation." Losers lose via liquidations — which are discrete, violent, and hard to fade cleanly (you're short into the same cascade). This is another reason idea 6 is downgraded.

## Suggested build order

1. **Now:** idea 5 (free) + idea 4a (honest funding accounting — correctness).
2. **Next:** idea 1's fill-rate experiment in paper mode (highest EV on the core book).
3. **In parallel:** idea 2's walk-forward harness (protects what we have).
4. **After:** idea 3's paper test (diversification, uncorrelated yield).
5. **Later/research:** ideas 6, 7.

---
*Sources: Hyperliquid fee schedule (datawallet.com, arx.trade); funding measurements (IvPalmer/Master-Trader 2026-08-29, n=500 obs); HLP economics (datawallet.com HLP explainer, KuCoin liquidation-alpha piece, hyperliquid-community wiki); copy-trading studies (alorse/copy-trading-intel, kelbic/crypto-copytrade-research, dropstab 2026); bots (djienne delta-neutral + cross-exchange, srono fork, second-state/fintool, jonny-traders copy bot, keitaj/hyperliquid-bot, webclinic017 HIP-4 MM, Harmonix vault docs, Pendle Boros docs); whale-hunting (10x Research via Cointelegraph); social sweep (IG/Threads/FB — promo content only, no quant signal).*
