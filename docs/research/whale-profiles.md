# Deep-profile of the operator's top 7 copy targets (2026-10-02)

Source: Blockscout API v2 via live browser (read-only). Coverage to block 77,996,388 (2026-10-02T05:52:26Z). USDG figures are observed on-chain quote legs (USDG rate 1.0); ETH figures native, converted only at explorer-displayed rates where cited. Buys paired to sells FIFO per token contract. Win rates/PnL computed on the priced subset only; priced subset stated per wallet, everything else counted-but-unpriced.

## HEADLINE FINDING

These are not 7 independent whales. Every Relay buy priced for wallets 1, 2, 3, 4, 5 AND 7 was funded by the SAME EOA, **0xf70da97812CB96acDF810712Aa562db8dfA3dbEF**, sending USDG into RelayRouter. They trade in lockstep: wallet 7 bought XRAY 15 seconds before wallet 2's XRAY buy (2026-10-02 ~02:15Z); wallet 6 (the only non-Relay wallet) bought IRIS and ZIP exactly one block after wallet 5's buys. The operator is mirroring **one bot fleet**, not seven independent smart-money wallets — copying adds no diversification.

**Fleet-wide priced realized PnL ≈ −5,095.82 USDG** across 34 priced USDG episodes (wallet 2's two partial closes are pro-rata estimates), plus wallet 6's small ETH subset (+0.004666594887 ETH ≈ +$12.4–12.7 at explorer-displayed rates). The operator's public claim (+$21.3k realized, 45/53 green) is **not supported** by the whales' own closed records.

## Wallet 1 — 0x8A71697cc8a6E820C0bc12B29C1b329C3ab6599b — AVOID
Coverage: 100 transfers, blocks 75,795,219–77,636,784 (2026-09-29 to 2026-10-01).
14 closed episodes identified, 11 priced; 1 open (VRAX-B). Win rate (priced): **1/11 = 9.1%**. Realized PnL (priced): **−5,099.502821 USDG**. Median hold ≈ 51 min (10m–~9h). Tickets: rigid fixed sizes ~497.25 / ~994.5 / ~1,989.1 USDG.
Copied-token outcomes (all 9 net RED): STEER −678.31 (−68.2%); DOTARENA −317.47 (−31.9%); ROBOT −1,126.48 (−90.0%); DOTTIE net −174.90 (ep 1 +788.57/+39.6% GREEN — the wallet's only green priced episode — then ep 2 −963.47/−48.4%); ZIP −629.76 (−28.8%); ZUPITER −419.66 (−42.2%) and −889.66 (−44.7%); GITPAD −503.63 (−56.9%); STONKCALL −163.25 (−32.8%); SIGIL −196.38 (−34.3%).
**Verdict: AVOID — the operator's most-copied wallet (9x) is its worst.**

## Wallet 2 — 0x23ad4067aF541ee28c7f5c69Eff348139Beb7BD8 — MARGINAL
Coverage: 200 transfers, blocks 76,317,006–77,887,212.
5 priced episodes (3 full closes, 2 partial); large open inventory. Win rate: **4/5 = 80%**. Realized PnL: **≈ +664.65 USDG**. Median hold ≈ 20 min (36s–1h14m). Tickets ~497–995 USDG (TANK open buy 1,861.84 outlier).
Copied tokens: DOTS +49.09 (+4.9%, GREEN, 36s); TIDE lot 1 +167.07 (+33.6%, GREEN; 11.92M TIDE still open); MTA partial ≈ +391.88 (+120.5% pro-rata — ESTIMATE; 19.52M still open); WAVE partial ≈ +318.54 (+233.7% pro-rata — ESTIMATE; 12.46M still open); XRAY −261.92 (−22.1%, RED); TANK OPEN (buy 1,861.835977); PONSHI OPEN (875.848584); DOTTIE OPEN (3 buys, costs not fetched); VLADBOT NOT FOUND in 200 transfers (gVLAD is a different token — gap).
Note: ~9.81M VRAX-B accumulated over 12 buys, then plain-transferred to 0xf2439241881964006369c0e2377D45F3740f48a0 (inter-wallet move, not a market exit).
**Verdict: MARGINAL — the only net-green realized record; best of the seven, but most capital still in unresolved open positions.**

## Wallet 3 — 0x0B64C0469Be9502A45c79840e180842463189327 — AVOID
Coverage: 200 transfers, blocks 73,124,766–77,956,075.
62 closed positions counted; 10 priced. Win rate: 2/10 = 20%. Realized PnL: **+12.332363 USDG** (positive only via ERRAND #2 +121.1% and VRAX-B #2 +37.1% outweighing eight small reds). Median priced hold ≈ **26 seconds** (6s–4h14m). Tickets ~9.79–13.87 USDG (~$10).
Copied tokens: DRAGON and bankme NOT FOUND here (actually wallet 4's trades — operator attribution for wallets 3/4 looks swapped). VRAX-A #1 −4.2%, Suited #1 −5.1% / #2 −2.3%, ZKHUB −0.15%, Watermelinu −6.2%. Also traded ERRAND/HARMONIC (attributed to wallet 4): ERRAND #2 +121.1%.
~52 further closes counted-but-unpriced; nearly all exact-quantity round trips held 6s–2m.
**Verdict: AVOID — seconds-scale ~$10 flipper; net is fee-dust, unreplicable.**

## Wallet 4 — 0x453f238A896538cA9560004500Af1392C7889875 — MARGINAL
Coverage: 150 transfers, blocks 72,287,517–77,761,350.
15 closed episodes; 3 priced. Open: DRAGON buy (299.331723 USDG). Win rate: 2/3 = 67% (tiny sample). Realized PnL: **+162.410671 USDG**. Median priced hold 3m42s. Tickets ~250–499 USDG.
Copied tokens: ERRAND/HARMONIC NOT FOUND here (they're wallet 3's). Its one genuinely-attributed copied token, DOTSPAD, closed RED −121.549074 (−24.4%, 9m39s). bankme (attributed to wallet 3, actually here) GREEN +118.824321 (+47.6%); APPSHARE +165.135424 (+33.1%); DRAGON OPEN.
12 of 15 closes counted-but-unpriced.
**Verdict: MARGINAL — small positive sample at copyable sizes, but its only truly-copied token lost −24.4%.**

## Wallet 5 — 0xbDcE13a1caDEa23a61013Fbfb470c7eEF4bA9520 — AVOID
Coverage: 100 transfers, blocks 76,367,352–77,976,638.
5 closed episodes, all priced. Win rate: **0/5 = 0%**. Realized PnL: **−822.725078 USDG**. Median hold 31m29s. Tickets ~237–1,445 USDG.
Copied tokens: ZIP −401.510211 (−27.8%); IRIS −14.189235 (−6.0%); VRAX unmatched sell (buy below window, unscored). Non-copied closes also all red: revenue −24.51, AVM −308.46, PAR −74.05. Accumulator: 24 buys vs 6 sells on page 1; open SCROOGE (6 buys), HOODIE (5), BOW (3).
**Verdict: AVOID — proven loser on the fully priced set.**

## Wallet 6 — 0x4189BF4fA87Df00DfFe5dEe85339747F615beAD4 — AVOID (structure)
Coverage: 100 transfers, blocks 76,258,135–77,996,388. Plain EOA direct with PoolManager via UniversalRouter — no Relay, no funder EOA.
40 closed episodes, zero open in coverage. Priced sample: 6 episodes, 2 green.
PnL (per asset, never summed): USDG subset **−12.982444 USDG** (PONS2 −6.7%; Suited −19.6%; VRAX-B −43.6%); ETH subset **+0.004666594887 ETH** (ZKSTR +0.004358471489/+43.6%; SCORE +0.000789523680/+7.9%; STRATTON −4.8%) ≈ +$12.4–12.7 at explorer rates.
Median hold 3m00s. Fixed tickets: exactly 27.000000 USDG, 13.500000 USDG, or 0.010000 ETH; holds 1s–~3m — a mechanical bot.
Copied tokens BOTH GREEN (ZKSTR +43.6%, SCORE +7.9%) — the operator's two best outcomes anywhere. GMECHAIN left unpriced (multi-user stock-token settlement hops).
**Verdict: AVOID as a copy target — genuinely green on its copied pair, but $13.50–$27 tickets and 1s–3m holds make the edge structurally uncopyable.**

## Wallet 7 — 0xf4d8eFcfEA218cE76BfDE064a2Be406345eA5ba6 — AVOID
Coverage: 100 transfers, blocks 76,654,316–77,975,602.
8 Relay buys, 15 Relay sells, ZERO fully closable positions in coverage (every sell's buy predates the window; every in-window buy still open). Win rate/PnL: NOT MEASURABLE.
Copied tokens: XRAY OPEN (buy 998.761249 USDG, block 77,867,512 — 15s before wallet 2's XRAY buy, which closed −22.1%); PARLEY OPEN (buy 2,823.412414 USDG, block 77,330,249). Both funded by the shared fleet funder.
Behavior: distributing older inventory (UBIK sold in 9 txs; ~7.04M VECTIS sold vs 11,902 in-window buy; CHEF, SI sells) while the operator copies its new buys.
**Verdict: AVOID — no profitability evidence; copying means buying alongside a net distributor.**

## Overall ranking (best → worst as copy targets)
1. **Wallet 2** — MARGINAL. Only net-green record (≈ +664.65, 4/5). Caveats: unresolved open inventory, partial-close estimates, VLADBOT unfound.
2. **Wallet 4** — MARGINAL. +162.41 on a tiny sample; its truly-copied token lost −24.4%; 12/15 closes unpriced.
3. **Wallet 6** — AVOID (structure). Copied pair green, but $27 tickets / 3-min flips uncopyable.
4. **Wallet 3** — AVOID. +12.33 is fee-dust; ~$10 tickets, ~26s holds; operator attribution demonstrably wrong here.
5. **Wallet 7** — AVOID. No closed evidence; net distributing.
6. **Wallet 5** — AVOID. 0/5 green, −822.73.
7. **Wallet 1** — AVOID, strongest negative. 1/11 green, −5,099.50; all 9 copied tokens net red — yet copied most (9x).

## Explicit gaps/caveats
1. Operator attributions for wallets 3↔4 appear swapped (DRAGON/bankme live in wallet 4; ERRAND/HARMONIC in wallet 3).
2. VLADBOT absent from wallet 2's 200 transfers (gVLAD ≠ VLADBOT).
3. Wallet 5's VRAX and wallet 7's UBIK/VECTIS/CHEF/SI sells have buys below coverage — unscored; wallet 7 has no closed PnL evidence at all.
4. Wallet 2 MTA/WAVE PnL are FIFO pro-rata estimates on partial closes; remainders still open.
5. Unpriced-but-counted: wallet 1 DOTSLNCH/VRAX-A/DOTS; wallet 4's 12 closes; ~52 of wallet 3's 62; 34 of wallet 6's 40; wallet 2 DOTTIE buy costs; wallet 5 SCROOGE/HOODIE/SI legs. Wallet 6 GMECHAIN deliberately unpriced (ambiguous settlement).
6. Wallet 6's ZKSTR sells exceeded buy quantity by 0.06 tokens (rounding residual).
7. Method: for Relay wallets, address-level transfers show only the memecoin leg; quote legs recovered per-tx from /api/v2/transactions/{hash}/token-transfers (buy = first USDG leg, funded EOA → RelayRouter; sell = USDG leg ending at RelayDepository). Wallet 6 priced from tx value + PoolManager/router internal transfers.
